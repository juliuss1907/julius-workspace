#!/usr/bin/env python3
"""Tests for OrderManager.close_position position_event notification.

Covers:
  - futures close success -> notify_position_event with FUTURES wording
  - spot close success -> notify_position_event with SPOT wording
  - close failure -> notify_position_event with *_FAILED wording
  - missing notifier -> no exception, returns bool from underlying trader

This test uses a FakeDB stub so it does not touch the real
state/trading.db. It also avoids running on the real Binance account.
"""
import asyncio
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Don't connect to the real DB. We patch the `db` symbol inside the
# order_manager module to a FakeDB below.
import state.database as db_module
import trading.order_manager as om_module
from trading.order_manager import OrderManager
from trading.base_trader import (
    TradeSide, MarketType, CloseReason, ClosedPosition
)
from utils import setup_logging

setup_logging("INFO")


def unique_id() -> str:
    return f"{int(time.time() * 1000)}-{uuid.uuid4().hex[:6]}"


class FakeDB:
    """In-memory stub for the parts of db used by close_position.

    Avoids any real SQLite connection and any real schema.
    """

    def __init__(self, positions: List[Dict[str, Any]]):
        self.positions = list(positions)

    async def get_open_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        return [p for p in self.positions if p.get("status") == "open"]


# Replace the `db` symbol inside order_manager with our fake.
# This is safe because close_position only calls get_open_positions.
_fake_db_holder: Dict[str, FakeDB] = {}


def set_fake_db(db: FakeDB) -> None:
    _fake_db_holder["db"] = db
    om_module.db = db  # patch in module namespace



class MockNotifier:
    """Captures notify_position_event calls for assertions."""
    def __init__(self):
        self.calls: List[Dict[str, Any]] = []

    async def notify_position_event(self, **kwargs) -> bool:
        self.calls.append(kwargs)
        return True


