# Survey Form（Django）— Simon 啟動筆記（WSL2）

這份文件是針對本 repo 的**安裝 / 啟動**流程整理（Django + Django REST Framework，DB 使用 SQLite）。

---

## 前置需求

- **Python**：建議使用 `python3`（搭配 `venv`）
- **OS**：本文以 **WSL2 (Ubuntu/Debian 系)** 為例

> 本 repo 的 `requirements.txt` 內含 `pygraphviz`，在 Linux 上常需要額外系統套件才能順利安裝。

---

## 1) 安裝依賴（WSL2）

在 WSL2 內進到專案資料夾：

```bash
cd /mnt/c/GitHub/survey-form
```

### 如果你是 conda 使用者（建議：不要用 base）

不建議把專案依賴直接裝進 `(base)`，比較乾淨的做法是替這個 repo 建一個專用環境：

```bash
cd /mnt/c/GitHub/survey-form

# 建議 python 3.10/3.11 都可（Django 4.1 支援）
conda create -n survey-form python=3.11 -y
conda activate survey-form
```

接著再往下做「系統套件」與 `pip install -r requirements.txt`。

#### 如果你 conda 這步遇到 `HTTP 403 FORBIDDEN`（repo.anaconda.com / pkgs/main）

這代表你的環境目前**無法存取 Anaconda 預設 channel**，因此 `conda create` 會失敗、後續也不會有 `survey-form` 這個 env。

你有兩條路：

- **推薦（最省事）**：直接用本 repo 的 `venv + pip`（不會動到 `(base)`，也不需要 conda 下載套件）
- **想繼續用 conda**：先檢查 conda channel / proxy 設定，確認你能存取可用的 channel（例如公司內網鏡像或 `conda-forge`）

快速檢查指令：

```bash
conda config --show channels
conda config --show-sources
```

安裝系統套件（避免 `pygraphviz` 編譯失敗）：

```bash
sudo apt update
sudo apt install -y \
  python3-venv python3-dev \
  build-essential pkg-config \
  graphviz graphviz-dev
```

建立並啟用 venv（若你已使用 conda env，可略過 venv 這步），安裝 Python 依賴：

```bash
python3 -m venv .venv
source .venv/bin/activate

python -m pip install -U pip
pip install -r requirements.txt
```

---

## 2) 初始化資料庫（migrate）

```bash
source .venv/bin/activate
python manage.py migrate
```

（建議）建立 admin 帳號：

```bash
python manage.py createsuperuser
```

---

## 3) 啟動開發伺服器

```bash
source .venv/bin/activate
python manage.py runserver
```

啟動後可用：

- **Django Admin**：`http://127.0.0.1:8000/admin/`
- **API 路由前綴**：`http://127.0.0.1:8000/api/`

---

## 4) 先建「必需資料」（不然部分 API 會直接噴錯）

### 必建 1：QuestionType

`POST /api/create-question/` 會用 `QuestionType.objects.get(type=...)` 查資料庫，
因此你至少需要先在 admin 建好下列 `QuestionType`：

- `INTEGER`
- `TEXT`
- `MULTIPLE_CHOICE`

位置：進 `admin/` → `Question types` → `Add`

### 必建 2：Respondent

`POST /api/submit-response/` 需要 `respondent_id`，所以也要先建立至少一個 `Respondent`。

位置：進 `admin/` → `Respondents` → `Add`

---

## 5) 主要 API endpoints（供你確認 server 有起來）

Base path：`/api/`

- `POST /api/create-survey/`
- `POST /api/create-question/`
- `GET  /api/show-form/<int:pk>/`
- `POST /api/submit-response/`

---

## 常見問題

### Q1：`pip install -r requirements.txt` 卡在 `pygraphviz`

通常是少系統套件。請先確認你有安裝：

- `graphviz`
- `graphviz-dev`
- `pkg-config`
- `python3-dev`
- `build-essential`

如果你的錯誤訊息是 `error: command 'gcc' failed: No such file or directory`，
代表你沒有安裝編譯器（gcc），請先補：

```bash
sudo apt update
sudo apt install -y build-essential
```

然後重新跑：

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

