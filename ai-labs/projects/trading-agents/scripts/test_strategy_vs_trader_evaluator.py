#!/usr/bin/env python3
"""Tests for offline Strategy-vs-TraderAgent evaluator."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.evaluate_strategy_vs_trader import (
    classify_alignment,
    evaluate_strategy_vs_trader,
    load_replay_records,
    render_markdown_evaluation,
    safe_rate,
)


ERRORS = []


def assert_true(cond, msg=""):
    if not cond:
        ERRORS.append(msg or "assertion failed")


def assert_eq(a, b, msg=""):
    if a != b:
        ERRORS.append(msg or f"expected {b!r}, got {a!r}")


def assert_close(a, b, msg="", tolerance=1e-9):
    if abs(a - b) > tolerance:
        ERRORS.append(msg or f"expected {b!r}, got {a!r}")


def _record(symbol, trader_action, strategy_signal=None, timeframe="1h"):
    record = {
        "timestamp": f"2026-06-29T08:00:00-{symbol}",
        "symbol": symbol,
        "final_signal": {
            "analysis": {"trader": {"action": trader_action}} if trader_action else {},
            "metadata": {},
        },
        "market_snapshot": {"timeframe": timeframe},
    }
    if strategy_signal is not None:
        record["strategy_signal"] = strategy_signal
    return record


def _strategy_signal(strategy_id, family, action, regime="trend_up", evaluated=None):
    return {
        "strategy_id": strategy_id,
        "family": family,
        "action": action,
        "confidence": 0.7,
        "setup": "fixture setup",
        "trigger": "fixture trigger",
        "invalidation": "fixture invalidation",
        "sizing_hint": "fixture sizing",
        "exit_plan": "fixture exit",
        "no_trade_reason": None,
        "risk_notes": [],
        "attribution": {
            "registry": True,
            "source": "fixture",
            "regime": regime,
            "evaluated": evaluated or [],
        },
    }


def _fixture_records():
    return [
        _record("BTCUSDT", "BUY", _strategy_signal("trend-following", "trend_following", "long", "trend_up")),
        _record("ETHUSDT", "SELL", _strategy_signal("trend-following", "trend_following", "short", "trend_down")),
        _record("SOLUSDT", "HOLD", _strategy_signal("volatility-skip", "volatility_skip", "hold", "trend_down")),
        _record("ADAUSDT", "BUY", _strategy_signal("volatility-skip", "volatility_skip", "skip", "volatile")),
        _record("XRPUSDT", "SELL", _strategy_signal("volatility-skip", "volatility_skip", "skip", "volatile")),
        _record("BNBUSDT", "BUY", _strategy_signal("breakout", "breakout", "short", "ranging")),
        _record("DOGEUSDT", "SELL", _strategy_signal("breakout", "breakout", "long", "ranging")),
        _record("MATICUSDT", "HOLD", None, timeframe="4h"),
    ]


def test_load_replay_records_skips_blank_lines():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "fixture.jsonl"
        rows = _fixture_records()[:2]
        path.write_text(json.dumps(rows[0]) + "\n\n" + json.dumps(rows[1]) + "\n", encoding="utf-8")

        loaded = load_replay_records(path)

        assert_eq(len(loaded), 2)
        assert_eq(loaded[0]["symbol"], "BTCUSDT")
        assert_eq(loaded[1]["symbol"], "ETHUSDT")


def test_load_replay_records_reports_invalid_json_line():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bad.jsonl"
        path.write_text(json.dumps(_fixture_records()[0]) + "\n{bad-json}\n", encoding="utf-8")

        try:
            load_replay_records(path)
            assert_true(False, "expected ValueError for invalid JSON")
        except ValueError as exc:
            assert_true("line 2" in str(exc), f"missing line number in error: {exc}")


def test_classify_alignment():
    assert_eq(classify_alignment("BUY", "long"), "aligned")
    assert_eq(classify_alignment("SELL", "short"), "aligned")
    assert_eq(classify_alignment("HOLD", "hold"), "aligned")
    assert_eq(classify_alignment("BUY", "short"), "conflicted")
    assert_eq(classify_alignment("SELL", "long"), "conflicted")
    assert_eq(classify_alignment("BUY", "skip"), "neutral_or_observational")
    assert_eq(classify_alignment("HOLD", "short"), "neutral_or_observational")
    assert_eq(classify_alignment("", "long"), "missing")
    assert_eq(classify_alignment("BUY", ""), "missing")


def test_safe_rate_handles_zero_denominator():
    assert_close(safe_rate(3, 6), 0.5)
    assert_close(safe_rate(1, 0), 0.0)
    assert_close(safe_rate(0, 0), 0.0)


def test_evaluate_strategy_vs_trader_counts_fixture():
    evaluation = evaluate_strategy_vs_trader(_fixture_records())
    dataset = evaluation["dataset"]
    counts = evaluation["counts"]
    rates = evaluation["rates"]
    gates = evaluation["gate_status"]

    assert_eq(dataset["total_records"], 8)
    assert_eq(dataset["records_with_strategy_signal"], 7)
    assert_eq(dataset["records_missing_strategy_signal"], 1)
    assert_eq(counts["action_alignment"]["aligned"], 3)
    assert_eq(counts["action_alignment"]["conflicted"], 2)
    assert_eq(counts["action_alignment"]["neutral_or_observational"], 2)
    assert_eq(counts["action_alignment"]["missing"], 1)
    assert_eq(counts["directional_strategy_signals"], 4)
    assert_eq(counts["skip_during_trader_action"], 2)
    assert_eq(counts["volatility_skip_direct_blocks"], 2)
    assert_eq(counts["strategy_family"]["volatility_skip"], 3)
    assert_eq(counts["strategy_family"]["trend_following"], 2)
    assert_eq(counts["strategy_family"]["breakout"], 2)
    assert_eq(counts["action_matrix"]["BUY|long"], 1)
    assert_eq(counts["action_matrix"]["SELL|short"], 1)
    assert_eq(counts["action_matrix"]["BUY|skip"], 1)
    assert_eq(counts["action_matrix"]["SELL|skip"], 1)
    assert_eq(counts["action_matrix"]["BUY|short"], 1)
    assert_eq(counts["action_matrix"]["SELL|long"], 1)
    assert_close(rates["attribution_coverage_rate"], 7 / 8)
    assert_close(rates["alignment_rate"], 3 / 8)
    assert_close(rates["conflict_rate"], 2 / 8)
    assert_close(rates["neutral_or_observational_rate"], 2 / 8)
    assert_close(rates["directional_strategy_coverage_rate"], 4 / 8)
    assert_close(rates["skip_during_trader_action_rate"], 2 / 8)
    assert_close(rates["volatility_skip_direct_block_rate"], 2 / 8)
    assert_eq(gates["attribution_ready"]["status"], "warn")
    assert_eq(gates["conflict_review_ready"]["status"], "warn")
    assert_eq(gates["execution_not_authorized"]["status"], "blocked")


def test_render_markdown_evaluation_contains_required_sections():
    evaluation = evaluate_strategy_vs_trader(_fixture_records())
    markdown = render_markdown_evaluation(evaluation)

    for heading in (
        "# Strategy vs TraderAgent Evaluation",
        "## Dataset",
        "## Core Metrics",
        "## Strategy Distribution",
        "## Action Matrix",
        "## Gate Status",
        "## Interpretation",
        "## Next Recommendation",
    ):
        assert_true(heading in markdown, f"missing heading {heading}")
    assert_true("StrategySignal remains observational-only" in markdown)
    assert_true("| Metric | Value |" in markdown)
    assert_true("| Trader Action + Strategy Action | Count |" in markdown)


def test_cli_writes_markdown_and_json_evaluation():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        input_path = tmp_path / "fixture.jsonl"
        md_path = tmp_path / "evaluation.md"
        json_path = tmp_path / "evaluation.json"
        input_path.write_text("\n".join(json.dumps(r) for r in _fixture_records()) + "\n", encoding="utf-8")

        rv = subprocess.run(
            [
                sys.executable,
                str(project_root / "scripts" / "evaluate_strategy_vs_trader.py"),
                "--input",
                str(input_path),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            ],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=15,
        )

        assert_eq(rv.returncode, 0, f"cli failed: stdout={rv.stdout} stderr={rv.stderr}")
        assert_true(md_path.exists(), "markdown output missing")
        assert_true(json_path.exists(), "json output missing")
        assert_true("Strategy vs TraderAgent Evaluation" in md_path.read_text(encoding="utf-8"))
        restored = json.loads(json_path.read_text(encoding="utf-8"))
        assert_eq(restored["dataset"]["total_records"], 8)
        assert_close(restored["rates"]["skip_during_trader_action_rate"], 2 / 8)


def run_tests():
    tests = [
        ("load_replay_records_skips_blank_lines", test_load_replay_records_skips_blank_lines),
        ("load_replay_records_reports_invalid_json_line", test_load_replay_records_reports_invalid_json_line),
        ("classify_alignment", test_classify_alignment),
        ("safe_rate_handles_zero_denominator", test_safe_rate_handles_zero_denominator),
        ("evaluate_strategy_vs_trader_counts_fixture", test_evaluate_strategy_vs_trader_counts_fixture),
        ("render_markdown_evaluation_contains_required_sections", test_render_markdown_evaluation_contains_required_sections),
        ("cli_writes_markdown_and_json_evaluation", test_cli_writes_markdown_and_json_evaluation),
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

    print(f"\nAll {passed} strategy-vs-trader evaluator tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
