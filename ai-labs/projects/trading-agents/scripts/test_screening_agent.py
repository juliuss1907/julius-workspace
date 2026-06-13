#!/usr/bin/env python3
"""Test Phase 8A: Screening Agent."""
import json
import math
import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.screening_agent import (
    ScreeningAgent,
    CandidateMetrics,
    score_liquidity,
    score_volatility,
    score_technical,
    score_risk,
    rating_from_score,
    recommended_action_for,
    DEFAULT_WEIGHTS,
    DEFAULT_LIQUIDITY_THRESHOLDS,
    DEFAULT_VOLATILITY,
    DEFAULT_RATINGS,
    _ema,
    _rsi,
    _atr_pct,
    _compute_quote_volume_24h,
)


def _make_ohlcv(n: int = 120, base_price: float = 100.0, trend: float = 0.0005,
                volatility: float = 0.01, seed: int = 0) -> list:
    """Build a synthetic OHLCV series for tests."""
    candles = []
    import random
    rng = random.Random(seed)
    price = base_price
    for i in range(n):
        t = i - n
        drift = (i - n / 2) * trend * base_price
        noise = rng.gauss(0, volatility * base_price)
        close = base_price + drift + noise
        high = close + abs(rng.gauss(0, volatility * base_price * 0.5))
        low = close - abs(rng.gauss(0, volatility * base_price * 0.5))
        open_p = close + rng.gauss(0, volatility * base_price * 0.3)
        candles.append({
            "timestamp": int(1_700_000_000) + t * 3600,
            "open": open_p,
            "high": high,
            "low": low,
            "close": close,
            "volume": 1000.0,
            "quote_volume": 1000.0 * close,
            "trades": 100,
        })
    return candles


# ---------------------------------------------------------------------------
# Indicator tests
# ---------------------------------------------------------------------------

def test_ema_basic():
    values = [float(i) for i in range(1, 51)]
    ema = _ema(values, 20)
    assert ema is not None
    assert 30 < ema < 60
    print("PASS test_ema_basic")


def test_ema_too_few():
    assert _ema([1.0, 2.0, 3.0], 20) is None
    print("PASS test_ema_too_few")


def test_rsi_neutral():
    closes = [100.0] * 30
    rsi = _rsi(closes, 14)
    assert rsi is None or rsi == 50.0 or rsi == 100.0
    print("PASS test_rsi_neutral")


def test_rsi_short():
    assert _rsi([100.0, 101.0], 14) is None
    print("PASS test_rsi_short")


def test_atr_pct_flat():
    candles = [{"open": 100, "high": 100, "low": 100, "close": 100} for _ in range(20)]
    atr = _atr_pct(candles, 14)
    assert atr is not None
    assert atr == 0.0
    print("PASS test_atr_pct_flat")


def test_atr_pct_volatile():
    candles = []
    for i in range(20):
        candles.append({
            "open": 100 + i,
            "high": 105 + i,
            "low": 95 + i,
            "close": 100 + i,
        })
    atr = _atr_pct(candles, 14)
    assert atr is not None
    assert atr > 0.05
    print("PASS test_atr_pct_volatile")


def test_compute_quote_volume_24h_from_quote_volume():
    ohlcv = [{"close": 100, "quote_volume": 5_000_000}]
    assert _compute_quote_volume_24h(ohlcv) == 5_000_000
    print("PASS test_compute_quote_volume_24h_from_quote_volume")


def test_compute_quote_volume_24h_from_volume():
    ohlcv = [{"close": 50, "volume": 100_000}]
    assert _compute_quote_volume_24h(ohlcv) == 5_000_000
    print("PASS test_compute_quote_volume_24h_from_volume")


def test_compute_quote_volume_24h_empty():
    assert _compute_quote_volume_24h([]) is None
    print("PASS test_compute_quote_volume_24h_empty")


# ---------------------------------------------------------------------------
# Component scoring tests
# ---------------------------------------------------------------------------

