#!/usr/bin/env python3
"""
Test script for Telegram Channels Scraper
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from dataflows import TelegramScraper
from utils import setup_logging, get_logger


setup_logging("INFO")
logger = get_logger(__name__)


async def test_telegram_scraper():
    """Test Telegram scraper functionality"""
    logger.info("=" * 80)
    logger.info("Testing Telegram Channels Scraper")
    logger.info("=" * 80)
    
    scraper = TelegramScraper()
    
    try:
        # Initialize (will prompt for code if first time)
        logger.info("\n1. Initializing Telegram client...")
        await scraper.initialize()
        logger.info("✓ Telegram client initialized")
        
        # Health check
        logger.info("\n2. Running health check...")
        is_healthy = await scraper.health_check()
        logger.info(f"   Health status: {'✓ OK' if is_healthy else '✗ FAILED'}")
        
        if not is_healthy:
            logger.error("Telegram client is not healthy")
            return False
        
        # Test fetching from single channel
        logger.info("\n3. Testing single channel fetch (@cointelegraph)...")
        messages = await scraper.fetch_messages('cointelegraph', hours=24, limit=10)
        logger.info(f"   Fetched {len(messages)} messages")
        
        if messages:
            logger.info("\n   Sample messages:")
            for i, msg in enumerate(messages[:3], 1):
                text_preview = msg['text'][:100].replace('\n', ' ')
                logger.info(f"   {i}. [{msg['date'][:16]}] {text_preview}...")
                logger.info(f"      Views: {msg['views']}, Forwards: {msg['forwards']}")
        
        # Test fetching from all channels
        logger.info("\n4. Testing all channels fetch (last 24h)...")
        all_messages = await scraper.fetch_all_channels(hours=24, limit=20)
        logger.info(f"   Total messages: {len(all_messages)}")
        
        if all_messages:
            # Show breakdown by channel
            channel_counts = {}
            for msg in all_messages:
                channel = msg['channel']
                channel_counts[channel] = channel_counts.get(channel, 0) + 1
            
            logger.info("\n   Messages by channel:")
            for channel, count in sorted(channel_counts.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"   @{channel}: {count} messages")
        
        # Test keyword filtering
        logger.info("\n5. Testing keyword filtering (BTC, ETH, SOL)...")
        filtered = scraper.filter_by_keywords(all_messages, ['BTC', 'ETH', 'SOL', 'Bitcoin', 'Ethereum', 'Solana'])
        logger.info(f"   Filtered messages: {len(filtered)}")
        
        if filtered:
            logger.info("\n   Sample filtered messages:")
            for i, msg in enumerate(filtered[:3], 1):
                text_preview = msg['text'][:100].replace('\n', ' ')
                keywords = ', '.join(msg.get('matched_keywords', []))
                logger.info(f"   {i}. [{msg['channel']}] {text_preview}...")
                logger.info(f"      Keywords: {keywords}")
        
        # Test duplicate removal
        logger.info("\n6. Testing duplicate removal...")
        unique_messages = scraper.remove_duplicates(all_messages, similarity_threshold=0.8)
        logger.info(f"   Unique messages: {len(unique_messages)} (removed {len(all_messages) - len(unique_messages)} duplicates)")
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ ALL TESTS PASSED")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}", exc_info=True)
        return False
    
    finally:
        await scraper.close()


async def main():
    """Main entry point"""
    logger.info("Starting Telegram Scraper Test\n")
    
    success = await test_telegram_scraper()
    
    if success:
        logger.info("\n✓ Telegram scraper is ready for News Analyst integration!")
        return 0
    else:
        logger.error("\n✗ Telegram scraper test failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
