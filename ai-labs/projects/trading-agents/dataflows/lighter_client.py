"""
Lighter Derivatives Data Client

Lighter API coverage is treated as optional. The client attempts common public
market endpoints and returns None when the public schema is unavailable.
"""
import time
from typing import Dict, List, Optional

import aiohttp

from utils import get_logger
from .base import DataSource


logger = get_logger(__name__)


class LighterClient(DataSource):
    """Best-effort public Lighter perp data client."""

    BASE_URL = "https://mainnet.zklighter.elliot.ai"


    def __init__(self):
        super().__init__("lighter")
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    def _coin_from_symbol(self, symbol: str) -> str:
        symbol = symbol.upper()
        return symbol[:-4] if symbol.endswith("USDT") else symbol

    async def _get(self, endpoint: str, params: Optional[Dict] = None, timeout: int = 10):
        try:
            session = await self._get_session()
            async with session.get(f"{self.BASE_URL}{endpoint}", params=params or {}, timeout=timeout) as resp:
                if resp.status != 200:
                    logger.debug(f"Lighter API {endpoint} returned {resp.status}")
                    self.record_error()
                    return None
                data = await resp.json()
                self.record_success()
                return data
        except Exception as e:
            logger.debug(f"Lighter request failed for {endpoint}: {e}")
            self.record_error()
            return None

    async def fetch_markets(self) -> List[Dict]:
        """Fetch public market metadata using best-effort endpoint names."""
        for endpoint in ("/api/v1/orderBookDetails", "/api/v1/markets", "/api/v1/ticker"):
            data = await self._get(endpoint)
            if isinstance(data, dict):
                for key in ("order_book_details", "markets", "data", "tickers"):
                    value = data.get(key)
                    if isinstance(value, list):
                        return value
            elif isinstance(data, list):
                return data
        return []

    async def fetch_derivatives_snapshot(self, symbol: str) -> Optional[Dict]:
        coin = self._coin_from_symbol(symbol)
        markets = await self.fetch_markets()
        if not markets:
            return None

        market = None
        for item in markets:
            text = " ".join(str(item.get(k, "")) for k in ("symbol", "name", "asset", "market", "ticker"))
            if coin in text.upper():
                market = item
                break

        if not market:
            return None

        mark_price = self._to_float(
            market.get("mark_price") or market.get("markPrice") or market.get("price") or market.get("last_price")
        )
        open_interest = self._to_float(market.get("open_interest") or market.get("openInterest"))
        funding_rate = self._to_float(market.get("funding_rate") or market.get("fundingRate") or market.get("funding"))

        return {
            "source": "lighter",
            "symbol": f"{coin}USDT",
            "funding_rate": funding_rate,
            "open_interest": open_interest,
            "open_interest_value": open_interest * mark_price if open_interest and mark_price else None,
            "long_short_ratio": None,
            "mark_price": mark_price,
            "last_price": mark_price,
            "price_change_24h_pct": self._to_float(market.get("price_change_24h_pct") or market.get("dailyPriceChange")),
            "timestamp": int(time.time()),
            "raw": market,
        }

    def _to_float(self, value) -> Optional[float]:
        try:
            if value in (None, ""):
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    async def health_check(self) -> bool:
        markets = await self.fetch_markets()
        return bool(markets)

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def fetch(self, symbol: str, **kwargs) -> Optional[Dict]:
        return await self.fetch_derivatives_snapshot(symbol)
