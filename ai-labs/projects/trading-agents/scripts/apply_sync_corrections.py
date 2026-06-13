#!/usr/bin/env python3
"""Fetch actual Binance Futures fills for suspect SYNC rows and produce
a high-confidence correction report.

For each suspect row, we:
  1. Query /fapi/v1/allOrders around (opened_at, closed_at) and find
     the most recent FILLED order (state='FILLED') that matches side and
     reduceOnly.
  2. Cross-check with /fapi/v1/userTrades (the fill records) to get the
     actual executed price.
  3. If the order data is missing avgPrice, fall back to the average of
     the fill records in the same order window.

Then we write a correction JSON to
reports/reconciliation/sync_row_correction_actual.json.

By default, this script does NOT mutate the DB. Pass --apply to commit
the corrections.
"""
import argparse
import asyncio
import json
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from dataflows.binance_futures_client import BinanceFuturesClient

DB_PATH = project_root / "state" / "trading.db"
REPORT_DIR = project_root / "reports" / "reconciliation"
TakerFee = 0.0005


def fetch_suspect_sync_rows() -> List[Dict[str, Any]]:
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


def compute_pnl(side: str, entry: float, exit_: float, qty: float, leverage: float) -> Dict[str, float]:
    if side == "LONG":
        gross = (exit_ - entry) * qty
    else:
        gross = (entry - exit_) * qty
    leveraged = gross * leverage
    fees = (entry * qty + exit_ * qty) * TakerFee
    net = leveraged - fees
    pct = (net / (entry * qty)) * 100 if entry * qty > 0 else 0.0
    return {
        "estimated_gross_pnl": gross,
        "estimated_leveraged_pnl": leveraged,
        "estimated_fees": fees,
        "estimated_net_pnl": net,
        "estimated_pnl_pct": pct,
    }


