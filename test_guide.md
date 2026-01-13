# Survey Form Repo — Admin UI Step-by-Step Test Guide

這份 guide 讓你用 **Django Admin UI** 從 0 建出一份「有題型 / 選項 / 題目排序 / constraints（JSON）/ 條件跳題」的範例 Survey，並透過 API 驗證「表單輸出」與「提交回覆」。

> 先決條件：你已成功 `python manage.py runserver`，並且能登入 `http://127.0.0.1:8000/admin/`（已建立 superuser）。

---

## 這個 repo 的「特點」會在這份測試裡展示什麼？

- **動態組表單**：Survey 與 Question 是分離的，靠 `QuestionOrder` 把題目掛到某份 Survey 並排序
- **多種題型**：`QuestionType`（`INTEGER` / `TEXT` / `MULTIPLE_CHOICE`）
- **題目 constraints**：`Question.constraints` 是 JSONField，可放一些限制資訊（此 repo 不會在後端強制驗證，但會原樣輸出到表單 API）
- **選擇題選項**：`ResponseChoice` 綁定在 Question
- **條件跳題（conditional logic）**：`ConditionalOrder` 讓你設定某題回答為「正向/負向」時，下一題的 order 要跳去哪題

---

## Part A — 用 Admin UI 建立測試資料（一步一步照做）

### A0. 登入 Admin

打開 `http://127.0.0.1:8000/admin/`，用你剛建立的 superuser 登入。

---

### A1. 建立 QuestionType（必做）

進入 `Question types` → `Add`，建立 **3 筆**：

1. `INTEGER`
2. `TEXT`
3. `MULTIPLE_CHOICE`

> 為什麼必做：API 建題目時會用 `QuestionType.objects.get(type=...)` 查資料庫，沒建會直接噴錯。

---

### A2. 建立 Respondent（測提交流程必做）

進入 `Respondents` → `Add`，建立一個使用者（這個會代表「填問卷的人」）。

建議欄位（範例）：

- Username: `demo_user`
- Password: 自訂（記得保存）

建立完成後，**點進去看它的 ID**（在列表或網址列通常能看到，例如 `/admin/survey_app/respondent/<id>/change/`）。

記下：

- `respondent_id = <你的ID>`

---

### A3. 建立 Survey（問卷本體）

進入 `Surveys` → `Add`，建立一份範例 survey：

- Name：`Vehicle Habits Survey (Demo)`
- Description：`Demo: ordering + constraints + conditional skip`
- Is open：✅（打勾）
- Opening/Closing time：可先留空

建立完成後，記下：

- `survey_id = <你的ID>`

---

### A4. 建立 3 個 Question（題目本體）

進入 `Questions` → `Add`，建立下面三題：

#### Q1（選擇題：用來展示 conditional）

- Name：`own_vehicle`
- Text：`Do you own a vehicle?`
- Question type：`MULTIPLE_CHOICE`
- Is mandatory：✅
- Constraints：留空（這題不放 constraints）

保存後，記下：

- `q1_id = <你的ID>`

#### Q2（整數題：用來展示 constraints JSON）

- Name：`weekly_mileage`
- Text：`How many kilometers do you travel per week?`
- Question type：`INTEGER`
- Is mandatory：✅
- Constraints（JSON）：貼上（示例）

```json
{"min": 0, "max": 2000, "unit": "km"}
```

保存後，記下：

- `q2_id = <你的ID>`

#### Q3（文字題：用來展示條件跳題的另一分支）

- Name：`no_vehicle_reason`
- Text：`If not, what is the main reason?`
- Question type：`TEXT`
- Is mandatory：✅
- Constraints（JSON）：貼上（示例）

```json
{"max_length": 200, "hint": "e.g. cost, no need, public transport"}
```

保存後，記下：

- `q3_id = <你的ID>`

---

### A5. 為 Q1 建立選項（ResponseChoice）

進入 `Response choices` → `Add`，建立兩筆（都指向同一題 Q1）：

1. Question：選 `own_vehicle`（Q1） / Text：`YES`
2. Question：選 `own_vehicle`（Q1） / Text：`NO`

> 這樣 `/api/show-form/<survey_id>/` 才會輸出 `response_choices` 讓前端能渲染選擇題。

---

### A6. 把題目掛到 Survey 並排序（QuestionOrder）

進入 `Question orders` → `Add`，建立三筆（都指向同一份 Survey）：

1. Survey：`Vehicle Habits Survey (Demo)` / Question：Q1 / Order：`1`
2. Survey：`Vehicle Habits Survey (Demo)` / Question：Q2 / Order：`2`
3. Survey：`Vehicle Habits Survey (Demo)` / Question：Q3 / Order：`3`

