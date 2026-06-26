#!/usr/bin/env python3
"""Tests for scripts/analyze_symbol_readonly.py thin CLI helpers."""
import runpy
from pathlib import Path
from types import SimpleNamespace
import sys

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from orchestration.contracts import AnalystSignalSummary


ERRORS = []


def assert_true(cond, msg=""):
    if not cond:
        ERRORS.append(msg or "assertion failed")


def assert_eq(a, b, msg=""):
    if a != b:
        ERRORS.append(msg or f"expected {b!r}, got {a!r}")


def _load_helpers():
    return runpy.run_path(
        str(project_root / "scripts" / "analyze_symbol_readonly.py"),
        run_name="readonly_helper_test",
    )


def test_analysis_payload_shape():
    helpers = _load_helpers()
    signal = AnalystSignalSummary(
        direction="bullish",
        score=0.75,
        confidence=0.66,
        reasoning="synthetic",
    )
    bundle = SimpleNamespace(
        final=SimpleNamespace(
            symbol="BTCUSDT",
            timeframe="4h",
            price=68000.0,
            timestamp="2026-06-13T00:00:00",
            analyst_signals={"technical": signal},
            draft_signal=signal,
            final_signal=signal,
            direction="bullish",
            confidence=0.66,
            action="BUY",
            hold_reason=None,
            research_debate={"consensus": "aligned"},
            market_snapshot={"ticker_price": 68000.0},
            risk_notes=[],
            metadata={"mode": "full"},
        )
    )

    payload = helpers["_analysis_payload"](bundle)

    assert_eq(payload["symbol"], "BTCUSDT")
    assert_eq(payload["timeframe"], "4h")
    assert_eq(payload["final_action"], "BUY")
    assert_eq(payload["analysts"]["technical"]["direction"], "bullish")
    assert_eq(payload["draft_signal"]["score"], 0.75)
    assert_true("demo_decision" not in payload)


def test_analysis_payload_preserves_strategy_signal_metadata():
    helpers = _load_helpers()
    signal = AnalystSignalSummary(
        direction="bullish",
        score=0.75,
        confidence=0.66,
        reasoning="synthetic",
    )
    strategy_signal = {
        "strategy_id": "trend_following",
        "family": "trend_following",
        "action": "long",
        "confidence": 0.68,
        "setup": "ema trend alignment",
        "trigger": "close above ema20",
        "invalidation": "close below ema50",
        "sizing_hint": "reduced size until replay validated",
        "exit_plan": "exit on invalidation",
        "no_trade_reason": None,
        "risk_notes": [],
        "attribution": {
            "registry": True,
            "evaluated": [
                {"strategy_id": "volatility_skip", "action": "hold", "confidence": 0.9},
                {"strategy_id": "trend_following", "action": "long", "confidence": 0.68},
            ],
        },
    }
    bundle = SimpleNamespace(
        final=SimpleNamespace(
            symbol="BTCUSDT",
            timeframe="4h",
            price=68000.0,
            timestamp="2026-06-13T00:00:00",
            analyst_signals={"technical": signal},
            draft_signal=signal,
            final_signal=signal,
            direction="bullish",
            confidence=0.66,
            action="BUY",
            hold_reason=None,
            research_debate={"consensus": "aligned"},
            market_snapshot={"ticker_price": 68000.0},
            risk_notes=[],
            metadata={"mode": "full", "strategy_signal": strategy_signal},
        )
    )

    payload = helpers["_analysis_payload"](bundle)

    restored_signal = payload["metadata"].get("strategy_signal")
    assert_true(isinstance(restored_signal, dict), "strategy_signal should be preserved")
    assert_eq(restored_signal["strategy_id"], "trend_following")
    assert_eq(restored_signal["action"], "long")
    assert_eq(payload["final_action"], "BUY", "readonly payload must keep FinalAnalysis action")


def test_parser_exposes_demo_flag_without_runtime_imports():
    helpers = _load_helpers()
    parser = helpers["_build_parser"]()
    args = parser.parse_args(["ETHUSDT", "--timeframe", "1d", "--include-demo-decision"])

    assert_eq(args.symbol, "ETHUSDT")
    assert_eq(args.timeframe, "1d")
    assert_true(args.include_demo_decision)


def run_tests():
    tests = [
        ("analysis_payload_shape", test_analysis_payload_shape),
        ("analysis_payload_preserves_strategy_signal_metadata", test_analysis_payload_preserves_strategy_signal_metadata),
        ("parser_exposes_demo_flag_without_runtime_imports", test_parser_exposes_demo_flag_without_runtime_imports),
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

    print(f"\nAll {passed} readonly analyzer tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_tests())
