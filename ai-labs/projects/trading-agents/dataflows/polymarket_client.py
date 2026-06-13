"""
Polymarket Client
Fetches prediction market data for crypto-related markets
"""
import aiohttp
from typing import List, Dict, Optional
from utils import get_logger
from .base import DataSource

logger = get_logger(__name__)

class PolymarketClient(DataSource):
    """Fetch prediction market data from Polymarket CLOB API"""

    CLOB_URL = "https://clob.polymarket.com"
    GAMMA_URL = "https://gamma-api.polymarket.com"

    CRYPTO_TAGS = ["crypto", "bitcoin", "ethereum", "solana", "defi",
                   "blockchain", "cryptocurrency", "btc", "eth", "sol"]

    def __init__(self):
        super().__init__("polymarket")
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def search_markets(self, query: str = "crypto", limit: int = 10) -> List[Dict]:
        """Search for markets related to a query"""
        try:
            session = await self._get_session()
            url = f"{self.GAMMA_URL}/markets"
            params = {"limit": limit, "tag": query, "active": "true", "closed": "false"}

            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    self.record_error()
                    return []
                markets = await resp.json()

            results = []
            for m in markets:
                results.append({
                    "id": m.get("id"),
                    "question": m.get("question", ""),
                    "slug": m.get("slug", ""),
                    "volume": float(m.get("volume", 0)),
                    "liquidity": float(m.get("liquidity", 0)),
                    "outcomes": m.get("outcomes", []),
                    "outcome_prices": m.get("outcomePrices", []),
                    "end_date": m.get("endDateIso", ""),
                    "source": "polymarket"
                })

            self.record_success()
            return results

        except Exception as e:
            logger.error(f"Error searching Polymarket: {e}")
            self.record_error()
            return []

    async def get_market_data(self, market_id: str) -> Optional[Dict]:
        """Get detailed data for a specific market"""
        try:
            session = await self._get_session()
            url = f"{self.GAMMA_URL}/markets/{market_id}"
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    return None
                m = await resp.json()

            prices = m.get("outcomePrices", [])
            dominant_outcome = max(prices) if prices else 0

            return {
                "id": m.get("id"),
                "question": m.get("question", ""),
                "volume": float(m.get("volume", 0)),
                "dominant_odds": float(dominant_outcome),
                "outcomes": m.get("outcomes", []),
                "outcome_prices": [float(p) for p in prices],
                "source": "polymarket"
            }

        except Exception as e:
            logger.error(f"Error fetching Polymarket market: {e}")
            return None

    async def fetch_crypto_markets(self, limit: int = 10) -> List[Dict]:
        """Fetch all crypto-related active markets"""
        import asyncio
        tasks = [self.search_markets(tag, limit=5) for tag in self.CRYPTO_TAGS[:4]]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_markets = []
        seen_ids = set()
        for result in results:
            if isinstance(result, Exception):
                continue
            for m in result:
                if m["id"] not in seen_ids:
                    seen_ids.add(m["id"])
                    all_markets.append(m)

        all_markets.sort(key=lambda x: x["volume"], reverse=True)
        logger.info(f"Fetched {len(all_markets)} Polymarket crypto markets")
        return all_markets[:limit]

    def calculate_sentiment(self, market: Dict) -> Dict:
        """Convert market odds to sentiment signal"""
        odds = market.get("dominant_odds", 0.5)
        prices = market.get("outcome_prices", [])

        # Higher odds = stronger bullish expectation
        if odds >= 0.7:
            sentiment = "bullish"
            score = 0.7 + (odds - 0.7) * 0.3
        elif odds <= 0.3:
            sentiment = "bearish"
            score = 0.3 - (0.3 - odds) * 0.3
        else:
            sentiment = "neutral"
            score = 0.5

        # More volume & liquidity = stronger signal
        volume_factor = min(1.0, market.get("volume", 0) / 100000)
        liquidity_factor = min(1.0, market.get("liquidity", 0) / 50000)
        confidence = (volume_factor + liquidity_factor) / 2

        return {
            "sentiment": sentiment,
            "score": self._clamp(score),
            "confidence": confidence,
            "market_odds": odds,
            "question": market.get("question", "")[:100]
        }

    def _clamp(self, val: float) -> float:
        return max(0.0, min(1.0, val))

    async def health_check(self) -> bool:
        try:
            session = await self._get_session()
            async with session.get(f"{self.CLOB_URL}", timeout=5) as resp:
                return resp.status in [200, 404]
        except:
            return False

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def fetch(self, **kwargs) -> List[Dict]:
        return await self.fetch_crypto_markets()
