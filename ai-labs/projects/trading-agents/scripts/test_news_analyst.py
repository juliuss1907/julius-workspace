#!/usr/bin/env python3
"""Test News Analyst Agent"""
import asyncio, sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from dotenv import load_dotenv; load_dotenv()
from utils import setup_logging, get_logger
from agents import NewsAnalyst; setup_logging("INFO"); logger = get_logger(__name__)

async def test():
    logger.info("=" * 60)
    logger.info("Testing NewsAnalyst Agent")
    logger.info("=" * 60)
    analyst = NewsAnalyst()
    await analyst.initialize()

    for coin in ['BTC', 'ETH', 'SOL']:
        symbol = f"{coin}USDT"
        logger.info(f"\n--- {symbol} ---")
        result = await analyst.analyze(symbol, {"coin": coin, "hours": 24})
        logger.info(f"  Direction: {result.direction.value}")
        logger.info(f"  Score: {result.sub_score:.3f} | Confidence: {result.confidence:.3f}")
        logger.info(f"  Reasoning: {result.reasoning}")
        sources = result.analysis.get("sources", {})
        logger.info(f"  Sources: TG={sources.get('telegram',0)}, RSS={sources.get('rss',0)}")
        for n in result.analysis.get("top_news", [])[:2]:
            logger.info(f"  📰 [{n['sentiment']}] {n['title'][:70]}")

    await analyst.close()
    logger.info("\n✓ NewsAnalyst tests passed")

asyncio.run(test())
