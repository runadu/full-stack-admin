# Backend

FastAPI + SQL Server backend for the full-stack demo.

共用的啟動方式、環境變數與 Docker 流程請看 root [README](/Users/daburudu/Desktop/side-projects/full-stack/README.md)；這份文件只補 backend 自己的架構與開發重點。

## Responsibilities

- JWT 驗證與受保護 API
- 使用者帳號註冊、登入、取得目前使用者
- 股票資料查詢與 Massive API 整合
- SQL Server 存取與資料模型管理

## Stack

- Python 3.11-3.12
- FastAPI
- SQLAlchemy 2.0
- pyodbc
- Poetry

## Structure

```text
backend/
├─ src/
│  ├─ main.py                # FastAPI app 入口
│  ├─ accounts/              # 帳號模組
│  ├─ stocks/                # 股票模組
│  └─ core/                  # 設定、DB、security 共用層
├─ pyproject.toml
├─ poetry.lock
└─ poetry.toml               # 使用 in-project .venv
```

## Architecture

### Accounts

- `routes.py`：HTTP endpoints
- `service.py`：帳號邏輯與登入流程
- `repository.py`：SQLAlchemy 查詢
- `models.py` / `schemas.py`：資料模型與 request/response schema

### Stocks

- `routes.py`：`GET /api/v1/stocks`
- `service.py`：Massive API 呼叫、快取、fallback 與欄位轉換
- `schemas.py`：Stocks response schema

Stocks 目前直接走 service layer，不經 repository，因為資料來源是外部 API，不是本地資料庫。

## Stocks Behavior

- 使用 Massive grouped daily aggregates 取得最近可用交易日資料
- 會補 ticker reference 資料，用來取得公司名稱與幣別
- 成功抓到資料後寫入記憶體快取
- Massive 暫時失敗時，會優先回 stale cache
- 單一 ticker reference 失敗時，會 fallback 到 `symbol` / `USD`，並保留 warning

## Local Dev Notes

- Poetry 會把虛擬環境建立在 `backend/.venv`
- VS Code interpreter 應使用 `backend/.venv/bin/python`
- 開發環境啟動時會執行 `Base.metadata.create_all()`；這不是 migration 機制

## API Modules

- `POST /api/v1/accounts/register`
- `POST /api/v1/accounts/login`
- `GET /api/v1/accounts/me`
- `GET /api/v1/stocks`

實際啟動方式、認證方式與 stocks response 欄位請看 root [README](/Users/daburudu/Desktop/side-projects/full-stack/README.md)。
