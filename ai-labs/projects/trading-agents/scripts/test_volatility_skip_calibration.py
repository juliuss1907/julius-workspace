#!/usr/bin/env python3
"""Tests for replay-only volatility-skip calibration helpers."""
import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.run_volatility_skip_calibration import (  # noqa: E402
    VARIANTS,
    compare_evaluations,
    render_markdown_comparison,
)
from strategies.contracts import MarketState, TechnicalState  # noqa: E402
from strategies.registry import StrategyRegistry  # noqa: E402
from strategies.volatility_skip import VolatilitySkipStrategy  # noqa: E402


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


def _evaluation(total=100, directional=10, skip_action=35, vol_block=57, conflict=0):
    aligned = 25
    neutral = total - aligned - conflict
    return {
        "dataset": {"total_records": total, "records_with_strategy_signal": total, "records_missing_strategy_signal": 0},
        "rates": {
            "attribution_coverage_rate": 1.0,
            "alignment_rate": aligned / total,
            "conflict_rate": conflict / total,
            "neutral_or_observational_rate": neutral / total,
            "directional_strategy_coverage_rate": directional / total,
            "skip_during_trader_action_rate": skip_action / total,
            "volatility_skip_direct_block_rate": vol_block / total,
        },
        "counts": {
            "strategy_id": {"volatility-skip": 90, "trend-following": 8, "breakout": 2},
            "strategy_action": {"skip": vol_block, "hold": total - vol_block - directional, "long": directional // 2, "short": directional - directional // 2},
            "action_matrix": {"BUY|skip": skip_action // 2, "SELL|skip": skip_action - skip_action // 2, "BUY|long": directional // 2, "SELL|short": directional - directional // 2},
        },
        "gate_status": {"execution_not_authorized": {"status": "blocked", "message": "fixture"}},
    }


def test_variants_are_explicit_replay_only_configs():
    assert_true("variant-a" in VARIANTS)
    assert_true("variant-b" in VARIANTS)
    assert_true("variant-c" in VARIANTS)
    assert_true("variant-d" in VARIANTS)
    for label, variant in VARIANTS.items():
        assert_true("strategy_config" in variant, f"missing strategy_config for {label}")
        assert_true("description" in variant, f"missing description for {label}")
        assert_eq(variant["strategy_config"].get("calibration", {}).get("replay_only"), True)


def test_volatility_skip_high_atr_override_is_not_default():
    default = VolatilitySkipStrategy()
    relaxed = VolatilitySkipStrategy({"high_atr_pct": 0.10})
    ts = TechnicalState(close=100.0, atr=9.0)
    ms = MarketState(regime="trend_up", confidence=0.7)

    assert_eq(default.evaluate(ts, ms).action, "skip")
    assert_eq(relaxed.evaluate(ts, ms).action, "hold")


def test_registry_calibration_can_evaluate_volatile_trend_down_short():
    registry = StrategyRegistry(config={
        "regime_strategy_order": {"volatile": ["volatility_skip", "trend_following", "breakout"]},
        "volatility_skip": {"volatile_confidence_floor": 0.95, "high_atr_pct": 0.20},
        "trend_following": {"allow_volatile_trend_down": True},
        "selection": {"min_action_confidence": 0.55},
    })
    ts = TechnicalState(close=95.0, ema_20=98.0, ema_50=100.0, macd_histogram=-1.5, rsi=45.0, atr=5.0)
    ms = MarketState(regime="volatile", confidence=0.75, trend_direction="down", adx=35.0)
    sig = registry.select(ts, ms)

    assert_eq(sig.strategy_id, "trend-following")
    assert_eq(sig.action, "short")
    assert_true(sig.attribution.get("original_regime") == "volatile")


def test_compare_evaluations_calculates_deltas():
    baseline = _evaluation(total=100, directional=10, skip_action=35, vol_block=57)
    variant = _evaluation(total=100, directional=20, skip_action=20, vol_block=40)
    comparison = compare_evaluations(baseline, {"variant-a": variant})
    row = comparison["variants"]["variant-a"]

    assert_close(row["deltas"]["directional_strategy_coverage_rate"], 0.10)
    assert_close(row["deltas"]["skip_during_trader_action_rate"], -0.15)
    assert_close(row["deltas"]["volatility_skip_direct_block_rate"], -0.17)
    assert_eq(row["promising"], True)


def test_render_markdown_comparison_contains_required_sections():
    baseline = _evaluation()
    comparison = compare_evaluations(baseline, {"variant-a": _evaluation(directional=20, skip_action=20, vol_block=40)})
    markdown = render_markdown_comparison(comparison)

    for heading in (
        "# Volatility-Skip Calibration Review",
        "## Baseline",
        "## Variant Comparison",
        "## Acceptance Review",
        "## Recommendation",
    ):
        assert_true(heading in markdown, f"missing heading {heading}")
    assert_true("variant-a" in markdown)
    assert_true("production/runtime thresholds were not changed" in markdown)


def test_cli_help_is_lightweight():
    rv = subprocess.run(
        [sys.executable, str(project_root / "scripts" / "run_volatility_skip_calibration.py"), "--help"],
        capture_output=True,
        text=True,
        cwd=str(project_root),
        timeout=15,
    )
    assert_eq(rv.returncode, 0, f"help failed: {rv.stderr[:300]}")
    assert_true("--variants" in rv.stdout)
    assert_true("--overwrite" in rv.stdout)


def run_tests():
    tests = [
        ("variants_are_explicit_replay_only_configs", test_variants_are_explicit_replay_only_configs),
        ("volatility_skip_high_atr_override_is_not_default", test_volatility_skip_high_atr_override_is_not_default),
        ("registry_calibration_can_evaluate_volatile_trend_down_short", test_registry_calibration_can_evaluate_volatile_trend_down_short),
        ("compare_evaluations_calculates_deltas", test_compare_evaluations_calculates_deltas),
        ("render_markdown_comparison_contains_required_sections", test_render_markdown_comparison_contains_required_sections),
        ("cli_help_is_lightweight", test_cli_help_is_lightweight),
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

    print(f"\nAll {passed} volatility-skip calibration tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_tests())
