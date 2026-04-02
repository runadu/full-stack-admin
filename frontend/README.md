# 會員系統 - Frontend

Vue 3 + TypeScript + Vite

------------------------------------------------------------------------

## 專案說明

本 Web App 為 Full-Stack 專案之前端，負責：

-   會員註冊 / 登入 / 登出流程
-   Dashboard（需登入）與 Route Guard
-   JWT（Access Token）前端保存與請求攔截
-   股票清單頁（加分項）
-   UI 分層設計與可重用元件

------------------------------------------------------------------------

## 技術棧

- Vue 3 (Composition API)
- TypeScript
- Vite
- Tailwind CSS（視覺層）
- Element Plus（行為層）
- Vue Router

------------------------------------------------------------------------

## 技術選擇說明

### 1. UI 架構

#### Tailwind CSS（視覺層）

-   負責 spacing、排版、Grid 與語意色彩
-   作為設計 Token 的使用層
-   避免樣式散落與覆寫成本過高

#### Element Plus（互動層）

-   提供表單驗證與常用互動元件（Dialog / Message 等）
-   提供 Table / Pagination 等資料型元件
-   提升資料介面開發效率與一致性

------------------------------------------------------------------------

### 2. 設計系統整合

本專案以 **CSS Variables 作為設計 Token 核心來源**，
並讓 Tailwind 與 Element Plus 共用同一套色彩系統。

-   Dark Mode 僅需切換 .dark
-   所有元件（UI Library + 自訂元件）主題一致
-   降低樣式覆寫與維護成本

------------------------------------------------------------------------

### 3. 驗證與錯誤處理策略

### JWT（Access Token）

-   適合前後端分離架構的無狀態驗證
-   Demo 以完整流程與整合為優先，前端使用 localStorage 保存 token

### 全域 401 處理

-   API 回傳 401 時統一處理：提示 → 清除 token → 導回登入
-   避免在各頁面重複撰寫錯誤處理與導頁邏輯

------------------------------------------------------------------------

### 架構設計說明

### 狀態管理

auth 拆分為：

- `auth-state.ts` → 全域登入狀態
- `auth.ts` → 登入流程
- `auth-session.ts` → 結束登入狀態

### Navigation

- Sidebar 由設定檔動態產生
- 圖示與選單邏輯分離


### Loading / Empty State

- 登入檢查期間顯示 loading
- 按鈕具備 loading 狀態
- 股票列表具備 Empty State 提示

------------------------------------------------------------------------

## 專案結構

```text
frontend/
├─ example.env              # 環境變數範例（請複製為 .env）
└─ src/
   ├─ main.ts
   ├─ App.vue
   ├─ api/                  # 後端 API 呼叫
   ├─ stores/               # 全域狀態管理（登入狀態 / 主題）
   ├─ router/               # 路由與 Route Guard
   ├─ layouts/              # 版型結構（Header / Sidebar）
   ├─ views/                # 頁面層
   ├─ components/           # 可重用 UI 元件
   ├─ navigation/           # 動態選單邏輯
   └─ styles/               # 全域樣式與主題（Design Tokens）
```

------------------------------------------------------------------------

## 環境變數

`.env`

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=AI Stock System
```

使用方式：

```ts
import.meta.env.VITE_API_BASE_URL
```

------------------------------------------------------------------------

## API Proxy 設定（Vite Proxy）

`vite.config.ts`

```ts
server: {
  proxy: {
    "/api/v1": {
      target: env.VITE_API_BASE_URL,
      changeOrigin: true,
    },
  },
}
```

------------------------------------------------------------------------

## 功能對照表

### 註冊

- Email 驗證
- Password 至少 6 碼
- 409 重複帳號處理
- 422 表單錯誤處理
- `POST /api/v1/accounts/register`

### 登入

- 表單驗證
- Token 存入 localStorage
- 呼叫 `GET /api/v1/accounts/me`
- 導向 Dashboard

### Dashboard

- Route Guard 保護
- 呼叫 `GET /api/v1/accounts/me`（需驗證）
- 顯示使用者 Email
- 顯示固定文字：「歡迎使用 會員系統」

### 登出

- 清除 token
- 清除使用者狀態
- 導回 login

### 股票清單（加分項）

- `GET /api/v1/stocks`（需登入）
- Loading / Error / Empty state

------------------------------------------------------------------------

## 前端啟動方式

```bash
npm install
npm run dev
```

------------------------------------------------------------------------

## 設計原則

-   視覺與行為分離（Tailwind / Element Plus）
-   Feature-based + Layered 分層（views / api / stores / layouts）
-   單一錯誤處理入口（全域 401）
-   元件可重用（AppCard / AppDialog）

------------------------------------------------------------------------

## 技術取捨

-   為了簡化 Demo，JWT 儲存在 localStorage（未採用 Cookie）
-   未實作 Refresh Token 機制
-   未加入單元測試
-   以流程完成度與可讀性為優先，部分功能（如 SettingsView）以展示架構為主

------------------------------------------------------------------------

## 尚可改進之處

1.  改為使用 HttpOnly Cookie + Refresh Token，提升安全性並支援長期登入。
2.  導入 Pinia 模組化 store，並補齊測試（Vitest / Cypress）。
3.  與後端透過 OpenAPI 產生型別，降低前後端 contract 不一致風險。
4.  錯誤處理再細分（例如：表單驗證錯誤 / 權限錯誤 / 網路錯誤）並統一 UI 呈現。
5.  強化 UI 可存取性（a11y）與互動細節（提示一致性、載入體驗）。
