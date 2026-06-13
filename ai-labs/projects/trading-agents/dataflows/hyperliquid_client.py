"""
Hyperliquid Derivatives Data Client
"""
import time
from typing import Dict, List, Optional

import aiohttp

from utils import get_logger
from .base import DataSource


logger = get_logger(__name__)


class HyperliquidClient(DataSource):
    """Fetch Hyperliquid perp asset contexts and normalize by symbol."""

    BASE_URL = "https://api.hyperliquid.xyz/info"

    def __init__(self):
        super().__init__("hyperliquid")
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    def _coin_from_symbol(self, symbol: str) -> str:
        symbol = symbol.upper()
        return symbol[:-4] if symbol.endswith("USDT") else symbol

    async def _post(self, payload: Dict, timeout: int = 10):
        try:
            session = await self._get_session()
            async with session.post(self.BASE_URL, json=payload, timeout=timeout) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.warning(f"Hyperliquid API error {resp.status}: {error_text}")
                    self.record_error()
                    return None
                data = await resp.json()
                self.record_success()
                return data
        except Exception as e:
            logger.warning(f"Hyperliquid request failed: {e}")
            self.record_error()
            return None

    async def fetch_asset_contexts(self) -> List[Dict]:
        data = await self._post({"type": "metaAndAssetCtxs"})
        if not data or not isinstance(data, list) or len(data) < 2:
            return []

        meta = data[0]
        contexts = data[1]
        universe = meta.get("universe", [])
        results = []

        for index, asset in enumerate(universe):
            if index >= len(contexts):
                continue
            ctx = contexts[index]
            results.append({"coin": asset.get("name"), "context": ctx, "raw_asset": asset})

        return results

    async def fetch_derivatives_snapshot(self, symbol: str) -> Optional[Dict]:
        coin = self._coin_from_symbol(symbol)
        contexts = await self.fetch_asset_contexts()
        item = next((ctx for ctx in contexts if ctx.get("coin") == coin), None)
        if not item:
            logger.warning(f"Hyperliquid symbol not found: {coin}")
            return None

        ctx = item["context"]
        mark_price = self._to_float(ctx.get("markPx"))
        open_interest = self._to_float(ctx.get("openInterest"))
        funding_rate = self._to_float(ctx.get("funding"))

        return {
            "source": "hyperliquid",
            "symbol": f"{coin}USDT",
            "funding_rate": funding_rate,
            "open_interest": open_interest,
            "open_interest_value": open_interest * mark_price if open_interest and mark_price else None,
            "long_short_ratio": None,
            "mark_price": mark_price,
            "last_price": self._to_float(ctx.get("midPx")) or mark_price,
            "price_change_24h_pct": None,
            "timestamp": int(time.time()),
            "raw": {"asset": item.get("raw_asset"), "context": ctx},
        }

    def _to_float(self, value) -> Optional[float]:
        try:
            if value in (None, ""):
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    async def health_check(self) -> bool:
        data = await self._post({"type": "meta"}, timeout=5)
        return data is not None

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def fetch(self, symbol: str, **kwargs) -> Optional[Dict]:
        return await self.fetch_derivatives_snapshot(symbol)