def test_score_liquidity_excellent():
    assert score_liquidity(150_000_000, DEFAULT_LIQUIDITY_THRESHOLDS) == 100.0
    print("PASS test_score_liquidity_excellent")


def test_score_liquidity_good():
    assert score_liquidity(70_000_000, DEFAULT_LIQUIDITY_THRESHOLDS) == 80.0
    print("PASS test_score_liquidity_good")


def test_score_liquidity_fair():
    assert score_liquidity(20_000_000, DEFAULT_LIQUIDITY_THRESHOLDS) == 60.0
    print("PASS test_score_liquidity_fair")


def test_score_liquidity_low():
    assert score_liquidity(2_000_000, DEFAULT_LIQUIDITY_THRESHOLDS) == 40.0
    print("PASS test_score_liquidity_low")


def test_score_liquidity_very_low():
    assert score_liquidity(500_000, DEFAULT_LIQUIDITY_THRESHOLDS) == 20.0
    print("PASS test_score_liquidity_very_low")


def test_score_liquidity_none():
    assert score_liquidity(None, DEFAULT_LIQUIDITY_THRESHOLDS) == 0.0
    print("PASS test_score_liquidity_none")


def test_score_volatility_ideal():
    assert score_volatility(0.025, DEFAULT_VOLATILITY) == 100.0
    print("PASS test_score_volatility_ideal")


def test_score_volatility_blocked():
    assert score_volatility(0.15, DEFAULT_VOLATILITY) == 5.0
    print("PASS test_score_volatility_blocked")


def test_score_volatility_too_quiet():
    score = score_volatility(0.005, DEFAULT_VOLATILITY)
    assert 0 < score < 100
    print("PASS test_score_volatility_too_quiet")


def test_score_volatility_none():
    assert score_volatility(None, DEFAULT_VOLATILITY) == 0.0
    print("PASS test_score_volatility_none")


def test_score_technical_uptend():
    ohlcv = _make_ohlcv(n=120, trend=0.001, volatility=0.005, seed=1)
    score = score_technical(ohlcv)
    assert score > 50
    print("PASS test_score_technical_uptend")


def test_score_technical_downtrend():
    ohlcv = _make_ohlcv(n=120, trend=-0.001, volatility=0.005, seed=2)
    score = score_technical(ohlcv)
    assert score < 50
    print("PASS test_score_technical_downtrend")


def test_score_technical_too_few():
    assert score_technical(_make_ohlcv(n=10)) == 0.0
    print("PASS test_score_technical_too_few")


def test_score_risk_no_warnings():
    assert score_risk([]) == 100.0
    print("PASS test_score_risk_no_warnings")


def test_score_risk_some_warnings():
    assert score_risk(["a", "b"]) == 50.0
    assert score_risk(["a", "b", "c", "d"]) == 0.0
    print("PASS test_score_risk_some_warnings")


def test_rating_from_score():
    assert rating_from_score(80, DEFAULT_RATINGS) == "strong_candidate"
    assert rating_from_score(70, DEFAULT_RATINGS) == "candidate"
    assert rating_from_score(50, DEFAULT_RATINGS) == "watch_only"
    assert rating_from_score(30, DEFAULT_RATINGS) == "avoid"
    print("PASS test_rating_from_score")


def test_recommended_action_for():
    assert recommended_action_for("strong_candidate") == "consider_watchlist"
    assert recommended_action_for("candidate") == "consider_watchlist"
    assert recommended_action_for("watch_only") == "monitor_only"
    assert recommended_action_for("avoid") == "skip"
    print("PASS test_recommended_action_for")


# ---------------------------------------------------------------------------
# ScreeningAgent.score_candidate
# ---------------------------------------------------------------------------

def test_score_candidate_basic():
    agent = ScreeningAgent({})
    ohlcv = _make_ohlcv(n=120, trend=0.0005, volatility=0.015, seed=10)
    ticker = {"quote_volume": 80_000_000}
    cand = agent.score_candidate("BTCUSDT", ohlcv=ohlcv, ticker=ticker, news_score=60)
    assert cand.symbol == "BTCUSDT"
    assert 0 <= cand.score <= 100
    assert cand.liquidity_score == 80.0
    assert cand.news_score == 60.0
    assert cand.rating in ("strong_candidate", "candidate", "watch_only", "avoid")
    assert cand.recommended_action in ("consider_watchlist", "monitor_only", "skip")
    print("PASS test_score_candidate_basic")


