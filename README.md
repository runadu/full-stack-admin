# 會員系統 - Full-Stack 專案

FastAPI + SQL Server + Vue 3

------------------------------------------------------------------------

## 專案說明

本專案為示範型 Full-Stack 系統，實作：

-   JWT 身分驗證流程
-   分層式後端架構（routes / service / repository）
-   Docker 化 SQL Server
-   前後端分離開發與部署模式

提供兩種執行模式：

-   本機開發模式：只啟動 DB（Docker），前後端本機執行
-   整合測試模式（建議）：Backend + DB 皆在 Docker 中執行，前端本機執行

------------------------------------------------------------------------

## 技術棧（Tech Stack）

### Backend

-   FastAPI（Python 3.12）
-   SQLAlchemy 2.0
-   PyODBC（連線 SQL Server）
-   Poetry（套件與虛擬環境管理）
-   JWT Authentication
-   分層架構設計

### Frontend

-   Vue 3
-   Vite
-   TypeScript
-   RESTful API 串接

### Infrastructure

-   Microsoft SQL Server 2022（Docker）
-   Docker Compose
-   Makefile

------------------------------------------------------------------------

## 環境需求

-   Docker Desktop（含 Docker Compose）
-   Node.js（LTS，本機執行 frontend 時需要）
-   Python 3.12（本機執行 backend 時需要）
-   Poetry

補充：
- 若使用「整合測試模式」，本機不需要安裝 Python / Poetry
- Windows 預設沒有 `make`，請直接使用 `docker compose` 指令

------------------------------------------------------------------------

## 專案結構

    full-stack/
    ├── backend/
    │   ├── src/
    │   └── pyproject.toml
    │
    ├── frontend/
    │   ├── src/
    │   ├── example.env   # 複製為 frontend/.env
    │   └── package.json
    │
    ├── docker-compose.yml
    ├── Makefile
    └── example.env       # 複製為 .env（供 Docker 與 Backend 使用）

------------------------------------------------------------------------

## 快速開始（整合測試模式，建議）

### 方法 A：使用 Makefile（有安裝 make 的環境）

```bash
cp example.env .env
cp frontend/example.env frontend/.env

make up-all      # 啟動 Backend + DB（Docker）
make fe          # 啟動 Frontend（本機）
```

### 方法 B：使用 Docker Compose（Windows 建議）

```bash
cp example.env .env
cp frontend/example.env frontend/.env

docker compose up -d --build

cd frontend
npm install
npm run dev
```

啟動後可確認容器狀態：

```bash
docker compose ps
```

開啟： 
- API: http://localhost:8000 
- Swagger: http://localhost:8000/docs

------------------------------------------------------------------------

## 本機開發模式（DB in Docker）

### Step 1 — 啟動資料庫（Docker）

```bash
make up
```

或：

```bash
docker compose up -d sqlserver
docker compose up -d --no-deps --force-recreate sqlserver-init
```

### Step 2 — 啟動後端（本機）

```bash
make be
```

或：

```bash
cd backend
poetry install
poetry run uvicorn src.main:app --reload
```

### Step 3 — 啟動前端（本機）

```bash
make fe
```

或：

```bash
cd frontend
npm install
npm run dev
```

------------------------------------------------------------------------

## DB 初始化機制

本專案包含兩層初始化機制：

1.  `sqlserver-init`：確保資料庫（預設 devdb）存在
2.  當 `ENV=development` 時，後端啟動會執行 `create_all()`
    建立不存在的資料表

注意：

-   `create_all()` 只會建立「不存在的資料表」
-   不會更新既有欄位（非 migration 機制）
-   若需修改資料表結構，請使用 Alembic 等 migration 工具（本專案未實作）
-   `docker compose down -v` 會刪除 volume，資料將被清空

------------------------------------------------------------------------

## 環境變數設定

### 根目錄 `.env`

-   Docker Compose 會讀取此檔
-   本機執行 backend 時，也會由 `load_dotenv()` 讀取此檔

請將 `example.env` 複製為 `.env`。

``` env
MSSQL_SA_PASSWORD=password
MSSQL_DB=devdb
MSSQL_HOST_PORT=14330

ENV=development
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

注意： 
- 同名環境變數請勿重複宣告（Docker Compose 會以最後出現的值為準） 
- 修改 `MSSQL_SA_PASSWORD` 後需執行 `docker compose down -v` 才會生效

------------------------------------------------------------------------

## DATABASE_URL 設定（依執行模式擇一）

### 整合測試模式（建議）

使用 sqlserver：

``` env
DATABASE_URL=mssql+pyodbc://sa:password@sqlserver:1433/devdb?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes
```

整合測試模式下，`DATABASE_URL` host 必須為 `sqlserver`。

### 本機開發模式

使用 localhost：

``` env
DATABASE_URL=mssql+pyodbc://sa:password@localhost:14330/devdb?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes
```

本模式下 `DATABASE_URL` host 必須為 `localhost`。

若連線錯誤，請確認目前執行模式與 DATABASE_URL 中的 host 是否一致（localhost 或 sqlserver）。

------------------------------------------------------------------------

## frontend/.env

``` env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=會員系統
```

------------------------------------------------------------------------

## SQL Server 注意事項

### 修改 sa 密碼

```bash
docker compose down -v
docker compose up -d --build
```

### 密碼含特殊字元

`! @ : /` 等字元需使用 URL encoding，例如：

    ChangeMe123! → ChangeMe123%21

------------------------------------------------------------------------

## API 列表

所有需要登入的 API 均使用 HTTP Bearer Token（JWT）。

### Accounts

-   POST /api/v1/accounts/register
-   POST /api/v1/accounts/login
-   GET /api/v1/accounts/me

### Stocks

-   GET /api/v1/stocks

------------------------------------------------------------------------

### 前後端詳細說明請參考：

-   /backend/README.md
-   /frontend/README.md