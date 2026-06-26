#!/usr/bin/env python3
"""Runner-level tests for orchestration/analysis_runner.py.

Pre-seeds sys.modules with mock placeholder modules so that
analysis_runner.py's own imports (agents.news_analyst → vaderSentiment,
agents.technical_analyst → numpy, dataflows → ccxt, etc.) never
trigger real heavy-dependency loading.  The test then patches the
orchestration module with real mock factories to control behaviour.
"""
import sys
from unittest.mock import MagicMock, AsyncMock, patch

# ── pre-seed heavy modules BEFORE anything touches orchestration ──────────
_HEAVY_MODULES = {
    "agents.technical_analyst",
    "agents.news_analyst",
    "agents.sentiment_analyst",
    "agents.fundamentals_analyst",
    "agents.derivatives_analyst",
    "agents.trader_agent",
    "agents.research_debate",
    "agents.bull_researcher",
    "agents.bear_researcher",
    "dataflows",
    "dataflows.data_manager",
    "dataflows.binance_client",
    "dataflows.binance_futures_client",
    "dataflows.binance_derivatives_client",
    "dataflows.hyperliquid_client",
    "dataflows.lighter_client",
    "dataflows.coingecko_client",
    "dataflows.fear_greed_client",
    "dataflows.polymarket_client",
    "dataflows.reddit_client",
    "dataflows.telegram_scraper",
    "dataflows.rss_fetcher",
    "dataflows.retry",
    "dataflows.parallel_fetcher",
    "dataflows.cache",
    "dataflows.base",
    "state",
    "state.database",
    "state.portfolio_context",
    "state.signal_recorder",
    "state.entry_guard",
    "state.runtime_health",
    "state.reconciliation",
    "trading",
    "trading.base_trader",
    "trading.spot_demo_trader",
    "trading.futures_testnet_trader",
    "trading.order_manager",
    "trading.position_monitor",
    "trading.trade_notifier",
    "telegram_bot",
    "telegram_bot.bot",
}

for mod_name in _HEAVY_MODULES:
    if mod_name not in sys.modules:
        mock_mod = MagicMock()
        sys.modules[mod_name] = mock_mod

# Also pre-seed utils submodules that analysis_runner reaches
if "utils" not in sys.modules:
    sys.modules["utils"] = MagicMock()
if "utils.logging_config" not in sys.modules:
    sys.modules["utils.logging_config"] = MagicMock()
if "utils.config_loader" not in sys.modules:
    sys.modules["utils.config_loader"] = MagicMock()
if "utils.watchlist" not in sys.modules:
    sys.modules["utils.watchlist"] = MagicMock()
if "utils.process_lock" not in sys.modules:
    sys.modules["utils.process_lock"] = MagicMock()
if "utils.log_rotation" not in sys.modules:
    sys.modules["utils.log_rotation"] = MagicMock()

# ── now safe to import from the project ───────────────────────────────────
import asyncio
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from orchestration.contracts import FinalAnalysis, AnalystSignalSummary
from agents.base_agent import AgentResult, SignalDirection


ERRORS = []


def assert_true(cond, msg=""):
    if not cond:
        msg = msg or "assertion failed"
        ERRORS.append(msg)


def assert_eq(a, b, msg=""):
    if a != b:
        msg = msg or f"expected {b!r}, got {a!r}"
        ERRORS.append(msg)


# ---------------------------------------------------------------------------
# Fake factories
# ---------------------------------------------------------------------------


def _fake_result(name="TechnicalAnalyst", direction=SignalDirection.BULLISH,
                 score=0.72, confidence=0.65, reasoning="ok",
                 extra_analysis=None):
    analysis = {"indicators": {"atr": 1500}}
    if extra_analysis:
        analysis.update(extra_analysis)
    return AgentResult(
        agent_name=name,
        symbol="BTCUSDT",
        timestamp=datetime.now(),
        direction=direction,
        sub_score=score,
        confidence=confidence,
        analysis=analysis,
        reasoning=reasoning,
        metadata={"timeframe": "1h"},
    )