建立完成後，記下這三筆 `QuestionOrder` 的 ID（或至少記下 order 對應哪一筆）。
我們後面要用來設定 `ConditionalOrder`。

建議你記成：

- `qo1`：order=1（對應 Q1）
- `qo2`：order=2（對應 Q2）
- `qo3`：order=3（對應 Q3）

---

### A7. 建立 ConditionalOrder（展示「回答 YES 跳到 Q2，回答 NO 跳到 Q3」）

進入 `Conditional orders` → `Add`，建立一筆：

- Question order：選 `qo1`（order=1 的那筆；也就是 Q1）
- Response question order：同樣選 `qo1`
- Positive response question order：選 `qo2`（order=2）
- Negative response question order：選 `qo3`（order=3）

> 這個 repo 的 `ConditionalOrder` 沒有存「哪個選項算正向/負向」，所以此 demo 的解讀是：
> - **Positive** ≈ `YES`
> - **Negative** ≈ `NO`
>
> 你會在 `show-form` API 回傳中看到 `conditional_order` 結構（以 order 表示跳題關係）。

---

## Part B — 用 API 驗證你剛建的 Survey 真的「可被動態渲染」

### B1. 取回表單（ShowForm API）

在另一個 terminal 執行（把 `<survey_id>` 換成你的）：

```bash
curl -s http://127.0.0.1:8000/api/show-form/<survey_id>/ | python -m json.tool
```

你應該會看到重點欄位：

- `data.name` / `data.description` / `data.is_open`
- `data.questions_details[]` 每題包含：
  - `order`
  - `question_type`
  - `constraints`（你貼的 JSON 會原樣出現）
  - `response_choices`（Q1 會有 `YES/NO`）
  - `conditional_order`（Q1 會出現，顯示正/負向要跳到第幾題）

---

## Part C — 提交回覆並回到 Admin 檢查資料落庫

### C1. 提交一筆回覆（SubmitResponse API）

> 小提醒：目前 `SaveResponseView` 在迴圈內就 `return`，所以一次傳多題時可能只會存到第一題。
> 這份 guide 先用「一次提交一題」來驗證落庫行為。

#### Case 1：回答 Q1 = YES（代表走正向分支）

把 `<survey_id>`、`<respondent_id>`、`<q1_id>` 換成你的：

```bash
curl -s -X POST http://127.0.0.1:8000/api/submit-response/ \
  -H 'Content-Type: application/json' \
  -d '{
    "survey_id": <survey_id>,
    "respondent_id": <respondent_id>,
    "started_at": "2026-01-13T00:00:00Z",
    "completed_at": "2026-01-13T00:01:00Z",
    "responses": [
      { "question_id": <q1_id>, "answer": "YES" }
    ]
  }' | python -m json.tool
```

預期回應：

- `{"msg": "Response successfully submitted"}`

#### Case 2：回答 Q2（整數題，搭配 constraints）

```bash
curl -s -X POST http://127.0.0.1:8000/api/submit-response/ \
  -H 'Content-Type: application/json' \
  -d '{
    "survey_id": <survey_id>,
    "respondent_id": <respondent_id>,
    "responses": [
      { "question_id": <q2_id>, "answer": "120" }
    ]
  }' | python -m json.tool
```

> 注意：此 repo 目前不會根據 `constraints` 驗證答案合法性；constraints 主要是提供給前端渲染/驗證用的資料。

---

### C2. 回到 Admin 驗證資料落在哪裡

在 Admin 你可以看到兩種層級的資料：

1. `Survey responses`：代表「某 respondent 對某 survey 的一次作答紀錄（started_at/completed_at）」
2. `Responses`：代表「每一題的答案」（連到 `SurveyResponse` + `Question`）

建議你這樣查：

- 先到 `Survey responses` 找到你剛剛那個 respondent/survey 的那筆
- 再到 `Responses` 用 filter（或直接點進 Response）確認：
  - `question` 是不是 Q1 / Q2
  - `answer` 是不是你剛送的 `YES` / `120`

---

## 你完成這份 guide 後，代表你驗證到什麼？

- 你能用 Admin **動態組出一份 Survey**（不用寫前端）
- 你能用 `QuestionOrder` 控制題目順序
- 你能用 `ResponseChoice` 做出選擇題
- 你能在 API 回傳中看到 `constraints` JSON（可給前端做驗證/提示）
- 你能在 API 回傳中看到 `ConditionalOrder`（可做條件跳題）
- 你能提交回覆，並在 Admin 看到 `SurveyResponse/Response` 落庫

