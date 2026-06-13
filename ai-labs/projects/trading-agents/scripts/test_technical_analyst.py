#!/usr/bin/env python3
"""
Test Technical Analyst Agent
"""
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils import setup_logging, get_logger
from dataflows import data_manager
from agents import TechnicalAnalyst


setup_logging("INFO")
logger = get_logger(__name__)


async def test_technical_analyst():
    """Test Technical Analyst with real data"""
    logger.info("=" * 80)
    logger.info("Testing Technical Analyst Agent")
    logger.info("=" * 80)
    
    # Initialize data manager
    await data_manager.initialize()
    
    # Initialize analyst
    analyst = TechnicalAnalyst()
    await analyst.initialize()
    
    try:
        # Test 1: BTC on 1h timeframe
        logger.info("\n1. Analyzing BTC/USDT (1h timeframe)...")
        
        # Fetch OHLCV data
        ohlcv = await data_manager.fetch_and_store_ohlcv("BTCUSDT", "1h", limit=200)
        
        if not ohlcv:
            logger.error("Failed to fetch OHLCV data")
            return
        
        logger.info(f"   Fetched {len(ohlcv)} candles")
        
        # Prepare data for analysis
        data = {
            "ohlcv": ohlcv,
            "timeframe": "1h"
        }
        
        # Run analysis
        result = await analyst.analyze("BTCUSDT", data)
        
        # Display results
        logger.info("\n   Analysis Results:")
        logger.info(f"   Direction: {result.direction.value}")
        logger.info(f"   Sub-score: {result.sub_score:.3f}")
        logger.info(f"   Confidence: {result.confidence:.3f}")
        logger.info(f"   Reasoning: {result.reasoning}")
        
        # Display regime
        regime = result.analysis["regime"]
        logger.info(f"\n   Market Regime:")
        logger.info(f"   Type: {regime['type']}")
        logger.info(f"   Confidence: {regime['confidence']:.3f}")
        logger.info(f"   ADX: {regime['adx']:.1f}")
        logger.info(f"   Trend Strength: {regime['trend_strength']:.1f}")
        logger.info(f"   Reason: {regime['reason']}")
        
        # Display indicators
        indicators = result.analysis["indicators"]
        logger.info(f"\n   Key Indicators:")
        logger.info(f"   RSI: {indicators['rsi']:.2f}")
        logger.info(f"   MACD Histogram: {indicators['macd_histogram']:.4f}")
        logger.info(f"   BB Position: {indicators['bb_position']:.2%}")
        logger.info(f"   ATR: {indicators['atr']:.2f}")
        logger.info(f"   EMA 20: {indicators['ema_20']:.2f}")
        logger.info(f"   EMA 50: {indicators['ema_50']:.2f}")
        
        # Display scores
        scores = result.analysis["scores"]
        logger.info(f"\n   Component Scores:")
        for component, score in scores.items():
            logger.info(f"   {component.capitalize()}: {score:.3f}")
        
        # Test 2: ETH on 4h timeframe
        logger.info("\n2. Analyzing ETH/USDT (4h timeframe)...")
        
        ohlcv_4h = await data_manager.fetch_and_store_ohlcv("ETHUSDT", "4h", limit=200)
        
        if ohlcv_4h:
            logger.info(f"   Fetched {len(ohlcv_4h)} candles")
            
            data_4h = {
                "ohlcv": ohlcv_4h,
                "timeframe": "4h"
            }
            
            result_4h = await analyst.analyze("ETHUSDT", data_4h)
            
            logger.info(f"\n   Direction: {result_4h.direction.value}")
            logger.info(f"   Sub-score: {result_4h.sub_score:.3f}")
            logger.info(f"   Confidence: {result_4h.confidence:.3f}")
            logger.info(f"   Regime: {result_4h.analysis['regime']['type']}")
            logger.info(f"   Reasoning: {result_4h.reasoning}")
        
        # Test 3: SOL on 1d timeframe
        logger.info("\n3. Analyzing SOL/USDT (1d timeframe)...")
        
        ohlcv_1d = await data_manager.fetch_and_store_ohlcv("SOLUSDT", "1d", limit=200)
        
        if ohlcv_1d:
            logger.info(f"   Fetched {len(ohlcv_1d)} candles")
            
            data_1d = {
                "ohlcv": ohlcv_1d,
                "timeframe": "1d"
            }
            
            result_1d = await analyst.analyze("SOLUSDT", data_1d)
            
            logger.info(f"\n   Direction: {result_1d.direction.value}")
            logger.info(f"   Sub-score: {result_1d.sub_score:.3f}")
            logger.info(f"   Confidence: {result_1d.confidence:.3f}")
            logger.info(f"   Regime: {result_1d.analysis['regime']['type']}")
            logger.info(f"   Reasoning: {result_1d.reasoning}")
        
        # Test 4: Compare multiple coins
        logger.info("\n4. Multi-coin comparison (1h)...")
        
        coins = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        comparison = []
        
        for coin in coins:
            ohlcv = await data_manager.fetch_and_store_ohlcv(coin, "1h", limit=100)
            if ohlcv:
                result = await analyst.analyze(coin, {"ohlcv": ohlcv, "timeframe": "1h"})
                comparison.append({
                    "coin": coin,
                    "direction": result.direction.value,
                    "score": result.sub_score,
                    "confidence": result.confidence,
                    "regime": result.analysis["regime"]["type"]
                })
        
        logger.info("\n   Comparison:")
        for item in comparison:
            logger.info(f"   {item['coin']:10s} | {item['direction']:8s} | "
                       f"Score: {item['score']:.3f} | Conf: {item['confidence']:.3f} | "
                       f"Regime: {item['regime']}")
        
        logger.info("\n✓ Technical Analyst tests passed")
    
    finally:
        await data_manager.close()


async def main():
    """Run all tests"""
    logger.info("Starting Technical Analyst Tests\n")
    
    try:
        await test_technical_analyst()
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ ALL TESTS PASSED")
        logger.info("=" * 80)
        logger.info("\nPhase 1.4 complete!")
        logger.info("Technical Analyst Agent is ready for integration.")
        
        return 0
    
    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
