"""
RSS Feed Fetcher
Fetches crypto news from active RSS feeds.
"""
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import feedparser
import re
from utils import get_logger
from .base import DataSource


logger = get_logger(__name__)


class RSSFetcher(DataSource):
    """Fetch news from RSS feeds"""
    
    # RSS feed URLs
    FEEDS = {
        'coindesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
        'cointelegraph': 'https://cointelegraph.com/rss',
        'decrypt': 'https://decrypt.co/feed'
    }

    JSON_FEEDS = {
        'thefeed': 'https://thefeed.today/rag/api/data'
    }
    
    def __init__(self):
        super().__init__("rss_fetcher")
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with User-Agent"""
        if self.session is None or self.session.closed:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def fetch_feed(
        self,
        feed_name: str,
        limit: int = 20,
        hours: int = 24
    ) -> List[Dict]:
        """
        Fetch articles from a single RSS feed
        
        Args:
            feed_name: Name of the configured feed
            limit: Maximum number of articles to fetch
            hours: Only fetch articles from last N hours
        
        Returns:
            List of article dicts with: title, link, published, summary, source
        """
        if feed_name not in self.FEEDS:
            logger.error(f"Unknown feed: {feed_name}. Available: {list(self.FEEDS.keys())}")
            return []
        
        feed_url = self.FEEDS[feed_name]
        
        try:
            session = await self._get_session()
            
            # Fetch RSS feed
            async with session.get(feed_url, timeout=10) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch {feed_name}: HTTP {response.status}")
                    self.record_error()
                    return []
                
                content = await response.text()
            
            # Parse RSS feed
            feed = feedparser.parse(content)
            
            if feed.bozo:
                logger.warning(f"Feed {feed_name} has parsing errors: {feed.bozo_exception}")
            
            # Calculate time threshold
            time_threshold = datetime.now() - timedelta(hours=hours)
            
            # Extract articles
            articles = []
            for entry in feed.entries[:limit]:
                # Parse published date
                published_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_date = datetime(*entry.updated_parsed[:6])
                
                # Filter by date
                if published_date and published_date < time_threshold:
                    continue
                
                # Extract article data
                article = {
                    'title': entry.get('title', '').strip(),
                    'link': entry.get('link', ''),
                    'published': published_date.isoformat() if published_date else None,
                    'summary': entry.get('summary', '').strip(),
                    'source': feed_name,
                    'feed_url': feed_url
                }
                
                # Clean up summary (remove HTML tags)
                if article['summary']:
                    import re
                    article['summary'] = re.sub(r'<[^>]+>', '', article['summary'])
                    article['summary'] = article['summary'][:500]  # Limit length
                
                articles.append(article)
            
            logger.info(f"Fetched {len(articles)} articles from {feed_name} (last {hours}h)")
            self.record_success()
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching feed {feed_name}: {e}")
            self.record_error()
            return []

    async def fetch_thefeed(
        self,
        limit: int = 20,
        hours: int = 24
    ) -> List[Dict]:
        """Fetch crypto trend summaries from The Feed JSON API."""
        feed_name = 'thefeed'
        feed_url = self.JSON_FEEDS[feed_name]

        try:
            session = await self._get_session()
            params = {
                'category': 'cryptocurrency',
                'sort': 'postedAt',
                'dir': 'desc',
                'limit': limit,
            }
            async with session.get(feed_url, params=params, timeout=10) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch {feed_name}: HTTP {response.status}")
                    self.record_error()
                    return []
                data = await response.json()

            rows = data.get('rows', []) if isinstance(data, dict) else []
            time_threshold = datetime.now() - timedelta(hours=hours)
            articles = []

            for row in rows[:limit]:
                published_date = self._parse_iso_datetime(row.get('postedAt'))
                if published_date and published_date < time_threshold:
                    continue

                summary = row.get('shortSummary') or row.get('summaryWhy') or row.get('text') or ''
                text = row.get('text') or summary
                author = row.get('username') or row.get('authorName') or 'thefeed'
                article = {
                    'title': str(summary).strip(),
                    'link': row.get('tweetUrl') or '',
                    'published': published_date.isoformat() if published_date else None,
                    'summary': str(row.get('summaryWhy') or summary).strip(),
                    'text': str(text).strip(),
                    'source': feed_name,
                    'feed_url': feed_url,
                    'author': author,
                    'metrics': {
                        'likes': row.get('likes'),
                        'comments': row.get('comments'),
                        'reposts': row.get('reposts'),
                        'impressions': row.get('impressions'),
                        'delta_impressions_1h': row.get('deltaImpressions1h'),
                    },
                }
                articles.append(article)

            logger.info(f"Fetched {len(articles)} articles from {feed_name} (last {hours}h)")
            self.record_success()
            return articles

        except Exception as e:
            logger.error(f"Error fetching feed {feed_name}: {e}")
            self.record_error()
            return []

    def _parse_iso_datetime(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value).replace('Z', '+00:00')).replace(tzinfo=None)
        except ValueError:
            return None
    
    async def fetch_all_feeds(
        self,
        hours: int = 24,
        limit: int = 20
    ) -> List[Dict]:
        """
        Fetch articles from all RSS feeds in parallel
        
        Args:
            hours: Only fetch articles from last N hours
            limit: Maximum number of articles per feed
        
        Returns:
            Aggregated list of articles from all feeds
        """
        total_feeds = len(self.FEEDS) + len(self.JSON_FEEDS)
        logger.info(f"Fetching articles from {total_feeds} news feeds (last {hours}h)...")
        
        # Create tasks for all feeds
        tasks = [
            self.fetch_feed(feed_name, limit, hours)
            for feed_name in self.FEEDS.keys()
        ]
        feed_names = list(self.FEEDS.keys())
        tasks.append(self.fetch_thefeed(limit=limit, hours=hours))
        feed_names.append('thefeed')
        
        # Run in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        all_articles = []
        for feed_name, result in zip(feed_names, results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching from {feed_name}: {result}")
                continue
            
            all_articles.extend(result)
        
        # Sort by date (newest first)
        all_articles.sort(
            key=lambda x: x['published'] if x['published'] else '',
            reverse=True
        )
        
        logger.info(f"✓ Fetched {len(all_articles)} total articles from all feeds")
        return all_articles
    
    async def fetch(
        self,
        hours: int = 24,
        limit: int = 20
    ) -> List[Dict]:
        """
        Fetch articles from all RSS feeds (implements DataSource.fetch)
        
        Args:
            hours: Only fetch articles from last N hours
            limit: Maximum number of articles per feed
        
        Returns:
            List of article dicts
        """
        return await self.fetch_all_feeds(hours=hours, limit=limit)
    
    async def health_check(self) -> bool:
        """Check if at least one RSS feed is accessible"""
        try:
            session = await self._get_session()
            
            accessible_feeds = 0
            total_feeds = len(self.FEEDS) + len(self.JSON_FEEDS)
            for feed_name, feed_url in self.FEEDS.items():
                try:
                    async with session.get(feed_url, timeout=5) as response:
                        if response.status == 200:
                            accessible_feeds += 1
                            logger.info(f"✓ {feed_name} is accessible")
                        else:
                            logger.warning(f"⚠ {feed_name} returned HTTP {response.status}")
                except Exception as e:
                    logger.warning(f"⚠ {feed_name} failed: {e}")

            try:
                async with session.get(self.JSON_FEEDS['thefeed'], params={'category': 'cryptocurrency', 'limit': 1}, timeout=5) as response:
                    if response.status == 200:
                        accessible_feeds += 1
                        logger.info("✓ thefeed is accessible")
                    else:
                        logger.warning(f"⚠ thefeed returned HTTP {response.status}")
            except Exception as e:
                logger.warning(f"⚠ thefeed failed: {e}")
            
            # At least one feed must be accessible
            if accessible_feeds > 0:
                logger.info(f"✓ {accessible_feeds}/{total_feeds} feeds are accessible")
                return True
            else:
                logger.error("✗ No feeds are accessible")
                return False
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def close(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("RSS fetcher session closed")
    
    def filter_by_keywords(
        self,
        articles: List[Dict],
        keywords: List[str]
    ) -> List[Dict]:
        """
        Filter articles by keywords (coin symbols, etc.)
        
        Args:
            articles: List of article dicts
            keywords: List of keywords to search for (case-insensitive)
        
        Returns:
            Filtered list of articles containing keywords
        """
        keywords_lower = [kw.lower() for kw in keywords]
        
        filtered = []
        for article in articles:
            text = f"{article['title']} {article['summary']}".lower()
            
            matched = [kw for kw in keywords_lower if self._keyword_matches(text, kw)]
            # Check if any keyword is in the article
            if matched:
                # Add matched keywords to article data
                article['matched_keywords'] = matched
                filtered.append(article)
        
        logger.info(f"Filtered {len(filtered)}/{len(articles)} articles by keywords: {keywords}")
        return filtered

    def _keyword_matches(self, text: str, keyword: str) -> bool:
        """Match short tickers as tokens so SOL does not match words like sold."""
        if len(keyword) <= 4 and keyword.isalnum():
            return re.search(rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])", text) is not None
        return keyword in text
    
    def remove_duplicates(
        self,
        articles: List[Dict],
        similarity_threshold: float = 0.8
    ) -> List[Dict]:
        """
        Remove duplicate articles based on title similarity
        
        Args:
            articles: List of article dicts
            similarity_threshold: Minimum similarity to consider as duplicate (0-1)
        
        Returns:
            Deduplicated list of articles
        """
        if not articles:
            return []
        
        unique_articles = []
        seen_titles = []
        
        for article in articles:
            title = article['title']
            
            # Check if similar title already seen
            is_duplicate = False
            for seen_title in seen_titles:
                similarity = self._calculate_similarity(title, seen_title)
                if similarity >= similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
                seen_titles.append(title)
        
        logger.info(f"Removed {len(articles) - len(unique_articles)} duplicate articles")
        return unique_articles
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity using Jaccard index
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity score (0-1)
        """
        # Tokenize
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Jaccard similarity
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
