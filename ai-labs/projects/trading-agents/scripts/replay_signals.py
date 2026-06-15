#!/usr/bin/env python3
"""
Signal Replay — replay the full analyst/trader/debate stack on historical OHLCV.

Phase 6A.1: signal-only replay — no PnL simulation, no live data feeds.
Produces logs/replay_signals.jsonl for analysis.
"""
import argparse
import asyncio
import sys
from datetime import datetime, date, time as dt_time, timedelta
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from utils import setup_logging, get_logger
from dataflows import BinanceClient
from dataflows.data_manager import DataManager
from state import db, SignalRecorder
from agents import TechnicalAnalyst, TraderAgent, ResearchDebate

setup_logging("INFO")
logger = get_logger(__name__)


class SignalReplay:
    """Slide historical candles through the agent stack and record signals."""

    def __init__(
        self,
        symbols: list,
        days: int = 30,
        window_size: int = 200,
        step_candles: int = 4,
        output_path: str = "logs/replay_signals.jsonl",
        config_override: dict = None,
        end_date: date = None,
    ):
        self.symbols = symbols
        self.days = days
        self.window_size = window_size
        self.step_candles = step_candles
        self.end_date = end_date
        self.config_override = config_override or {}
        self.recorder = SignalRecorder(log_path=Path(output_path))
        self.technical = TechnicalAnalyst()
        self.trader = TraderAgent(config_override=self.config_override)
        self.debate = ResearchDebate(config_override=self.config_override)

    async def initialize(self):
        await db.connect()
        await self.technical.initialize()
        await self.trader.initialize()
        await self.debate.initialize()

    async def close(self):
        await self.technical.close()
        await self.trader.close()
        await self.debate.close()
        await db.close()

    async def fetch_candles(self, symbol: str) -> list:
        bc = BinanceClient()
        try:
            if self.end_date:
                end_dt = datetime.combine(self.end_date, dt_time(23, 59, 59))
                start_dt = datetime.combine(
                    self.end_date, dt_time(0, 0, 0)
                ) - timedelta(days=self.days)
                candles = await bc.fetch_ohlcv(
                    symbol, "1h",
                    start_time=start_dt,
                    end_time=end_dt,
                    limit=self.days * 24 + 50,
                )
            else:
                candles = await bc.fetch_ohlcv(symbol, "1h", limit=self.days * 24 + 50)
        finally:
            await bc.close()
        logger.info(f"{symbol}: fetched {len(candles)} candles")
        return candles

    async def analyze_window(self, symbol: str, ohlcv: list, index: int, timestamp: str):
        window = ohlcv[max(0, index - self.window_size):index + 1]
        candle_ts = ohlcv[index]["timestamp"]
        candle_close = ohlcv[index]["close"]

        data = {"ohlcv": window, "timeframe": "1h"}

        technical_signal = None
        try:
            technical_signal = await self.technical.analyze(symbol, data)
        except Exception as e:
            logger.warning(f"{symbol} Technical failed at candle {candle_ts}: {e}")

        analyst_signals = {
            "technical": technical_signal,
            "news": None,
            "sentiment": None,
            "fundamentals": None,
            "derivatives": None,
        }

        draft_signal = await self.trader.analyze(symbol, {"mode": "full", "signals": analyst_signals})
        research_debate = await self.debate.debate(symbol, analyst_signals, draft_signal)
        final_signal = await self.trader.analyze(
            symbol, {"mode": "full", "signals": analyst_signals, "research_debate": research_debate}
        )

        trader_analysis = final_signal.analysis.get("trader", {})
        final_action = trader_analysis.get("action", "HOLD")
        final_dir = final_signal.direction.value
        final_conf = final_signal.confidence
        consensus = research_debate.get("consensus")

        tech_dir = technical_signal.direction.value if technical_signal else "FAIL"
        tech_s = technical_signal.sub_score if technical_signal else 0.0
        tech_c = technical_signal.confidence if technical_signal else 0.0

        logger.info(
            f"  [{timestamp}] {symbol} "
            f"Tech={tech_dir} S:{tech_s:.3f} C:{tech_c:.3f} | "
            f"Final={final_dir} Action={final_action} C:{final_conf:.3f} Research={consensus}"
        )

        return self.recorder.record_signal(
            symbol=symbol,
            analyst_signals=analyst_signals,
            draft_signal=draft_signal,
            final_signal=final_signal,
            research_debate=research_debate,
            market_snapshot={
                "mode": "replay",
                "timeframe": "1h",
                "ohlcv_candles": len(window),
                "last_close": candle_close,
                "candle_timestamp": candle_ts,
                "lookback_window": self.window_size,
            },
            execution_status="replay_recorded",
        )

    async def run(self):
        await self.initialize()
        try:
            for symbol in self.symbols:
                logger.info(f"--- {symbol} replay ({self.days}d, window={self.window_size}, step={self.step_candles}) ---")
                candles = await self.fetch_candles(symbol)
                if len(candles) < self.window_size:
                    logger.warning(f"{symbol}: only {len(candles)} candles, skipping")
                    continue

                total = 0
                for i in range(self.window_size - 1, len(candles), self.step_candles):
                    ts = datetime.fromtimestamp(candles[i]["timestamp"]).strftime("%Y-%m-%d %H:%M")
                    try:
                        await self.analyze_window(symbol, candles, i, ts)
                        total += 1
                    except Exception as e:
                        logger.error(f"{symbol} replay error at index {i}: {e}")

                logger.info(f"{symbol}: recorded {total} replay signals")
        finally:
            await self.close()


def _parse_end_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"--end-date must be YYYY-MM-DD: {e}")


def parse_args():
    parser = argparse.ArgumentParser(description="Replay agent stack on historical OHLCV")
    parser.add_argument("--symbols", nargs="+", default=["BTCUSDT", "ETHUSDT", "SOLUSDT"])
    parser.add_argument("--days", type=int, default=30, help="Days of historical data")
    parser.add_argument("--window", type=int, default=200, help="Candle window size")
    parser.add_argument("--step", type=int, default=4, help="Step size in candles (4 = ~4h)")
    parser.add_argument("--output", default="logs/replay_signals.jsonl", help="Output JSONL path")
    parser.add_argument(
        "--end-date",
        type=_parse_end_date,
        default=None,
        help="End date for historical window (YYYY-MM-DD). When set, replay looks back --days from this date.",
    )
    return parser.parse_args()


async def main():
    args = parse_args()
    replay = SignalReplay(
        symbols=args.symbols,
        days=args.days,
        window_size=args.window,
        step_candles=args.step,
        output_path=args.output,
        end_date=args.end_date,
    )
    await replay.run()
    logger.info("Replay complete")


if __name__ == "__main__":
    asyncio.run(main())
