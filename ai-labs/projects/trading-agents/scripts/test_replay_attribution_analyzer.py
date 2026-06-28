#!/usr/bin/env python3
"""Tests for offline replay attribution analyzer."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.analyze_replay_attribution import (
    classify_alignment,
    load_replay_records,
    render_markdown_summary,
    summarize_strategy_attribution,
)


ERRORS = []


def assert_true(cond, msg=""):
    if not cond:
        ERRORS.append(msg or "assertion failed")


def assert_eq(a, b, msg=""):
    if a != b:
        ERRORS.append(msg or f"expected {b!r}, got {a!r}")


def _record(symbol, trader_action, strategy_signal=None, timeframe="1h"):
    record = {
        "timestamp": f"2026-06-26T15:00:00-{symbol}",
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
        _record(
            "BTCUSDT",
            "BUY",
            _strategy_signal("trend-following", "trend_following", "long", "trend_up"),
        ),
        _record(
            "ETHUSDT",
            "BUY",
            _strategy_signal("volatility-skip", "volatility_skip", "skip", "volatile"),
        ),
        _record(
            "SOLUSDT",
            "SELL",
            _strategy_signal("breakout", "breakout", "long", "ranging"),
        ),
        _record("HYPEUSDT", "BUY", None),
        _record(
            "BTCUSDT",
            "HOLD",
            _strategy_signal(
                "registry",
                "registry",
                "hold",
                "trend_up",
                evaluated=[{"strategy_id": "volatility-skip", "action": "skip", "confidence": 0.8}],
            ),
            timeframe="4h",
        ),
        _record("DOGEUSDT", None, _strategy_signal("breakout", "breakout", "short", "ranging")),
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
    assert_eq(classify_alignment("HOLD", "long"), "neutral_or_observational")
    assert_eq(classify_alignment("", "long"), "missing")
    assert_eq(classify_alignment("BUY", ""), "missing")


def test_summarize_strategy_attribution_counts_fixture():
    summary = summarize_strategy_attribution(_fixture_records(), max_examples=3)

    assert_eq(summary["total_records"], 6)
    assert_eq(summary["records_with_strategy_signal"], 5)
    assert_eq(summary["records_missing_strategy_signal"], 1)
    assert_eq(summary["by_symbol"]["BTCUSDT"], 2)
    assert_eq(summary["by_timeframe"]["1h"], 5)
    assert_eq(summary["by_timeframe"]["4h"], 1)
    assert_eq(summary["by_strategy_id"]["trend-following"], 1)
    assert_eq(summary["by_strategy_id"]["volatility-skip"], 1)
    assert_eq(summary["by_strategy_action"]["long"], 2)
    assert_eq(summary["by_strategy_action"]["skip"], 1)
    assert_eq(summary["by_strategy_family"]["breakout"], 2)
    assert_eq(summary["by_market_regime"]["trend_up"], 2)
    assert_eq(summary["by_market_regime"]["ranging"], 2)
    assert_eq(summary["volatility_skip_blocks"], 2)
    assert_eq(summary["alignment_matrix"]["BUY|long"], 1)
    assert_eq(summary["alignment_matrix"]["SELL|long"], 1)
    assert_eq(summary["action_alignment"]["aligned"], 2)
    assert_eq(summary["action_alignment"]["conflicted"], 1)
    assert_eq(summary["action_alignment"]["neutral_or_observational"], 1)
    assert_eq(summary["action_alignment"]["missing"], 2)
    assert_eq(len(summary["examples"]["conflicts"]), 1)
    assert_eq(len(summary["examples"]["volatility_skips"]), 2)
    assert_eq(len(summary["examples"]["missing_strategy_signal"]), 1)


def test_render_markdown_summary_contains_required_sections():
    summary = summarize_strategy_attribution(_fixture_records(), max_examples=3)
    markdown = render_markdown_summary(summary)

    for heading in (
        "# Replay Attribution Summary",
        "## Overview",
        "## Strategy Decisions",
        "## Symbols and Timeframes",
        "## Market Regimes",
        "## Trader vs Strategy Comparison",
        "## Volatility Skip Blocks",
        "## Examples for Review",
        "## Notes",
    ):
        assert_true(heading in markdown, f"missing heading {heading}")
    assert_true("StrategySignal is observational-only" in markdown)
    assert_true("| Strategy ID | Count |" in markdown)
    assert_true("| Trader Action + Strategy Action | Count |" in markdown)


def test_cli_writes_flat_markdown_and_json_summary():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        input_path = tmp_path / "fixture.jsonl"
        md_path = tmp_path / "summary.md"
        json_path = tmp_path / "summary.json"
        input_path.write_text("\n".join(json.dumps(r) for r in _fixture_records()) + "\n", encoding="utf-8")

        rv = subprocess.run(
            [
                sys.executable,
                str(project_root / "scripts" / "analyze_replay_attribution.py"),
                "--input",
                str(input_path),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
                "--max-examples",
                "2",
            ],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=15,
        )

        assert_eq(rv.returncode, 0, f"cli failed: stdout={rv.stdout} stderr={rv.stderr}")
        assert_true(md_path.exists(), "markdown output missing")
        assert_true(json_path.exists(), "json output missing")
        assert_true("Replay Attribution Summary" in md_path.read_text(encoding="utf-8"))
        restored = json.loads(json_path.read_text(encoding="utf-8"))
        assert_eq(restored["total_records"], 6)
        assert_eq(restored["volatility_skip_blocks"], 2)


def run_tests():
    tests = [
        ("load_replay_records_skips_blank_lines", test_load_replay_records_skips_blank_lines),
        ("load_replay_records_reports_invalid_json_line", test_load_replay_records_reports_invalid_json_line),
        ("classify_alignment", test_classify_alignment),
        ("summarize_strategy_attribution_counts_fixture", test_summarize_strategy_attribution_counts_fixture),
        ("render_markdown_summary_contains_required_sections", test_render_markdown_summary_contains_required_sections),
        ("cli_writes_flat_markdown_and_json_summary", test_cli_writes_flat_markdown_and_json_summary),
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

    print(f"\nAll {passed} replay attribution analyzer tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_tests())
