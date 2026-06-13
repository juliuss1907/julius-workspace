#!/usr/bin/env python3
"""
Run a single futures reconciliation pass (Binance testnet vs local DB).

Usage:
    ./venv/bin/python scripts/reconcile_positions.py --once
    ./venv/bin/python scripts/reconcile_positions.py --once --json
    ./venv/bin/python scripts/reconcile_positions.py --loop --interval 60
    ./venv/bin/python scripts/reconcile_positions.py --once --no-auto-sync
    ./venv/bin/python scripts/reconcile_positions.py --once --no-auto-close-db
"""
import argparse
import asyncio
import json
import os
import signal
import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from dataflows.binance_futures_client import BinanceFuturesClient
from state import db
from state.reconciliation import FuturesReconciler, ReconcileResult
from utils import get_logger


logger = get_logger("reconcile_cli")


def parse_args():
    p = argparse.ArgumentParser(description="Reconcile Binance futures positions vs local DB")
    p.add_argument("--once", action="store_true", help="Run once and exit")
    p.add_argument("--loop", action="store_true", help="Run in a polling loop")
    p.add_argument("--interval", type=int, default=60, help="Loop interval in seconds (default 60)")
    p.add_argument("--no-auto-sync", action="store_true", help="Disable auto-inserting SYNC rows for Binance-only positions")
    p.add_argument("--no-auto-close-db", action="store_true", help="Disable auto-marking DB-only positions as closed_external")
    p.add_argument("--auto-fix-qty", action="store_true", help="Auto-fix DB qty to match Binance (use with care)")
    p.add_argument("--qty-tolerance", type=float, default=0.5, help="Qty tolerance pct (default 0.5)")
    p.add_argument("--json", action="store_true", help="Print result as JSON")
    p.add_argument("--quiet", action="store_true", help="Suppress human-readable output")
    return p.parse_args()


def make_reconciler(args) -> FuturesReconciler:
    client = BinanceFuturesClient(
        api_key=os.getenv("BINANCE_FUTURES_TESTNET_API_KEY"),
        api_secret=os.getenv("BINANCE_FUTURES_TESTNET_SECRET"),
        environment="testnet",
    )
    return FuturesReconciler(
        client=client,
        db=db,
        qty_tolerance_pct=args.qty_tolerance,
        auto_sync_orphans=not args.no_auto_sync,
        auto_close_db_missing=not args.no_auto_close_db,
        auto_fix_qty_mismatch=args.auto_fix_qty,
    )


def format_human(result: ReconcileResult) -> str:
    lines = [
        f"Run: {result.run_id}",
        f"Started: {result.started_at}",
        f"Finished: {result.finished_at}",
        f"Duration: {result.finished_at - result.started_at}s",
    ]
    if result.error:
        lines.append(f"ERROR: {result.error}")
    counts = result.counts
    lines.append("")
    lines.append("Counts:")
    for k, v in counts.items():
        lines.append(f"  {k}: {v}")
    if result.events:
        lines.append("")
        lines.append("Events:")
        for ev in result.events:
            lines.append(
                f"  [{ev.severity}] {ev.event_type} {ev.symbol} {ev.side or '-'} "
                f"db_trade_id={ev.db_trade_id or '-'} "
                f"binance_qty={ev.binance_qty} db_qty={ev.db_qty} "
                f"action={ev.action_taken}"
            )
            if ev.details:
                lines.append(f"    details: {ev.details}")
    return "\n".join(lines)


def format_json(result: ReconcileResult) -> str:
    payload = {
        "run_id": result.run_id,
        "started_at": result.started_at,
        "finished_at": result.finished_at,
        "duration_seconds": result.finished_at - result.started_at,
        "error": result.error,
        "counts": result.counts,
        "events": [ev.to_dict() for ev in result.events],
    }
    return json.dumps(payload, indent=2, default=str)


async def main():
    args = parse_args()
    if not args.once and not args.loop:
        args.once = True

    if not os.getenv("BINANCE_FUTURES_TESTNET_API_KEY") or not os.getenv("BINANCE_FUTURES_TESTNET_SECRET"):
        print("ERROR: missing BINANCE_FUTURES_TESTNET_API_KEY/SECRET in .env", file=sys.stderr)
        sys.exit(1)

    reconciler = make_reconciler(args)

    await db.connect()
    stop_flag = {"stop": False}
    try:
        if args.loop:
            def _handle_sig(*_):
                stop_flag["stop"] = True
            try:
                loop = asyncio.get_running_loop()
                loop.add_signal_handler(signal.SIGINT, _handle_sig)
                loop.add_signal_handler(signal.SIGTERM, _handle_sig)
            except NotImplementedError:
                pass
            while not stop_flag["stop"]:
                result = await reconciler.reconcile_once()
                if not args.quiet:
                    if args.json:
                        print(format_json(result))
                    else:
                        print(format_human(result))
                for _ in range(args.interval):
                    if stop_flag["stop"]:
                        break
                    await asyncio.sleep(1)
        else:
            result = await reconciler.reconcile_once()
            if not args.quiet:
                if args.json:
                    print(format_json(result))
                else:
                    print(format_human(result))
    finally:
        try:
            await reconciler.client.close()
        except Exception:
            pass
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
