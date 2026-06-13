#!/usr/bin/env python3
"""Standalone DerivativesAnalyst smoke test."""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from agents.derivatives_analyst import DerivativesAnalyst
from dataflows import data_manager
from utils import setup_logging


setup_logging("INFO")


async def main():
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    analyst = DerivativesAnalyst()
    await data_manager.initialize()
    await analyst.initialize()

    try:
        for symbol in symbols:
            ohlcv = await data_manager.get_ohlcv(symbol, "1h", limit=50)
            result = await analyst.analyze(symbol, {"ohlcv": ohlcv})
            sources = result.metadata.get("sources", [])
            print(
                f"{symbol}: {result.direction.value} "
                f"S:{result.sub_score:.3f} C:{result.confidence:.3f} "
                f"sources:{','.join(sources) or 'none'} | {result.reasoning}"
            )
    finally:
        await analyst.close()
        await data_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
