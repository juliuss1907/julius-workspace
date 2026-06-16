#!/usr/bin/env python3
"""Tests for canonical technical indicator config mapping."""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.technical_analyst import TechnicalAnalyst


ERRORS = []


def assert_true(cond, msg=""):
    if not cond:
        ERRORS.append(msg or "assertion failed")


def assert_eq(a, b, msg=""):
    if a != b:
        ERRORS.append(msg or f"expected {b!r}, got {a!r}")


def _run_named(test_fn):
    """Run a test and attribute any ERRORS to it."""
    before = len(ERRORS)
    try:
        test_fn()
    except Exception as e:
        ERRORS.append(f"{test_fn.__name__}: {e}")
        print(f"FAIL {test_fn.__name__}: {e}")
        return
    if len(ERRORS) == before:
        print(f"PASS {test_fn.__name__}")
    else:
        print(f"FAIL {test_fn.__name__}")


def test_default_config_loaded_from_technical_indicators():
    """Without override, TechnicalAnalyst uses technical_indicators defaults."""
    analyst = TechnicalAnalyst()
    assert_eq(analyst.rsi_period, 14)
    assert_eq(analyst.rsi_overbought, 70)
    assert_eq(analyst.rsi_oversold, 30)
    assert_eq(analyst.macd_fast, 12)
    assert_eq(analyst.macd_slow, 26)
    assert_eq(analyst.macd_signal, 9)
    assert_eq(analyst.bb_period, 20)
    assert_eq(analyst.bb_std, 2.0)
    assert_eq(analyst.atr_period, 14)


def test_config_override_wins():
    """Explicit config_override beats canonical defaults."""
    analyst = TechnicalAnalyst(config_override={"rsi_period": 21, "atr_period": 10})
    assert_eq(analyst.rsi_period, 21)
    assert_eq(analyst.atr_period, 10)
    # Others remain canonical defaults
    assert_eq(analyst.macd_fast, 12)
    assert_eq(analyst.bb_period, 20)


def test_legacy_technical_analysis_override_wins_over_canonical():
    """Legacy technical_analysis keys override canonical mapped values."""
    default_config = {
        "technical_indicators": {
            "rsi": {"period": 14, "overbought": 70, "oversold": 30},
            "macd": {"fast": 12, "slow": 26, "signal": 9},
            "bollinger_bands": {"period": 20, "std_dev": 2.0},
            "atr": {"period": 14},
        },
        "technical_analysis": {
            "rsi_period": 9,
            "macd_fast": 8,
            "bb_std": 2.5,
        },
    }
    cfg = TechnicalAnalyst._load_indicator_config(default_config, None)
    assert_eq(cfg["rsi_period"], 9, "legacy rsi_period should win")
    assert_eq(cfg["macd_fast"], 8, "legacy macd_fast should win")
    assert_eq(cfg["bb_std"], 2.5, "legacy bb_std should win")
    # Non-legacy canonical values still present
    assert_eq(cfg["macd_slow"], 26)
    assert_eq(cfg["bb_period"], 20)
    assert_eq(cfg["atr_period"], 14)


def test_explicit_override_wins_over_legacy():
    """config_override wins over both canonical and legacy."""
    default_config = {
        "technical_indicators": {
            "rsi": {"period": 14, "overbought": 70, "oversold": 30},
        },
        "technical_analysis": {
            "rsi_period": 9,
        },
    }
    cfg = TechnicalAnalyst._load_indicator_config(default_config, {"rsi_period": 7})
    assert_eq(cfg["rsi_period"], 7)


def test_donchian_breakout_up():
    """breakout_up_20 only fires when close exceeds previous 20-candle high."""
    analyst = TechnicalAnalyst()
    highs = [60.0] * 21
    lows = [40.0] * 21
    closes = [50.0] * 20 + [61.0]
    # current close = 61 > max(highs[-21:-1]) = 60
    indicators = analyst._calculate_indicators(closes, highs, lows, [1.0] * len(closes))
    assert_eq(indicators["recent_high_20"], 60.0)
    assert_eq(indicators["breakout_up_20"], True)
    assert_eq(indicators["breakout_down_20"], False)


