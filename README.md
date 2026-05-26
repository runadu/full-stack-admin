# Full-Stack Auth + Stocks Demo

一個前後端分離的示範專案，包含會員註冊 / 登入、JWT 驗證、受保護頁面，以及簡單的股票清單頁。

後端使用 FastAPI + SQL Server，前端使用 Vue 3 + Vite。專案提供 Docker 化的資料庫與 API，方便其他開發者直接在本機啟動和測試。

## 專案內容

- 使用者註冊、登入、取得目前登入者資訊
- JWT Bearer Token 驗證流程
- 受保護的 Dashboard 與 Stocks 頁面
- Vue Router Route Guard
- SQL Server 容器化啟動與初始化
- FastAPI Swagger 文件

## Tech Stack

### Backend

- Python 3.11-3.12
- FastAPI
- SQLAlchemy 2.0
- PyODBC
- Poetry

### Frontend

- Node.js LTS
- Vue 3
- TypeScript
- Vite
- Element Plus
- Tailwind CSS 4

### Infra

- Docker Compose
- Microsoft SQL Server 2022

## 專案結構

```text
full-stack/
├─ backend/                  # FastAPI API
├─ frontend/                 # Vue 3 Web App
├─ docker-compose.yml        # SQL Server / API 容器
├─ Makefile                  # 常用啟動指令
├─ example.env               # 根目錄環境變數範本
└─ README.md
```

## 功能概覽

### 已實作

- `POST /api/v1/accounts/register`
- `POST /api/v1/accounts/login`
- `GET /api/v1/accounts/me`
- `GET /api/v1/stocks`
- 前端登入 / 註冊表單驗證
- 全域 401 處理
- Dashboard 與 Stocks 路由保護
- Dashboard 與 Stocks 頁面串接 Massive（Polygon）股票資料

### 目前範圍

- `stocks` API 目前透過 Massive（Polygon）daily aggregates 取得資料
- `development` 環境下，後端啟動時會自動建立資料表
- 尚未導入 migration、refresh token、完整測試

## 環境需求

依照你要採用的啟動方式，準備以下工具：

- Docker Desktop
- Node.js LTS
- npm
- Python 3.11 或 3.12
- Poetry

如果你使用「Docker 跑 API + DB、前端本機跑」的方式，Python 和 Poetry 只在你需要本機啟動後端時才需要。

## 快速開始

這個專案最適合的起手式是：

- API + DB 用 Docker
- Frontend 在本機開發模式執行

### 1. 建立環境變數

```bash
cp example.env .env
cp frontend/example.env frontend/.env
```

### 2. 啟動 API 與資料庫

有 `make`：

```bash
make up-all
```

沒有 `make`：

```bash
docker compose up -d --build
```

### 3. 啟動前端

```bash
cd frontend
npm install
npm run dev
```

### 4. 開啟服務

- Frontend: [http://localhost:5173](http://localhost:5173)
- API: [http://localhost:8000](http://localhost:8000)
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)

## 另一種開發方式：只用 Docker 跑資料庫

如果你想本機直接 debug FastAPI，可以只啟動 SQL Server container。

### 1. 啟動資料庫

```bash
make up
```

或：

```bash
docker compose up -d sqlserver
docker compose up -d --no-deps --force-recreate sqlserver-init
```

### 2. 把根目錄 `.env` 的 `DATABASE_URL` 改成 `localhost`

```env
DATABASE_URL=mssql+pyodbc://sa:ChangeMe123%21@localhost:14330/devdb?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes
```

### 3. 本機啟動後端

```bash
cd backend
poetry install
poetry run uvicorn src.main:app --reload
```

### 4. 本機啟動前端

```bash
cd frontend
npm install
npm run dev
```

## 環境變數

### 根目錄 `.env`

請從 `example.env` 複製，主要欄位如下：

```env
MSSQL_SA_PASSWORD=ChangeMe123!
MSSQL_DB=devdb
MSSQL_HOST_PORT=14330

ENV=development
JWT_SECRET=ChangeMe_To_A_Long_Random_String_At_Least_32_Chars
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
MASSIVE_API_KEY=your_massive_api_key
MASSIVE_STOCK_TICKERS=AAPL,MSFT,NVDA,TSLA,AMZN,GOOGL
MASSIVE_TIMEOUT_SECONDS=10
STOCKS_CACHE_TTL_SECONDS=60
STOCKS_CACHE_STALE_IF_ERROR_SECONDS=900

DATABASE_URL=mssql+pyodbc://sa:ChangeMe123%21@sqlserver:1433/devdb?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes
```

注意：

- `MSSQL_SA_PASSWORD` 若含特殊字元，`DATABASE_URL` 中要改成 URL encode 後的值
- Docker 模式下 `DATABASE_URL` host 應為 `sqlserver`
- 本機啟動後端時 `DATABASE_URL` host 應改為 `localhost`
- 更改 SQL Server SA 密碼後，通常需要重新建立 volume 才會生效
- `MASSIVE_API_KEY` 需到 [Massive](https://massive.com/) 申請
- `MASSIVE_STOCK_TICKERS` 是 Stocks 頁面要顯示的 ticker 清單，使用逗號分隔
- Massive `Stocks Basic` 可用 aggregates / end-of-day 資料；若要 snapshot 或更接近即時的資料，需升級方案
- `STOCKS_CACHE_TTL_SECONDS` 控制正常快取秒數
- `STOCKS_CACHE_STALE_IF_ERROR_SECONDS` 控制上游失敗時可接受的陳舊快取秒數

### `frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=會員系統
```

## 常用指令

```bash
make up         # 啟動 DB 與初始化
make up-all     # 啟動 API + DB
make down       # 關閉容器，保留資料
make reset      # 關閉容器並清空 DB volume
make ps         # 查看容器狀態
make logs       # 查看所有服務 logs
make be         # 本機啟動後端
make fe         # 本機啟動前端
```

## API 一覽

所有受保護 API 都使用 `Authorization: Bearer <token>`。

| Method | Path | 說明 |
| --- | --- | --- |
| `POST` | `/api/v1/accounts/register` | 建立帳號 |
| `POST` | `/api/v1/accounts/login` | 取得 JWT token |
| `GET` | `/api/v1/accounts/me` | 取得目前登入者 |
| `GET` | `/api/v1/stocks` | 取得股票清單 |

## 實作備註

- 後端採用 `routes -> service -> repository` 分層
- `Base.metadata.create_all()` 僅適合開發階段，不等同 migration
- 前端 token 目前儲存在 `localStorage`，以 demo 完整流程為主
- Dashboard 與 Stocks 頁面皆使用 Massive（原 Polygon）API 的股票資料
- Stocks 清單資料由 Massive（原 Polygon）API 提供，目前顯示最近可用交易日的 OHLC、成交量、VWAP 與日內漲跌
- Stocks API 會在 Swagger / JSON 中回傳 `cache_status`、`fetched_at`、`warning`，用來觀察快取命中、stale fallback 與部分 ticker 失敗
- 若 Massive 暫時失敗，後端會優先回最後一次成功快取；若單一 ticker 的 reference data 失敗，會回退到 symbol / USD 預設值並保留 warning

## 後續可延伸

- 導入 Alembic migration
- 改為 HttpOnly cookie + refresh token
- 補齊單元測試與整合測試
- 擴充股票欄位，例如漲跌幅、成交量、更新時間

## 參考文件

- [backend README](/Users/daburudu/Desktop/side-projects/full-stack/backend/README.md)
- [frontend README](/Users/daburudu/Desktop/side-projects/full-stack/frontend/README.md)
