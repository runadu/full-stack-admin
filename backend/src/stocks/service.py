import json
import logging
import time
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any
from urllib import error, parse, request

from fastapi import HTTPException

from src.core.settings import settings

logger = logging.getLogger(__name__)

MASSIVE_GROUPED_DAILY_URL = "https://api.massive.com/v2/aggs/grouped/locale/us/market/stocks/{date}"
MASSIVE_TICKER_OVERVIEW_URL = "https://api.massive.com/v3/reference/tickers/{ticker}"
MAX_LOOKBACK_DAYS = 10
DEFAULT_CURRENCY = "USD"
SOURCE_NAME = "massive"
DATA_DELAY = "end_of_day"


@dataclass(frozen=True)
class StockItem:
    symbol: str
    name: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    vwap_price: float | None
    trade_count: int | None
    day_change: float
    day_change_percent: float
    price_date: str
    currency: str
    source: str
    data_delay: str
    warning: str | None = None


@dataclass(frozen=True)
class StockReference:
    symbol: str
    name: str
    currency: str


@dataclass(frozen=True)
class StockCollection:
    items: list[StockItem]
    warnings: list[str]


@dataclass(frozen=True)
class CachedStocks:
    items: list[StockItem]
    warnings: list[str]
    fetched_at: str
    fresh_expires_at: float
    stale_expires_at: float


class MassiveApiError(Exception):
    def __init__(self, status_code: int, user_detail: str, log_detail: str | None = None):
        super().__init__(user_detail)
        self.status_code = status_code
        self.user_detail = user_detail
        self.log_detail = log_detail or user_detail


_cache_snapshot: CachedStocks | None = None
_reference_cache: dict[str, StockReference] = {}


def get_stocks() -> list[dict[str, Any]]:
    global _cache_snapshot

    now = time.time()
    cached = _cache_snapshot
    if cached is not None and now < cached.fresh_expires_at:
        return _serialize_cached_items(cached, cache_status="hit")

    tickers = _get_tickers()
    try:
        collection = _fetch_stock_collection(tickers)
    except MassiveApiError as exc:
        stale_cache = _get_usable_stale_cache(now)
        if stale_cache is not None:
            logger.warning("Serving stale stocks cache due to Massive error: %s", exc.log_detail)
            return _serialize_cached_items(
                stale_cache,
                cache_status="stale",
                extra_warning=exc.user_detail,
            )
        raise HTTPException(status_code=exc.status_code, detail=exc.user_detail) from exc

    fetched_at = _utc_now_iso()
    _cache_snapshot = CachedStocks(
        items=collection.items,
        warnings=collection.warnings,
        fetched_at=fetched_at,
        fresh_expires_at=now + max(settings.stocks_cache_ttl_seconds, 0),
        stale_expires_at=now
        + max(settings.stocks_cache_ttl_seconds, 0)
        + max(settings.stocks_cache_stale_if_error_seconds, 0),
    )
    return _serialize_cached_items(_cache_snapshot, cache_status="miss")


def _get_tickers() -> list[str]:
    tickers = [item.strip().upper() for item in settings.massive_stock_tickers.split(",")]
    tickers = [item for item in tickers if item]
    if not tickers:
        raise HTTPException(status_code=500, detail="MASSIVE_STOCK_TICKERS is empty")
    return tickers


def _get_usable_stale_cache(now: float) -> CachedStocks | None:
    if _cache_snapshot is None:
        return None
    if now >= _cache_snapshot.stale_expires_at:
        return None
    return _cache_snapshot


def _fetch_stock_collection(tickers: list[str]) -> StockCollection:
    if not settings.massive_api_key:
        raise MassiveApiError(500, "MASSIVE_API_KEY is not configured")

    desired = set(tickers)
    checked_dates: list[str] = []

    for target_date in _recent_market_dates():
        checked_dates.append(target_date)
        results = _fetch_grouped_daily(target_date)
        filtered = [
            result
            for result in results
            if isinstance(result, dict) and result.get("T") in desired
        ]
        if not filtered:
            logger.info("No Massive grouped daily rows for configured tickers on %s", target_date)
            continue

        items: list[StockItem] = []
        warnings: list[str] = []
        found_symbols: set[str] = set()

        for result in filtered:
            symbol = result.get("T")
            if isinstance(symbol, str):
                found_symbols.add(symbol)

            item, warning = _try_build_stock_item(result)
            if item is not None:
                items.append(item)
            if warning:
                warnings.append(warning)

        missing = [symbol for symbol in tickers if symbol not in found_symbols]
        if missing:
            warnings.append(f"No market data returned for: {', '.join(missing)}")

        if items:
            logger.info(
                "Loaded %s stock rows from Massive for %s; warnings=%s",
                len(items),
                target_date,
                len(warnings),
            )
            return StockCollection(items=items, warnings=warnings)

    raise MassiveApiError(
        503,
        "Massive API returned no recent market data for the configured tickers",
        log_detail=f"Checked dates: {', '.join(checked_dates)}",
    )