def test_score_candidate_insufficient_data():
    agent = ScreeningAgent({})
    ohlcv = _make_ohlcv(n=10)
    cand = agent.score_candidate("TESTUSDT", ohlcv=ohlcv)
    assert cand.score == 0.0
    assert cand.rating == "avoid"
    assert cand.recommended_action == "skip"
    assert any("insufficient_data" in w for w in cand.warnings)
    print("PASS test_score_candidate_insufficient_data")


def test_score_candidate_no_ohlcv():
    agent = ScreeningAgent({})
    cand = agent.score_candidate("TESTUSDT", ohlcv=None)
    assert cand.score == 0.0
    assert cand.rating == "avoid"
    assert any("insufficient_data" in w for w in cand.warnings)
    print("PASS test_score_candidate_no_ohlcv")


def test_score_candidate_low_liquidity_warning():
    agent = ScreeningAgent({})
    ohlcv = _make_ohlcv(n=120, volatility=0.015, seed=3)
    ticker = {"quote_volume": 500_000}
    cand = agent.score_candidate("LOWUSDT", ohlcv=ohlcv, ticker=ticker)
    assert any("low_liquidity" in w for w in cand.warnings)
    print("PASS test_score_candidate_low_liquidity_warning")


def test_score_candidate_extreme_volatility_warning():
    agent = ScreeningAgent({})
    candles = []
    for i in range(120):
        candles.append({
            "open": 100, "high": 130, "low": 70, "close": 100,
            "volume": 1000, "quote_volume": 100000, "trades": 100,
            "timestamp": int(1_700_000_000) + i * 3600,
        })
    cand = agent.score_candidate("VOLUSDT", ohlcv=candles)
    assert any("extreme_volatility" in w for w in cand.warnings)
    print("PASS test_score_candidate_extreme_volatility_warning")


def test_score_candidate_open_position_warning():
    agent = ScreeningAgent({})
    ohlcv = _make_ohlcv(n=120, seed=4)
    cand = agent.score_candidate(
        "OPENUSDT", ohlcv=ohlcv,
        open_positions=[{"symbol": "OPENUSDT", "side": "LONG"}],
    )
    assert any("open_position" in w for w in cand.warnings)
    print("PASS test_score_candidate_open_position_warning")


# ---------------------------------------------------------------------------
# ScreeningAgent.screen / rank
# ---------------------------------------------------------------------------

def test_screen_ranks_by_score():
    agent = ScreeningAgent({})
    symbols = ["AAAUSDT", "BBBUSDT", "CCCUSDT", "DDDUSDT"]
    ohlcv_map = {
        "AAAUSDT": _make_ohlcv(n=120, trend=0.001, volatility=0.02, seed=10),
        "BBBUSDT": _make_ohlcv(n=120, trend=0.0, volatility=0.02, seed=20),
        "CCCUSDT": _make_ohlcv(n=120, trend=-0.001, volatility=0.02, seed=30),
        "DDDUSDT": _make_ohlcv(n=120, trend=0.0008, volatility=0.02, seed=40),
    }
    ticker_map = {
        "AAAUSDT": {"quote_volume": 80_000_000},
        "BBBUSDT": {"quote_volume": 80_000_000},
        "CCCUSDT": {"quote_volume": 80_000_000},
        "DDDUSDT": {"quote_volume": 80_000_000},
    }
    news_scores = {
        "AAAUSDT": 70, "BBBUSDT": 50, "CCCUSDT": 30, "DDDUSDT": 65,
    }
    candidates = agent.screen(symbols, ohlcv_map, ticker_map, news_scores)
    assert len(candidates) == 4
    assert candidates[0].rank == 1
    for i in range(len(candidates) - 1):
        assert candidates[i].score >= candidates[i + 1].score
    print("PASS test_screen_ranks_by_score")