class FakeClosedPosition:
    """Stand-in for ClosedPosition to avoid dataclass equality issues."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @property
    def quantity(self):
        return self.__dict__.get("quantity", 0.0)


class FuturesTraderOK:
    market_type = "futures"

    def __init__(self):
        self.closed_with: List[str] = []

    async def initialize(self):
        return None

    async def close_position(self, trade_id, reason, close_quantity=None):
        self.closed_with.append(trade_id)
        return ClosedPosition(
            trade_id=trade_id,
            symbol="BTCUSDT",
            side=TradeSide.SHORT,
            market_type=MarketType.FUTURES,
            entry_price=63000.0,
            exit_price=63100.0,
            quantity=0.05,
            leverage=10.0,
            pnl=50.0,
            pnl_pct=1.59,
            fees=3.15,
            close_reason=reason,
            opened_at=None,
            closed_at=None,
            duration_seconds=0,
        )


class FuturesTraderFail:
    market_type = "futures"

    async def initialize(self):
        return None

    async def close_position(self, trade_id, reason, close_quantity=None):
        return None


class SpotTraderOK:
    market_type = "spot"

    def __init__(self):
        self.closed_with: List[str] = []

    async def initialize(self):
        return None

    async def close_position(self, trade_id, reason, close_quantity=None):
        self.closed_with.append(trade_id)
        return ClosedPosition(
            trade_id=trade_id,
            symbol="ETHUSDT",
            side=TradeSide.LONG,
            market_type=MarketType.SPOT,
            entry_price=1700.0,
            exit_price=1690.0,
            quantity=0.5,
            leverage=1.0,
            pnl=-5.0,
            pnl_pct=-0.29,
            fees=0.85,
            close_reason=reason,
            opened_at=None,
            closed_at=None,
            duration_seconds=0,
        )


def assert_eq(a, b, msg=""):
    if a != b:
        raise AssertionError(f"{msg}: expected {b!r}, got {a!r}")


def assert_true(cond, msg=""):
    if not cond:
        raise AssertionError(msg)


def make_om_with_traders(futures_trader, spot_trader, notifier, db=None):
    om = OrderManager(notifier=notifier)
    om.futures_trader = futures_trader
    om.spot_trader = spot_trader
    om._initialized = True
    if db is not None:
        set_fake_db(db)
    return om


def make_position_dict(
    trade_id: str,
    symbol: str,
    side: str,
    market_type: str,
    quantity: float = 0.05,
    entry_price: float = 63000.0,
) -> Dict[str, Any]:
    return {
        "trade_id": trade_id,
        "symbol": symbol,
        "side": side,
        "market_type": market_type,
        "entry_price": entry_price,
        "quantity": quantity,
        "leverage": 10.0 if market_type == "futures" else 1.0,
        "stop_loss": None,
        "take_profit": None,
        "trailing_stop": None,
        "order_id": "test",
        "status": "open",
        "signal_data": {},
    }


async def test_futures_close_success_notifies_with_futures_wording():
    notifier = MockNotifier()
    fut = FuturesTraderOK()
    spot = SpotTraderOK()
    tid = f"BTCUSDT_SHORT_OK_{unique_id()}"
    pos = make_position_dict(tid, "BTCUSDT", "SHORT", "futures",
                             quantity=0.05, entry_price=63000.0)
    fake = FakeDB([pos])
    om = make_om_with_traders(fut, spot, notifier, db=fake)

    ok = await om.close_position(tid, reason=CloseReason.MANUAL)
    assert_eq(ok, True, "futures close should succeed")
    assert_eq(len(notifier.calls), 1, "expected 1 notify call")
    call = notifier.calls[0]
    assert_eq(call["market_type"], "futures", "market_type should be futures")
    assert_eq(call["execution_status"], "position_closed", "expected position_closed")
    assert_eq(call["position_side"], "SHORT", "expected position_side=SHORT")
    assert_eq(call["trade_id"], tid)
    assert_eq(call["action"], "close_position")
    print("PASS test_futures_close_success_notifies_with_futures_wording")


async def test_spot_close_success_notifies_with_spot_wording():
    notifier = MockNotifier()
    fut = FuturesTraderOK()
    spot = SpotTraderOK()
    tid = f"ETHUSDT_LONG_OK_{unique_id()}"
    pos = make_position_dict(tid, "ETHUSDT", "LONG", "spot",
                             quantity=0.5, entry_price=1700.0)
    fake = FakeDB([pos])
    om = make_om_with_traders(fut, spot, notifier, db=fake)

    ok = await om.close_position(tid, reason=CloseReason.SL_HIT)
    assert_eq(ok, True, "spot close should succeed")
    assert_eq(len(notifier.calls), 1)
    call = notifier.calls[0]
    assert_eq(call["market_type"], "spot")
    assert_eq(call["execution_status"], "position_closed")
    assert_eq(call["position_side"], "", "spot should not have position_side in notify")
    print("PASS test_spot_close_success_notifies_with_spot_wording")


async def test_futures_close_failure_notifies_with_failed_wording():
    notifier = MockNotifier()
    fut = FuturesTraderFail()
    spot = SpotTraderOK()
    tid = f"BTCUSDT_LONG_FAIL_{unique_id()}"
    pos = make_position_dict(tid, "BTCUSDT", "LONG", "futures",
                             quantity=0.01, entry_price=63000.0)
    fake = FakeDB([pos])
    om = make_om_with_traders(fut, spot, notifier, db=fake)

    ok = await om.close_position(tid, reason=CloseReason.MANUAL)
    assert_eq(ok, False, "futures close should fail")
    assert_eq(len(notifier.calls), 1)
    call = notifier.calls[0]
    assert_eq(call["execution_status"], "position_close_failed")
    assert_eq(call["market_type"], "futures")
    print("PASS test_futures_close_failure_notifies_with_failed_wording")


async def test_close_position_not_found_emits_failed_event():
    notifier = MockNotifier()
    fut = FuturesTraderOK()
    spot = SpotTraderOK()
    fake = FakeDB([])  # no open positions
    om = make_om_with_traders(fut, spot, notifier, db=fake)

    ok = await om.close_position("UNKNOWN_TRADE_999", reason=CloseReason.MANUAL)
    assert_eq(ok, False)
    assert_eq(len(notifier.calls), 1)
    call = notifier.calls[0]
    assert_eq(call["execution_status"], "position_close_failed")
    assert_true("position_not_found" in call["reason"], "expected not-found reason")
    print("PASS test_close_position_not_found_emits_failed_event")


async def test_no_notifier_injected_does_not_raise():
    fut = FuturesTraderOK()
    spot = SpotTraderOK()
    tid = f"BTCUSDT_SHORT_NONOTIF_{unique_id()}"
    pos = make_position_dict(tid, "BTCUSDT", "SHORT", "futures",
                             quantity=0.01, entry_price=63000.0)
    fake = FakeDB([pos])
    om = make_om_with_traders(fut, spot, notifier=None, db=fake)

    ok = await om.close_position(tid, reason=CloseReason.MANUAL)
    assert_eq(ok, True, "futures close should still succeed without notifier")
    print("PASS test_no_notifier_injected_does_not_raise")


async def test_partial_reduce_still_uses_close_position_path():
    notifier = MockNotifier()
    fut = FuturesTraderOK()
    spot = SpotTraderOK()
    tid = f"BTCUSDT_LONG_REDUCE_{unique_id()}"
    pos = make_position_dict(tid, "BTCUSDT", "LONG", "futures",
                             quantity=0.1, entry_price=63000.0)
    fake = FakeDB([pos])
    om = make_om_with_traders(fut, spot, notifier, db=fake)

    ok = await om.close_position(tid, reason=CloseReason.RISK_REDUCTION)
    assert_eq(ok, True)
    assert_eq(len(notifier.calls), 1)
    assert_eq(notifier.calls[0]["execution_status"], "position_closed")
    print("PASS test_partial_reduce_still_uses_close_position_path")


async def main():
    await test_futures_close_success_notifies_with_futures_wording()
    await test_spot_close_success_notifies_with_spot_wording()
    await test_futures_close_failure_notifies_with_failed_wording()
    await test_close_position_not_found_emits_failed_event()
    await test_no_notifier_injected_does_not_raise()
    await test_partial_reduce_still_uses_close_position_path()
    print()
    print("All 6 OrderManager close notification tests passed.")


if __name__ == "__main__":
    asyncio.run(main())
