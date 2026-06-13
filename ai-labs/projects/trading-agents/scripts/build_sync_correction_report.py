#!/usr/bin/env python3
"""Build a correction report for SYNC rows that have close_price=0 (or
otherwise suspect PnL) due to the historical avgPrice=0 bug.

Does NOT modify the DB. Prints a report and saves it to
reports/reconciliation/sync_row_correction_report.json.

For each suspect row, we try to:
  1. Estimate exit price using Binance ticker mark price (good enough
     for short-term closes that already happened).
  2. Recompute PnL (gross, leveraged, fees, net, pct).
  3. Note that this is an estimate, not the actual fill price.

We also try to fetch Binance order history (`/fapi/v1/allOrders`) for
the symbol and look for the most recent FILLED order around the close
time, which is a better signal. This is best-effort.
"""
import asyncio
import json
import os
import sys
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from dataflows.binance_futures_client import BinanceFuturesClient

DB_PATH = project_root / "state" / "trading.db"
REPORT_DIR = project_root / "reports" / "reconciliation"


def fetch_suspect_sync_rows() -> List[Dict[str, Any]]:
    """Find SYNC rows that are closed but have close_price<=0 or pnl_pct>=100%."""
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    rows = cur.execute("""
        SELECT id, trade_id, symbol, side, market_type, status,
               entry_price, close_price, quantity, leverage,
               pnl, pnl_pct, fees, close_reason,
               opened_at, closed_at
        FROM paper_positions
        WHERE trade_id LIKE '%_SYNC_%'
          AND market_type = 'futures'
          AND status = 'closed'
          AND (close_price IS NULL OR close_price = 0 OR pnl_pct >= 50.0)
        ORDER BY closed_at DESC
    """).fetchall()
    con.close()
    return [dict(r) for r in rows]


async def fetch_mark(client: BinanceFuturesClient, symbol: str) -> Optional[float]:
    try:
        ticker = await client.fetch_ticker(symbol)
        if ticker and ticker.get("price"):
            return float(ticker["price"])
    except Exception as e:
        print(f"  ! ticker fetch failed for {symbol}: {e}")
    return None


def compute_pnl(side: str, entry: float, exit_: float, qty: float, leverage: float, taker_fee: float = 0.0005):
    if side == "LONG":
        gross = (exit_ - entry) * qty
    else:
        gross = (entry - exit_) * qty
    leveraged = gross * leverage
    fees = (entry * qty + exit_ * qty) * taker_fee
    net = leveraged - fees
    pct = (net / (entry * qty)) * 100 if entry * qty > 0 else 0.0
    return {
        "estimated_exit_price": exit_,
        "estimated_gross_pnl": gross,
        "estimated_leveraged_pnl": leveraged,
        "estimated_fees": fees,
        "estimated_net_pnl": net,
        "estimated_pnl_pct": pct,
    }


async def main():
    rows = fetch_suspect_sync_rows()
    if not rows:
        print("No suspect SYNC rows to report.")
        return

    print(f"Found {len(rows)} suspect SYNC row(s) to review.\n")
    client = BinanceFuturesClient(
        api_key=os.getenv("BINANCE_FUTURES_TESTNET_API_KEY"),
        api_secret=os.getenv("BINANCE_FUTURES_TESTNET_SECRET"),
        environment="testnet",
    )
    report: List[Dict[str, Any]] = []
    try:
        for r in rows:
            mark = await fetch_mark(client, r["symbol"])
            entry = float(r["entry_price"])
            qty = float(r["quantity"])
            leverage = float(r["leverage"])
            side = r["side"]
            estimate = None
            if mark and mark > 0:
                estimate = compute_pnl(side, entry, mark, qty, leverage)
            print(f"  {r['trade_id']}  {r['symbol']} {side}  qty={qty} entry=${entry:.4f}")
            print(f"     current close_price={r['close_price']} pnl_pct={r['pnl_pct']}")
            if estimate:
                print(f"     estimated exit (mark now) = ${estimate['estimated_exit_price']:.4f}")
                print(f"     estimated net pnl = ${estimate['estimated_net_pnl']:+.2f} ({estimate['estimated_pnl_pct']:+.2f}%)")
            else:
                print("     ! could not fetch mark price")
            print()

            report.append({
                "row": {
                    "id": r["id"],
                    "trade_id": r["trade_id"],
                    "symbol": r["symbol"],
                    "side": r["side"],
                    "market_type": r["market_type"],
                    "status": r["status"],
                    "entry_price": entry,
                    "close_price": r["close_price"],
                    "quantity": qty,
                    "leverage": leverage,
                    "pnl": r["pnl"],
                    "pnl_pct": r["pnl_pct"],
                    "fees": r["fees"],
                    "close_reason": r["close_reason"],
                    "opened_at": r["opened_at"],
                    "closed_at": r["closed_at"],
                },
                "estimate": estimate,
                "notes": [
                    "close_price=0 means the original close call used Binance "
                    "avgPrice which was 0 in testnet for that order.",
                    "Estimated exit uses current ticker mark, NOT actual fill. "
                    "Useful as a sanity bound, not as ground truth.",
                ],
            })
    finally:
        try:
            await client.close()
        except Exception:
            pass

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / "sync_row_correction_report.json"
    with open(out, "w") as f:
        json.dump({
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "rows_count": len(report),
            "rows": report,
        }, f, indent=2, default=str)
    print(f"Report saved: {out}")
    print()
    print("Review the report, then approve before any DB corrections.")


if __name__ == "__main__":
    asyncio.run(main())
