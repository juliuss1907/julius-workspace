#!/usr/bin/env python3
"""Test OrderManager.close_position_group closes every open leg."""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import trading.order_manager as om_module
from state.database import Database
from trading.base_trader import CloseReason, ClosedPosition, MarketType, TradeSide
from trading.order_manager import OrderManager


TEST_DB = project_root / "state" / "test_position_group_close.db"


class FakeFuturesTrader:
    async def initialize(self):
        return None

    async def close_position(self, trade_id, reason=CloseReason.MANUAL, close_quantity=None):
        await om_module.db.close_paper_position(
            trade_id=trade_id,
            close_price=61000.0,
            pnl=200.0,
            pnl_pct=3.0,
            close_reason=reason.value,
            fees=1.0,
        )
        return ClosedPosition(
            trade_id=trade_id,
            symbol="BTCUSDT",
            side=TradeSide.SHORT,
            market_type=MarketType.FUTURES,
            entry_price=63000.0,
            exit_price=61000.0,
            quantity=0.01,
            leverage=10.0,
            pnl=200.0,
            pnl_pct=3.0,
            fees=1.0,
            close_reason=reason,
            opened_at=None,
            closed_at=None,
            duration_seconds=0,
        )

    async def close(self):
        return None


class FakeSpotTrader:
    async def initialize(self): return None
    async def close(self): return None


async def insert_leg(db, trade_id, group_id, dca_index):
    await db.insert_paper_position({
        "trade_id": trade_id,
        "symbol": "BTCUSDT",
        "side": "SHORT",
        "market_type": "futures",
        "entry_price": 63000.0 - dca_index * 1000,
        "quantity": 0.01,
        "leverage": 10.0,
        "stop_loss": None,
        "take_profit": None,
        "trailing_stop": None,
        "order_id": "test",
        "signal_data": {},
        "position_group_id": group_id,
        "entry_kind": "base" if dca_index == 0 else "dca",
        "dca_index": dca_index,
    })


async def main():
    if TEST_DB.exists():
        TEST_DB.unlink()
    test_db = Database(str(TEST_DB))
    await test_db.connect()
    om_module.db = test_db
    try:
        group_id = "BTCUSDT_SHORT_GROUP_TEST"
        await insert_leg(test_db, "BTC_SHORT_BASE_TEST", group_id, 0)
        await insert_leg(test_db, "BTC_SHORT_DCA1_TEST", group_id, 1)
        await insert_leg(test_db, "BTC_SHORT_DCA2_TEST", group_id, 2)

        om = OrderManager(notifier=None)
        om.futures_trader = FakeFuturesTrader()
        om.spot_trader = FakeSpotTrader()
        om._initialized = True
        ok = await om.close_position_group(group_id, reason=CloseReason.MANUAL)
        assert ok is True, "group close should succeed"

        async with test_db._conn.execute(
            "SELECT COUNT(*) FROM paper_positions WHERE position_group_id=? AND status='open'",
            (group_id,),
        ) as cur:
            row = await cur.fetchone()
        assert row[0] == 0, f"expected 0 open legs, got {row[0]}"
        print("PASS position_group_close_closes_all_legs")
        print("All position group close tests passed.")
    finally:
        await test_db.close()
        if TEST_DB.exists():
            TEST_DB.unlink()


if __name__ == "__main__":
    asyncio.run(main())
