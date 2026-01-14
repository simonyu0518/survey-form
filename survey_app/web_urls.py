from django.urls import path
from . import web_views

app_name = 'survey_web'

urlpatterns = [
    path('', web_views.survey_list, name='survey_list'),
    path('survey/<int:survey_id>/', web_views.survey_form_view, name='survey_form'),
    path('survey/<int:survey_id>/submit/', web_views.survey_submit, name='survey_submit'),
    path('survey/<int:survey_id>/success/', web_views.survey_success, name='survey_success'),
]
