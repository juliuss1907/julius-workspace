#!/usr/bin/env python3
"""Send notify_position_event for SYNC futures closes that used the old path.

The bot's close script (close_futures_synced.py) calls OrderManager.close_position()
which uses the legacy path and does NOT trigger the new
notify_position_event (FUTURES POSITION CLOSED wording). To prove the new
notification works against real closed positions, this script:
  1. Reads SYNC rows from local DB (status=closed, market_type=futures).
  2. Builds a synthetic ClosedPosition for each using:
       - entry_price from DB
       - exit_price queried from Binance via /fapi/v1/trades (best effort)
         or falls back to ticker mark price.
  3. Calls TradeNotifier.notify_position_event() with
     execution_status=position_closed, market_type=futures.
"""
import asyncio
import os
import sys
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from dataflows.binance_futures_client import BinanceFuturesClient
from state import db
from trading.trade_notifier import TradeNotifier
from trading.base_trader import TradeSide, MarketType, CloseReason, ClosedPosition


DB_PATH = project_root / "state" / "trading.db"


def fetch_sync_rows():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute("""
        SELECT trade_id, symbol, side, entry_price, quantity, leverage,
               opened_at, closed_at
        FROM paper_positions
        WHERE trade_id LIKE '%_SYNC_%'
          AND market_type = 'futures'
          AND status = 'closed'
        ORDER BY opened_at ASC
    """).fetchall()
    con.close()
    return [dict(r) for r in rows]


async def get_mark_price(client: BinanceFuturesClient, symbol: str) -> float:
    """Best-effort mark price for the close notification."""
    try:
        ticker = await client.fetch_ticker(symbol)
        if ticker and ticker.get("price"):
            return float(ticker["price"])
    except Exception as e:
        print(f"  ! ticker fetch failed for {symbol}: {e}")
    return 0.0


async def main():
    await db.connect()
    try:
        client = BinanceFuturesClient(
            api_key=os.getenv("BINANCE_FUTURES_TESTNET_API_KEY"),
            api_secret=os.getenv("BINANCE_FUTURES_TESTNET_SECRET"),
            environment="testnet",
        )
        notifier = TradeNotifier()

        rows = fetch_sync_rows()
        if not rows:
            print("No SYNC rows to notify.")
            return

        print(f"Sending notify_position_event for {len(rows)} synced closes...")
        for r in rows:
            exit_price = await get_mark_price(client, r["symbol"])
            if exit_price <= 0:
                print(f"  ! could not determine exit price for {r['symbol']}, skipping notify")
                continue

            # Recompute PnL (SHORT) with corrected exit price
            entry_price = float(r["entry_price"])
            quantity = float(r["quantity"])
            leverage = float(r["leverage"])
            taker_fee = 0.0005
            gross_pnl = (entry_price - exit_price) * quantity  # SHORT
            leveraged_pnl = gross_pnl * leverage
            fees = (entry_price * quantity + exit_price * quantity) * taker_fee
            net_pnl = leveraged_pnl - fees
            pnl_pct = (net_pnl / (entry_price * quantity)) * 100 if quantity > 0 else 0.0
            opened_at = int(r["opened_at"]) if r["opened_at"] else int(time.time())
            closed_at = int(r["closed_at"]) if r["closed_at"] else int(time.time())
            duration = max(0, closed_at - opened_at)

            closed = ClosedPosition(
                trade_id=r["trade_id"],
                symbol=r["symbol"],
                side=TradeSide(r["side"]),
                market_type=MarketType.FUTURES,
                entry_price=entry_price,
                exit_price=exit_price,
                quantity=quantity,
                leverage=leverage,
                pnl=net_pnl,
                pnl_pct=pnl_pct,
                fees=fees,
                close_reason=CloseReason.MANUAL,
                opened_at=datetime.fromtimestamp(opened_at),
                closed_at=datetime.fromtimestamp(closed_at),
                duration_seconds=duration,
            )

            print(
                f"  -> {r['trade_id']} exit=${exit_price:.4f} pnl=${net_pnl:+,.2f} ({pnl_pct:+.2f}%)"
            )
            ok = await notifier.notify_position_event(
                symbol=r["symbol"],
                action="close_position",
                reason="manual reconciliation close via OrderManager path",
                close_reason="manual",
                final_direction="N/A",
                final_confidence=0.0,
                execution_status="position_closed",
                mode="execute_close_only",
                market_type="futures",
                position_side=r["side"],
                requested_qty=quantity,
                executed_qty=quantity,
                trade_id=r["trade_id"],
            )
            print(f"     notify ok={ok}")

        try:
            await client.close()
        except Exception:
            pass
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
