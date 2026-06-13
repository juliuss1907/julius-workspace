"""
News Sentiment Classification
Hybrid approach: VADER (rule-based) + LLM (accurate)
"""
from typing import List, Dict, Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from utils import get_logger


logger = get_logger(__name__)


class NewsSentimentClassifier:
    """Hybrid sentiment classifier for news articles"""
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.llm_client = None  # Will be initialized when needed
    
    def classify_rule_based(self, text: str) -> Dict:
        """
        Classify sentiment using VADER (rule-based)
        
        Args:
            text: Article text or summary
        
        Returns:
            Dict with sentiment, score, and breakdown
        """
        scores = self.vader.polarity_scores(text)
        
        # VADER returns: neg, neu, pos, compound
        # compound: -1 (most negative) to +1 (most positive)
        compound = scores['compound']
        
        # Classify based on compound score
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': compound,
            'breakdown': {
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu']
            },
            'method': 'vader'
        }
    
    def _get_llm_client(self):
        """Get LLM client (lazy init with graceful fallback)"""
        if self.llm_client is not None:
            return self.llm_client
        
        try:
            from llm_clients.openai_client import OpenAIClient
            self.llm_client = OpenAIClient()
        except Exception as e1:
            logger.debug(f"OpenAIClient not available: {e1}")
            try:
                import os
                from openai import AsyncOpenAI
                key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENCODE_GO_API_KEY', '')
                base = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
                if not key:
                    raise ValueError("No API key configured")
                client = AsyncOpenAI(api_key=key, base_url=base)
                self.llm_client = client
            except Exception as e2:
                logger.warning(f"No LLM client available ({e2}), using VADER only")
                self.llm_client = None
        
        return self.llm_client
    
    async def classify_with_llm(self, text: str) -> Dict:
        """
        Classify sentiment using LLM (accurate but slower)
        
        Args:
            text: Article text or summary
        
        Returns:
            Dict with sentiment, score, impact, and reasoning
        """
        client = self._get_llm_client()
        if client is None:
            return self.classify_rule_based(text)
        
        prompt = f"""Analyze the sentiment of this crypto news article and provide:
1. Sentiment: positive, negative, or neutral
2. Score: -1.0 to 1.0 (negative to positive)
3. Impact: high, medium, or low (how much this could affect crypto markets)
4. Reasoning: brief explanation (1-2 sentences)

Article:
{text}

Respond ONLY in JSON format, no other text:
{{
    "sentiment": "positive|negative|neutral",
    "score": 0.0,
    "impact": "high|medium|low",
    "reasoning": "..."
}}"""
        
        try:
            # Try different client interfaces
            if hasattr(client, 'generate'):
                response = await client.generate(prompt)
            elif hasattr(client, 'chat'):
                response = await client.chat(prompt)
            else:
                completion = await client.chat.completions.create(
                    model=os.environ.get('LLM_MODEL', 'gpt-3.5-turbo'),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=200
                )
                response = completion.choices[0].message.content
            
            # Try to parse JSON from response
            import json
            import re
            
            # Find JSON in response
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                result = json.loads(json_match.group())
            else:
                return self.classify_rule_based(text)
            
            # Validate and normalize
            sentiment = result.get('sentiment', 'neutral').lower()
            if sentiment not in ['positive', 'negative', 'neutral']:
                sentiment = 'neutral'
            
            score = float(result.get('score', 0.0))
            score = max(-1.0, min(1.0, score))
            
            impact = result.get('impact', 'medium').lower()
            if impact not in ['high', 'medium', 'low']:
                impact = 'medium'
            
            reasoning = result.get('reasoning', 'No reasoning provided')
            
            return {
                'sentiment': sentiment,
                'score': score,
                'impact': impact,
                'reasoning': reasoning,
                'method': 'llm'
            }
            
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            return self.classify_rule_based(text)
    
    async def classify_article(
        self,
        article: Dict,
        use_llm: bool = False
    ) -> Dict:
        """
        Classify a single article
        
        Args:
            article: Article dict with title, summary, etc.
            use_llm: Whether to use LLM (slower but more accurate)
        
        Returns:
            Article dict with added sentiment analysis
        """
        # Combine title and summary for analysis
        text = f"{article.get('title', '')} {article.get('summary', '')}".strip()
        
        if not text:
            logger.warning("Empty article text, skipping sentiment analysis")
            article['sentiment'] = {
                'sentiment': 'neutral',
                'score': 0.0,
                'method': 'none'
            }
            return article
        
        # Classify
        if use_llm:
            sentiment_result = await self.classify_with_llm(text)
        else:
            sentiment_result = self.classify_rule_based(text)
        
        # Add to article
        article['sentiment'] = sentiment_result
        
        return article
    
    async def classify_articles(
        self,
        articles: List[Dict],
        llm_threshold: int = 10
    ) -> List[Dict]:
        """
        Classify multiple articles with hybrid approach
        
        Args:
            articles: List of article dicts
            llm_threshold: Use LLM for top N articles (by importance)
        
        Returns:
            List of articles with sentiment analysis added
        """
        logger.info(f"Classifying sentiment for {len(articles)} articles...")
        
        # Sort articles by importance (views/forwards for Telegram, recency for RSS)
        sorted_articles = self._sort_by_importance(articles)
        
        # Classify top N with LLM, rest with VADER
        classified = []
        
        for i, article in enumerate(sorted_articles):
            use_llm = (i < llm_threshold)
            
            if use_llm:
                logger.debug(f"Using LLM for article {i+1}/{len(sorted_articles)}: {article.get('title', '')[:50]}")
                article = await self.classify_article(article, use_llm=True)
            else:
                article = await self.classify_article(article, use_llm=False)
            
            classified.append(article)
        
        # Log summary
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for article in classified:
            sentiment = article.get('sentiment', {}).get('sentiment', 'neutral')
            sentiment_counts[sentiment] += 1
        
        logger.info(f"Sentiment breakdown: {sentiment_counts}")
        
        return classified
    
    def _sort_by_importance(self, articles: List[Dict]) -> List[Dict]:
        """
        Sort articles by importance
        
        For Telegram: views + forwards
        For RSS: recency (published date)
        
        Args:
            articles: List of article dicts
        
        Returns:
            Sorted list (most important first)
        """
        def importance_score(article):
            # Telegram articles have views/forwards
            if 'views' in article and 'forwards' in article:
                views = article.get('views', 0)
                forwards = article.get('forwards', 0)
                return views + (forwards * 10)  # Forwards weighted more
            
            # RSS articles: use published date (more recent = more important)
            elif 'published' in article and article['published']:
                from datetime import datetime
                try:
                    pub_date = datetime.fromisoformat(article['published'])
                    # Convert to timestamp (higher = more recent)
                    return pub_date.timestamp()
                except:
                    return 0
            
            # Default: no importance signal
            return 0
        
        return sorted(articles, key=importance_score, reverse=True)
    
    def aggregate_sentiment(self, articles: List[Dict]) -> Dict:
        """
        Aggregate sentiment from multiple articles
        
        Args:
            articles: List of articles with sentiment analysis
        
        Returns:
            Aggregated sentiment summary
        """
        if not articles:
            return {
                'total': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'avg_score': 0.0,
                'dominant_sentiment': 'neutral'
            }
        
        # Count sentiments
        counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        scores = []
        
        for article in articles:
            sentiment_data = article.get('sentiment', {})
            sentiment = sentiment_data.get('sentiment', 'neutral')
            score = sentiment_data.get('score', 0.0)
            
            counts[sentiment] += 1
            scores.append(score)
        
        # Calculate average score
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        # Determine dominant sentiment
        dominant = max(counts, key=counts.get)
        
        return {
            'total': len(articles),
            'positive': counts['positive'],
            'negative': counts['negative'],
            'neutral': counts['neutral'],
            'avg_score': avg_score,
            'dominant_sentiment': dominant,
            'positive_pct': (counts['positive'] / len(articles)) * 100,
            'negative_pct': (counts['negative'] / len(articles)) * 100,
            'neutral_pct': (counts['neutral'] / len(articles)) * 100
        }