def _fake_technical_result_with_states():
    return _fake_result(
        name="TechnicalAnalyst",
        direction=SignalDirection.BULLISH,
        score=0.72,
        confidence=0.65,
        reasoning="technical state available",
        extra_analysis={
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
        },
    )


def _singleton_mock(analyze_result=None, analyze_side_effect=None):
    mock = MagicMock()
    mock.initialize = AsyncMock()
    if analyze_side_effect:
        mock.analyze = AsyncMock(side_effect=analyze_side_effect)
    else:
        mock.analyze = AsyncMock(return_value=analyze_result)
    mock.close = AsyncMock()
    return (lambda: mock), mock


def _singleton_trader(draft_result, final_result):
    mock = MagicMock()
    mock.initialize = AsyncMock()
    calls = []

    async def analyze(symbol, data):
        calls.append(data)
        return draft_result if len(calls) == 1 else final_result

    mock.analyze = analyze
    mock.close = AsyncMock()
    return (lambda: mock), mock


def _singleton_debate(debate_dict):
    mock = MagicMock()
    mock.initialize = AsyncMock()
    mock.debate = AsyncMock(return_value=debate_dict)
    mock.close = AsyncMock()
    return (lambda: mock), mock


def _mock_dm(ohlcv=None, ticker=None, fundamentals=None):
    m = MagicMock()
    m.initialize = AsyncMock()
    m.fetch_and_store_ohlcv = AsyncMock(
        return_value=ohlcv or [{"close": 68000, "high": 68200, "low": 67800, "volume": 1000, "open": 67900}]
    )
    m.get_ticker = AsyncMock(return_value=ticker or {"price": 68000.0})
    m.get_fundamentals = AsyncMock(return_value=fundamentals or {})
    m.close = AsyncMock()
    return m


# ---------------------------------------------------------------------------
# Test helper — import analyze_symbol only inside the fully-patched context
# ---------------------------------------------------------------------------


async def _run_patched(dm_mock, tech, news, sent, fund, deriv, trader, debate,
                       symbol="BTCUSDT"):
    """Patch module-level names, then import analyze_symbol lazily."""
    with patch("orchestration.analysis_runner.dm", dm_mock):
        with patch("orchestration.analysis_runner.TechnicalAnalyst", tech[0]):
            with patch("orchestration.analysis_runner.NewsAnalyst", news[0]):
                with patch("orchestration.analysis_runner.SentimentAnalyst", sent[0]):
                    with patch("orchestration.analysis_runner.FundamentalsAnalyst", fund[0]):
                        with patch("orchestration.analysis_runner.DerivativesAnalyst", deriv[0]):
                            with patch("orchestration.analysis_runner.TraderAgent", trader[0]):
                                with patch("orchestration.analysis_runner.ResearchDebate", debate[0]):
                                    from orchestration.analysis_runner import analyze_symbol
                                    return await analyze_symbol(symbol)


# ---------------------------------------------------------------------------
# Default fixtures
# ---------------------------------------------------------------------------


def _default_analyst_pair(score=0.72, direction=SignalDirection.BULLISH):
    return _singleton_mock(analyze_result=_fake_result(score=score, direction=direction))


def _default_trader_pair(draft_score=0.68, final_score=0.70):
    return _singleton_trader(
        draft_result=_fake_result(score=draft_score, confidence=0.60, name="TraderAgent"),
        final_result=_fake_result(
            score=final_score, confidence=0.65, name="TraderAgent",
            extra_analysis={"trader": {"action": "BUY"}},
        ),
    )


