#!/usr/bin/env python3
"""Tests for the orchestration contracts (FinalAnalysis, AnalystSignalSummary)."""
import json
import sys
from dataclasses import asdict
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from orchestration import FinalAnalysis, AnalystSignalSummary


ERRORS = []


def assert_true(cond, msg=""):
    if not cond:
        msg = msg or "assertion failed"
        ERRORS.append(msg)


def assert_eq(a, b, msg=""):
    if a != b:
        msg = msg or f"expected {b!r}, got {a!r}"
        ERRORS.append(msg)


def make_final_analysis(**overrides) -> FinalAnalysis:
    defaults = {
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "price": 68000.0,
        "timestamp": "2026-06-11T12:00:00",
        "analyst_signals": {
            "technical": AnalystSignalSummary(
                direction="bullish", score=0.72, confidence=0.65,
                reasoning="RSI bullish, MACD crossover",
            ),
            "news": AnalystSignalSummary(
                direction="neutral", score=0.50, confidence=0.40,
                reasoning="no significant news",
            ),
        },
        "draft_signal": AnalystSignalSummary(
            direction="bullish", score=0.68, confidence=0.60,
            reasoning="draft bullish",
        ),
        "research_debate": {
            "consensus": "aligned",
            "confidence_adjustment": 0.05,
            "winner": "bull",
        },
        "final_signal": AnalystSignalSummary(
            direction="bullish", score=0.70, confidence=0.65,
            reasoning="final bullish",
        ),
        "market_snapshot": {"timeframe": "1h", "ohlcv_candles": 200},
        "direction": "bullish",
        "confidence": 0.65,
        "action": "BUY",
        "hold_reason": None,
        "risk_notes": [],
        "metadata": {"mode": "full"},
    }
    defaults.update(overrides)
    return FinalAnalysis(**defaults)


def test_analyst_signal_summary_fields():
    sig = AnalystSignalSummary(
        direction="bullish", score=0.75, confidence=0.65,
        reasoning="strong uptrend",
    )
    assert_eq(sig.direction, "bullish", "direction mismatch")
    assert_eq(sig.score, 0.75, "score mismatch")
    assert_eq(sig.confidence, 0.65, "confidence mismatch")
    assert_eq(sig.reasoning, "strong uptrend", "reasoning mismatch")
    assert_true(isinstance(sig.score, float), "score should be float")
    assert_true(isinstance(sig.confidence, float), "confidence should be float")

    d = asdict(sig)
    assert_eq(d["direction"], "bullish")
    assert_eq(d["score"], 0.75)
    assert_eq(d["confidence"], 0.65)


def test_final_analysis_fields_present():
    fa = make_final_analysis()
    assert_true(fa.symbol == "BTCUSDT", "symbol missing")
    assert_true(fa.timeframe == "1h", "timeframe missing")
    assert_true(fa.price == 68000.0, "price missing")
    assert_true(fa.timestamp is not None, "timestamp missing")
    assert_true(len(fa.analyst_signals) >= 1, "analyst_signals empty")
    assert_true(fa.draft_signal is not None, "draft_signal missing")
    assert_true(fa.final_signal is not None, "final_signal missing")
    assert_true(fa.market_snapshot is not None, "market_snapshot missing")
    assert_true(fa.direction is not None, "direction missing")
    assert_true(fa.action is not None, "action missing")


def test_final_analysis_direction_valid():
    for direction in ("bullish", "bearish", "neutral"):
        fa = make_final_analysis(direction=direction)
        assert_eq(fa.direction, direction, f"direction should allow {direction}")


def test_final_analysis_action_valid():
    for action in ("BUY", "SELL", "HOLD"):
        fa = make_final_analysis(action=action)
        assert_eq(fa.action, action, f"action should allow {action}")


def test_final_analysis_hold_reason_optional():
    fa_with = make_final_analysis(hold_reason="conflicting signals")
    assert_eq(fa_with.hold_reason, "conflicting signals")

    fa_without = make_final_analysis(hold_reason=None)
    assert_true(fa_without.hold_reason is None, "hold_reason should accept None")


def test_final_analysis_serialization():
    fa = make_final_analysis()
    d = fa.to_dict()

    assert_true(isinstance(d, dict), "to_dict must return dict")
    assert_eq(d["symbol"], "BTCUSDT")
    assert_eq(d["direction"], "bullish")
    assert_eq(d["action"], "BUY")
    assert_eq(d["confidence"], 0.65)

    json_str = json.dumps(d)
    assert_true(isinstance(json_str, str), "should serialize to JSON string")

    restored = json.loads(json_str)
    assert_eq(restored["symbol"], "BTCUSDT")
    assert_eq(restored["direction"], "bullish")
    assert_eq(restored["confidence"], 0.65)
    assert_true(isinstance(restored["analyst_signals"], dict))
    assert_eq(
        restored["analyst_signals"]["technical"]["direction"],
        "bullish",
    )


def test_final_analysis_risk_notes_default():
    fa = FinalAnalysis(
        symbol="ETHUSDT",
        timeframe="1h",
        price=None,
        timestamp="2026-01-01T00:00:00",
        analyst_signals={},
        draft_signal=AnalystSignalSummary(
            direction="neutral", score=0.5, confidence=0.3, reasoning="n/a",
        ),
        research_debate=None,
        final_signal=AnalystSignalSummary(
            direction="neutral", score=0.5, confidence=0.3, reasoning="n/a",
        ),
        market_snapshot={},
        direction="neutral",
        confidence=0.3,
        action="HOLD",
    )
    assert_eq(fa.risk_notes, [], "risk_notes default should be empty list")
    assert_eq(fa.hold_reason, None, "hold_reason default should be None")
    assert_eq(fa.metadata, {}, "metadata default should be empty dict")


def test_final_analysis_research_debate_optional():
    fa_with = make_final_analysis(research_debate={"consensus": "aligned"})
    assert_true(fa_with.research_debate is not None)

    fa_without = make_final_analysis(research_debate=None)
    assert_true(fa_without.research_debate is None)


def run_tests():
    tests = [
        ("analyst_signal_summary_fields", test_analyst_signal_summary_fields),
        ("final_analysis_fields_present", test_final_analysis_fields_present),
        ("final_analysis_direction_valid", test_final_analysis_direction_valid),
        ("final_analysis_action_valid", test_final_analysis_action_valid),
        ("final_analysis_hold_reason_optional", test_final_analysis_hold_reason_optional),
        ("final_analysis_serialization", test_final_analysis_serialization),
        ("final_analysis_risk_notes_default", test_final_analysis_risk_notes_default),
        ("final_analysis_research_debate_optional", test_final_analysis_research_debate_optional),
    ]

    for name, fn in tests:
        try:
            fn()
            print(f"PASS {name}")
        except Exception as e:
            ERRORS.append(f"{name}: {e}")
            print(f"FAIL {name}: {e}")

    if ERRORS:
        print(f"\n{len(ERRORS)} FAILURES:")
        for err in ERRORS:
            print(f"  - {err}")
        return 1

    print(f"\nAll {len(tests)} tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
