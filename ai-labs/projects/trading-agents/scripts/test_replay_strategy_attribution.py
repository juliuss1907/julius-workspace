#!/usr/bin/env python3
"""Tests for strategy attribution in scripts/replay_signals.py."""
import asyncio
from datetime import datetime
from pathlib import Path
import sys
from unittest.mock import AsyncMock

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.base_agent import AgentResult, SignalDirection
from scripts.replay_signals import SignalReplay


ERRORS = []


def assert_true(cond, msg=""):
    if not cond:
        ERRORS.append(msg or "assertion failed")


def assert_eq(a, b, msg=""):
    if a != b:
        ERRORS.append(msg or f"expected {b!r}, got {a!r}")


def _agent_result(name="TechnicalAnalyst", action="BUY", extra_analysis=None):
    analysis = extra_analysis or {}
    if name == "TraderAgent":
        analysis = {"trader": {"action": action}, **analysis}
    return AgentResult(
        agent_name=name,
        symbol="BTCUSDT",
        timestamp=datetime.now(),
        direction=SignalDirection.BULLISH,
        sub_score=0.70,
        confidence=0.80,
        analysis=analysis,
        reasoning="fixture",
        metadata={},
    )


def _technical_analysis_with_states():
    return {
        "technical_state": {
            "close": 68000.0,
            "rsi": 58.0,
            "macd_histogram": 120.0,
            "macd_crossing_up": False,
            "macd_crossing_down": False,
            "bb_position": 0.62,
            "atr": 1500.0,
            "ema_20": 67000.0,
            "ema_50": 65000.0,
            "ema_200": 60000.0,
            "volume": 1000.0,
            "obv": 10000.0,
            "obv_prev": 9500.0,
            "recent_high_20": 67500.0,
            "recent_low_20": 62000.0,
            "breakout_up_20": True,
            "breakout_down_20": False,
            "scores": {"momentum": 0.7},
        },
        "market_state": {
            "regime": "trend_up",
            "confidence": 0.75,
            "trend_direction": "up",
            "trend_strength": 0.7,
            "adx": 28.0,
            "bb_width": 0.04,
            "reason": "uptrend regime",
        },
    }


class _FakeRecorder:
    def __init__(self):
        self.calls = []

    def record_signal(self, **kwargs):
        self.calls.append(kwargs)
        return kwargs


async def _run_replay_with_technical(technical_result):
    replay = SignalReplay(symbols=["BTCUSDT"], days=1, window_size=3, step_candles=1)
    replay.technical = type("FakeTechnical", (), {})()
    replay.technical.analyze = AsyncMock(return_value=technical_result)

    replay.trader = type("FakeTrader", (), {})()
    replay.trader.analyze = AsyncMock(return_value=_agent_result("TraderAgent", action="BUY"))

    replay.debate = type("FakeDebate", (), {})()
    replay.debate.debate = AsyncMock(return_value={"consensus": "aligned"})

    replay.recorder = _FakeRecorder()

    ohlcv = [
        {"timestamp": 1, "close": 65000.0},
        {"timestamp": 2, "close": 66000.0},
        {"timestamp": 3, "close": 68000.0},
    ]
    record = await replay.analyze_window("BTCUSDT", ohlcv, 2, "fixture-ts")
    return record, replay.recorder.calls[0]


def test_replay_records_strategy_signal_when_states_exist():
    technical_result = _agent_result(
        "TechnicalAnalyst",
        extra_analysis=_technical_analysis_with_states(),
    )

    record, call = asyncio.run(_run_replay_with_technical(technical_result))

    strategy_signal = call.get("strategy_signal")
    assert_true(isinstance(strategy_signal, dict), "strategy_signal should be passed to recorder")
    assert_true(strategy_signal["action"] in ("long", "short", "hold", "skip"))
    assert_true("evaluated" in strategy_signal["attribution"])
    assert_eq(strategy_signal["attribution"].get("source"), "replay_signals")
    assert_eq(call["final_signal"].analysis["trader"]["action"], "BUY")
    assert_eq(record["strategy_signal"], strategy_signal)


def test_replay_records_skip_strategy_signal_when_states_missing():
    technical_result = _agent_result("TechnicalAnalyst", extra_analysis={})

    record, call = asyncio.run(_run_replay_with_technical(technical_result))

    strategy_signal = call.get("strategy_signal")
    assert_true(isinstance(strategy_signal, dict), "strategy_signal should still be passed")
    assert_eq(strategy_signal["strategy_id"], "registry")
    assert_eq(strategy_signal["action"], "skip")
    assert_true("missing" in strategy_signal["trigger"])
    assert_eq(call["final_signal"].analysis["trader"]["action"], "BUY")
    assert_eq(record["strategy_signal"], strategy_signal)


def run_tests():
    tests = [
        ("replay_records_strategy_signal_when_states_exist", test_replay_records_strategy_signal_when_states_exist),
        ("replay_records_skip_strategy_signal_when_states_missing", test_replay_records_skip_strategy_signal_when_states_missing),
    ]
    all_errors = []
    passed = 0
    for name, fn in tests:
        ERRORS.clear()
        try:
            fn()
            if ERRORS:
                for err in ERRORS:
                    all_errors.append(f"{name}: {err}")
                    print(f"FAIL {name}: {err}")
            else:
                print(f"PASS {name}")
                passed += 1
        except Exception as exc:
            all_errors.append(f"{name}: {exc}")
            print(f"FAIL {name}: {exc}")

    if all_errors:
        print(f"\n{len(all_errors)} FAILURES:")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print(f"\nAll {passed} replay strategy attribution tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_tests())