def test_screen_with_missing_symbol():
    agent = ScreeningAgent({})
    symbols = ["MISSUSDT", "GOTUSDT"]
    ohlcv_map = {
        "MISSUSDT": [],
        "GOTUSDT": _make_ohlcv(n=120, trend=0.0005, volatility=0.015, seed=5),
    }
    ticker_map = {
        "GOTUSDT": {"quote_volume": 30_000_000},
    }
    candidates = agent.screen(symbols, ohlcv_map, ticker_map)
    assert len(candidates) == 2
    miss = next(c for c in candidates if c.symbol == "MISSUSDT")
    got = next(c for c in candidates if c.symbol == "GOTUSDT")
    assert miss.score < got.score
    assert miss.rating == "avoid"
    print("PASS test_screen_with_missing_symbol")


def test_screen_ratings_distinct():
    agent = ScreeningAgent({})
    symbols = ["HIGHUSDT", "MIDUSDT", "LOWUSDT"]
    ohlcv_map = {
        "HIGHUSDT": _make_ohlcv(n=120, trend=0.002, volatility=0.015, seed=100),
        "MIDUSDT": _make_ohlcv(n=120, trend=0.0, volatility=0.02, seed=200),
        "LOWUSDT": _make_ohlcv(n=120, trend=-0.002, volatility=0.04, seed=300),
    }
    ticker_map = {
        s: {"quote_volume": 80_000_000} for s in symbols
    }
    candidates = agent.screen(symbols, ohlcv_map, ticker_map)
    assert candidates[0].score > candidates[-1].score
    assert candidates[0].rank == 1
    print("PASS test_screen_ratings_distinct")


# ---------------------------------------------------------------------------
# Config override
# ---------------------------------------------------------------------------

def test_config_override_weights():
    config = {"weights": {"liquidity": 0.5, "volatility": 0.1, "technical": 0.2, "news": 0.1, "risk": 0.1}}
    agent = ScreeningAgent(config)
    assert agent.weights["liquidity"] == 0.5
    ohlcv = _make_ohlcv(n=120, trend=0.0005, volatility=0.015, seed=99)
    cand = agent.score_candidate("XUSDT", ohlcv=ohlcv, ticker={"quote_volume": 200_000_000})
    assert cand.liquidity_score == 100.0
    print("PASS test_config_override_weights")


def test_config_override_rating_thresholds():
    config = {"rating_thresholds": {"strong_candidate": 50, "candidate": 30, "watch_only": 10}}
    agent = ScreeningAgent(config)
    ohlcv = _make_ohlcv(n=120, trend=0.0005, volatility=0.015, seed=11)
    cand = agent.score_candidate("XUSDT", ohlcv=ohlcv, ticker={"quote_volume": 80_000_000})
    if cand.score >= 50:
        assert cand.rating == "strong_candidate"
    print("PASS test_config_override_rating_thresholds")


# ---------------------------------------------------------------------------
# to_dict / serialization
# ---------------------------------------------------------------------------

def test_candidate_to_dict():
    c = CandidateMetrics(symbol="BTCUSDT", score=75.0, rating="strong_candidate")
    d = c.to_dict()
    assert d["symbol"] == "BTCUSDT"
    assert d["score"] == 75.0
    assert d["rating"] == "strong_candidate"
    print("PASS test_candidate_to_dict")


# ---------------------------------------------------------------------------
# CLI smoke
# ---------------------------------------------------------------------------

def test_run_screening_offline():
    """Run the script with --offline --dry-run against the 6-symbol universe."""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts/run_screening.py"),
         "--symbols", "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "HYPEUSDT", "ZECUSDT",
         "--offline", "--dry-run"],
        capture_output=True, text=True, timeout=60,
        cwd=str(project_root),
    )
    assert result.returncode == 0, f"exit {result.returncode}\n{result.stdout}\n{result.stderr}"
    combined = result.stdout + result.stderr
    assert "[OFFLINE]" in combined
    assert "BTCUSDT" in combined
    assert "HYPEUSDT" in combined
    assert "ZECUSDT" in combined
    print("PASS test_run_screening_offline")


