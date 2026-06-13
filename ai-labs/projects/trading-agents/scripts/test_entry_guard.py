#!/usr/bin/env python3
"""Tests for EntryGuard v2 DCA-aware behavior."""
import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from state.entry_guard import EntryGuard


def assert_eq(a, b, msg=""):
    if a != b:
        raise AssertionError(f"{msg}: expected {b!r}, got {a!r}")


def assert_true(cond, msg=""):
    if not cond:
        raise AssertionError(msg)


def make_guard(**overrides) -> EntryGuard:
    dca = {
        "enabled": True,
        "max_adds_per_symbol_side": 3,
        "min_price_distance_pct": 0.02,
        "min_confidence": 0.80,
        "max_symbol_portfolio_pct": 0.20,
        "max_leverage": 10,
    }
    dca.update(overrides.pop("dca", {}))
    cfg = {
        "enabled": True,
        "enforce_trade_watchlist": True,
        "block_opposite_side": True,
        "notify_on_block": False,
        "dca": dca,
    }
    cfg.update(overrides)
    return EntryGuard(
        config=cfg,
        trade_watchlist=overrides.get(
            "trade_watchlist", ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        ),
    )


def pos(trade_id: str, symbol: str, side: str, entry: float) -> Dict[str, Any]:
    return {
        "trade_id": trade_id,
        "symbol": symbol,
        "side": side,
        "market_type": "futures",
        "status": "open",
        "entry_price": entry,
        "quantity": 0.1,
    }


def open_source(rows: List[Dict[str, Any]]):
    async def _get(symbol: str):
        return [r for r in rows if r["symbol"] == symbol and r["status"] == "open"]
    return _get


async def test_first_entry_allowed_when_no_open_positions():
    g = make_guard()
    d = await g.check("BTCUSDT", "SHORT", 63000.0, 0.70, open_source([]))
    assert_eq(d.allowed, True)
    assert_eq(d.reason, "first_entry_allowed")
    print("PASS first_entry_allowed_when_no_open_positions")


async def test_block_symbol_not_in_trade_watchlist():
    g = make_guard()
    d = await g.check("HYPEUSDT", "SHORT", 62.0, 0.90, open_source([]))
    assert_eq(d.allowed, False)
    assert_eq(d.reason, "not_in_trade_watchlist")
    print("PASS block_symbol_not_in_trade_watchlist")


async def test_block_opposite_side_open():
    g = make_guard()
    rows = [pos("BTC_LONG_1", "BTCUSDT", "LONG", 63000.0)]
    d = await g.check("BTCUSDT", "SHORT", 62000.0, 0.90, open_source(rows))
    assert_eq(d.allowed, False)
    assert_eq(d.reason, "opposite_side_open")
    print("PASS block_opposite_side_open")


async def test_block_dca_when_price_too_close():
    g = make_guard()
    rows = [pos("BTC_SHORT_1", "BTCUSDT", "SHORT", 63000.0)]
    d = await g.check("BTCUSDT", "SHORT", 62400.0, 0.90, open_source(rows))
    assert_eq(d.allowed, False)
    assert_eq(d.reason, "dca_price_too_close")
    assert_true(d.details["distance_pct"] < 0.02)
    print("PASS block_dca_when_price_too_close")


async def test_block_dca_when_confidence_too_low():
    g = make_guard()
    rows = [pos("BTC_SHORT_1", "BTCUSDT", "SHORT", 63000.0)]
    d = await g.check("BTCUSDT", "SHORT", 61000.0, 0.79, open_source(rows))
    assert_eq(d.allowed, False)
    assert_eq(d.reason, "dca_confidence_too_low")
    print("PASS block_dca_when_confidence_too_low")


async def test_allow_dca_when_far_enough_and_confident():
    g = make_guard()
    rows = [pos("BTC_SHORT_1", "BTCUSDT", "SHORT", 63000.0)]
    d = await g.check("BTCUSDT", "SHORT", 61000.0, 0.82, open_source(rows))
    assert_eq(d.allowed, True)
    assert_eq(d.reason, "dca_allowed")
    assert_true(d.details["distance_pct"] >= 0.02)
    print("PASS allow_dca_when_far_enough_and_confident")


async def test_block_dca_when_symbol_exposure_too_high():
    g = make_guard()
    rows = [pos("BTC_SHORT_1", "BTCUSDT", "SHORT", 63000.0)]
    d = await g.check(
        "BTCUSDT", "SHORT", 61000.0, 0.90, open_source(rows),
        proposed_notional=5000.0, portfolio_value=10000.0,
    )
    assert_eq(d.allowed, False)
    assert_eq(d.reason, "symbol_exposure_cap_exceeded")
    print("PASS block_dca_when_symbol_exposure_too_high")


async def test_block_entry_when_leverage_too_high():
    g = make_guard()
    d = await g.check(
        "BTCUSDT", "SHORT", 63000.0, 0.90, open_source([]), leverage=11,
    )
    assert_eq(d.allowed, False)
    assert_eq(d.reason, "leverage_too_high")
    print("PASS block_entry_when_leverage_too_high")


async def test_block_fourth_dca_add():
    g = make_guard()
    rows = [
        pos("BTC_SHORT_BASE", "BTCUSDT", "SHORT", 63000.0),
        pos("BTC_SHORT_ADD1", "BTCUSDT", "SHORT", 61000.0),
        pos("BTC_SHORT_ADD2", "BTCUSDT", "SHORT", 59000.0),
        pos("BTC_SHORT_ADD3", "BTCUSDT", "SHORT", 57000.0),
    ]
    d = await g.check("BTCUSDT", "SHORT", 55000.0, 0.90, open_source(rows))
    assert_eq(d.allowed, False)
    assert_eq(d.reason, "max_dca_adds_reached")
    print("PASS block_fourth_dca_add")


async def test_dca_disabled_blocks_same_side_add():
    g = make_guard(dca={"enabled": False})
    rows = [pos("BTC_SHORT_1", "BTCUSDT", "SHORT", 63000.0)]
    d = await g.check("BTCUSDT", "SHORT", 61000.0, 0.90, open_source(rows))
    assert_eq(d.allowed, False)
    assert_eq(d.reason, "dca_disabled")
    print("PASS dca_disabled_blocks_same_side_add")


async def test_disabled_guard_allows_everything():
    g = make_guard(enabled=False)
    rows = [pos("BTC_LONG_1", "BTCUSDT", "LONG", 63000.0)]
    d = await g.check("BTCUSDT", "SHORT", 62000.0, 0.10, open_source(rows))
    assert_eq(d.allowed, True)
    assert_eq(d.reason, "entry_guard_disabled")
    print("PASS disabled_guard_allows_everything")


async def main():
    await test_first_entry_allowed_when_no_open_positions()
    await test_block_symbol_not_in_trade_watchlist()
    await test_block_opposite_side_open()
    await test_block_dca_when_price_too_close()
    await test_block_dca_when_confidence_too_low()
    await test_allow_dca_when_far_enough_and_confident()
    await test_block_dca_when_symbol_exposure_too_high()
    await test_block_entry_when_leverage_too_high()
    await test_block_fourth_dca_add()
    await test_dca_disabled_blocks_same_side_add()
    await test_disabled_guard_allows_everything()
    print("\nAll 11 entry guard v2 tests passed.")


if __name__ == "__main__":
    asyncio.run(main())