def _default_debate_pair():
    return _singleton_debate({"consensus": "aligned", "confidence_adjustment": 0.05,
                              "winner": "bull", "margin": 0.10})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_returns_normalized_final_analysis_shape():
    tech = _default_analyst_pair()
    news = _default_analyst_pair(0.55, SignalDirection.NEUTRAL)
    sent = _default_analyst_pair(0.60, SignalDirection.NEUTRAL)
    fund = _default_analyst_pair(0.50, SignalDirection.NEUTRAL)
    deriv = _default_analyst_pair(0.58, SignalDirection.BULLISH)
    trader = _default_trader_pair()
    debate = _default_debate_pair()

    bundle = asyncio.run(_run_patched(
        dm_mock=_mock_dm(),
        tech=tech, news=news, sent=sent, fund=fund, deriv=deriv,
        trader=trader, debate=debate,
    ))

    fa = bundle.final
    assert isinstance(fa, FinalAnalysis)
    assert_eq(fa.symbol, "BTCUSDT")
    assert_eq(fa.timeframe, "1h")
    assert_eq(fa.price, 68000.0)
    assert_true(fa.timestamp is not None)
    assert_eq(fa.direction, "bullish")
    assert_eq(fa.action, "BUY")

    assert isinstance(fa.analyst_signals, dict)
    assert_eq(len(fa.analyst_signals), 5)
    for key in ("technical", "news", "sentiment", "fundamentals", "derivatives"):
        assert key in fa.analyst_signals
        sig = fa.analyst_signals[key]
        assert isinstance(sig, AnalystSignalSummary)

    assert isinstance(fa.draft_signal, AnalystSignalSummary)
    assert isinstance(fa.final_signal, AnalystSignalSummary)
    assert isinstance(fa.market_snapshot, dict)
    assert isinstance(fa.to_dict(), dict)
    assert_true(0 <= fa.confidence <= 1.0)

    assert isinstance(bundle.raw_signals, dict)
    assert_eq(len(bundle.raw_signals), 5)
    assert isinstance(bundle.raw_draft, AgentResult)
    assert isinstance(bundle.raw_final, AgentResult)


def test_optional_analyst_failure_degrades_to_na():
    tech = _default_analyst_pair()
    fund = _default_analyst_pair(0.50, SignalDirection.NEUTRAL)
    deriv = _default_analyst_pair(0.58, SignalDirection.BULLISH)
    trader = _default_trader_pair()
    debate = _default_debate_pair()

    news_mock = MagicMock()
    news_mock.initialize = AsyncMock()
    news_mock.analyze = AsyncMock(side_effect=ValueError("news unavailable"))
    news_mock.close = AsyncMock()
    news = (lambda: news_mock), news_mock

    sent_mock = MagicMock()
    sent_mock.initialize = AsyncMock()
    sent_mock.analyze = AsyncMock(return_value=None)
    sent_mock.close = AsyncMock()
    sent = (lambda: sent_mock), sent_mock

    bundle = asyncio.run(_run_patched(
        dm_mock=_mock_dm(),
        tech=tech, news=news, sent=sent, fund=fund, deriv=deriv,
        trader=trader, debate=debate,
    ))

    fa = bundle.final

    news_sig = fa.analyst_signals["news"]
    assert_eq(news_sig.direction, "N/A")
    assert_eq(news_sig.score, 0.0)
    assert_eq(news_sig.confidence, 0.0)

    sent_sig = fa.analyst_signals["sentiment"]
    assert_eq(sent_sig.direction, "N/A")
    assert_eq(sent_sig.score, 0.0)
    assert_eq(sent_sig.confidence, 0.0)

    tech_sig = fa.analyst_signals["technical"]
    assert_eq(tech_sig.direction, "bullish")


def test_technical_analyst_raises_runtime_error():
    tech_mock = MagicMock()
    tech_mock.initialize = AsyncMock()
    tech_mock.analyze = AsyncMock(side_effect=ConnectionError("binance unreachable"))
    tech_mock.close = AsyncMock()
    tech = (lambda: tech_mock), tech_mock

    news = _default_analyst_pair(0.5, SignalDirection.NEUTRAL)
    sent = _default_analyst_pair(0.5, SignalDirection.NEUTRAL)
    fund = _default_analyst_pair(0.5, SignalDirection.NEUTRAL)
    deriv = _default_analyst_pair(0.5, SignalDirection.NEUTRAL)
    trader = _default_trader_pair()
    debate = _default_debate_pair()

    try:
        asyncio.run(_run_patched(
            dm_mock=_mock_dm(),
            tech=tech, news=news, sent=sent, fund=fund, deriv=deriv,
            trader=trader, debate=debate,
        ))
        assert_true(False, "should have raised RuntimeError")
    except RuntimeError as e:
        assert_true("TechnicalAnalyst failed" in str(e))
        assert isinstance(e.__cause__, ConnectionError)
        assert_true("binance unreachable" in str(e.__cause__))


