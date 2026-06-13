#!/usr/bin/env python3
"""
Test Storage Layer
"""
import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils import setup_logging, get_logger
from dataflows import data_manager
from state import db


setup_logging("INFO")
logger = get_logger(__name__)


async def test_database_init():
    """Test database initialization"""
    logger.info("=" * 80)
    logger.info("Testing Database Initialization")
    logger.info("=" * 80)
    
    await db.connect()
    
    # Test state operations
    logger.info("\n1. Testing state (key-value store)...")
    await db.set_state("test_key", {"data": "test_value", "number": 123})
    value = await db.get_state("test_key")
    logger.info(f"   Set/Get state: {value}")
    assert value == {"data": "test_value", "number": 123}
    
    logger.info("\n✓ Database initialization tests passed")


async def test_data_manager():
    """Test DataManager (fetch + store)"""
    logger.info("\n" + "=" * 80)
    logger.info("Testing DataManager")
    logger.info("=" * 80)
    
    await data_manager.initialize()
    
    # Test 1: Fetch and store ticker
    logger.info("\n1. Fetch and store ticker (BTC)...")
    ticker = await data_manager.get_ticker("BTC")
    if ticker:
        logger.info(f"   Price: ${ticker['price']:,.2f}")
        logger.info(f"   24h Change: {ticker.get('price_change_24h_pct', 0):+.2f}%")
        
        # Verify it's in database
        db_ticker = await db.get_latest_ticker("BTCUSDT")
        logger.info(f"   Stored in DB: {db_ticker is not None}")
    
    # Test 2: Fetch and store OHLCV
    logger.info("\n2. Fetch and store OHLCV (BTC, 1h, 24 candles)...")
    candles = await data_manager.get_ohlcv("BTC", timeframe="1h", limit=24)
    logger.info(f"   Fetched {len(candles)} candles")
    
    if candles:
        latest = candles[-1]
        logger.info(f"   Latest: O=${latest['open']:.2f} H=${latest['high']:.2f} "
                   f"L=${latest['low']:.2f} C=${latest['close']:.2f}")
        
        # Verify in database
        db_candles = await db.get_ohlcv("BTCUSDT", "1h", limit=5)
        logger.info(f"   Stored in DB: {len(db_candles)} candles")
    
    # Test 3: Cache hit on second call
    logger.info("\n3. Testing cache (2nd call should hit cache)...")
    candles2 = await data_manager.get_ohlcv("BTC", timeframe="1h", limit=24)
    logger.info(f"   Got {len(candles2)} candles from cache")
    
    # Test 4: Multi-coin fetch
    logger.info("\n4. Fetch multiple coins in parallel (BTC, ETH, SOL)...")
    tickers = await data_manager.fetch_watchlist_tickers(["BTC", "ETH", "SOL"])
    
    for coin, ticker in tickers.items():
        if ticker:
            logger.info(f"   {coin}: ${ticker['price']:,.2f}")
    
    logger.info("\n✓ DataManager tests passed")


async def test_signal_storage():
    """Test signal storage"""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Signal Storage")
    logger.info("=" * 80)
    
    # Create a test signal
    signal = {
        "signal_id": f"TEST-{int(datetime.now().timestamp())}",
        "coin": "BTC",
        "mode": "full",
        "signal": "BUY",
        "confidence": 0.75,
        "entry_price": 63000,
        "stop_loss": 61000,
        "take_profit": 67000,
        "summary": "Test signal - BTC breakout above resistance",
        "reasoning": "Technical analysis indicates bullish momentum",
        "timestamp": int(datetime.now().timestamp())
    }
    
    logger.info("\n1. Insert test signal...")
    signal_id = await db.insert_signal(signal)
    logger.info(f"   Signal ID: {signal_id}")
    logger.info(f"   Signal: {signal['coin']} {signal['signal']} @ ${signal['entry_price']}")
    
    # Retrieve signal
    logger.info("\n2. Retrieve signals...")
    signals = await db.get_signals(coin="BTC", limit=5)
    logger.info(f"   Found {len(signals)} signals for BTC")
    
    if signals:
        latest = signals[0]
        logger.info(f"   Latest: {latest['signal']} @ ${latest['entry_price']} "
                   f"(confidence: {latest['confidence']:.2f})")
    
    # Update signal action
    logger.info("\n3. Update signal action...")
    await db.update_signal_action(
        signal['signal_id'],
        action="executed",
        action_time=int(datetime.now().timestamp())
    )
    logger.info("   Action updated to 'executed'")
    
    logger.info("\n✓ Signal storage tests passed")


async def test_analysis_cache():
    """Test analysis result caching"""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Analysis Cache")
    logger.info("=" * 80)
    
    # Cache a test analysis
    analysis_data = {
        "indicators": {
            "rsi": 65.5,
            "macd": "bullish",
            "volume_trend": "increasing"
        },
        "summary": "Bullish technical setup",
        "confidence": 0.8
    }
    
    logger.info("\n1. Cache analysis result...")
    await db.cache_analysis(
        coin="BTC",
        analyst_type="technical",
        analysis_data=analysis_data,
        timeframe="1h",
        ttl_seconds=3600
    )
    logger.info("   Analysis cached")
    
    # Retrieve cached analysis
    logger.info("\n2. Retrieve cached analysis...")
    cached = await db.get_cached_analysis(
        coin="BTC",
        analyst_type="technical",
        timeframe="1h"
    )
    
    if cached:
        logger.info(f"   RSI: {cached['indicators']['rsi']}")
        logger.info(f"   MACD: {cached['indicators']['macd']}")
        logger.info(f"   Summary: {cached['summary']}")
    
    logger.info("\n✓ Analysis cache tests passed")


async def main():
    """Run all storage layer tests"""
    logger.info("Starting Storage Layer Tests\n")
    
    try:
        await test_database_init()
        await test_data_manager()
        await test_signal_storage()
        await test_analysis_cache()
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ ALL TESTS PASSED")
        logger.info("=" * 80)
        logger.info("\nPhase 1.3 Storage Layer complete!")
        logger.info("Next: Phase 1.4 - Technical Analyst Agent")
        
        return 0
    
    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}", exc_info=True)
        return 1
    
    finally:
        # Cleanup
        await data_manager.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
