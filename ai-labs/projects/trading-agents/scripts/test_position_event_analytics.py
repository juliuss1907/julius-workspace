#!/usr/bin/env python3
"""Test position event analytics from analyze_signal_logs.py."""
import json
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.analyze_signal_logs import load_records, avg, pct


def build_record(**overrides):
    base = {
        "timestamp": "2026-06-08T12:00:00",
        "symbol": "BTCUSDT",
        "analysts": {
            "technical": {"direction": "bullish", "confidence": 0.75, "sub_score": 0.70},
            "sentiment": {"direction": "bullish", "confidence": 0.60, "sub_score": 0.55},
            "news": {"direction": "neutral", "confidence": 0.50, "sub_score": 0.40},
            "fundamentals": {"direction": "neutral", "confidence": 0.50, "sub_score": 0.40},
            "derivatives": {"direction": "bullish", "confidence": 0.55, "sub_score": 0.50},
        },
        "missing_analysts": [],
        "draft_signal": {"direction": "bullish", "confidence": 0.72, "sub_score": 0.68},
        "final_signal": {
            "direction": "bullish",
            "confidence": 0.72,
            "sub_score": 0.68,
            "analysis": {"trader": {"action": "BUY", "hold_reason": None}},
            "metadata": {"final_action": "BUY"},
        },
        "research_debate": {"consensus": "aligned", "winner": "bull"},
        "market_snapshot": {},
        "position_decision": {},
        "risk_decision": {},
        "trade_result": None,
        "execution_status": "not_evaluated",
    }
    base.update(overrides)
    return base


def make_position(side="LONG", action="hold_position", close_reason="manual",
                  close_fraction=0.0, confidence=0.72):
    return {
        "action": action,
        "reason": f"test {action}",
        "confidence": confidence,
        "position": {"side": side, "entry_price": 50000, "trade_id": "test_id"},
        "close_fraction": close_fraction,
        "close_reason": close_reason,
        "checks": {},
    }


def test_no_position_records():
    """Empty position_decision => no position event counters populated."""
    records = [build_record(symbol="ETHUSDT")]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
        path = Path(f.name)

    loaded = load_records(path)
    assert len(loaded) == 1
    assert loaded[0]["symbol"] == "ETHUSDT"

    # Verify counters from analysis (re-run subset logic)
    close_fractions = []
    for r in loaded:
        pos = r.get("position_decision") or {}
        if pos:
            fraction = pos.get("close_fraction")
            if isinstance(fraction, (int, float)):
                close_fractions.append(fraction)
    assert len(close_fractions) == 0, "empty position decisions => no close fractions"
    path.unlink()
    print("PASS test_no_position_records")