def _recent_market_dates() -> list[str]:
    dates: list[str] = []
    cursor = date.today() - timedelta(days=1)

    while len(dates) < MAX_LOOKBACK_DAYS:
        if cursor.weekday() < 5:
            dates.append(cursor.isoformat())
        cursor -= timedelta(days=1)

    return dates


def _fetch_grouped_daily(target_date: str) -> list[dict[str, Any]]:
    query = parse.urlencode(
        {
            "adjusted": "true",
            "include_otc": "false",
            "apiKey": settings.massive_api_key,
        }
    )
    url = f"{MASSIVE_GROUPED_DAILY_URL.format(date=target_date)}?{query}"
    payload = _request_json(url)

    if payload.get("status") != "OK":
        raise _build_payload_error(payload, default_status=503)

    results = payload.get("results")
    if results is None:
        return []
    if not isinstance(results, list):
        raise MassiveApiError(502, "Massive API returned an invalid market data payload")

    return results


def _fetch_stock_reference(symbol: str) -> tuple[StockReference, str | None]:
    cached = _reference_cache.get(symbol)
    if cached is not None:
        return cached, None

    query = parse.urlencode({"apiKey": settings.massive_api_key})
    url = f"{MASSIVE_TICKER_OVERVIEW_URL.format(ticker=symbol)}?{query}"

    try:
        payload = _request_json(url)
        if payload.get("status") != "OK":
            raise _build_payload_error(payload, default_status=503)
        result = payload.get("results")
        if not isinstance(result, dict):
            raise MassiveApiError(502, f"Massive API did not return reference data for {symbol}")
    except MassiveApiError as exc:
        warning = f"Reference fallback used for {symbol}: {exc.user_detail}"
        logger.warning("%s", warning)
        reference = StockReference(symbol=symbol, name=symbol, currency=DEFAULT_CURRENCY)
        return reference, warning

    name = result.get("name")
    currency = result.get("currency_symbol") or result.get("currency_name") or DEFAULT_CURRENCY
    if not isinstance(name, str) or not name:
        name = symbol
    currency = _normalize_currency(currency)

    reference = StockReference(symbol=symbol, name=name, currency=currency)
    _reference_cache[symbol] = reference
    return reference, None


def _request_json(url: str) -> dict[str, Any]:
    req = request.Request(url, headers={"Accept": "application/json"})

    try:
        with request.urlopen(req, timeout=settings.massive_timeout_seconds) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = _extract_error_detail(exc)
        raise _map_http_error(exc.code, detail) from exc
    except error.URLError as exc:
        raise MassiveApiError(503, "Failed to reach Massive API", log_detail=str(exc.reason)) from exc
    except json.JSONDecodeError as exc:
        raise MassiveApiError(502, "Massive API returned invalid JSON") from exc


def _extract_error_detail(exc: error.HTTPError) -> str:
    try:
        payload = json.loads(exc.read().decode("utf-8"))
    except Exception:
        return f"Massive API request failed with status {exc.code}"

    return (
        payload.get("error")
        or payload.get("message")
        or f"Massive API request failed with status {exc.code}"
    )


def _map_http_error(status_code: int, detail: str) -> MassiveApiError:
    detail_lower = detail.lower()
    if status_code == 429 or "rate limit" in detail_lower:
        return MassiveApiError(503, "Massive API rate limit reached; retry later", log_detail=detail)
    if status_code in {401, 403} or "not entitled" in detail_lower or "upgrade your plan" in detail_lower:
        return MassiveApiError(503, "Massive API plan does not include this data", log_detail=detail)
    if 500 <= status_code <= 599:
        return MassiveApiError(503, "Massive API is temporarily unavailable", log_detail=detail)
    return MassiveApiError(502, detail, log_detail=detail)


