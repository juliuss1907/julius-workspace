#!/usr/bin/env python3
"""Sync Binance Futures testnet positions into local DB as 'open' rows.

After this runs, the standard bot close path can pick them up via
OrderManager.close_position() -> FuturesTestnetTrader.close_position().

This does NOT place any orders. It only inserts paper_positions rows.
"""
import asyncio
import os
import sys
import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Any

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from dataflows.binance_futures_client import BinanceFuturesClient

DB_PATH = project_root / "state" / "trading.db"
TS = int(time.time() * 1000)


def insert_sync_row(symbol: str, side: str, qty: float, entry_price: float, leverage: int) -> int:
    trade_id = f"{symbol}_{side}_SYNC_{TS}"
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO paper_positions
        (trade_id, symbol, side, market_type, entry_price, quantity, leverage,
         stop_loss, take_profit, trailing_stop, status, opened_at, signal_data, order_id)
        VALUES (?, ?, ?, 'futures', ?, ?, ?, NULL, NULL, NULL, 'open', ?, ?, NULL)
        """,
        (
            trade_id,
            symbol,
            side,
            entry_price,
            qty,
            leverage,
            int(time.time()),
            __import__("json").dumps({
                "source": "manual_reconcile_sync",
                "note": "synthetic open row from Binance testnet reconciliation",
                "binance_entry_price": entry_price,
                "binance_qty": qty,
                "leverage": leverage,
            }),
        ),
    )
    con.commit()
    con.close()
    return trade_id


async def main():
    if not os.getenv("BINANCE_FUTURES_TESTNET_API_KEY") or not os.getenv("BINANCE_FUTURES_TESTNET_SECRET"):
        print("ERROR: missing BINANCE_FUTURES_TESTNET_API_KEY/SECRET in .env", file=sys.stderr)
        sys.exit(1)

    client = BinanceFuturesClient(
        api_key=os.getenv("BINANCE_FUTURES_TESTNET_API_KEY"),
        api_secret=os.getenv("BINANCE_FUTURES_TESTNET_SECRET"),
        environment="testnet",
    )
    positions: List[Dict[str, Any]] = await client.get_positions()
    try:
        if not positions:
            print("No open Binance futures positions to sync.")
            return

        print(f"Inserting {len(positions)} sync rows into DB...")
        for p in positions:
            tid = insert_sync_row(
                symbol=p["symbol"],
                side=p["side"],
                qty=p["amount"],
                entry_price=p["entry_price"],
                leverage=int(p["leverage"]),
            )
            print(f"  + {tid}  qty={p['amount']:.6f} entry=${p['entry_price']:.4f} lev={int(p['leverage'])}x")

        print()
        print("Sync complete. Now run close path, e.g.:")
        print("  ./venv/bin/python scripts/run_paper_trading.py --single-cycle")
        print("Or per-position:")
        print("  ./venv/bin/python scripts/close_futures_synced.py")
    finally:
        try:
            await client.close()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
