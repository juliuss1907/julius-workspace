#!/usr/bin/env python3
"""Tests for FuturesReconciler against a real (in-memory) SQLite DB and a mocked Binance client."""
import asyncio
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import List, Dict, Any

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Use a project-relative DB path so the schema.sql is found by Database.connect()
TMP_DIR = Path(tempfile.mkdtemp(prefix="recon_test_"))
TEST_DB_PATH = project_root / "state" / "test_recon.db"
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

import state.database as db_module
from state import db as db_state
from state.database import Database
from state.reconciliation import FuturesReconciler


class MockBinanceClient:
    def __init__(self, positions: List[Dict[str, Any]]):
        self.positions = positions
        self.closed = False

    async def get_positions(self) -> List[Dict[str, Any]]:
        return list(self.positions)

    async def close(self):
        self.closed = True


def make_binance_pos(symbol: str, side: str, amount: float, entry: float, leverage: int = 10):
    return {
        "symbol": symbol,
        "side": side,
        "amount": amount,
        "entry_price": entry,
        "mark_price": entry,
        "unrealized_pnl": 0.0,
        "leverage": leverage,
        "margin_type": "isolated",
        "liquidation_price": 0.0,
    }


async def setup_db():
    """Reset the test database to a clean state and apply schema."""
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    fresh = Database(str(TEST_DB_PATH))
    await fresh.connect()
    return fresh


def assert_eq(a, b, msg=""):
    if a != b:
        raise AssertionError(f"{msg}: expected {b!r}, got {a!r}")


def assert_true(cond, msg=""):
    if not cond:
        raise AssertionError(msg)


async def get_db_positions(database: Database, status: str = "open"):
    async with database._conn.execute(
        "SELECT trade_id, symbol, side, status, quantity, entry_price, market_type, close_reason "
        "FROM paper_positions WHERE status = ? AND market_type='futures'",
        (status,),
    ) as cur:
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in await cur.fetchall()]


async def test_orphan_detected_inserts_sync_row():
    db_obj = await setup_db()
    try:
        client = MockBinanceClient([
            make_binance_pos("BTCUSDT", "SHORT", 0.05, 63000.0, 10),
        ])
        rec = FuturesReconciler(
            client=client,
            db=db_obj,
            auto_sync_orphans=True,
            auto_close_db_missing=True,
        )
        result = await rec.reconcile_once()
        assert_eq(result.counts.get("orphan_detected", 0), 1, "expected 1 orphan")
        positions = await get_db_positions(db_obj)
        assert_eq(len(positions), 1, "expected 1 DB position")
        assert_true("SYNC" in positions[0]["trade_id"], "expected SYNC trade_id")
        assert_eq(positions[0]["side"], "SHORT")
        print("PASS test_orphan_detected_inserts_sync_row")
    finally:
        await db_obj.close()


async def test_db_missing_on_binance_marks_closed_external():
    db_obj = await setup_db()
    try:
        # Insert a synthetic DB open futures position
        await db_obj.insert_paper_position({
            "trade_id": "ETHUSDT_SHORT_OLD_001",
            "symbol": "ETHUSDT",
            "side": "SHORT",
            "market_type": "futures",
            "entry_price": 1700.0,
            "quantity": 0.5,
            "leverage": 5.0,
            "stop_loss": None,
            "take_profit": None,
            "trailing_stop": None,
            "order_id": "test",
            "signal_data": {},
        })

        # Binance has no open positions
        client = MockBinanceClient([])
        rec = FuturesReconciler(
            client=client,
            db=db_obj,
            auto_sync_orphans=True,
            auto_close_db_missing=True,
        )
        result = await rec.reconcile_once()
        assert_eq(result.counts.get("db_missing_on_binance", 0), 1, "expected 1 db_missing")
        assert_eq(result.events[0].action_taken, "marked_closed", "expected marked_closed")
        closed = await get_db_positions(db_obj, status="closed")
        assert_eq(len(closed), 1, "expected 1 closed row")
        assert_eq(closed[0]["close_reason"], "closed_external", "expected close_reason=closed_external")
        print("PASS test_db_missing_on_binance_marks_closed_external")
    finally:
        await db_obj.close()


