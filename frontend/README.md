# Frontend

Vue 3 + TypeScript + Vite frontend for the full-stack demo.

共用的啟動方式、環境變數與 API 路徑請看 root [README](/Users/daburudu/Desktop/side-projects/full-stack/README.md)；這份文件只保留 frontend 自己的畫面結構、狀態管理與開發重點。

## Responsibilities

- 註冊、登入、登出流程
- Route Guard 與登入狀態維護
- Dashboard 與 Stocks 頁面
- API 呼叫與全域 401 處理
- Element Plus + Tailwind 的 UI 組裝

## Stack

- Vue 3
- TypeScript
- Vite
- Vue Router
- Element Plus
- Tailwind CSS 4

## Structure

```text
frontend/
├─ src/
│  ├─ api/                   # 後端 API 封裝
│  ├─ components/            # 可重用 UI 元件
│  ├─ layouts/               # Header / Sidebar / Main layout
│  ├─ navigation/            # Sidebar metadata 與 icon map
│  ├─ router/                # Vue Router 與 auth guard
│  ├─ stores/                # auth / theme state
│  ├─ styles/                # Element Plus theme overrides
│  └─ views/                 # 頁面層
├─ example.env
├─ package.json
└─ vite.config.ts
```

## App Structure

### Auth Flow

- `src/api/http.ts`：fetch wrapper、token 注入、401 統一處理
- `src/stores/auth-state.ts`：登入者狀態
- `src/stores/auth.ts`：登入與 `checkAuth`
- `src/stores/auth-session.ts`：清理 session

### Routing

- `src/router/index.ts`：公開路由、受保護路由與 route guard
- `src/navigation/`：sidebar 選單定義與圖示映射

### Views

- `DashboardView.vue`：使用 Massive 股票資料計算 KPI 與 snapshot
- `StocksListView.vue`：股票表格、pagination、detail dialog
- `views/auth/*`：登入 / 註冊頁

## UI Notes

- Dashboard 與 Stocks 都使用同一支 `GET /api/v1/stocks`
- Stocks 列表為高密度表格，詳細欄位收進 dialog，避免長欄位破版
- `AppCard`、`AppDialog` 是主要共用容器元件
- Tailwind 負責 layout / spacing，Element Plus 負責 table、dialog、pagination 等互動元件

## Formatting

- Prettier 設定放在 root `.prettierrc.json`
- `npm run format`
- `npm run format:check`
- VS Code workspace 已預設 `formatOnSave` 並指定 `esbenp.prettier-vscode`

## Tradeoffs

- Token 目前保存在 `localStorage`，以 demo 完整流程為主
- Settings 頁面仍以結構展示為主
- 尚未導入前端測試與自動產生 API 型別
