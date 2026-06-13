"""
News Analyst Agent
Analyzes crypto news from Telegram channels and RSS feeds
"""
from datetime import datetime
from typing import Dict, List, Optional
import re
from agents.base_agent import BaseAgent, AgentResult, SignalDirection
from agents.news_sentiment import NewsSentimentClassifier
from dataflows import TelegramScraper, RSSFetcher
from utils import get_logger, config


logger = get_logger(__name__)


class NewsAnalyst(BaseAgent):
    """
    News Analyst Agent
    
    Fetches news from Telegram channels and RSS feeds,
    classifies sentiment, and generates trading signals.
    """
    
    # Coin keywords mapping
    COIN_KEYWORDS = {
        'BTC': ['BTC', 'Bitcoin', 'BTCUSDT', 'BTC/USDT'],
        'ETH': ['ETH', 'Ethereum', 'ETHUSDT', 'ETH/USDT'],
        'SOL': ['SOL', 'Solana', 'SOLUSDT', 'SOL/USDT'],
        'BNB': ['BNB', 'Binance Coin', 'BNBUSDT'],
        'XRP': ['XRP', 'Ripple', 'XRPUSDT'],
        'ADA': ['ADA', 'Cardano', 'ADAUSDT'],
        'DOGE': ['DOGE', 'Dogecoin', 'DOGEUSDT'],
    }
    
    def __init__(self, config_override: Optional[Dict] = None):
        super().__init__("NewsAnalyst", config_override)
        
        # Load config
        default_config = config.load_default_params()
        self.config = {**default_config.get("news_analysis", {}), **(config_override or {})}
        
        # Initialize components
        self.telegram_scraper = TelegramScraper()
        self.rss_fetcher = RSSFetcher()
        self.classifier = NewsSentimentClassifier()
        
        # Scoring weights for each source
        self.weights = self.config.get("weights", {
            "telegram": 0.40,  # Telegram channels (fast, real-time)
            "rss": 0.30,       # RSS feeds (professional, curated)
            "volume": 0.15,    # Article volume
            "recency": 0.15,   # How recent the news is
        })
        
        # Thresholds
        self.sentiment_threshold = self.config.get("sentiment_threshold", 0.1)
        self.min_articles = self.config.get("min_articles", 5)
    
    async def initialize(self):
        """Initialize the agent"""
        if self._initialized:
            return
        
        await self.telegram_scraper.initialize()
        logger.info("NewsAnalyst initialized")
        self._initialized = True
    
    async def analyze(self, symbol: str, data: Dict) -> AgentResult:
        """
        Perform news analysis
        
        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT)
            data: Dict containing:
                - coin: Coin name (e.g., BTC)
                - hours: How many hours to look back (default 24)
        
        Returns:
            AgentResult with analysis
        """
        if not self._initialized:
            await self.initialize()
        
        coin = data.get("coin", symbol.replace("USDT", ""))
        hours = data.get("hours", 24)
        
        # Get keywords for this coin
        keywords = self.COIN_KEYWORDS.get(coin, [coin])
        
        # Fetch news from all sources (parallel)
        telegram_messages = await self.telegram_scraper.fetch_all_channels(hours=hours, limit=30)
        rss_articles = await self.rss_fetcher.fetch_all_feeds(hours=hours, limit=20)
        
        # Filter by keywords
        telegram_filtered = self._filter_by_keywords(telegram_messages, keywords)
        rss_filtered = self._filter_by_keywords(rss_articles, keywords)
        
        # Combine all articles
        all_articles = telegram_filtered + rss_filtered
        
        if len(all_articles) < self.min_articles:
            logger.warning(f"{symbol}: Insufficient news ({len(all_articles)} articles)")
            return self._create_neutral_result(symbol, f"Insufficient news ({len(all_articles)} articles)")
        
        # Classify sentiment (hybrid)
        classified = await self.classifier.classify_articles(all_articles, llm_threshold=5)
        
        # Calculate scores
        scores = self._calculate_scores(classified, telegram_filtered, rss_filtered, hours)
        
        # Calculate overall sub-score
        sub_score = self._calculate_overall_score(scores)
        
        # Determine direction
        direction = self._determine_direction(sub_score)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(scores, classified)
        
        # Calculate confidence
        confidence = self._calculate_confidence(len(classified), scores)
        
        # Build analysis
        analysis = {
            "sources": {
                "telegram": len(telegram_filtered),
                "rss": len(rss_filtered),
                "total": len(classified)
            },
            "sentiment_breakdown": {
                "positive": scores.get("sentiment", {}).get("positive", 0),
                "negative": scores.get("sentiment", {}).get("negative", 0),
                "neutral": scores.get("sentiment", {}).get("neutral", 0),
                "avg_score": scores.get("sentiment", {}).get("avg", 0)
            },
            "scores": scores,
            "top_news": self._get_top_news(classified, 3),
            "hours_lookback": hours
        }
        
        return AgentResult(
            agent_name=self.name,
            symbol=symbol,
            timestamp=datetime.now(),
            direction=direction,
            sub_score=sub_score,
            confidence=confidence,
            analysis=analysis,
            reasoning=reasoning,
            metadata={"source_count": len(classified)}
        )
    
    def _filter_by_keywords(self, articles: List[Dict], keywords: List[str]) -> List[Dict]:
        """Filter articles by keywords"""
        if not articles:
            return []
        
        keywords_lower = [kw.lower() for kw in keywords]
        filtered = []
        
        for article in articles:
            text = ""
            if 'title' in article:
                text += article['title'] + " "
            if 'text' in article:
                text += article['text'] + " "
            if 'summary' in article:
                text += article['summary']
            
            text = text.lower()
            
            matched = [kw for kw in keywords_lower if self._keyword_matches(text, kw)]
            if matched:
                article['matched_keywords'] = matched
                filtered.append(article)
        
        return filtered

    def _keyword_matches(self, text: str, keyword: str) -> bool:
        """Match short tickers as tokens so SOL does not match words like sold."""
        if len(keyword) <= 4 and keyword.isalnum():
            return re.search(rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])", text) is not None
        return keyword in text
    
    def _calculate_scores(self, articles: List[Dict], telegram: List[Dict], rss: List[Dict], hours: int) -> Dict:
        """Calculate component scores"""
        scores = {}
        
        # Aggregate sentiment
        summary = self.classifier.aggregate_sentiment(articles)
        
        # Convert sentiment to score (0-1)
        avg_score = summary['avg_score']  # -1 to 1
        sentiment_score = self._clamp_score((avg_score + 1) / 2)  # Convert to 0-1
        
        scores["sentiment"] = {
            "positive": summary['positive'],
            "negative": summary['negative'],
            "neutral": summary['neutral'],
            "avg": avg_score,
            "score": sentiment_score
        }
        
        # Telegram vs RSS distribution
        if len(telegram) > 0 or len(rss) > 0:
            # Telegram tends to be faster (more weight if lots of Telegram messages)
            telegram_ratio = len(telegram) / max(len(telegram) + len(rss), 1)
            scores["source_quality"] = self._clamp_score(0.5 + telegram_ratio * 0.3 + 0.2)
        else:
            scores["source_quality"] = 0.5
        
        # Article volume (more articles = stronger signal)
        volume_threshold = 10
        if len(articles) >= volume_threshold:
            scores["volume"] = 0.8
        elif len(articles) >= 5:
            scores["volume"] = 0.6
        else:
            scores["volume"] = 0.4
        
        # Recency (recent news = stronger signal)
        recent_count = 0
        for article in articles:
            # Check if article is recent (< 6 hours)
            if self._is_recent(article, 6):
                recent_count += 1
        
        if recent_count > 0:
            recency_ratio = recent_count / max(len(articles), 1)
            scores["recency"] = self._clamp_score(0.4 + recency_ratio * 0.6)
        else:
            scores["recency"] = 0.5
        
        return scores
    
    def _is_recent(self, article: Dict, hours: int) -> bool:
        """Check if article is recent"""
        # Try different date fields
        date_str = None
        if 'date' in article:
            date_str = article['date']
        elif 'published' in article:
            date_str = article['published']
        
        if not date_str:
            return False
        
        try:
            article_date = datetime.fromisoformat(date_str)
            hours_diff = (datetime.now() - article_date).total_seconds() / 3600
            return hours_diff <= hours
        except:
            return False
    
    def _calculate_overall_score(self, scores: Dict) -> float:
        """Calculate weighted overall score"""
        weight_map = {
            "sentiment": self.weights.get("telegram", 0.40) + self.weights.get("rss", 0.30),
            "volume": self.weights.get("volume", 0.15),
            "recency": self.weights.get("recency", 0.15),
        }
        
        total = 0.0
        total_weight = 0.0
        
        for component, weight in weight_map.items():
            if component == "sentiment":
                value = scores.get("sentiment", {}).get("score", 0.5)
            else:
                value = scores.get(component, 0.5)
            
            total += value * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.5
        
        return self._clamp_score(total / total_weight)
    
    def _calculate_confidence(self, article_count: int, scores: Dict) -> float:
        """Calculate confidence in the analysis"""
        confidence = 0.5
        
        # More articles = higher confidence
        if article_count >= 20:
            confidence += 0.2
        elif article_count >= 10:
            confidence += 0.15
        elif article_count >= 5:
            confidence += 0.1
        
        # Strong sentiment = higher confidence
        avg_score = scores.get("sentiment", {}).get("avg", 0)
        if abs(avg_score) > 0.3:
            confidence += 0.15
        elif abs(avg_score) > 0.15:
            confidence += 0.1
        
        # Recent news = higher confidence
        recency_score = scores.get("recency", 0.5)
        confidence += (recency_score - 0.5) * 0.3
        
        return self._clamp_score(confidence)
    
    def _get_top_news(self, articles: List[Dict], top_n: int = 3) -> List[Dict]:
        """Get top N news articles by impact"""
        # Sort by sentiment score (most extreme first)
        sorted_articles = sorted(
            articles,
            key=lambda a: abs(a.get('sentiment', {}).get('score', 0)),
            reverse=True
        )
        
        top_news = []
        for article in sorted_articles[:top_n]:
            top_news.append({
                "title": article.get('title', '')[:100] or article.get('text', '')[:100],
                "source": article.get('source', article.get('channel', 'unknown')),
                "sentiment": article.get('sentiment', {}).get('sentiment', 'neutral'),
                "score": article.get('sentiment', {}).get('score', 0),
                "impact": article.get('sentiment', {}).get('impact', 'medium')
            })
        
        return top_news
    
    def _generate_reasoning(self, scores: Dict, articles: List[Dict]) -> str:
        """Generate human-readable reasoning"""
        parts = []
        
        sentiment = scores.get("sentiment", {})
        total = sum([
            sentiment.get("positive", 0),
            sentiment.get("negative", 0),
            sentiment.get("neutral", 0)
        ])
        
        if total > 0:
            positive_pct = (sentiment.get("positive", 0) / total) * 100
            negative_pct = (sentiment.get("negative", 0) / total) * 100
            
            if negative_pct > 50:
                parts.append(f"Mostly negative news ({negative_pct:.0f}%)")
            elif positive_pct > 50:
                parts.append(f"Mostly positive news ({positive_pct:.0f}%)")
            else:
                parts.append(f"Mixed news sentiment")
        
        # Mention top news
        top = self._get_top_news(articles, 1)
        if top:
            parts.append(f"Top: {top[0]['title'][:60]}")
        
        # Article count
        parts.append(f"{len(articles)} articles analyzed")
        
        return "; ".join(parts)
    
    def _create_neutral_result(self, symbol: str, reason: str) -> AgentResult:
        """Create a neutral result when analysis cannot be performed"""
        return AgentResult(
            agent_name=self.name,
            symbol=symbol,
            timestamp=datetime.now(),
            direction=SignalDirection.NEUTRAL,
            sub_score=0.5,
            confidence=0.3,
            analysis={"error": reason},
            reasoning=reason,
            metadata={"error": True}
        )
    
    async def close(self):
        """Clean up resources"""
        await self.telegram_scraper.close()
        await self.rss_fetcher.close()
