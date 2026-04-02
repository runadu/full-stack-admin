# 會員系統 - Backend

FastAPI + SQL Server 後端服務

------------------------------------------------------------------------

## 專案說明

本 API 為 Full-Stack 專案之後端，負責：

-   JWT 身分驗證（Access Token）
-   使用者帳號管理
-   股票資料查詢 API
-   SQL Server 資料存取
-   分層架構設計（routes / service / repository）

------------------------------------------------------------------------

## 技術棧

-   FastAPI
-   SQLAlchemy 2.0
-   Microsoft SQL Server 2022
-   pyodbc + ODBC Driver 18
-   JWT（Bearer Token）
-   Poetry
-   Docker / Docker Compose

------------------------------------------------------------------------

## 技術選擇說明

### Docker

-   確保開發與測試環境一致
-   快速建立 SQL Server 測試環境
-   降低專案啟動門檻
-   方便未來部署與環境管理

### FastAPI

-   自動產生 Swagger / OpenAPI 文件
-   原生支援型別提示與 Pydantic 驗證
-   適合 RESTful API 開發

### SQLAlchemy 2.0

-   使用 ORM 定義資料表並進行資料存取
-   減少手寫 SQL，提高可維護性
-   提升程式碼可讀性與一致性

### JWT 認證

-   無狀態驗證機制
-   適合前後端分離架構

### 分層架構

透過將責任拆分為不同層級，使程式更容易維護與擴充：

- routes：處理 HTTP 請求與回應
- service：負責業務規則
- repository：負責資料存取

------------------------------------------------------------------------

## 系統架構與資料存取方式

Route → Service → Repository → SQLAlchemy ORM → SQL Server

-   Repository 層負責資料庫操作
-   Service 層不直接操作資料庫
-   未使用原生 SQL

------------------------------------------------------------------------

## 專案結構

    backend/
    ├── src/
    │   ├── main.py              # FastAPI 入口
    │   ├── accounts/            # 會員帳號模組
    │   ├── stocks/              # 股票模組
    │   └── core/                # 共用模組
    │       ├── base.py
    │       ├── db.py
    │       ├── settings.py
    │       └── security.py
    ├── Dockerfile
    ├── pyproject.toml
    └── README.md

------------------------------------------------------------------------

## 環境需求

-   Docker Desktop（含 Docker Compose）
-   Python 3.12（本機開發時）
-   Poetry（本機開發時）

------------------------------------------------------------------------

## 啟動方式

### Docker 模式（建議）

在 full-stack 根目錄執行：

``` bash
docker compose up -d --build
```

查看後端日誌：

``` bash
docker logs -f backend-api
```

------------------------------------------------------------------------

### 本機執行（開發用）

``` bash
poetry install
poetry run uvicorn src.main:app --reload
```

------------------------------------------------------------------------

## 存取位置

-   API: http://localhost:8000
-   Swagger: http://localhost:8000/docs

------------------------------------------------------------------------

# API 詳細說明

## Accounts API

  功能         Method   Path
  ------------ -------- ---------------------------
  註冊         POST     /api/v1/accounts/register
  登入         POST     /api/v1/accounts/login
  目前使用者   GET      /api/v1/accounts/me

### 驗證與錯誤處理說明

錯誤分為兩類：

1. **資料驗證錯誤（422）**
   - 由 FastAPI + Pydantic 自動處理
   - 驗證失敗時，請求不會進入 route function

2. **應用層錯誤（401 / 409）**
   - 由程式主動拋出 HTTPException
   - 發生於帳號驗證或資料衝突情境

#### 密碼儲存機制

-   密碼不以明碼儲存
-   使用 bcrypt 進行雜湊後存入 `password_hash`
-   登入時以雜湊比對驗證

------------------------------------------------------------------------

### POST /api/v1/accounts/register（註冊）

**成功**

-   `200 OK`

``` json
{ "ok": true }
```

**常見失敗**

-   `409 Conflict`（Email 已存在）

``` json
{ "detail": "Email already exists" }
```

-   `422 Unprocessable Entity`（格式或驗證失敗）

------------------------------------------------------------------------

### POST /api/v1/accounts/login（登入）

**成功**

-   `200 OK`

``` json
{ "token": "<JWT_TOKEN>" }
```

**常見失敗**

-   `401 Unauthorized`（帳號不存在或密碼錯誤）

``` json
{ "detail": "Invalid credentials" }
```

-   `422 Unprocessable Entity`（輸入格式錯誤）

------------------------------------------------------------------------

### GET /api/v1/accounts/me（取得目前使用者）

需於 Header 加入：

``` text
Authorization: Bearer <token>
```

**成功**

-   `200 OK`
-   回傳使用者資料（id / email / full_name(非必填) / created_at）

**常見失敗**

-   `401 Unauthorized`
    -   未提供 Token
    -   Token 無效
    -   Token 過期

------------------------------------------------------------------------

## Stocks API

  功能   Method   Path
  ------ -------- ----------------
  清單   GET      /api/v1/stocks

### GET /api/v1/stocks（股票清單）

**成功**

-   `200 OK`
-   回傳股票清單資料

**常見失敗**

-   `401 Unauthorized`（未提供或無效 Token）

------------------------------------------------------------------------

## 錯誤回傳格式

### 一般錯誤（401 / 409）

``` json
{ "detail": "錯誤訊息" }
```

### 驗證錯誤（422）

``` json
{
  "detail": [
    {
      "loc": ["body", "欄位名稱"],
      "msg": "錯誤說明",
      "type": "錯誤類型"
    }
  ]
}
```

------------------------------------------------------------------------

## 資料庫結構

Table: users

-   id (primary key)
-   email (unique)
-   password_hash
-   created_at
-   full_name (nullable)

------------------------------------------------------------------------

## 安全性設計

-   密碼使用 bcrypt 雜湊後儲存
-   Email 設為唯一索引
-   受保護 API 需 JWT 驗證
-   未授權回傳 401

------------------------------------------------------------------------

## 資料庫初始化機制

開發環境啟動時會執行：

Base.metadata.create_all(bind=engine)

若修改欄位後出現錯誤：

Invalid column name 'xxx'

請重建資料庫：

``` bash
docker compose down -v
docker compose up -d --build
```

------------------------------------------------------------------------

## 尚可改進之處

1.  未使用 Alembic 管理資料庫 migration，目前 `Base.metadata.create_all()` 僅適合開發環境。
2.  JWT 未實作 Refresh Token，目前僅提供 Access Token。
3.  未加入登入失敗次數限制。
4.  未加入 Email 驗證流程。
5.  尚未加入自動化測試。
6.  尚未區分正式與開發環境設定。

------------------------------------------------------------------------