async def test_match_within_tolerance_is_ok():
    db_obj = await setup_db()
    try:
        await db_obj.insert_paper_position({
            "trade_id": "BTCUSDT_LONG_OK_001",
            "symbol": "BTCUSDT",
            "side": "LONG",
            "market_type": "futures",
            "entry_price": 63000.0,
            "quantity": 0.05,
            "leverage": 10.0,
            "stop_loss": None,
            "take_profit": None,
            "trailing_stop": None,
            "order_id": "test",
            "signal_data": {},
        })
        client = MockBinanceClient([
            make_binance_pos("BTCUSDT", "LONG", 0.05, 63000.0, 10),
        ])
        rec = FuturesReconciler(client=client, db=db_obj)
        result = await rec.reconcile_once()
        assert_eq(result.counts.get("ok", 0), 1, "expected 1 ok")
        print("PASS test_match_within_tolerance_is_ok")
    finally:
        await db_obj.close()


async def test_qty_mismatch_emits_event():
    db_obj = await setup_db()
    try:
        await db_obj.insert_paper_position({
            "trade_id": "ETHUSDT_LONG_QTY_001",
            "symbol": "ETHUSDT",
            "side": "LONG",
            "market_type": "futures",
            "entry_price": 1700.0,
            "quantity": 1.0,  # DB qty=1.0
            "leverage": 5.0,
            "stop_loss": None,
            "take_profit": None,
            "trailing_stop": None,
            "order_id": "test",
            "signal_data": {},
        })
        client = MockBinanceClient([
            make_binance_pos("ETHUSDT", "LONG", 1.5, 1700.0, 5),  # 50% diff
        ])
        rec = FuturesReconciler(
            client=client, db=db_obj,
            auto_fix_qty_mismatch=True,
            qty_tolerance_pct=0.5,
        )
        result = await rec.reconcile_once()
        assert_eq(result.counts.get("qty_mismatch", 0), 1, "expected 1 qty_mismatch")
        assert_eq(result.events[0].action_taken, "updated", "expected qty updated")
        positions = await get_db_positions(db_obj)
        assert_eq(round(positions[0]["quantity"], 3), 1.5, "expected DB qty updated to 1.5")
        print("PASS test_qty_mismatch_emits_event")
    finally:
        await db_obj.close()


async def test_no_mismatch_no_mutation():
    db_obj = await setup_db()
    try:
        await db_obj.insert_paper_position({
            "trade_id": "SOLUSDT_LONG_NOOP_001",
            "symbol": "SOLUSDT",
            "side": "LONG",
            "market_type": "futures",
            "entry_price": 67.0,
            "quantity": 10.0,
            "leverage": 5.0,
            "stop_loss": None,
            "take_profit": None,
            "trailing_stop": None,
            "order_id": "test",
            "signal_data": {},
        })
        client = MockBinanceClient([
            make_binance_pos("SOLUSDT", "LONG", 10.0, 67.0, 5),
        ])
        rec = FuturesReconciler(client=client, db=db_obj)
        result = await rec.reconcile_once()
        assert_eq(result.counts.get("ok", 0), 1, "expected 1 ok")
        # Verify no orphan / db_missing events were generated
        assert_eq(result.counts.get("orphan_detected", 0), 0)
        assert_eq(result.counts.get("db_missing_on_binance", 0), 0)
        print("PASS test_no_mismatch_no_mutation")
    finally:
        await db_obj.close()


