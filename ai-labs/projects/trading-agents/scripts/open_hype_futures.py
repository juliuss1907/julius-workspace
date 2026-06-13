#!/usr/bin/env python3
"""
Manually open a HYPEUSDT futures position via the OrderManager path.

Useful for testing notification flow, reconciliation, and the bot
close path against a known position.

Usage:
  ./venv/bin/python scripts/open_hype_futures.py --side SHORT --qty 1 --leverage 5
  ./venv/bin/python scripts/open_hype_futures.py --side LONG --qty 1 --leverage 5
  ./venv/bin/python scripts/open_hype_futures.py --side SHORT --qty 1 --dry-run
"""
import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Any, Dict

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from datetime import datetime
from agents.base_agent import AgentResult, SignalDirection
from state import db
from trading.order_manager import OrderManager
from trading.trade_notifier import TradeNotifier
from trading.base_trader import TradeSide, MarketType, CloseReason


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--side", choices=["LONG", "SHORT"], default="SHORT")
    p.add_argument("--qty", type=float, default=1.0)
    p.add_argument("--leverage", type=int, default=5)
    p.add_argument("--dry-run", action="store_true",
                   help="Compute sizing only, do not place an order")
    args = p.parse_args()

    await db.connect()
    try:
        om = OrderManager(notifier=TradeNotifier())
        await om.initialize()

        # Build a synthetic AgentResult that satisfies the bot's
        # execute_signal contract. The bot uses confidence to size
        # position; we override size by patching _calculate_position_size
        # via the manual qty parameter below.
        symbol = "HYPEUSDT"
        ticker = await om.futures_trader.client.fetch_ticker(symbol)
        if not ticker:
            print(f"ERROR: could not fetch ticker for {symbol}")
            return
        current_price = float(ticker["price"])
        atr = 0.5  # placeholder; not used since we override qty

        # Build a synthetic AgentResult and call execute_signal,
        # but bypass _calculate_position_size by monkey-patching
        # it to return our desired qty.
        direction = (
            SignalDirection.BEARISH if args.side == "SHORT"
            else SignalDirection.BULLISH
        )
        signal = AgentResult(
            agent_name="manual_test",
            symbol=symbol,
            timestamp=datetime.utcnow(),
            direction=direction,
            sub_score=0.6,
            confidence=0.85,  # > min_confidence so it executes
            analysis={"indicators": {"atr": atr}},
            reasoning=f"manual test: open {args.side} {args.qty} HYPE futures",
            metadata={"regime": "ranging"},
        )

        original_calc = om._calculate_position_size
        def _patched_calc(*_a, **_kw):
            return float(args.qty)
        om._calculate_position_size = _patched_calc

        if args.dry_run:
            print(f"[dry-run] Would open {args.side} {args.qty} HYPE @ ${current_price} lev={args.leverage}x")
            return

        # Ensure leverage is set (ignore "no need" errors)
        try:
            await om.futures_trader.client.set_leverage(symbol, args.leverage)
        except Exception as e:
            print(f"  set_leverage warn: {e}")

        risk_decision = {
            "approved": True,
            "risk_level": "low",
            "position_size_multiplier": 1.0,
            "reason": "manual test",
        }
        result = await om.execute_signal(
            signal, current_price, atr, risk_decision=risk_decision,
        )
        if result and result.success:
            print(f"  OPENED {result.trade_id} {result.side.value} {result.quantity} "
                  f"{result.symbol} @ ${result.entry_price:.4f} lev={result.leverage}x")
        else:
            err = getattr(result, "error_message", "unknown")
            print(f"  FAILED: {err}")
    finally:
        await db.close()
        try:
            await om.close()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
