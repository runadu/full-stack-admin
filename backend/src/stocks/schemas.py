from pydantic import BaseModel


class StockItem(BaseModel):
    symbol: str
    name: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    vwap_price: float | None = None
    trade_count: int | None = None
    day_change: float
    day_change_percent: float
    price_date: str
    currency: str
    source: str
    data_delay: str
    cache_status: str | None = None
    fetched_at: str | None = None
    warning: str | None = None