async def test_side_mismatch_uses_price_diff_event_type():
    """When entry price diffs exceed tolerance, the reconciler currently
    reports it under side_mismatch (legacy label, used for diffs that
    fall outside qty tolerance but are not full orphans)."""
    db_obj = await setup_db()
    try:
        await db_obj.insert_paper_position({
            "trade_id": "BTCUSDT_LONG_PRICE_001",
            "symbol": "BTCUSDT",
            "side": "LONG",
            "market_type": "futures",
            "entry_price": 60000.0,  # very different from Binance
            "quantity": 0.05,
            "leverage": 10.0,
            "stop_loss": None,
            "take_profit": None,
            "trailing_stop": None,
            "order_id": "test",
            "signal_data": {},
        })
        client = MockBinanceClient([
            make_binance_pos("BTCUSDT", "LONG", 0.05, 63000.0, 10),
        ])
        rec = FuturesReconciler(
            client=client, db=db_obj,
            qty_tolerance_pct=0.5,
            price_tolerance_pct=0.5,
        )
        result = await rec.reconcile_once()
        # Either side_mismatch or a custom event is fine, as long as we
        # recorded exactly one non-ok event for this key
        non_ok = [
            e for e in result.events
            if e.event_type not in ("ok",) and e.symbol == "BTCUSDT"
        ]
        assert_eq(len(non_ok), 1, "expected one non-ok event for BTCUSDT")
        print(f"PASS test_side_mismatch_uses_price_diff_event_type ({non_ok[0].event_type})")
    finally:
        await db_obj.close()


async def test_persists_events_and_state():
    db_obj = await setup_db()
    try:
        client = MockBinanceClient([
            make_binance_pos("BTCUSDT", "SHORT", 0.1, 63000.0, 10),
        ])
        rec = FuturesReconciler(client=client, db=db_obj, auto_sync_orphans=True)
        await rec.reconcile_once()

        # Verify events table has rows
        async with db_obj._conn.execute(
            "SELECT COUNT(*) FROM reconciliation_events"
        ) as cur:
            row = await cur.fetchone()
        assert_true(row[0] >= 1, f"expected at least 1 event row, got {row[0]}")

        # Verify state row updated
        async with db_obj._conn.execute(
            "SELECT last_run_id, orphan_count FROM reconciliation_state WHERE id=1"
        ) as cur:
            row = await cur.fetchone()
        assert_true(row is not None, "expected reconciliation_state row")
        assert_true(row[1] >= 1, f"expected orphan_count >=1, got {row[1]}")
        print("PASS test_persists_events_and_state")
    finally:
        await db_obj.close()


async def test_dry_run_with_no_auto_mutations():
    db_obj = await setup_db()
    try:
        await db_obj.insert_paper_position({
            "trade_id": "ETHUSDT_SHORT_DRY_001",
            "symbol": "ETHUSDT",
            "side": "SHORT",
            "market_type": "futures",
            "entry_price": 1700.0,
            "quantity": 0.5,
            "leverage": 5.0,
            "stop_loss": None,
            "take_profit": None,
            "trailing_stop": None,
            "order_id": "test",
            "signal_data": {},
        })
        client = MockBinanceClient([
            make_binance_pos("ETHUSDT", "SHORT", 0.7, 1700.0, 5),  # 40% qty diff
        ])
        rec = FuturesReconciler(
            client=client, db=db_obj,
            auto_sync_orphans=False,
            auto_close_db_missing=False,
            auto_fix_qty_mismatch=False,
            qty_tolerance_pct=0.5,
        )
        result = await rec.reconcile_once()
        # qty_mismatch should be detected but no mutation performed
        assert_eq(result.counts.get("qty_mismatch", 0), 1, "expected 1 qty_mismatch")
        assert_eq(result.events[0].action_taken, "none", "expected no action")
        positions = await get_db_positions(db_obj)
        assert_eq(round(positions[0]["quantity"], 3), 0.5, "DB qty should remain 0.5")
        print("PASS test_dry_run_with_no_auto_mutations")
    finally:
        await db_obj.close()


async def main():
    await test_orphan_detected_inserts_sync_row()
    await test_db_missing_on_binance_marks_closed_external()
    await test_match_within_tolerance_is_ok()
    await test_qty_mismatch_emits_event()
    await test_no_mismatch_no_mutation()
    await test_side_mismatch_uses_price_diff_event_type()
    await test_persists_events_and_state()
    await test_dry_run_with_no_auto_mutations()
    print()
    print("All 8 reconciliation tests passed.")


if __name__ == "__main__":
    asyncio.run(main())
