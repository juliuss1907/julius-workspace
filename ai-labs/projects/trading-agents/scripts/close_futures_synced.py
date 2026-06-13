#!/usr/bin/env python3
"""Close all open futures positions in local DB via OrderManager path.

Iterates paper_positions where market_type='futures' and status='open',
calls OrderManager.close_position() for each. This exercises the bot's
real close path so the new Telegram notification wording is triggered.
"""
import asyncio
import sys
import sqlite3
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from state import db
from trading.order_manager import OrderManager
from trading.base_trader import CloseReason


async def main():
    await db.connect()
    try:
        om = OrderManager()
        await om.initialize()

        con = sqlite3.connect(project_root / "state" / "trading.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        rows = cur.execute("""
            SELECT trade_id, symbol, side, market_type, quantity
            FROM paper_positions
            WHERE market_type = 'futures' AND status = 'open'
            ORDER BY opened_at ASC
        """).fetchall()
        con.close()

        if not rows:
            print("No open futures positions to close.")
            return

        print(f"Closing {len(rows)} open futures positions...")
        results = []
        for r in rows:
            print(f"  -> {r['trade_id']} ({r['symbol']} {r['side']} qty={r['quantity']:.6f})")
            ok = await om.close_position(r["trade_id"], reason=CloseReason.MANUAL)
            results.append((r["trade_id"], ok))
            print(f"     result: {'closed' if ok else 'FAILED'}")

        print()
        print("--- Summary ---")
        for tid, ok in results:
            print(f"  {tid}: {'OK' if ok else 'FAILED'}")
    finally:
        await db.close()
        try:
            await om.close()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
