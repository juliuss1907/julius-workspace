"""
Fear & Greed Index Client
Fetches market sentiment from alternative.me API
"""
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime
from utils import get_logger
from .base import DataSource

logger = get_logger(__name__)

class FearGreedClient(DataSource):
    """Fetch Fear & Greed Index"""

    BASE_URL = "https://api.alternative.me/fng"

    def __init__(self):
        super().__init__("fear_greed")
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def fetch_current(self) -> Optional[Dict]:
        """Fetch current Fear & Greed value"""
        try:
            session = await self._get_session()
            async with session.get(self.BASE_URL, timeout=10) as resp:
                if resp.status != 200:
                    self.record_error()
                    return None
                data = await resp.json()
                item = data["data"][0]
                result = {
                    "value": int(item["value"]),
                    "classification": item["value_classification"],
                    "timestamp": int(item["timestamp"]),
                    "source": "fear_greed"
                }
                self.record_success()
                return result
        except Exception as e:
            logger.error(f"Error fetching Fear & Greed: {e}")
            self.record_error()
            return None

    async def fetch_history(self, days: int = 7) -> List[Dict]:
        """Fetch historical Fear & Greed values"""
        try:
            session = await self._get_session()
            limit = min(days, 30)
            async with session.get(f"{self.BASE_URL}?limit={limit}", timeout=10) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                history = []
                for item in data["data"]:
                    history.append({
                        "value": int(item["value"]),
                        "classification": item["value_classification"],
                        "timestamp": int(item["timestamp"]),
                        "source": "fear_greed"
                    })
                self.record_success()
                return history
        except Exception as e:
            logger.error(f"Error fetching Fear & Greed history: {e}")
            self.record_error()
            return []

    def classify_sentiment(self, value: int) -> Dict:
        """Convert Fear & Greed value to sentiment score"""
        if value <= 25:
            return {"sentiment": "extreme_fear", "score": 0.8, "contrarian": True,
                    "note": "Extreme fear — contrarian bullish signal"}
        elif value <= 45:
            return {"sentiment": "fear", "score": 0.65, "contrarian": False}
        elif value <= 55:
            return {"sentiment": "neutral", "score": 0.50, "contrarian": False}
        elif value <= 75:
            return {"sentiment": "greed", "score": 0.35, "contrarian": False}
        else:
            return {"sentiment": "extreme_greed", "score": 0.2, "contrarian": True,
                    "note": "Extreme greed — contrarian bearish signal"}

    async def health_check(self) -> bool:
        try:
            session = await self._get_session()
            async with session.get(self.BASE_URL, timeout=5) as resp:
                return resp.status == 200
        except:
            return False

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def fetch(self, **kwargs) -> List[Dict]:
        return await self.fetch_history()
