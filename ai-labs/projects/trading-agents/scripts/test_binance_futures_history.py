#!/usr/bin/env python3
"""Smoke tests for the new BinanceFuturesClient history methods.

These hit the Binance Futures testnet and verify basic shape. They are
opt-in: only run when RUN_BINANCE_NETWORK_TESTS=1 is set in env.
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from dataflows.binance_futures_client import BinanceFuturesClient


def assert_eq(a, b, msg=""):
    if a != b:
        raise AssertionError(f"{msg}: expected {b!r}, got {a!r}")


def assert_true(cond, msg=""):
    if not cond:
        raise AssertionError(msg)


async def main():
    if os.getenv("RUN_BINANCE_NETWORK_TESTS") != "1":
        print("SKIP (set RUN_BINANCE_NETWORK_TESTS=1 to enable)")
        return

    if not os.getenv("BINANCE_FUTURES_TESTNET_API_KEY") or not os.getenv("BINANCE_FUTURES_TESTNET_SECRET"):
        print("SKIP (missing API keys)")
        return

    client = BinanceFuturesClient(
        api_key=os.getenv("BINANCE_FUTURES_TESTNET_API_KEY"),
        api_secret=os.getenv("BINANCE_FUTURES_TESTNET_SECRET"),
        environment="testnet",
    )
    try:
        # allOrders: should return a list (possibly empty)
        orders = await client.get_all_orders("BTCUSDT", limit=10)
        assert_true(isinstance(orders, list), f"allOrders should be list, got {type(orders)}")
        for o in orders[:5]:
            assert_true("orderId" in o, "order should have orderId")
            assert_true("symbol" in o, "order should have symbol")
            assert_true("status" in o, "order should have status")
        print(f"PASS allOrders returns list (n={len(orders)})")

        # userTrades: should return a list (possibly empty)
        trades = await client.get_user_trades("BTCUSDT", limit=10)
        assert_true(isinstance(trades, list), f"userTrades should be list, got {type(trades)}")
        for t in trades[:5]:
            assert_true("orderId" in t, "trade should have orderId")
            assert_true("price" in t, "trade should have price")
            assert_true("qty" in t, "trade should have qty")
        print(f"PASS userTrades returns list (n={len(trades)})")

        # allOrders on bogus symbol should return [] (no error)
        bogus = await client.get_all_orders("NOTREALUSDT", limit=5)
        assert_eq(bogus, [], "bogus allOrders should be empty")
        bogus_t = await client.get_user_trades("NOTREALUSDT", limit=5)
        assert_eq(bogus_t, [], "bogus userTrades should be empty")
        print("PASS bogus symbol returns empty list (no error)")
    finally:
        try:
            await client.close()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