def test_technical_analyst_returns_none_raises_runtime_error():
    tech = _singleton_mock(analyze_result=None)
    news = _default_analyst_pair(0.5, SignalDirection.NEUTRAL)
    sent = _default_analyst_pair(0.5, SignalDirection.NEUTRAL)
    fund = _default_analyst_pair(0.5, SignalDirection.NEUTRAL)
    deriv = _default_analyst_pair(0.5, SignalDirection.NEUTRAL)
    trader = _default_trader_pair()
    debate = _default_debate_pair()

    try:
        asyncio.run(_run_patched(
            dm_mock=_mock_dm(),
            tech=tech, news=news, sent=sent, fund=fund, deriv=deriv,
            trader=trader, debate=debate,
        ))
        assert_true(False, "should have raised RuntimeError")
    except RuntimeError as e:
        assert_true("returned no result" in str(e))
        assert_true(e.__cause__ is None)


def test_confidence_within_range():
    tech = _default_analyst_pair(0.85, SignalDirection.BULLISH)
    news = _default_analyst_pair(0.70, SignalDirection.BULLISH)
    sent = _default_analyst_pair(0.65, SignalDirection.BULLISH)
    fund = _default_analyst_pair(0.55, SignalDirection.BULLISH)
    deriv = _default_analyst_pair(0.75, SignalDirection.BULLISH)
    trader = _default_trader_pair(draft_score=0.80, final_score=0.82)
    debate = _default_debate_pair()

    bundle = asyncio.run(_run_patched(
        dm_mock=_mock_dm(),
        tech=tech, news=news, sent=sent, fund=fund, deriv=deriv,
        trader=trader, debate=debate,
    ))

    assert_true(0.0 <= bundle.final.confidence <= 1.0)
    assert_true(0.0 <= bundle.final.final_signal.confidence <= 1.0)
    assert_true(0.0 <= bundle.final.final_signal.score <= 1.0)


def test_market_snapshot_has_required_keys():
    tech = _default_analyst_pair()
    news = _default_analyst_pair(0.5, SignalDirection.NEUTRAL)
    sent = _default_analyst_pair(0.5, SignalDirection.NEUTRAL)
    fund = _default_analyst_pair(0.5, SignalDirection.NEUTRAL)
    deriv = _default_analyst_pair(0.5, SignalDirection.NEUTRAL)
    trader = _default_trader_pair()
    debate = _default_debate_pair()

    bundle = asyncio.run(_run_patched(
        dm_mock=_mock_dm(),
        tech=tech, news=news, sent=sent, fund=fund, deriv=deriv,
        trader=trader, debate=debate,
    ))

    ms = bundle.final.market_snapshot
    for key in ("timeframe", "ohlcv_candles", "last_close", "ticker_price", "atr"):
        assert key in ms, f"missing key {key!r} in market_snapshot"


def test_strategy_signal_serialized_when_technical_states_exist():
    tech = _singleton_mock(analyze_result=_fake_technical_result_with_states())
    news = _default_analyst_pair(0.55, SignalDirection.NEUTRAL)
    sent = _default_analyst_pair(0.60, SignalDirection.NEUTRAL)
    fund = _default_analyst_pair(0.50, SignalDirection.NEUTRAL)
    deriv = _default_analyst_pair(0.58, SignalDirection.BULLISH)
    trader = _default_trader_pair()
    debate = _default_debate_pair()

    bundle = asyncio.run(_run_patched(
        dm_mock=_mock_dm(),
        tech=tech, news=news, sent=sent, fund=fund, deriv=deriv,
        trader=trader, debate=debate,
    ))

    strategy_signal = bundle.final.metadata.get("strategy_signal")

    assert_true(isinstance(strategy_signal, dict), "strategy_signal should be serialized dict")
    assert_true(strategy_signal["action"] in ("long", "short", "hold", "skip"))
    assert_true(strategy_signal["strategy_id"] in ("volatility-skip", "trend-following", "breakout", "registry"))
    assert_true("evaluated" in strategy_signal["attribution"])
    assert_eq(bundle.final.action, "BUY", "existing FinalAnalysis.action semantics must remain unchanged")