def test_run_screening_offline_writes_files():
    """Run the script with --offline, verify JSON+MD outputs exist."""
    import subprocess
    with tempfile.TemporaryDirectory() as tmp:
        out_json = Path(tmp) / "out.json"
        out_md = Path(tmp) / "out.md"
        result = subprocess.run(
            [sys.executable, str(project_root / "scripts/run_screening.py"),
             "--symbols", "BTCUSDT", "ETHUSDT", "SOLUSDT",
             "--offline",
             "--output-json", str(out_json),
             "--output-md", str(out_md)],
            capture_output=True, text=True, timeout=60,
            cwd=str(project_root),
        )
        assert result.returncode == 0, f"exit {result.returncode}\n{result.stdout}\n{result.stderr}"
        assert out_json.exists()
        assert out_md.exists()
        data = json.loads(out_json.read_text(encoding="utf-8"))
        assert "candidates" in data
        assert len(data["candidates"]) == 3
        for c in data["candidates"]:
            assert "symbol" in c
            assert "score" in c
            assert "rating" in c
        md = out_md.read_text(encoding="utf-8")
        assert "# Screening Report" in md
        assert "Distribution" in md
    print("PASS test_run_screening_offline_writes_files")


# ---------------------------------------------------------------------------
# No-mutation guards
# ---------------------------------------------------------------------------

def test_screen_does_not_mutate_config():
    config = {
        "weights": {"liquidity": 0.25, "volatility": 0.20, "technical": 0.25, "news": 0.15, "risk": 0.15}
    }
    snapshot = json.dumps(config, sort_keys=True)
    agent = ScreeningAgent(config)
    ohlcv_map = {"XUSDT": _make_ohlcv(n=120, seed=42)}
    agent.screen(["XUSDT"], ohlcv_map, {"XUSDT": {"quote_volume": 80_000_000}})
    assert json.dumps(config, sort_keys=True) == snapshot
    print("PASS test_screen_does_not_mutate_config")


def run_all():
    tests = [
        test_ema_basic, test_ema_too_few,
        test_rsi_neutral, test_rsi_short,
        test_atr_pct_flat, test_atr_pct_volatile,
        test_compute_quote_volume_24h_from_quote_volume,
        test_compute_quote_volume_24h_from_volume,
        test_compute_quote_volume_24h_empty,
        test_score_liquidity_excellent, test_score_liquidity_good,
        test_score_liquidity_fair, test_score_liquidity_low,
        test_score_liquidity_very_low, test_score_liquidity_none,
        test_score_volatility_ideal, test_score_volatility_blocked,
        test_score_volatility_too_quiet, test_score_volatility_none,
        test_score_technical_uptend, test_score_technical_downtrend,
        test_score_technical_too_few,
        test_score_risk_no_warnings, test_score_risk_some_warnings,
        test_rating_from_score, test_recommended_action_for,
        test_score_candidate_basic,
        test_score_candidate_insufficient_data, test_score_candidate_no_ohlcv,
        test_score_candidate_low_liquidity_warning,
        test_score_candidate_extreme_volatility_warning,
        test_score_candidate_open_position_warning,
        test_screen_ranks_by_score, test_screen_with_missing_symbol,
        test_screen_ratings_distinct,
        test_config_override_weights, test_config_override_rating_thresholds,
        test_candidate_to_dict,
        test_run_screening_offline, test_run_screening_offline_writes_files,
        test_screen_does_not_mutate_config,
    ]

    failures = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            print(f"FAIL {t.__name__}: {e}")
            failures += 1
        except Exception as e:
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
            failures += 1

    if failures:
        print(f"\n{failures} test(s) failed")
        sys.exit(1)
    print(f"\nAll {len(tests)} tests passed")


if __name__ == "__main__":
    run_all()
