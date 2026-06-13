#!/usr/bin/env python3
"""Analyze paper positions and trades from the SQLite database."""
import argparse
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def pct(value: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{(value / total) * 100:.1f}"


def avg(values):
    values = [v for v in values if isinstance(v, (int, float))]
    return sum(values) / len(values) if values else 0.0


def print_counter(title: str, counter: Counter, total: int, limit: int = 20):
    print(f"\n{title}")
    if not counter:
        print("  none")
        return
    for key, count in counter.most_common(limit):
        print(f"  {key}: {count} ({pct(count, total)})")


def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def analyze(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory

    # ── Open Positions ──────────────────────────────────────────────────
    cursor = conn.execute(
        "SELECT * FROM paper_positions WHERE status = 'open' ORDER BY opened_at DESC"
    )
    open_positions = cursor.fetchall()
    print("Position DB Analysis")
    print("=" * 80)
    print(f"Open Positions: {len(open_positions)}")

    if open_positions:
        open_by_symbol = Counter()
        open_by_side = Counter()
        open_by_market = Counter()
        open_entry_prices = []
        open_quantities = []
        for p in open_positions:
            open_by_symbol[p["symbol"]] += 1
            open_by_side[p["side"]] += 1
            open_by_market[p["market_type"]] += 1
            if p.get("entry_price"):
                open_entry_prices.append(p["entry_price"])
            if p.get("quantity"):
                open_quantities.append(p["quantity"])

        print_counter("Open By Symbol", open_by_symbol, len(open_positions))
        print_counter("Open By Side", open_by_side, len(open_positions))
        print_counter("Open By Market", open_by_market, len(open_positions))
        if open_entry_prices:
            print(f"\nOpen Positions Avg Entry Price\n  {avg(open_entry_prices):.2f}")
        if open_quantities:
            print(f"\nOpen Positions Avg Quantity\n  {avg(open_quantities):.4f}")

        print("\nOpen Position Details")
        for p in open_positions:
            print(
                f"  {p['trade_id']}: {p['symbol']} {p['side']} "
                f"entry={p['entry_price']} qty={p['quantity']} "
                f"market={p['market_type']} lev={p.get('leverage', 1)}"
            )
    else:
        print("  none")

    # ── Closed Trades ───────────────────────────────────────────────────
    cursor = conn.execute(
        "SELECT * FROM paper_trades ORDER BY closed_at DESC"
    )
    trades = cursor.fetchall()
    print(f"\nClosed Trades: {len(trades)}")

    if trades:
        close_reasons = Counter()
        trades_by_symbol = defaultdict(Counter)
        trades_by_market = Counter()
        trades_by_side = Counter()
        pnls = []
        pnl_pcts = []
        durations = []
        profits = 0
        losses = 0
        breakeven = 0

        for t in trades:
            reason = t.get("close_reason") or "unknown"
            close_reasons[reason] += 1
            trades_by_symbol[t["symbol"]][t["side"]] += 1
            trades_by_market[t["market_type"]] += 1
            trades_by_side[t["side"]] += 1

            pnl = t.get("pnl")
            if isinstance(pnl, (int, float)):
                pnls.append(pnl)
            pnl_pct = t.get("pnl_pct")
            if isinstance(pnl_pct, (int, float)):
                pnl_pcts.append(pnl_pct)
            dur = t.get("duration_seconds")
            if isinstance(dur, (int, float)):
                durations.append(dur)

            if pnl is not None and pnl_pct is not None:
                if pnl_pct > 0.001:
                    profits += 1
                elif pnl_pct < -0.001:
                    losses += 1
                else:
                    breakeven += 1

        print_counter("Close Reasons", close_reasons, len(trades))
        print_counter("Trades By Market", trades_by_market, len(trades))
        print_counter("Trades By Side", trades_by_side, len(trades))

        print("\nTrades By Symbol")
        for sym in sorted(trades_by_symbol.keys()):
            actions = ", ".join(f"{k}={v}" for k, v in trades_by_symbol[sym].most_common())
            print(f"  {sym}: {actions}")

        if pnls:
            print(f"\nPnL Summary")
            print(f"  Total PnL: {sum(pnls):.4f}")
            print(f"  Avg PnL: {avg(pnls):.4f}")
            print(f"  Min PnL: {min(pnls):.4f}")
            print(f"  Max PnL: {max(pnls):.4f}")
            print(f"  Win/Loss/BE: {profits}W / {losses}L / {breakeven}BE")
            if profits + losses + breakeven > 0:
                win_rate = profits / max(profits + losses + breakeven, 1) * 100
                print(f"  Win Rate: {win_rate:.1f}%")

        if pnl_pcts:
            print(f"\nPnL % Summary")
            print(f"  Avg PnL%: {avg(pnl_pcts):.2f}%")
            print(f"  Min PnL%: {min(pnl_pcts):.2f}%")
            print(f"  Max PnL%: {max(pnl_pcts):.2f}%")

        if durations:
            avg_sec = avg(durations)
            hours = avg_sec / 3600
            print(f"\nTrade Duration")
            print(f"  Avg: {avg_sec:.0f}s ({hours:.1f}h)")

        # Latest 10 trades
        print("\nLatest Trades")
        for t in trades[:10]:
            reason = t.get("close_reason") or "unknown"
            pnl = t.get("pnl", 0) or 0
            pnl_pct = t.get("pnl_pct", 0) or 0
            exit_p = f" exit={t['exit_price']}" if t.get("exit_price") else ""
            print(
                f"  {t['symbol']} {t['side']} | pnl={pnl:.4f} ({pnl_pct:+.2f}%)"
                f" | reason={reason}"
                f" | qty={t['quantity']} entry={t['entry_price']}{exit_p}"
            )

    else:
        print("  none")

    # ── Portfolio Snapshot ──────────────────────────────────────────────
    cursor = conn.execute(
        "SELECT * FROM paper_portfolio ORDER BY timestamp DESC LIMIT 1"
    )
    snap = cursor.fetchone()
    if snap:
        print(f"\nLatest Portfolio Snapshot")
        print(f"  Spot Balance:      {snap.get('spot_balance', 'N/A')}")
        print(f"  Futures Balance:   {snap.get('futures_balance', 'N/A')}")
        print(f"  Total Equity:      {snap.get('total_equity', 'N/A')}")
        print(f"  Open Positions:    {snap.get('open_positions_count', 'N/A')}")
        print(f"  Daily PnL:         {snap.get('daily_pnl', 'N/A')}")
        print(f"  Total PnL:         {snap.get('total_pnl', 'N/A')}")
        total_pnl_pct = snap.get('total_pnl_pct')
        print(f"  Total PnL%:        {total_pnl_pct}%")

    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Analyze paper positions and trades from SQLite")
    parser.add_argument(
        "--path",
        default=str(project_root / "state" / "trading.db"),
        help="Path to trading.db",
    )
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"Database not found: {path}")
        sys.exit(1)

    analyze(str(path))


if __name__ == "__main__":
    main()