async def find_close_fill(
    client: BinanceFuturesClient,
    row: Dict[str, Any],
) -> Dict[str, Any]:
    """Find the most plausible close fill for this SYNC row.

    Strategy:
      - Window: 1h before opened_at to 1h after closed_at.
      - Among FILLED orders, prefer the one whose side matches closing side
        (LONG -> SELL, SHORT -> BUY) AND reduceOnly is true.
      - If no reduce-only, fall back to the FILLED order on closing side.
      - If still none, return None and let the report fall back to mark price.

    Returns:
      dict with keys: order (raw) | trades (raw list) | exit_price | source
    """
    side = row["side"]
    close_order_side = "SELL" if side == "LONG" else "BUY"
    opened_at_ms = int(row["opened_at"]) * 1000 if row["opened_at"] else int(time.time() * 1000) - 3600_000
    closed_at_ms = int(row["closed_at"]) * 1000 if row["closed_at"] else int(time.time() * 1000)
    start_ms = max(0, opened_at_ms - 3600_000)
    end_ms = closed_at_ms + 3600_000

    orders = await client.get_all_orders(
        symbol=row["symbol"],
        start_time=start_ms,
        end_time=end_ms,
        limit=200,
    )
    candidates: List[Dict[str, Any]] = []
    for o in orders:
        if o.get("status") != "FILLED":
            continue
        if o.get("side") != close_order_side:
            continue
        if bool(o.get("reduceOnly")) is True:
            candidates.append(o)
    chosen = None
    if candidates:
        # Most recent reduce-only filled
        chosen = max(candidates, key=lambda o: int(o.get("updateTime") or o.get("time") or 0))
    else:
        # Fallback: any FILLED order on closing side
        any_filled = [o for o in orders if o.get("status") == "FILLED" and o.get("side") == close_order_side]
        if any_filled:
            chosen = max(any_filled, key=lambda o: int(o.get("updateTime") or o.get("time") or 0))

    if not chosen:
        return {"order": None, "trades": [], "exit_price": None, "source": "no_match"}

    # Now find matching trades (userTrades) for this orderId
    trades = await client.get_user_trades(
        symbol=row["symbol"],
        start_time=start_ms,
        end_time=end_ms,
        limit=200,
    )
    matched = [t for t in trades if str(t.get("orderId")) == str(chosen.get("orderId"))]
    exit_price = None
    if matched:
        # Use volume-weighted average of fill prices
        total_qty = sum(float(t.get("qty") or 0) for t in matched)
        if total_qty > 0:
            exit_price = sum(float(t.get("price") or 0) * float(t.get("qty") or 0) for t in matched) / total_qty
    if exit_price is None or exit_price <= 0:
        # Order-level avgPrice
        ap = chosen.get("avgPrice")
        if ap and float(ap) > 0:
            exit_price = float(ap)
    if exit_price is None or exit_price <= 0:
        return {
            "order": chosen,
            "trades": matched,
            "exit_price": None,
            "source": "order_or_trades_have_no_price",
        }
    return {"order": chosen, "trades": matched, "exit_price": exit_price, "source": "user_trades_or_order_avg"}


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="Apply corrections to the DB after reporting")
    args = parser.parse_args()

    rows = fetch_suspect_sync_rows()
    if not rows:
        print("No suspect SYNC rows found.")
        return

    print(f"Found {len(rows)} suspect SYNC row(s). Querying Binance...\n")
    client = BinanceFuturesClient(
        api_key=os.getenv("BINANCE_FUTURES_TESTNET_API_KEY"),
        api_secret=os.getenv("BINANCE_FUTURES_TESTNET_SECRET"),
        environment="testnet",
    )
    report: List[Dict[str, Any]] = []
    try:
        for r in rows:
            res = await find_close_fill(client, r)
            exit_price = res["exit_price"]
            entry = float(r["entry_price"])
            qty = float(r["quantity"])
            leverage = float(r["leverage"])
            side = r["side"]

            estimate = None
            if exit_price and exit_price > 0:
                estimate = compute_pnl(side, entry, exit_price, qty, leverage)

            print(f"  {r['trade_id']}  {r['symbol']} {side}  qty={qty} entry=${entry:.4f}")
            print(f"     current close_price={r['close_price']} pnl_pct={r['pnl_pct']}")
            print(f"     source={res['source']}")
            if exit_price:
                print(f"     actual exit (from Binance) = ${exit_price:.4f}")
                print(f"     corrected net pnl = ${estimate['estimated_net_pnl']:+.2f} ({estimate['estimated_pnl_pct']:+.2f}%)")
            else:
                print("     ! no actual fill found in window")
            print()

            # Trim the raw order/trades payload for the report
            raw_order = res.get("order") or {}
            raw_trades = res.get("trades") or []
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
                "binance_evidence": {
                    "source": res["source"],
                    "order": {
                        "orderId": raw_order.get("orderId"),
                        "side": raw_order.get("side"),
                        "type": raw_order.get("type"),
                        "status": raw_order.get("status"),
                        "avgPrice": raw_order.get("avgPrice"),
                        "executedQty": raw_order.get("executedQty"),
                        "cumQuote": raw_order.get("cumQuote"),
                        "reduceOnly": raw_order.get("reduceOnly"),
                        "time": raw_order.get("time"),
                        "updateTime": raw_order.get("updateTime"),
                    },
                    "matched_trade_count": len(raw_trades),
                    "matched_trade_qty_sum": sum(float(t.get("qty") or 0) for t in raw_trades),
                    "matched_trade_quote_sum": sum(float(t.get("quoteQty") or 0) for t in raw_trades),
                },
                "correction": {
                    "exit_price": exit_price,
                    "pnl": (estimate or {}).get("estimated_net_pnl"),
                    "pnl_pct": (estimate or {}).get("estimated_pnl_pct"),
                    "fees": (estimate or {}).get("estimated_fees"),
                    "leverage": leverage,
                },
            })
    finally:
        try:
            await client.close()
        except Exception:
            pass

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / "sync_row_correction_actual.json"
    with open(out, "w") as f:
        json.dump({
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "rows_count": len(report),
            "rows": report,
        }, f, indent=2, default=str)
    print(f"Report saved: {out}")

    if not args.apply:
        applyable = [r for r in report if r["correction"]["exit_price"]]
        print()
        print(f"Applyable rows: {len(applyable)} / {len(report)}")
        print("Re-run with --apply to commit corrections to the DB.")
        return

    # Apply
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    applied = 0
    for r in report:
        corr = r["correction"]
        if not corr["exit_price"]:
            continue
        trade_id = r["row"]["trade_id"]
        cur.execute(
            """
            UPDATE paper_positions
            SET close_price = ?,
                pnl = ?,
                pnl_pct = ?,
                fees = ?,
                notes = COALESCE(notes, '') || ?
            WHERE trade_id = ? AND status = 'closed'
            """,
            (
                float(corr["exit_price"]),
                float(corr["pnl"] or 0.0),
                float(corr["pnl_pct"] or 0.0),
                float(corr["fees"] or 0.0),
                f"\n[recon-correction {int(time.time())}] exit_price/PnL from Binance userTrades",
                trade_id,
            ),
        )
        # Also mirror to paper_trades if a row exists
        cur.execute(
            """
            UPDATE paper_trades
            SET exit_price = ?,
                pnl = ?,
                pnl_pct = ?,
                fees = ?
            WHERE trade_id = ?
            """,
            (
                float(corr["exit_price"]),
                float(corr["pnl"] or 0.0),
                float(corr["pnl_pct"] or 0.0),
                float(corr["fees"] or 0.0),
                trade_id,
            ),
        )
        applied += 1
    con.commit()
    con.close()
    print()
    print(f"Applied corrections to {applied} row(s).")


if __name__ == "__main__":
    asyncio.run(main())
