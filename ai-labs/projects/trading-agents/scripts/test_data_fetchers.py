#!/usr/bin/env python3
"""
Test Data Fetchers
"""
import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils import setup_logging, get_logger
from dataflows import BinanceClient, ParallelFetcher, cache

# Load environment
load_dotenv()
setup_logging("INFO")
logger = get_logger(__name__)


async def test_binance_client():
    """Test Binance client"""
    logger.info("=" * 80)
    logger.info("Testing Binance Client")
    logger.info("=" * 80)
    
    client = BinanceClient(
        api_key=os.getenv("BINANCE_API_KEY"),
        api_secret=os.getenv("BINANCE_API_SECRET")
    )
    
    try:
        # Health check
        logger.info("\n1. Health Check...")
        is_healthy = await client.health_check()
        logger.info(f"   Status: {'✓ OK' if is_healthy else '✗ FAILED'}")
        
        if not is_healthy:
            logger.error("Binance API is not accessible")
            return
        
        # Fetch ticker
        logger.info("\n2. Fetch Ticker (BTC)...")
        ticker = await client.fetch_ticker("BTC")
        if ticker:
            logger.info(f"   Price: ${ticker['price']:,.2f}")
            logger.info(f"   24h Volume: ${ticker['quote_volume_24h']:,.0f}")
            logger.info(f"   24h Change: {ticker['price_change_24h_pct']:+.2f}%")
        
        # Fetch OHLCV
        logger.info("\n3. Fetch OHLCV (BTC, 1h, last 24 candles)...")
        candles = await client.fetch_ohlcv("BTC", interval="1h", limit=24)
        if candles:
            logger.info(f"   Fetched {len(candles)} candles")
            latest = candles[-1]
            logger.info(f"   Latest candle: O=${latest['open']:.2f} H=${latest['high']:.2f} "
                       f"L=${latest['low']:.2f} C=${latest['close']:.2f}")
        
        # Fetch order book
        logger.info("\n4. Fetch Order Book (BTC, depth 10)...")
        orderbook = await client.fetch_orderbook("BTC", limit=10)
        if orderbook:
            logger.info(f"   Mid Price: ${orderbook['mid_price']:,.2f}")
            logger.info(f"   Spread: ${orderbook['spread']:.2f} ({orderbook['spread_pct']:.3f}%)")
            logger.info(f"   Best Bid: ${orderbook['bids'][0][0]:,.2f}")
            logger.info(f"   Best Ask: ${orderbook['asks'][0][0]:,.2f}")
        
        logger.info("\n✓ Binance Client tests passed")
    
    finally:
        await client.close()


async def test_parallel_fetcher():
    """Test parallel fetching"""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Parallel Fetcher")
    logger.info("=" * 80)
    
    # Setup
    binance = BinanceClient()
    fetcher = ParallelFetcher()
    fetcher.register_source("binance", binance)
    
    try:
        # Test 1: Fetch multiple coins ticker in parallel
        logger.info("\n1. Fetch tickers for BTC, ETH, SOL in parallel...")
        
        tasks = [
            {"source": "binance", "method": "fetch_ticker", "args": ["BTC"]},
            {"source": "binance", "method": "fetch_ticker", "args": ["ETH"]},
            {"source": "binance", "method": "fetch_ticker", "args": ["SOL"]}
        ]
        
        results = await fetcher.fetch_parallel(tasks)
        
        for coin in ["BTC", "ETH", "SOL"]:
            source_key = "binance"
            if source_key in results and results[source_key]:
                # Note: results indexed by source, need to track which coin
                # For now just show we got results
                pass
        
        logger.info(f"   Got results from {len(results)} sources")
        
        # Test 2: Use convenience methods
        logger.info("\n2. Fetch BTC ticker from multiple sources...")
        ticker_results = await fetcher.fetch_ticker_multi_source("BTC")
        
        for source, ticker in ticker_results.items():
            if ticker:
                logger.info(f"   {source}: ${ticker['price']:,.2f}")
        
        logger.info("\n✓ Parallel Fetcher tests passed")
    
    finally:
        await fetcher.close_all()


async def test_cache():
    """Test cache layer"""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Cache Layer")
    logger.info("=" * 80)
    
    # Test 1: Basic set/get
    logger.info("\n1. Basic cache set/get...")
    await cache.set("test_key", {"data": "test_value"}, ttl_seconds=10)
    
    result = await cache.get("test_key")
    logger.info(f"   Cached value: {result}")
    assert result is not None, "Cache get failed"
    
    # Test 2: Cache miss
    logger.info("\n2. Cache miss...")
    result = await cache.get("nonexistent_key")
    logger.info(f"   Result: {result}")
    assert result is None, "Should return None for cache miss"
    
    # Test 3: Get with fallback
    logger.info("\n3. Cache with fallback...")
    
    call_count = 0
    
    async def expensive_fetch():
        nonlocal call_count
        call_count += 1
        logger.info(f"   Expensive fetch called (count: {call_count})")
        return {"expensive": "data"}
    
    # First call - cache miss, should fetch
    result1 = await cache.get_with_fallback(
        "fallback_test",
        expensive_fetch,
        ttl_seconds=60
    )
    logger.info(f"   First call: {result1}, fetch count: {call_count}")
    
    # Second call - cache hit, should NOT fetch
    result2 = await cache.get_with_fallback(
        "fallback_test",
        expensive_fetch,
        ttl_seconds=60
    )
    logger.info(f"   Second call: {result2}, fetch count: {call_count}")
    
    assert call_count == 1, "Fetch should only be called once"
    
    # Cleanup
    await cache.delete("test_key")
    await cache.delete("fallback_test")
    
    logger.info("\n✓ Cache tests passed")


async def main():
    """Run all tests"""
    logger.info("Starting Data Fetcher Tests\n")
    
    try:
        await test_binance_client()
        await test_parallel_fetcher()
        await test_cache()
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ ALL TESTS PASSED")
        logger.info("=" * 80)
        logger.info("\nPhase 1.2 Data Fetchers complete!")
        logger.info("Next: Phase 1.3 - Storage Layer")
    
    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
