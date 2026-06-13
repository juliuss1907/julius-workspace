"""
Reddit Client
Fetches posts from crypto-related subreddits
"""
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from utils import get_logger
from .base import DataSource

logger = get_logger(__name__)

class RedditClient(DataSource):
    """Fetch Reddit posts for sentiment analysis"""

    SUBREDDITS = ["cryptocurrency", "bitcoin", "ethereum", "solana"]
    BASE_URL = "https://www.reddit.com/r"
    USER_AGENT = "Mozilla/5.0 (compatible; TradingBot/1.0)"

    def __init__(self):
        super().__init__("reddit")
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            headers = {"User-Agent": self.USER_AGENT}
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session

    async def fetch_posts(self, subreddit: str, limit: int = 25, hours: int = 24) -> List[Dict]:
        """Fetch hot posts from a subreddit"""
        try:
            session = await self._get_session()
            url = f"{self.BASE_URL}/{subreddit}/hot.json"
            params = {"limit": limit, "raw_json": 1}

            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    logger.warning(f"Reddit {subreddit} returned HTTP {resp.status}")
                    self.record_error()
                    return []
                data = await resp.json()

            posts = []
            threshold = datetime.utcnow() - timedelta(hours=hours)

            for child in data.get("data", {}).get("children", []):
                post = child["data"]
                created = datetime.utcfromtimestamp(post["created_utc"])

                if created < threshold:
                    continue

                posts.append({
                    "title": post.get("title", ""),
                    "text": post.get("selftext", ""),
                    "subreddit": subreddit,
                    "upvotes": post.get("ups", 0),
                    "comments": post.get("num_comments", 0),
                    "score": post.get("score", 0),
                    "url": f"https://reddit.com{post.get('permalink', '')}",
                    "author": post.get("author", "unknown"),
                    "created": created.isoformat(),
                    "source": "reddit",
                    "flair": post.get("link_flair_text", "")
                })

            self.record_success()
            return posts

        except Exception as e:
            logger.error(f"Error fetching r/{subreddit}: {e}")
            self.record_error()
            return []

    async def fetch_all_subreddits(self, hours: int = 24, limit: int = 25) -> List[Dict]:
        """Fetch from all crypto subreddits"""
        import asyncio
        tasks = [self.fetch_posts(sr, limit, hours) for sr in self.SUBREDDITS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_posts = []
        for sr, result in zip(self.SUBREDDITS, results):
            if isinstance(result, Exception):
                logger.error(f"Error from r/{sr}: {result}")
                continue
            all_posts.extend(result)

        all_posts.sort(key=lambda x: x["upvotes"], reverse=True)
        logger.info(f"Fetched {len(all_posts)} Reddit posts from {len(self.SUBREDDITS)} subreddits")
        return all_posts

    async def health_check(self) -> bool:
        try:
            session = await self._get_session()
            async with session.get(f"{self.BASE_URL}/cryptocurrency/hot.json?limit=1", timeout=5) as resp:
                return resp.status == 200
        except:
            return False

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def fetch(self, **kwargs) -> List[Dict]:
        return await self.fetch_all_subreddits()
