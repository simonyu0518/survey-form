# Q1/Q2/Q3（test_guide.md Demo）模型關係對照圖與 Mapping

本文件把 `test_guide.md` 裡的 Demo Survey（Q1/Q2/Q3）用**資料模型**的角度重新解釋，讓你能清楚回答：

- 「`Survey` 到底包含什麼？」
- 「題目順序 `order=1/2/3` 存在哪？」
- 「選擇題的選項（YES/NO）跟哪個物件綁？」
- 「條件跳題（YES 去 Q2、NO 去 Q3）是用哪個表表示？」
- 「提交後答案落庫在哪兩層（一次作答 vs 每題答案）？」

---

## 1) 先講結論：核心關係（最重要的連線）

### A. 出題（問卷長相）

- `Survey` **不直接**連到 `Question`
- `Survey` 透過 **`QuestionOrder`** 連到 `Question`，並且用 `QuestionOrder.order` 表示題目順序
- `Question` 會連到 `QuestionType`（題型）
- 若 `QuestionType = MULTIPLE_CHOICE`，`Question` 會再連到多個 `ResponseChoice`（選項）

### B. 作答（誰填了什麼）

- 一次「某個人填某份問卷」會先建立/更新 `SurveyResponse`（一筆作答紀錄）
- 每一題答案是一筆 `Response`（程式中常用別名 `UserResponse`）
  - `Response` 會連到：`SurveyResponse` + `Question`

---

## 2) 用 Q1 / Q2 / Q3 來 mapping 每個模型

你在 `test_guide.md` 建的 Demo（簡化描述）：

- Survey：`Vehicle Habits Survey (Demo)`
- Q1：`Do you own a vehicle?`（選擇題，必填，選項 YES/NO）
- Q2：`How many kilometers...`（整數題，必填，有 constraints）
- Q3：`If not, what is the main reason?`（文字題，必填，有 constraints）
- 題目順序：Q1=order 1、Q2=order 2、Q3=order 3
- 跳題：Q1 回答 YES → 跳到 order=2；回答 NO → 跳到 order=3

---

## 3) 一張圖看懂所有連線（Q1/Q2/Q3 版本）

```text
出題（問卷長相）

                ┌────────────────────────────────────────────┐
                │ Survey                                     │
                │  Vehicle Habits Survey (Demo)              │
                └────────────────────────────────────────────┘
                                  1
                                  │
                                  │ has many
                                  ▼
                     ┌───────────────────────────┐
                     │ QuestionOrder (中介表)      │
                     │  qo1: order=1  ──┐        │
                     │  qo2: order=2  ──┼──► Question (Q1/Q2/Q3)
                     │  qo3: order=3  ──┘        │
                     └───────────────────────────┘
                                  │
                                  │ each points to exactly one
                                  ▼
                     ┌───────────────────────────┐
                     │ Question                   │
                     │  Q1 own_vehicle            │──► QuestionType = MULTIPLE_CHOICE
                     │  Q2 weekly_mileage         │──► QuestionType = INTEGER
                     │  Q3 no_vehicle_reason      │──► QuestionType = TEXT
                     └───────────────────────────┘
                                  │
                                  │ (only for MULTIPLE_CHOICE)
                                  ▼
                     ┌───────────────────────────┐
                     │ ResponseChoice             │
                     │  (Q1) YES                  │
                     │  (Q1) NO                   │
                     └───────────────────────────┘


條件跳題（用 QuestionOrder 表示“第幾題”）

  ConditionalOrder
    question_order = qo1 (order=1)
    positive_response_question_order = qo2 (order=2)
    negative_response_question_order = qo3 (order=3)


作答（提交後落庫）

Respondent (demo_user) 1 ───< SurveyResponse >─── 1 Survey
SurveyResponse 1 ───< Response(UserResponse) >─── 1 Question
```

---

## 4) 逐一對照：你在 Admin 做的每一步到底建立了什麼

### 4.1 建 `QuestionType`（必做）

建立三筆字典資料：

- `INTEGER`
- `TEXT`
- `MULTIPLE_CHOICE`

目的：`Question.question_type` 會指向其中一筆。

---

### 4.2 建三題 `Question`（Q1/Q2/Q3）

每一題是一筆 `Question`：

- **Q1**：`own_vehicle` / MULTIPLE_CHOICE / mandatory ✅
- **Q2**：`weekly_mileage` / INTEGER / mandatory ✅ / constraints `{"min":0,"max":2000,"unit":"km"}`
- **Q3**：`no_vehicle_reason` / TEXT / mandatory ✅ / constraints `{"max_length":200,"hint":"..."}`

這裡要記得：

- `Question` 還**沒有**跟 `Survey` 綁在一起
- 題目順序也**不在** `Question` 這張表裡

---

### 4.3 建 `ResponseChoice`（Q1 的 YES/NO）

為 Q1 建兩筆 `ResponseChoice`：

- (Question=Q1) Text=`YES`
- (Question=Q1) Text=`NO`

重點：選項是綁在 **`Question`** 上，不是綁在 `Survey` 或 `QuestionOrder` 上。

---

### 4.4 建 `QuestionOrder`（把題目掛上 Survey 並排序）

建立三筆 `QuestionOrder`：

- **qo1**：Survey=Demo / Question=Q1 / **order=1**
- **qo2**：Survey=Demo / Question=Q2 / **order=2**
- **qo3**：Survey=Demo / Question=Q3 / **order=3**

你現在就可以回答：「Survey 包含什麼？」

- **Survey 包含很多 `QuestionOrder`**
- 每個 `QuestionOrder` 再指向一個 `Question`

---

### 4.5 建 `ConditionalOrder`（YES→Q2、NO→Q3）

建立一筆 `ConditionalOrder`：

- `question_order = qo1`（因為條件發生在第 1 題）
- `positive_response_question_order = qo2`
- `negative_response_question_order = qo3`

注意：這個 repo 的 demo 前端把「YES/NO」的正負向判斷寫死在 JS：

- YES / true / 1 → positive
- 其他 → negative

因此 `ConditionalOrder` 本身並不存「哪個選項是正向/負向」，它只存「正向跳到哪個 order、負向跳到哪個 order」。

---

## 5) API / 資料流：為什麼 ShowForm 需要 QuestionOrder？

### 5.1 `GET /api/show-form/<survey_id>/`

後端會：

1. 先找到 `Survey`
2. 取出該 survey 的全部 `QuestionOrder`（內含 order + question）
3. 對每個 `QuestionOrder` 取出：
   - `Question` 本體（題幹、題型、mandatory、constraints…）
   - 如果是選擇題：`ResponseChoice` 列表（YES/NO）
   - 如果有：`ConditionalOrder`（跳題關係）

所以「問卷的題目順序」一定要靠 `QuestionOrder` 才能組出來。

---

### 5.2 `POST /api/submit-response/`

提交時會寫兩層：

1. `SurveyResponse`（代表 respondent 對 survey 的一次作答；可存 started/completed）
2. `Response`（每一題一筆答案；連回 Question + SurveyResponse）

---

## 6) 小抄：你看到的名詞對應哪個表？

- Survey（問卷本體）→ `Survey`
- Question（題目本體）→ `Question`
- QuestionType（題型字典）→ `QuestionType`
- ResponseChoice（選擇題選項）→ `ResponseChoice`
- QuestionOrder（把題目掛到問卷 + 排序）→ `QuestionOrder`
- ConditionalOrder（跳題關係，用 order 表示）→ `ConditionalOrder`
- SurveyResponse（一次作答）→ `SurveyResponse`
- Response（每題答案）→ `Response`（程式碼常別名 `UserResponse`）

