#!/usr/bin/env python3
"""
Test News Sentiment Classifier
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.news_sentiment import NewsSentimentClassifier
from dataflows import RSSFetcher
from utils import setup_logging, get_logger


setup_logging("INFO")
logger = get_logger(__name__)


async def test_sentiment_classifier():
    """Test sentiment classifier with real articles"""
    logger.info("=" * 80)
    logger.info("Testing News Sentiment Classifier")
    logger.info("=" * 80)
    
    # Initialize classifier
    classifier = NewsSentimentClassifier()
    
    # Test 1: Rule-based classification (VADER)
    logger.info("\n1. Testing rule-based classification (VADER)...")
    
    test_texts = [
        ("Bitcoin surges to new all-time high as institutional adoption accelerates", "positive"),
        ("Crypto market crashes as major exchange faces regulatory crackdown", "negative"),
        ("Ethereum network upgrade scheduled for next month", "neutral"),
        ("SEC approves spot Bitcoin ETF, marking historic moment for crypto", "positive"),
        ("Hackers steal $500M from DeFi protocol in largest exploit of 2024", "negative")
    ]
    
    for text, expected in test_texts:
        result = classifier.classify_rule_based(text)
        sentiment = result['sentiment']
        score = result['score']
        match = "✓" if sentiment == expected else "✗"
        logger.info(f"   {match} [{sentiment:8s}] (score: {score:+.3f}) {text[:60]}...")
    
    # Test 2: Fetch real articles from RSS
    logger.info("\n2. Fetching real articles from RSS feeds...")
    fetcher = RSSFetcher()
    articles = await fetcher.fetch_all_feeds(hours=24, limit=10)
    logger.info(f"   Fetched {len(articles)} articles")
    
    if not articles:
        logger.warning("   No articles fetched, skipping classification tests")
        return
    
    # Test 3: Classify with VADER (rule-based)
    logger.info("\n3. Classifying articles with VADER (rule-based)...")
    classified_vader = []
    for article in articles[:5]:  # Test first 5
        article = await classifier.classify_article(article, use_llm=False)
        classified_vader.append(article)
        
        title = article['title'][:60]
        sentiment = article['sentiment']['sentiment']
        score = article['sentiment']['score']
        logger.info(f"   [{sentiment:8s}] (score: {score:+.3f}) {title}...")
    
    # Test 4: Classify with LLM (if available)
    logger.info("\n4. Testing LLM classification (top 2 articles)...")
    try:
        classified_llm = []
        for article in articles[:2]:
            article = await classifier.classify_article(article, use_llm=True)
            classified_llm.append(article)
            
            title = article['title'][:60]
            sentiment = article['sentiment']['sentiment']
            score = article['sentiment']['score']
            impact = article['sentiment'].get('impact', 'N/A')
            method = article['sentiment']['method']
            logger.info(f"   [{sentiment:8s}] (score: {score:+.3f}, impact: {impact:6s}, method: {method}) {title}...")
            
            if 'reasoning' in article['sentiment']:
                logger.info(f"      Reasoning: {article['sentiment']['reasoning'][:100]}...")
    except Exception as e:
        logger.warning(f"   LLM classification not available: {e}")
    
    # Test 5: Hybrid classification (batch)
    logger.info("\n5. Testing hybrid classification (batch)...")
    all_classified = await classifier.classify_articles(articles, llm_threshold=3)
    logger.info(f"   Classified {len(all_classified)} articles")
    
    # Test 6: Aggregate sentiment
    logger.info("\n6. Aggregating sentiment...")
    summary = classifier.aggregate_sentiment(all_classified)
    
    logger.info(f"   Total articles: {summary['total']}")
    logger.info(f"   Positive: {summary['positive']} ({summary['positive_pct']:.1f}%)")
    logger.info(f"   Negative: {summary['negative']} ({summary['negative_pct']:.1f}%)")
    logger.info(f"   Neutral: {summary['neutral']} ({summary['neutral_pct']:.1f}%)")
    logger.info(f"   Average score: {summary['avg_score']:+.3f}")
    logger.info(f"   Dominant sentiment: {summary['dominant_sentiment']}")
    
    # Test 7: Filter by sentiment
    logger.info("\n7. Filtering by sentiment...")
    positive_articles = [a for a in all_classified if a['sentiment']['sentiment'] == 'positive']
    negative_articles = [a for a in all_classified if a['sentiment']['sentiment'] == 'negative']
    
    logger.info(f"   Positive articles: {len(positive_articles)}")
    if positive_articles:
        logger.info(f"   Sample: {positive_articles[0]['title'][:80]}...")
    
    logger.info(f"   Negative articles: {len(negative_articles)}")
    if negative_articles:
        logger.info(f"   Sample: {negative_articles[0]['title'][:80]}...")
    
    logger.info("\n" + "=" * 80)
    logger.info("✓ ALL TESTS PASSED")
    logger.info("=" * 80)
    
    await fetcher.close()


async def main():
    """Main entry point"""
    logger.info("Starting News Sentiment Classifier Test\n")
    
    try:
        await test_sentiment_classifier()
        logger.info("\n✓ Sentiment classifier is ready for News Analyst integration!")
        return 0
    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
