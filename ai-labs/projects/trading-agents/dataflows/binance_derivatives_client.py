"""
Binance Derivatives Data Client

Fetches public USDT-M futures market structure data and normalizes it for
DerivativesAnalyst. This client is read-only and does not require API keys.
"""
import asyncio
import time
from typing import Dict, Optional

import aiohttp

from utils import get_logger
from .base import DataSource


logger = get_logger(__name__)


class BinanceDerivativesClient(DataSource):
    """Fetch Binance Futures funding, OI, long/short ratio, and mark price."""

    BASE_URL = "https://fapi.binance.com"

    def __init__(self):
        super().__init__("binance_derivatives")
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _request(self, endpoint: str, params: Optional[Dict] = None, timeout: int = 10):
        try:
            session = await self._get_session()
            async with session.get(f"{self.BASE_URL}{endpoint}", params=params or {}, timeout=timeout) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.warning(f"Binance derivatives API error {resp.status}: {error_text}")
                    self.record_error()
                    return None
                data = await resp.json()
                self.record_success()
                return data
        except Exception as e:
            logger.warning(f"Binance derivatives request failed: {e}")
            self.record_error()
            return None

    def _normalize_symbol(self, symbol: str) -> str:
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        return symbol

    async def fetch_funding_rate(self, symbol: str) -> Optional[Dict]:
        symbol = self._normalize_symbol(symbol)
        data = await self._request("/fapi/v1/premiumIndex", {"symbol": symbol})
        if not data:
            return None
        return {
            "funding_rate": float(data.get("lastFundingRate") or 0),
            "next_funding_time": int(data.get("nextFundingTime") or 0) // 1000,
            "mark_price": float(data.get("markPrice") or 0),
            "index_price": float(data.get("indexPrice") or 0),
            "timestamp": int(data.get("time") or int(time.time() * 1000)) // 1000,
            "raw": data,
        }

    async def fetch_open_interest(self, symbol: str) -> Optional[Dict]:
        symbol = self._normalize_symbol(symbol)
        data = await self._request("/fapi/v1/openInterest", {"symbol": symbol})
        if not data:
            return None
        return {
            "open_interest": float(data.get("openInterest") or 0),
            "timestamp": int(data.get("time") or int(time.time() * 1000)) // 1000,
            "raw": data,
        }

    async def fetch_long_short_ratio(self, symbol: str, period: str = "1h") -> Optional[Dict]:
        symbol = self._normalize_symbol(symbol)
        params = {"symbol": symbol, "period": period, "limit": 1}
        data = await self._request("/futures/data/globalLongShortAccountRatio", params)
        if not data:
            return None
        latest = data[-1] if isinstance(data, list) and data else data
        return {
            "long_short_ratio": float(latest.get("longShortRatio") or 0),
            "long_account": float(latest.get("longAccount") or 0),
            "short_account": float(latest.get("shortAccount") or 0),
            "timestamp": int(latest.get("timestamp") or int(time.time() * 1000)) // 1000,
            "raw": latest,
        }

    async def fetch_ticker(self, symbol: str) -> Optional[Dict]:
        symbol = self._normalize_symbol(symbol)
        data = await self._request("/fapi/v1/ticker/24hr", {"symbol": symbol})
        if not data:
            return None
        return {
            "last_price": float(data.get("lastPrice") or 0),
            "price_change_24h_pct": float(data.get("priceChangePercent") or 0),
            "quote_volume_24h": float(data.get("quoteVolume") or 0),
            "timestamp": int(data.get("closeTime") or int(time.time() * 1000)) // 1000,
            "raw": data,
        }

    async def fetch_derivatives_snapshot(self, symbol: str) -> Optional[Dict]:
        """Fetch and normalize a one-symbol derivatives snapshot."""
        symbol = self._normalize_symbol(symbol)
        funding, oi, ratio, ticker = await asyncio.gather(
            self.fetch_funding_rate(symbol),
            self.fetch_open_interest(symbol),
            self.fetch_long_short_ratio(symbol),
            self.fetch_ticker(symbol),
            return_exceptions=True,
        )

        parts = []
        normalized = {
            "source": "binance",
            "symbol": symbol,
            "funding_rate": None,
            "open_interest": None,
            "open_interest_value": None,
            "long_short_ratio": None,
            "mark_price": None,
            "last_price": None,
            "price_change_24h_pct": None,
            "timestamp": int(time.time()),
            "raw": {},
        }

        for name, result in (("funding", funding), ("open_interest", oi), ("long_short_ratio", ratio), ("ticker", ticker)):
            if isinstance(result, Exception) or not result:
                continue
            parts.append(name)
            normalized["raw"][name] = result.get("raw", result)
            for key in normalized.keys():
                if key in result and result[key] not in (None, 0, ""):
                    normalized[key] = result[key]

        if not parts:
            return None

        if normalized["open_interest"] and normalized["mark_price"]:
            normalized["open_interest_value"] = normalized["open_interest"] * normalized["mark_price"]
        elif normalized["open_interest"] and normalized["last_price"]:
            normalized["open_interest_value"] = normalized["open_interest"] * normalized["last_price"]

        normalized["available_fields"] = parts
        return normalized

    async def health_check(self) -> bool:
        data = await self._request("/fapi/v1/ping", timeout=5)
        return data is not None

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def fetch(self, symbol: str, **kwargs) -> Optional[Dict]:
        return await self.fetch_derivatives_snapshot(symbol)
