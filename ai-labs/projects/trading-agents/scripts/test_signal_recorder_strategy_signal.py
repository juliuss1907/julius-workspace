#!/usr/bin/env python3
"""Tests for SignalRecorder strategy_signal support."""
import json
import tempfile
from pathlib import Path
import sys
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.base_agent import AgentResult, SignalDirection
from state.signal_recorder import SignalRecorder


ERRORS = []


def assert_true(cond, msg=""):
    if not cond:
        ERRORS.append(msg or "assertion failed")


def assert_eq(a, b, msg=""):
    if a != b:
        ERRORS.append(msg or f"expected {b!r}, got {a!r}")


def _agent_result(name="TraderAgent", action="BUY"):
    return AgentResult(
        agent_name=name,
        symbol="BTCUSDT",
        timestamp=datetime.now(),
        direction=SignalDirection.BULLISH,
        sub_score=0.7,
        confidence=0.8,
        analysis={"trader": {"action": action}},
        reasoning="fixture",
        metadata={},
    )


def _strategy_signal():
    return {
        "strategy_id": "trend_following",
        "family": "trend_following",
        "action": "long",
        "confidence": 0.68,
        "setup": "fixture setup",
        "trigger": "fixture trigger",
        "invalidation": "fixture invalidation",
        "sizing_hint": "fixture sizing",
        "exit_plan": "fixture exit",
        "no_trade_reason": None,
        "risk_notes": [],
        "attribution": {"registry": True, "source": "unit_test", "evaluated": []},
    }


def test_record_signal_writes_top_level_strategy_signal():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "signals.jsonl"
        recorder = SignalRecorder(log_path=path)
        final = _agent_result(action="BUY")
        strategy_signal = _strategy_signal()

        record = recorder.record_signal(
            symbol="BTCUSDT",
            analyst_signals={"technical": None},
            draft_signal=final,
            final_signal=final,
            strategy_signal=strategy_signal,
            execution_status="replay_recorded",
        )

        assert_true("strategy_signal" in record)
        assert_eq(record["strategy_signal"]["strategy_id"], "trend_following")
        assert_eq(record["final_signal"]["analysis"]["trader"]["action"], "BUY")

        lines = path.read_text().strip().splitlines()
        assert_eq(len(lines), 1)
        restored = json.loads(lines[0])
        assert_eq(restored["strategy_signal"]["action"], "long")
        assert_eq(restored["execution_status"], "replay_recorded")


def test_record_signal_defaults_strategy_signal_to_empty_dict():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "signals.jsonl"
        recorder = SignalRecorder(log_path=path)
        final = _agent_result(action="HOLD")

        record = recorder.record_signal(
            symbol="BTCUSDT",
            analyst_signals={"technical": None},
            draft_signal=final,
            final_signal=final,
            execution_status="replay_recorded",
        )

        assert_true("strategy_signal" in record)
        assert_eq(record["strategy_signal"], {})


def run_tests():
    tests = [
        ("record_signal_writes_top_level_strategy_signal", test_record_signal_writes_top_level_strategy_signal),
        ("record_signal_defaults_strategy_signal_to_empty_dict", test_record_signal_defaults_strategy_signal_to_empty_dict),
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

    print(f"\nAll {passed} signal recorder strategy tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_tests())