def test_strategy_signal_degrades_when_states_missing():
    tech = _default_analyst_pair()
    news = _default_analyst_pair(0.55, SignalDirection.NEUTRAL)
    sent = _default_analyst_pair(0.60, SignalDirection.NEUTRAL)
    fund = _default_analyst_pair(0.50, SignalDirection.NEUTRAL)
    deriv = _default_analyst_pair(0.58, SignalDirection.BULLISH)
    trader = _default_trader_pair()
    debate = _default_debate_pair()

    bundle = asyncio.run(_run_patched(
        dm_mock=_mock_dm(),
        tech=tech, news=news, sent=sent, fund=fund, deriv=deriv,
        trader=trader, debate=debate,
    ))

    strategy_signal = bundle.final.metadata.get("strategy_signal")

    assert_true(isinstance(strategy_signal, dict), "strategy_signal should still be present")
    assert_eq(strategy_signal["action"], "skip")
    assert_eq(strategy_signal["strategy_id"], "registry")
    assert_true("missing" in strategy_signal["trigger"])
    assert_eq(bundle.final.action, "BUY", "strategy degradation must not change existing action")


def test_strategy_registry_receives_nested_strategy_config():
    tech = _singleton_mock(analyze_result=_fake_technical_result_with_states())
    news = _default_analyst_pair(0.55, SignalDirection.NEUTRAL)
    sent = _default_analyst_pair(0.60, SignalDirection.NEUTRAL)
    fund = _default_analyst_pair(0.50, SignalDirection.NEUTRAL)
    deriv = _default_analyst_pair(0.58, SignalDirection.BULLISH)
    trader = _default_trader_pair()
    debate = _default_debate_pair()

    with patch(
        "orchestration.analysis_runner._load_strategy_layer_config",
        return_value={"selection": {"min_action_confidence": 0.99}},
    ):
        bundle = asyncio.run(_run_patched(
            dm_mock=_mock_dm(),
            tech=tech, news=news, sent=sent, fund=fund, deriv=deriv,
            trader=trader, debate=debate,
        ))

    strategy_signal = bundle.final.metadata.get("strategy_signal")

    assert_true(isinstance(strategy_signal, dict), "strategy_signal should be serialized dict")
    assert_eq(strategy_signal["action"], "hold")
    assert_eq(bundle.final.action, "BUY", "strategy config must not change existing action")


def run_tests():
    tests = [
        ("returns_normalized_final_analysis_shape", test_returns_normalized_final_analysis_shape),
        ("optional_analyst_failure_degrades_to_na", test_optional_analyst_failure_degrades_to_na),
        ("technical_analyst_raises_runtime_error", test_technical_analyst_raises_runtime_error),
        ("technical_analyst_returns_none_raises_runtime_error", test_technical_analyst_returns_none_raises_runtime_error),
        ("confidence_within_range", test_confidence_within_range),
        ("market_snapshot_has_required_keys", test_market_snapshot_has_required_keys),
        ("strategy_signal_serialized_when_technical_states_exist", test_strategy_signal_serialized_when_technical_states_exist),
        ("strategy_signal_degrades_when_states_missing", test_strategy_signal_degrades_when_states_missing),
        ("strategy_registry_receives_nested_strategy_config", test_strategy_registry_receives_nested_strategy_config),
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
        except Exception as e:
            all_errors.append(f"{name}: {e}")
            print(f"FAIL {name}: {e}")

    if all_errors:
        print(f"\n{len(all_errors)} FAILURES:")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print(f"\nAll {passed} tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
