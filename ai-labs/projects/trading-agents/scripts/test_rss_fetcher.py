#!/usr/bin/env python3
"""
Test RSS Fetcher
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dataflows import RSSFetcher
from utils import setup_logging, get_logger


setup_logging("INFO")
logger = get_logger(__name__)


async def test_rss_fetcher():
    """Test RSS fetcher functionality"""
    logger.info("=" * 80)
    logger.info("Testing RSS Fetcher")
    logger.info("=" * 80)
    
    fetcher = RSSFetcher()
    
    try:
        # Test 1: Health check
        logger.info("\n1. Running health check...")
        is_healthy = await fetcher.health_check()
        logger.info(f"   Health status: {'✓ OK' if is_healthy else '✗ FAILED'}")
        
        if not is_healthy:
            logger.error("RSS feeds are not accessible")
            return False
        
        # Test 2: Fetch from CoinDesk
        logger.info("\n2. Testing single feed fetch (CoinDesk)...")
        articles = await fetcher.fetch_feed('coindesk', limit=10, hours=24)
        logger.info(f"   Fetched {len(articles)} articles")
        
        if articles:
            logger.info("\n   Sample articles:")
            for i, article in enumerate(articles[:3], 1):
                title = article['title'][:80]
                published = article['published'][:16] if article['published'] else 'N/A'
                logger.info(f"   {i}. [{published}] {title}...")
                logger.info(f"      Link: {article['link']}")
        
        # Test 3: Fetch from CoinTelegraph
        logger.info("\n3. Testing CoinTelegraph feed...")
        articles = await fetcher.fetch_feed('cointelegraph', limit=10, hours=24)
        logger.info(f"   Fetched {len(articles)} articles")
        
        if articles:
            logger.info("\n   Sample articles:")
            for i, article in enumerate(articles[:3], 1):
                title = article['title'][:80]
                published = article['published'][:16] if article['published'] else 'N/A'
                logger.info(f"   {i}. [{published}] {title}...")
        
        # Test 4: Fetch from The Feed JSON source
        logger.info("\n4. Testing The Feed source...")
        articles = await fetcher.fetch_thefeed(limit=10, hours=24)
        logger.info(f"   Fetched {len(articles)} articles")

        if articles:
            logger.info("\n   Sample articles:")
            for i, article in enumerate(articles[:3], 1):
                title = article['title'][:80]
                published = article['published'][:16] if article['published'] else 'N/A'
                logger.info(f"   {i}. [{published}] {title}...")

        # Test 5: Fetch from all feeds
        logger.info("\n5. Testing all feeds fetch (last 24h)...")
        all_articles = await fetcher.fetch_all_feeds(hours=24, limit=20)
        logger.info(f"   Total articles: {len(all_articles)}")
        
        if all_articles:
            # Show breakdown by source
            source_counts = {}
            for article in all_articles:
                source = article['source']
                source_counts[source] = source_counts.get(source, 0) + 1
            
            logger.info("\n   Articles by source:")
            for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"   {source}: {count} articles")
        
        # Test 6: Keyword filtering
        logger.info("\n6. Testing keyword filtering (BTC, ETH, SOL)...")
        filtered = fetcher.filter_by_keywords(all_articles, ['BTC', 'ETH', 'SOL', 'Bitcoin', 'Ethereum', 'Solana'])
        logger.info(f"   Filtered articles: {len(filtered)}")
        
        if filtered:
            logger.info("\n   Sample filtered articles:")
            for i, article in enumerate(filtered[:3], 1):
                title = article['title'][:80]
                keywords = ', '.join(article.get('matched_keywords', []))
                logger.info(f"   {i}. [{article['source']}] {title}...")
                logger.info(f"      Keywords: {keywords}")
        
        # Test 7: Duplicate removal
        logger.info("\n7. Testing duplicate removal...")
        unique_articles = fetcher.remove_duplicates(all_articles, similarity_threshold=0.8)
        logger.info(f"   Unique articles: {len(unique_articles)} (removed {len(all_articles) - len(unique_articles)} duplicates)")
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ ALL TESTS PASSED")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}", exc_info=True)
        return False
    
    finally:
        await fetcher.close()


async def main():
    """Main entry point"""
    logger.info("Starting RSS Fetcher Test\n")
    
    success = await test_rss_fetcher()
    
    if success:
        logger.info("\n✓ RSS fetcher is ready for News Analyst integration!")
        return 0
    else:
        logger.error("\n✗ RSS fetcher test failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