def _build_payload_error(payload: dict[str, Any], default_status: int) -> MassiveApiError:
    detail = payload.get("error") or payload.get("message") or "Massive API returned an error"
    status_code = default_status
    detail_lower = detail.lower()
    if "rate limit" in detail_lower:
        status_code = 503
        detail = "Massive API rate limit reached; retry later"
    elif "not entitled" in detail_lower or "upgrade your plan" in detail_lower:
        status_code = 503
        detail = "Massive API plan does not include this data"
    return MassiveApiError(status_code, detail, log_detail=str(payload))


def _try_build_stock_item(result: dict[str, Any]) -> tuple[StockItem | None, str | None]:
    symbol = result.get("T")
    if not isinstance(symbol, str) or not symbol:
        warning = "Skipped one Massive row because it had no valid ticker"
        logger.warning("%s", warning)
        return None, warning

    close_price = result.get("c")
    if not isinstance(close_price, (int, float)):
        warning = f"Skipped {symbol} because Massive returned no close price"
        logger.warning("%s", warning)
        return None, warning

    open_price = result.get("o")
    if not isinstance(open_price, (int, float)):
        warning = f"Skipped {symbol} because Massive returned no open price"
        logger.warning("%s", warning)
        return None, warning

    high_price = result.get("h")
    if not isinstance(high_price, (int, float)):
        warning = f"Skipped {symbol} because Massive returned no high price"
        logger.warning("%s", warning)
        return None, warning

    low_price = result.get("l")
    if not isinstance(low_price, (int, float)):
        warning = f"Skipped {symbol} because Massive returned no low price"
        logger.warning("%s", warning)
        return None, warning

    volume = result.get("v")
    if not isinstance(volume, (int, float)):
        warning = f"Skipped {symbol} because Massive returned no volume"
        logger.warning("%s", warning)
        return None, warning

    aggregate_timestamp = result.get("t")
    if not isinstance(aggregate_timestamp, (int, float)):
        warning = f"Skipped {symbol} because Massive returned no price date"
        logger.warning("%s", warning)
        return None, warning

    reference, reference_warning = _fetch_stock_reference(symbol)
    price_date = datetime.fromtimestamp(aggregate_timestamp / 1000, UTC).date().isoformat()
    day_change = float(close_price) - float(open_price)
    day_change_percent = (day_change / float(open_price) * 100) if float(open_price) != 0 else 0.0
    vwap_price = result.get("vw")
    trade_count = result.get("n")

    return (
        StockItem(
            symbol=symbol,
            name=reference.name,
            open_price=float(open_price),
            high_price=float(high_price),
            low_price=float(low_price),
            close_price=float(close_price),
            volume=float(volume),
            vwap_price=float(vwap_price) if isinstance(vwap_price, (int, float)) else None,
            trade_count=int(trade_count) if isinstance(trade_count, (int, float)) else None,
            day_change=day_change,
            day_change_percent=day_change_percent,
            price_date=price_date,
            currency=reference.currency,
            source=SOURCE_NAME,
            data_delay=DATA_DELAY,
            warning=reference_warning,
        ),
        reference_warning,
    )


def _normalize_currency(value: Any) -> str:
    if not isinstance(value, str) or not value:
        return DEFAULT_CURRENCY
    normalized = value.upper()
    if len(normalized) != 3 or not normalized.isalpha():
        return DEFAULT_CURRENCY
    return normalized


def _serialize_cached_items(
    cached: CachedStocks,
    cache_status: str,
    extra_warning: str | None = None,
) -> list[dict[str, Any]]:
    shared_warning = _merge_warnings(cached.warnings, extra_warning)

    return [
        {
            "symbol": item.symbol,
            "name": item.name,
            "open_price": item.open_price,
            "high_price": item.high_price,
            "low_price": item.low_price,
            "close_price": item.close_price,
            "volume": item.volume,
            "vwap_price": item.vwap_price,
            "trade_count": item.trade_count,
            "day_change": item.day_change,
            "day_change_percent": item.day_change_percent,
            "price_date": item.price_date,
            "currency": item.currency,
            "source": item.source,
            "data_delay": item.data_delay,
            "cache_status": cache_status,
            "fetched_at": cached.fetched_at,
            "warning": _merge_warnings([item.warning] if item.warning else [], shared_warning),
        }
        for item in cached.items
    ]


def _merge_warnings(warnings: list[str] | None, extra_warning: str | None) -> str | None:
    parts = [warning for warning in (warnings or []) if warning]
    if extra_warning:
        parts.append(extra_warning)
    if not parts:
        return None
    return " | ".join(dict.fromkeys(parts))


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()
