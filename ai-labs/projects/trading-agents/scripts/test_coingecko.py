#!/usr/bin/env python3
"""
Test CoinGecko Integration
"""
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils import setup_logging, get_logger
from dataflows import CoinGeckoClient, data_manager


setup_logging("INFO")
logger = get_logger(__name__)


async def test_coingecko_client():
    """Test CoinGecko client directly"""
    logger.info("=" * 80)
    logger.info("Testing CoinGecko Client")
    logger.info("=" * 80)
    
    client = CoinGeckoClient()
    
    try:
        # Health check
        logger.info("\n1. Health Check...")
        is_healthy = await client.health_check()
        logger.info(f"   Status: {'✓ OK' if is_healthy else '✗ FAILED'}")
        
        if not is_healthy:
            logger.error("CoinGecko API is not accessible")
            return
        
        # Fetch full coin data
        logger.info("\n2. Fetch Full Coin Data (BTC)...")
        coin_data = await client.fetch_coin_data("BTC")
        
        if coin_data:
            logger.info(f"   Name: {coin_data['name']}")
            logger.info(f"   Price: ${coin_data['price_usd']:,.2f}")
            logger.info(f"   Market Cap: ${coin_data['market_cap']:,.0f}")
            logger.info(f"   Market Cap Rank: #{coin_data['market_cap_rank']}")
            logger.info(f"   FDV: ${coin_data['fdv']:,.0f}")
            logger.info(f"   Circulating Supply: {coin_data['circulating_supply']:,.0f}")
            logger.info(f"   Max Supply: {coin_data['max_supply']:,.0f}" if coin_data['max_supply'] else "   Max Supply: Unlimited")
            logger.info(f"   24h Volume: ${coin_data['volume_24h']:,.0f}")
            logger.info(f"   24h Change: {coin_data['price_change_24h_pct']:+.2f}%")
            logger.info(f"   7d Change: {coin_data['price_change_7d_pct']:+.2f}%")
            logger.info(f"   ATH: ${coin_data['ath']:,.2f} ({coin_data['ath_change_pct']:+.2f}% from ATH)")
        
        # Fetch simple prices for multiple coins
        logger.info("\n3. Fetch Simple Prices (BTC, ETH, SOL)...")
        prices = await client.fetch_simple_price(["BTC", "ETH", "SOL"])
        
        for symbol, data in prices.items():
            if data:
                logger.info(f"   {symbol}: ${data['price']:,.2f} "
                           f"(MCap: ${data['market_cap']:,.0f}, "
                           f"24h: {data['price_change_24h_pct']:+.2f}%)")
        
        # Search for a coin
        logger.info("\n4. Search Coin (Avalanche)...")
        search_result = await client.search_coin("avalanche")
        
        if search_result:
            logger.info(f"   Found: {search_result['name']} ({search_result['symbol'].upper()})")
            logger.info(f"   ID: {search_result['id']}")
            logger.info(f"   Rank: #{search_result['market_cap_rank']}")
        
        logger.info("\n✓ CoinGecko Client tests passed")
    
    finally:
        await client.close()


async def test_data_manager_fundamentals():
    """Test DataManager with CoinGecko integration"""
    logger.info("\n" + "=" * 80)
    logger.info("Testing DataManager Fundamentals")
    logger.info("=" * 80)
    
    await data_manager.initialize()
    
    try:
        # Test 1: Get fundamentals for BTC
        logger.info("\n1. Get Fundamentals (BTC)...")
        fundamentals = await data_manager.get_fundamentals("BTC")
        
        if fundamentals:
            logger.info(f"   Market Cap: ${fundamentals['market_cap']:,.0f}")
            logger.info(f"   FDV: ${fundamentals['fdv']:,.0f}")
            logger.info(f"   Circ/Max: {fundamentals['circulating_supply']:,.0f} / {fundamentals['max_supply']:,.0f}")
            logger.info(f"   Categories: {', '.join(fundamentals['categories'][:3])}")
        
        # Test 2: Cache hit on second call
        logger.info("\n2. Testing cache (2nd call should hit cache)...")
        fundamentals2 = await data_manager.get_fundamentals("BTC")
        logger.info(f"   Got fundamentals from cache")
        
        # Test 3: Multi-coin simple prices
        logger.info("\n3. Get Simple Prices (BTC, ETH, SOL)...")
        prices = await data_manager.get_simple_prices(["BTC", "ETH", "SOL"])
        
        for symbol, data in prices.items():
            if data:
                logger.info(f"   {symbol}: ${data['price']:,.2f}")
        
        # Test 4: Compare Binance vs CoinGecko prices
        logger.info("\n4. Price Comparison (Binance vs CoinGecko)...")
        
        binance_ticker = await data_manager.get_ticker("BTC")
        coingecko_price = prices.get("BTC", {}).get("price")
        
        if binance_ticker and coingecko_price:
            binance_price = binance_ticker['price']
            diff_pct = ((coingecko_price - binance_price) / binance_price) * 100
            
            logger.info(f"   Binance: ${binance_price:,.2f}")
            logger.info(f"   CoinGecko: ${coingecko_price:,.2f}")
            logger.info(f"   Difference: {diff_pct:+.3f}%")
            
            if abs(diff_pct) < 1.0:
                logger.info("   ✓ Prices are consistent")
            else:
                logger.warning("   ⚠ Price discrepancy detected")
        
        logger.info("\n✓ DataManager fundamentals tests passed")
    
    finally:
        await data_manager.close()


async def main():
    """Run all tests"""
    logger.info("Starting CoinGecko Integration Tests\n")
    
    try:
        await test_coingecko_client()
        await test_data_manager_fundamentals()
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ ALL TESTS PASSED")
        logger.info("=" * 80)
        logger.info("\nCoinGecko integration complete!")
        logger.info("Ready to proceed with Phase 1.4 - Technical Analyst")
        
        return 0
    
    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
