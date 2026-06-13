#!/usr/bin/env python3
"""Reconcile Binance Futures testnet open positions vs local SQLite.

Read-only: prints side-by-side and a mapping suggestion.
Does NOT mutate DB or place any orders.
"""
import asyncio
import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load .env so BINANCE_FUTURES_TESTNET_API_KEY/SECRET are available
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from dataflows.binance_futures_client import BinanceFuturesClient

DB_PATH = project_root / "state" / "trading.db"


def fetch_db_futures() -> Dict[str, Dict[str, Any]]:
    """Return DB futures positions keyed by (symbol, side)."""
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    rows = cur.execute("""
        SELECT trade_id, symbol, side, status, entry_price, quantity,
               leverage, stop_loss, take_profit, opened_at, closed_at, close_reason
        FROM paper_positions
        WHERE market_type = 'futures'
        ORDER BY opened_at ASC
    """).fetchall()
    con.close()
    out = {}
    for r in rows:
        d = dict(r)
        d["entry_price"] = float(d["entry_price"] or 0)
        d["quantity"] = float(d["quantity"] or 0)
        d["leverage"] = float(d["leverage"] or 1)
        key = (d["symbol"], d["side"])
        out[key] = d
    return out


async def fetch_binance_positions(client: BinanceFuturesClient) -> List[Dict[str, Any]]:
    return await client.get_positions()


def main():
    if not os.getenv("BINANCE_FUTURES_TESTNET_API_KEY") or not os.getenv("BINANCE_FUTURES_TESTNET_SECRET"):
        print("ERROR: BINANCE_FUTURES_TESTNET_API_KEY/SECRET not loaded from .env", file=sys.stderr)
        sys.exit(1)

    client = BinanceFuturesClient(
        api_key=os.getenv("BINANCE_FUTURES_TESTNET_API_KEY"),
        api_secret=os.getenv("BINANCE_FUTURES_TESTNET_SECRET"),
        environment="testnet",
    )

    binance_positions = asyncio.run(fetch_binance_positions(client))
    db_positions = fetch_db_futures()

    print("=" * 80)
    print(f"Reconciliation @ {datetime.utcnow().isoformat()}Z")
    print("=" * 80)
    print()
    print("--- BINANCE FUTURES TESTNET (open positions) ---")
    if not binance_positions:
        print("(no open positions)")
    for p in binance_positions:
        print(
            f"  {p['symbol']:<12} {p['side']:<6} qty={p['amount']:.6f} "
            f"entry=${p['entry_price']:.4f} mark=${p['mark_price']:.4f} "
            f"uPnL=${p['unrealized_pnl']:.4f} lev={int(p['leverage'])}x "
            f"margin={p['margin_type']}"
        )
    print()
    print("--- LOCAL DB (paper_positions where market_type='futures') ---")
    if not db_positions:
        print("(no rows)")
    for k, d in db_positions.items():
        sym, side = k
        print(
            f"  {sym:<12} {side:<6} status={d['status']:<7} qty={d['quantity']:.6f} "
            f"entry=${d['entry_price']:.4f} lev={int(d['leverage'])}x "
            f"trade_id={d['trade_id']} reason={d.get('close_reason')}"
        )
    print()
    print("--- MAPPING SUGGESTION ---")
    binance_keys = {(p["symbol"], p["side"]) for p in binance_positions}
    db_open_keys = {k for k, v in db_positions.items() if v["status"] == "open"}
    db_closed_keys = {k for k, v in db_positions.items() if v["status"] == "closed"}

    on_both = binance_keys & db_open_keys
    binance_only = binance_keys - db_open_keys
    db_open_only = db_open_keys - binance_keys
    binance_only_but_db_has_closed = sorted(
        (k for k in binance_only if k in db_closed_keys)
    )
    binance_only_no_db = sorted(
        (k for k in binance_only if k not in db_closed_keys)
    )

    print(f"  matched (Binance open & DB open):   {len(on_both)}")
    for k in sorted(on_both):
        print(f"    {k}")
    print()
    print(f"  Binance open but DB has NO open row: {len(binance_only)}")
    for k in sorted(binance_only):
        in_closed = "db-closed-row-exists" if k in db_closed_keys else "no-db-history"
        print(f"    {k}  ({in_closed})")
    print()
    print(f"  DB open but not on Binance:         {len(db_open_only)}")
    for k in sorted(db_open_only):
        print(f"    {k}")
    print()
    if binance_only_but_db_has_closed:
        print("  Note: a closed DB row for the same symbol+side already exists.")
        print("  Suggest creating a NEW open DB row with a unique trade_id like:")
        for k in binance_only_but_db_has_closed:
            sym, side = k
            print(f"    {sym}_{side}_SYNC_<ts>")
    if binance_only_no_db:
        print("  Binance has positions with no DB history. Suggest:")
        for k in binance_only_no_db:
            sym, side = k
            print(f"    {sym}_{side}_ORPHAN_<ts>")

    print()
    print("Reconciliation complete (read-only). No DB or API mutations performed.")


if __name__ == "__main__":
    main()
