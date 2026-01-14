from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from rest_framework.test import APIRequestFactory
from rest_framework import status
import json
import logging

from .models import Survey, Respondent
from .views import ShowFormView, SaveResponseView
from django.utils import timezone

logger = logging.getLogger(__name__)


def survey_list(request):
    """
    首頁：列出所有 is_open=True 的 surveys
    注意：因為沒有對應的 API，這裡直接查 DB
    """
    surveys = Survey.objects.filter(is_open=True).order_by('-created_at')
    return render(request, 'survey_list.html', {'surveys': surveys})


def survey_form_view(request, survey_id):
    """
    填寫問卷頁：透過 API 取得表單資料（模擬外部系統調用）
    """
    survey = get_object_or_404(Survey, id=survey_id, is_open=True)
    
    # 記錄開始時間（用於提交時）
    if 'started_at' not in request.session:
        request.session['started_at'] = timezone.now().isoformat()
    
    # 使用 DRF APIClient 調用現有 API（模擬外部系統）
    # 注意：要透過 DRF 的 dispatch 流程（as_view），才能正確套用 parsers/renderers 等設定
    factory = APIRequestFactory()
    api_request = factory.get(f'/api/show-form/{survey_id}/')
    api_response = ShowFormView.as_view()(api_request, pk=survey_id)
    
    if api_response.status_code != status.HTTP_200_OK:
        return render(request, 'survey_error.html', {
            'error': '無法載入問卷資料',
            'details': api_response.data if hasattr(api_response, 'data') else str(api_response)
        })
    
    survey_data = api_response.data.get('data', {})
    
    # 將 conditional_order 轉成 JSON 字串（用於 HTML data attribute）
    if 'questions_details' in survey_data:
        for question in survey_data['questions_details']:
            if 'conditional_order' in question and question['conditional_order']:
                question['conditional_order_json'] = json.dumps(question['conditional_order'])
    
    return render(request, 'survey_form.html', {
        'survey': survey,
        'survey_data': survey_data,
    })


def survey_submit(request, survey_id):
    """
    處理表單提交：透過 API 提交（模擬外部系統調用）
    """
    logger.info(f"survey_submit called with method: {request.method}, survey_id: {survey_id}")
    
    if request.method != 'POST':
        logger.warning(f"survey_submit called with non-POST method: {request.method}")
        return redirect('survey_web:survey_form', survey_id=survey_id)
    
    survey = get_object_or_404(Survey, id=survey_id, is_open=True)
    logger.info(f"Processing submission for survey: {survey.name} (ID: {survey_id})")
    
    # 取得或建立 respondent（從 session 或建立匿名）
    respondent_id = request.session.get('respondent_id')
    if not respondent_id:
        # 建立匿名 respondent（直接查 DB，因為沒有對應 API）
        logger.info("Creating anonymous respondent")
        respondent = Respondent.objects.create_user(
            username=f'anonymous_{timezone.now().timestamp()}',
            password=None
        )
        request.session['respondent_id'] = respondent.id
        respondent_id = respondent.id
    else:
        logger.info(f"Using existing respondent_id: {respondent_id}")
    
    # 收集表單答案
    responses = []
    logger.info(f"POST data: {dict(request.POST)}")
    for key, value in request.POST.items():
        if key.startswith('question_') and value:  # 只收集有值的答案
            question_id = int(key.replace('question_', ''))
            responses.append({
                'question_id': question_id,
                'answer': value
            })
            logger.info(f"Collected response: question_id={question_id}, answer={value}")
    
    if not responses:
        logger.warning("No responses collected from form")
        return render(request, 'survey_error.html', {
            'error': '請至少回答一題',
            'survey': survey,
        })
    
    logger.info(f"Total responses collected: {len(responses)}")
    
    # 使用 DRF APIRequestFactory 調用現有 API（模擬外部系統）
    try:
        factory = APIRequestFactory()
        request_data = {
            'survey_id': survey_id,
            'respondent_id': respondent_id,
            'started_at': request.session.get('started_at', timezone.now().isoformat()),
            'completed_at': timezone.now().isoformat(),
            'responses': responses
        }
        logger.info(f"Calling API with data: {request_data}")
        
        api_request = factory.post(
            '/api/submit-response/',
            request_data,
            format='json'
        )
        api_response = SaveResponseView.as_view()(api_request)
        
        logger.info(f"API response status: {api_response.status_code}")
        logger.info(f"API response data: {getattr(api_response, 'data', 'No data')}")
        
        if api_response.status_code != status.HTTP_200_OK:
            error_msg = '提交失敗'
            if hasattr(api_response, 'data'):
                if isinstance(api_response.data, dict):
                    error_msg = api_response.data.get('msg', error_msg)
                else:
                    error_msg = str(api_response.data)
            logger.error(f"API returned error: {error_msg}")
            return render(request, 'survey_error.html', {
                'error': error_msg,
                'details': api_response.data if hasattr(api_response, 'data') else str(api_response),
                'survey': survey,
            })
        
        # 清除 started_at（如果有的話）
        if 'started_at' in request.session:
            del request.session['started_at']
        
        logger.info(f"Submission successful, redirecting to success page")
        return redirect('survey_web:survey_success', survey_id=survey_id)
    
    except Exception as e:
        # 捕獲所有異常並顯示給用戶
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Exception in survey_submit: {str(e)}\n{error_trace}")
        return render(request, 'survey_error.html', {
            'error': f'提交時發生錯誤: {str(e)}',
            'details': error_trace,
            'survey': survey,
        })


def survey_success(request, survey_id):
    """提交成功頁"""
    survey = get_object_or_404(Survey, id=survey_id)
    return render(request, 'survey_success.html', {'survey': survey})
