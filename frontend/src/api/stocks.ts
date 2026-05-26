import { http } from "./http";

export type Stock = {
  symbol: string;
  name: string;
  open_price: number;
  high_price: number;
  low_price: number;
  close_price: number;
  volume: number;
  vwap_price?: number | null;
  trade_count?: number | null;
  day_change: number;
  day_change_percent: number;
  price_date: string;
  currency: string;
  source: string;
  data_delay: string;
  cache_status?: string | null;
  fetched_at?: string | null;
  warning?: string | null;
};

export function listStocksApi() {
  return http<Stock[]>("stocks");
}
