# Phase 2: Web UI Implementation Plan

## 目標
在現有 API-only 專案上新增 Web UI，透過 DRF APIClient 調用現有 API（模擬外部系統），讓使用者可以透過瀏覽器填寫問卷。

## 設計原則
- **不修改現有 API**：所有 API endpoints 保持不變
- **模擬外部系統**：Web views 透過 `rest_framework.test.APIClient` 調用現有 API
- **滿足測試需求**：支援 `test_guide.md` 的 Part B（驗證表單）和 Part C（提交回覆）

## 實作步驟

### Step 1: 建立計畫紀錄文件
建立 `phase2_improve_plan.md`，記錄此階段的目標、設計決策和實作細節。

### Step 2: 新增 Web Views
建立 `survey_app/web_views.py`，包含：
- `survey_list()`: 列出所有 `is_open=True` 的 surveys（直接查 DB，因為沒有對應 API）
- `survey_form_view()`: 透過 `APIClient.get('/api/show-form/<pk>/')` 取得表單資料並渲染
- `survey_submit()`: 透過 `APIClient.post('/api/submit-response/')` 提交回覆
- `survey_success()`: 顯示提交成功頁面

### Step 3: 新增 Web URLs
建立 `survey_app/web_urls.py`，定義 Web UI 路由：
- `''` → `survey_list` (首頁)
- `'survey/<int:survey_id>/'` → `survey_form_view` (填寫問卷)
- `'survey/<int:survey_id>/submit/'` → `survey_submit` (處理提交)
- `'survey/<int:survey_id>/success/'` → `survey_success` (成功頁)

### Step 4: 修改主 URL 配置
修改 `survey_form/urls.py`，在現有路由後新增：
```python
path("", include("survey_app.web_urls")),  # Web UI 掛在根路徑
```

### Step 5: 配置 Static Files
修改 `survey_form/settings.py`，在 `STATIC_URL` 下方新增：
```python
STATICFILES_DIRS = [
    BASE_DIR / "survey_app" / "static",
]
```

### Step 6: 建立 Templates
在 `survey_app/templates/` 目錄下建立：
- `base.html`: 基礎模板（含導航、CSS/JS 引用）
- `survey_list.html`: 首頁（列出所有可用問卷）
- `survey_form.html`: 填寫問卷頁（動態渲染不同題型、支援條件跳題）
- `survey_success.html`: 提交成功頁
- `survey_error.html`: 錯誤頁面（API 調用失敗時顯示）

### Step 7: 建立 Static Files
在 `survey_app/static/` 目錄下建立：
- `css/survey.css`: 問卷表單樣式
- `js/survey.js`: 前端邏輯（條件跳題、表單驗證）

## 技術細節

### Web Views 實作重點
- 使用 `rest_framework.test.APIClient` 調用現有 API
- 匿名 respondent 處理：透過 session 儲存，首次提交時自動建立
- 錯誤處理：API 調用失敗時顯示錯誤頁面

### Templates 實作重點
- 支援三種題型：`MULTIPLE_CHOICE`、`INTEGER`、`TEXT`
- 顯示 `constraints` JSON 資訊（min/max、unit、hint 等）
- 條件跳題邏輯：透過 JavaScript 根據 `conditional_order` 隱藏/顯示問題

### 已知限制
- `SaveResponseView` 現有 bug（迴圈內 return）仍然存在，但不影響單題提交測試
- 沒有列出 surveys 的 API，所以 `survey_list` 直接查 DB（這是 Web UI 專屬功能）

## 檔案清單

### 新增檔案
- `phase2_improve_plan.md`
- `survey_app/web_views.py`
- `survey_app/web_urls.py`
- `survey_app/templates/base.html`
- `survey_app/templates/survey_list.html`
- `survey_app/templates/survey_form.html`
- `survey_app/templates/survey_success.html`
- `survey_app/templates/survey_error.html`
- `survey_app/static/css/survey.css`
- `survey_app/static/js/survey.js`

### 修改檔案
- `survey_form/urls.py`
- `survey_form/settings.py`
