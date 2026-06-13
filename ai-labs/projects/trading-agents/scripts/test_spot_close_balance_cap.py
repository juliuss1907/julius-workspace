#!/usr/bin/env python3
"""Regression tests for spot close quantity capping against free base balance."""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import state.database as db_module
from trading.base_trader import CloseReason
from trading.spot_demo_trader import SpotDemoTrader


class FakeClient:
    def __init__(self, balances):
        self.balances = balances
        self.orders = []

    async def get_balance(self, asset='USDT'):
        return self.balances.get(asset, 0.0)

    async def place_order(self, symbol, side, order_type, quantity):
        self.orders.append({
            'symbol': symbol,
            'side': side,
            'order_type': order_type,
            'quantity': quantity,
        })
        return {
            'orderId': 123,
            'fills': [{'price': '1680.00'}],
        }

    async def close(self):
        pass


async def test_full_close_caps_to_free_balance():
    position = {
        'trade_id': 'ETHUSDT_LONG_fee_case',
        'symbol': 'ETHUSDT',
        'side': 'LONG',
        'market_type': 'spot',
        'entry_price': 1685.53,
        'quantity': 0.89,
        'opened_at': 1780884139,
    }
    close_calls = []

    original_get_open = db_module.db.get_open_positions
    original_close = db_module.db.close_paper_position

    async def fake_get_open_positions(symbol=None):
        return [position]

    async def fake_close_paper_position(**kwargs):
        close_calls.append(kwargs)

    db_module.db.get_open_positions = fake_get_open_positions
    db_module.db.close_paper_position = fake_close_paper_position

    try:
        trader = SpotDemoTrader()
        trader._initialized = True
        trader.client = FakeClient({'ETH': 0.88911})

        closed = await trader.close_position(position['trade_id'], reason=CloseReason.SIGNAL_REVERSAL)

        assert closed is not None
        assert trader.client.orders[0]['quantity'] == 0.889
        assert trader.client.orders[0]['side'] == 'SELL'
        assert closed.quantity == 0.889
        assert close_calls[0]['trade_id'] == position['trade_id']
        assert close_calls[0]['close_reason'] == CloseReason.SIGNAL_REVERSAL.value
        print('PASS test_full_close_caps_to_free_balance')
    finally:
        db_module.db.get_open_positions = original_get_open
        db_module.db.close_paper_position = original_close


async def test_full_close_rejects_zero_free_balance():
    position = {
        'trade_id': 'ETHUSDT_LONG_zero_balance',
        'symbol': 'ETHUSDT',
        'side': 'LONG',
        'market_type': 'spot',
        'entry_price': 1685.53,
        'quantity': 0.89,
        'opened_at': 1780884139,
    }

    original_get_open = db_module.db.get_open_positions

    async def fake_get_open_positions(symbol=None):
        return [position]

    db_module.db.get_open_positions = fake_get_open_positions

    try:
        trader = SpotDemoTrader()
        trader._initialized = True
        trader.client = FakeClient({'ETH': 0.0})

        closed = await trader.close_position(position['trade_id'], reason=CloseReason.SIGNAL_REVERSAL)

        assert closed is None
        assert trader.client.orders == []
        print('PASS test_full_close_rejects_zero_free_balance')
    finally:
        db_module.db.get_open_positions = original_get_open


async def main():
    await test_full_close_caps_to_free_balance()
    await test_full_close_rejects_zero_free_balance()
    print('\nAll spot close balance cap tests passed')


if __name__ == '__main__':
    asyncio.run(main())