def test_donchian_breakout_down():
    """breakout_down_20 only fires when close is below previous 20-candle low."""
    analyst = TechnicalAnalyst()
    highs = [60.0] * 21
    lows = [40.0] * 21
    closes = [50.0] * 20 + [39.0]
    # current close = 39 < min(lows[-21:-1]) = 40
    indicators = analyst._calculate_indicators(closes, highs, lows, [1.0] * len(closes))
    assert_eq(indicators["recent_low_20"], 40.0)
    assert_eq(indicators["breakout_down_20"], True)
    assert_eq(indicators["breakout_up_20"], False)


def test_donchian_excludes_current_candle():
    """Current candle's high/low must not influence recent high/low."""
    analyst = TechnicalAnalyst()
    highs = [1.0] * 20 + [999.0]
    lows = [1.0] * 20 + [0.1]
    closes = [1.0] * 21
    indicators = analyst._calculate_indicators(closes, highs, lows, [1.0] * 21)
    # recent_high_20 should be 1.0, not 999.0
    assert_eq(indicators["recent_high_20"], 1.0)
    assert_eq(indicators["breakout_up_20"], False)
    # recent_low_20 should be 1.0, not 0.1
    assert_eq(indicators["recent_low_20"], 1.0)
    assert_eq(indicators["breakout_down_20"], False)


def test_donchian_wick_only_does_not_count():
    """A wick-only breakout does not count because trigger uses close."""
    analyst = TechnicalAnalyst()
    highs = list(range(1, 21)) + [25]
    lows = [h - 0.5 for h in highs]
    closes = list(range(1, 21)) + [20]  # close equal to recent high, not above
    indicators = analyst._calculate_indicators(closes, highs, lows, [1.0] * 21)
    assert_eq(indicators["recent_high_20"], 20)
    assert_eq(indicators["breakout_up_20"], False)


def test_technical_state_in_analysis_output():
    """analyze() includes technical_state and market_state in analysis."""
    analyst = TechnicalAnalyst()
    asyncio.run(analyst.initialize())

    ohlcv = []
    for i in range(60):
        ohlcv.append({
            "open": 100.0 + i,
            "high": 102.0 + i,
            "low": 99.0 + i,
            "close": 101.0 + i,
            "volume": 1000.0,
        })

    result = asyncio.run(analyst.analyze("BTCUSDT", {"ohlcv": ohlcv, "timeframe": "1h"}))
    analysis = result.analysis
    assert_true("technical_state" in analysis, "technical_state missing")
    assert_true("market_state" in analysis, "market_state missing")
    ts = analysis["technical_state"]
    ms = analysis["market_state"]
    assert_true("close" in ts, "technical_state missing close")
    assert_true("regime" in ms, "market_state missing regime")
    assert_true("breakout_up_20" in ts, "technical_state missing breakout_up_20")
    assert_true("breakout_down_20" in ts, "technical_state missing breakout_down_20")


def run_tests():
    tests = [
        test_default_config_loaded_from_technical_indicators,
        test_config_override_wins,
        test_legacy_technical_analysis_override_wins_over_canonical,
        test_explicit_override_wins_over_legacy,
        test_donchian_breakout_up,
        test_donchian_breakout_down,
        test_donchian_excludes_current_candle,
        test_donchian_wick_only_does_not_count,
        test_technical_state_in_analysis_output,
    ]
    for t in tests:
        _run_named(t)

    if ERRORS:
        print(f"\n{len(ERRORS)} FAILURES:")
        for err in ERRORS:
            print(f"  - {err}")
        return 1

    print(f"\nAll {len(tests)} tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