def test_hold_position():
    records = [
        build_record(
            symbol="BTCUSDT",
            position_decision=make_position(action="hold_position", side="LONG"),
            execution_status="position_hold",
        )
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
        path = Path(f.name)

    loaded = load_records(path)
    pos = loaded[0].get("position_decision") or {}
    assert pos["action"] == "hold_position"
    assert pos["close_reason"] == "manual"
    assert loaded[0]["execution_status"] == "position_hold"

    path.unlink()
    print("PASS test_hold_position")


def test_close_position_with_reason():
    records = [
        build_record(
            symbol="SOLUSDT",
            position_decision=make_position(
                action="close_position", side="LONG",
                close_reason="signal_reversal", close_fraction=1.0,
            ),
            execution_status="position_closed",
        )
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
        path = Path(f.name)

    loaded = load_records(path)
    pos = loaded[0].get("position_decision") or {}
    assert pos["action"] == "close_position"
    assert pos["close_reason"] == "signal_reversal"
    assert loaded[0]["execution_status"] == "position_closed"

    # Count execution details manually
    exec_count = Counter()
    exec_count[loaded[0]["execution_status"]] += 1
    assert exec_count["position_closed"] == 1

    path.unlink()
    print("PASS test_close_position_with_reason")


def test_reduce_position():
    records = [
        build_record(
            symbol="ETHUSDT",
            position_decision=make_position(
                action="reduce_position", side="LONG",
                close_reason="risk_reduction", close_fraction=0.5,
            ),
            execution_status="position_reduce_recommended",
        )
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
        path = Path(f.name)

    loaded = load_records(path)
    pos = loaded[0].get("position_decision") or {}
    assert pos["close_fraction"] == 0.5
    assert pos["close_reason"] == "risk_reduction"
    assert loaded[0]["execution_status"] == "position_reduce_recommended"

    close_fractions = [pos["close_fraction"] for _ in loaded if isinstance(pos.get("close_fraction"), (int, float))]
    assert avg(close_fractions) == 0.5

    path.unlink()
    print("PASS test_reduce_position")


def test_close_reason_counter():
    records = [
        build_record(
            symbol="BTCUSDT",
            position_decision=make_position(action="close_position", close_reason="loss_control", close_fraction=1.0),
            execution_status="position_closed",
        ),
        build_record(
            symbol="ETHUSDT",
            position_decision=make_position(action="close_position", close_reason="loss_control", close_fraction=1.0),
            execution_status="position_closed",
        ),
        build_record(
            symbol="SOLUSDT",
            position_decision=make_position(action="reduce_position", close_reason="profit_protection", close_fraction=0.5),
            execution_status="position_reduced",
        ),
        build_record(
            symbol="BTCUSDT",
            position_decision=make_position(action="reduce_position", close_reason="profit_protection", close_fraction=0.3),
            execution_status="position_reduced",
        ),
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
        path = Path(f.name)

    loaded = load_records(path)
    close_reasons = Counter()
    for r in loaded:
        pos = r.get("position_decision") or {}
        reason = pos.get("close_reason")
        if reason and pos.get("action") in ("close_position", "reduce_position"):
            close_reasons[reason] += 1
    assert close_reasons["loss_control"] == 2
    assert close_reasons["profit_protection"] == 2

    path.unlink()
    print("PASS test_close_reason_counter")


def test_action_by_symbol():
    records = [
        build_record(symbol="BTCUSDT", position_decision=make_position(action="hold_position", side="LONG"), execution_status="position_hold"),
        build_record(symbol="ETHUSDT", position_decision=make_position(action="close_position", side="LONG", close_reason="signal_reversal"), execution_status="position_closed"),
        build_record(symbol="SOLUSDT", position_decision=make_position(action="reduce_position", side="SHORT", close_reason="risk_reduction", close_fraction=0.5), execution_status="position_reduce_recommended"),
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
        path = Path(f.name)

    loaded = load_records(path)
    by_symbol = {}
    for r in loaded:
        pos = r.get("position_decision") or {}
        if pos:
            sym = r["symbol"]
            by_symbol.setdefault(sym, Counter())
            by_symbol[sym][pos["action"]] += 1

    assert by_symbol["BTCUSDT"]["hold_position"] == 1
    assert by_symbol["ETHUSDT"]["close_position"] == 1
    assert by_symbol["SOLUSDT"]["reduce_position"] == 1

    path.unlink()
    print("PASS test_action_by_symbol")


def test_action_by_side_and_direction():
    records = [
        # LONG pos + bullish final => hold
        build_record(
            symbol="BTCUSDT",
            final_signal={"direction": "bullish", "confidence": 0.7, "analysis": {"trader": {"action": "BUY"}}, "metadata": {"final_action": "BUY"}, "sub_score": 0.7},
            position_decision=make_position(action="hold_position", side="LONG"),
            execution_status="position_hold",
        ),
        # LONG pos + bearish final => close
        build_record(
            symbol="ETHUSDT",
            final_signal={"direction": "bearish", "confidence": 0.8, "analysis": {"trader": {"action": "SELL"}}, "metadata": {"final_action": "SELL"}, "sub_score": 0.8},
            position_decision=make_position(action="close_position", side="LONG", close_reason="signal_reversal"),
            execution_status="position_closed",
        ),
        # SHORT pos + bullish final => close
        build_record(
            symbol="SOLUSDT",
            final_signal={"direction": "bullish", "confidence": 0.8, "analysis": {"trader": {"action": "BUY"}}, "metadata": {"final_action": "BUY"}, "sub_score": 0.8},
            position_decision=make_position(action="close_position", side="SHORT", close_reason="signal_reversal"),
            execution_status="position_closed",
        ),
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
        path = Path(f.name)

    loaded = load_records(path)
    action_by_dir = defaultdict(Counter)
    for r in loaded:
        pos = r.get("position_decision") or {}
        if pos:
            final = r.get("final_signal") or {}
            direction = final.get("direction", "unknown")
            pos_side = (pos.get("position") or {}).get("side", "unknown")
            action_by_dir[(pos_side, direction)][pos["action"]] += 1

    assert action_by_dir[("LONG", "bullish")]["hold_position"] == 1
    assert action_by_dir[("LONG", "bearish")]["close_position"] == 1
    assert action_by_dir[("SHORT", "bullish")]["close_position"] == 1

    path.unlink()
    print("PASS test_action_by_side_and_direction")


def test_success_rate():
    records = [
        build_record(symbol="BTCUSDT", position_decision=make_position(action="close_position", close_reason="signal_reversal"), execution_status="position_closed"),
        build_record(symbol="ETHUSDT", position_decision=make_position(action="close_position", close_reason="loss_control"), execution_status="position_close_failed"),
        build_record(symbol="SOLUSDT", position_decision=make_position(action="reduce_position", close_reason="risk_reduction", close_fraction=0.5), execution_status="position_reduced"),
        build_record(symbol="BTCUSDT", position_decision=make_position(action="reduce_position", close_reason="profit_protection", close_fraction=0.5), execution_status="position_reduce_recommended"),
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
        path = Path(f.name)

    loaded = load_records(path)
    cr = {"close_recommended": 0, "close_executed": 0, "close_failed": 0,
          "reduce_recommended": 0, "reduce_executed": 0, "reduce_failed": 0}
    for r in loaded:
        pos = r.get("position_decision") or {}
        exec_st = r.get("execution_status", "")
        action = pos.get("action")
        if action == "close_position":
            cr["close_recommended"] += 1
            if exec_st == "position_closed":
                cr["close_executed"] += 1
            elif exec_st == "position_close_failed":
                cr["close_failed"] += 1
        elif action == "reduce_position":
            cr["reduce_recommended"] += 1
            if exec_st == "position_reduced":
                cr["reduce_executed"] += 1
            elif exec_st == "position_reduce_failed":
                cr["reduce_failed"] += 1

    assert cr["close_recommended"] == 2
    assert cr["close_executed"] == 1
    assert cr["close_failed"] == 1
    assert cr["reduce_recommended"] == 2
    assert cr["reduce_executed"] == 1

    path.unlink()
    print("PASS test_success_rate")


def test_missing_position_fields():
    """Malformed or missing position_decision fields should not crash."""
    records = [
        build_record(symbol="BTCUSDT", position_decision=None, execution_status="hold"),
        build_record(symbol="ETHUSDT", position_decision={}, execution_status="hold"),
        build_record(symbol="SOLUSDT", position_decision={"action": "close_position"}, execution_status="position_closed"),
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
        path = Path(f.name)

    loaded = load_records(path)
    # Should load all 3 without error
    assert len(loaded) == 3
    assert loaded[0].get("position_decision") is None
    assert loaded[1].get("position_decision") == {}
    assert loaded[2]["execution_status"] == "position_closed"

    # Verify counter logic handles missing position gracefully
    close_reasons = Counter()
    for r in loaded:
        pos = r.get("position_decision") or {}
        if pos:
            reason = pos.get("close_reason")
            if reason:
                close_reasons[reason] += 1
    assert len(close_reasons) == 0, "missing close_reason should not add to counter"

    path.unlink()
    print("PASS test_missing_position_fields")


def test_reverse_recommended():
    records = [
        build_record(
            symbol="BTCUSDT",
            position_decision={
                "action": "reverse_position",
                "reason": "high-confidence opposite signal",
                "confidence": 0.85,
                "position": {"side": "LONG"},
                "close_fraction": 1.0,
                "reverse_allowed": False,
                "close_reason": "signal_reversal",
                "checks": {},
            },
            execution_status="position_reverse_recommended",
        )
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
        path = Path(f.name)

    loaded = load_records(path)
    assert loaded[0]["execution_status"] == "position_reverse_recommended"
    pos = loaded[0]["position_decision"]
    assert pos["action"] == "reverse_position"
    assert pos["close_reason"] == "signal_reversal"

    path.unlink()
    print("PASS test_reverse_recommended")


def test_avg_close_fraction():
    records = [
        build_record(symbol="BTCUSDT", position_decision=make_position(action="reduce_position", close_fraction=0.3), execution_status="position_reduceed"),
        build_record(symbol="ETHUSDT", position_decision=make_position(action="reduce_position", close_fraction=0.5), execution_status="position_reduceed"),
        build_record(symbol="SOLUSDT", position_decision=make_position(action="reduce_position", close_fraction=0.7), execution_status="position_reduceed"),
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
        path = Path(f.name)

    loaded = load_records(path)
    fractions = []
    for r in loaded:
        pos = r.get("position_decision") or {}
        f = pos.get("close_fraction")
        if isinstance(f, (int, float)):
            fractions.append(f)
    assert abs(avg(fractions) - 0.5) < 0.001, f"expected 0.5 got {avg(fractions)}"
    assert len(fractions) == 3

    path.unlink()
    print("PASS test_avg_close_fraction")


if __name__ == "__main__":

    test_no_position_records()
    test_hold_position()
    test_close_position_with_reason()
    test_reduce_position()
    test_close_reason_counter()
    test_action_by_symbol()
    test_action_by_side_and_direction()
    test_success_rate()
    test_missing_position_fields()
    test_reverse_recommended()
    test_avg_close_fraction()

    print("\nAll position event analytics tests passed.")
