#!/usr/bin/env python3
"""Policy-level tests for policies/demo_execution.py.

Pre-seeds sys.modules so zero heavy deps load during import.
"""
import sys
from unittest.mock import AsyncMock, MagicMock

# ── pre-seed heavy modules ────────────────────────────────────────────
_HEAVY = {
    # policy-layer imports
    "agents.risk_manager",
    "agents.position_manager",
    # agent analysis modules (heavy deps: numpy, vaderSentiment, etc.)
    "agents.technical_analyst",
    "agents.news_analyst",
    "agents.sentiment_analyst",
    "agents.fundamentals_analyst",
    "agents.derivatives_analyst",
    "agents.trader_agent",
    "agents.research_debate",
    "agents.bull_researcher",
    "agents.bear_researcher",
    "agents.indicators",
    "agents.market_regime",
    "agents.news_sentiment",
    "agents.sentiment_scorer",
    "agents.screening_agent",
    # state / trading / data / utils heavy chains
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
    "utils",
    "utils.logging_config",
    "utils.config_loader",
    "utils.watchlist",
    "utils.process_lock",
    "utils.log_rotation",
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
}
for m in _HEAVY:
    if m not in sys.modules:
        sys.modules[m] = MagicMock()

import asyncio
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.base_agent import AgentResult, SignalDirection
from orchestration.analysis_runner import AnalysisBundle
from orchestration.contracts import FinalAnalysis, AnalystSignalSummary
from policies.demo_execution import (
    DemoExecutionDecision,
    build_demo_execution_decision,
)
from policies.reverse_planner import (
    GuardedReversePlan,
    plan_guarded_reverse,
)


ERRORS = []


def assert_true(cond, msg=""):
    if not cond:
        msg = msg or "assertion failed"
        ERRORS.append(msg)


def assert_eq(a, b, msg=""):
    if a != b:
        msg = msg or f"expected {b!r}, got {a!r}"
        ERRORS.append(msg)


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------


def _fake_result(name="TechnicalAnalyst", direction=SignalDirection.BULLISH,
                 score=0.72, confidence=0.65, reasoning="ok"):
    return AgentResult(
        agent_name=name,
        symbol="BTCUSDT",
        timestamp=datetime.now(),
        direction=direction,
        sub_score=score,
        confidence=confidence,
        analysis={"indicators": {"atr": 1500}, "trader": {"action": "BUY"}},
        reasoning=reasoning,
        metadata={"timeframe": "1h"},
    )


def _make_bundle(direction=SignalDirection.BULLISH, action="BUY",
                 confidence=0.70, hold_reason=None):
    final_result = _fake_result(direction=direction, score=0.70,
                                confidence=confidence)
    draft_result = _fake_result(name="TraderAgent", score=0.65,
                                confidence=0.60)
    analyst_signals = {
        "technical": _fake_result(score=0.72),
        "news": _fake_result(score=0.55, direction=SignalDirection.NEUTRAL),
        "sentiment": _fake_result(score=0.60, direction=SignalDirection.NEUTRAL),
        "fundamentals": _fake_result(score=0.50, direction=SignalDirection.NEUTRAL),
        "derivatives": _fake_result(score=0.58, direction=SignalDirection.BULLISH),
    }
    analyst_summaries = {
        name: AnalystSignalSummary(
            direction=sig.direction.value, score=sig.sub_score,
            confidence=sig.confidence, reasoning=sig.reasoning,
        )
        for name, sig in analyst_signals.items()
    }
    final = FinalAnalysis(
        symbol="BTCUSDT", timeframe="1h", price=68000.0,
        timestamp=datetime.now().isoformat(),
        analyst_signals=analyst_summaries,
        draft_signal=AnalystSignalSummary(
            direction=draft_result.direction.value, score=draft_result.sub_score,
            confidence=draft_result.confidence, reasoning=draft_result.reasoning,
        ),
        research_debate={"consensus": "aligned", "confidence_adjustment": 0.05,
                         "winner": "bull"},
        final_signal=AnalystSignalSummary(
            direction=final_result.direction.value, score=final_result.sub_score,
            confidence=final_result.confidence, reasoning=final_result.reasoning,
        ),
        market_snapshot={"timeframe": "1h", "ohlcv_candles": 200,
                         "last_close": 68000, "ticker_price": 68000.0, "atr": 1500,
                         "fundamentals_available": True},
        direction=direction.value, confidence=confidence, action=action,
        hold_reason=hold_reason, risk_notes=[], metadata={"mode": "full"},
    )
    return AnalysisBundle(
        final=final,
        raw_signals=analyst_signals,
        raw_draft=draft_result,
        raw_final=final_result,
    )


def _mock_risk_manager(approved=True, risk_level="low"):
    m = MagicMock()
    m.evaluate = AsyncMock(return_value={
        "approved": approved, "risk_level": risk_level,
        "position_size_multiplier": 1.0, "max_leverage": 5,
        "reason": "ok" if approved else "too risky",
    })
    return m


def _mock_position_manager(action="no_position"):
    m = MagicMock()
    m.evaluate = AsyncMock(return_value={
        "action": action,
        "reason": "evaluated",
        "position": {},
    })
    return m


def _mock_portfolio_context_builder():
    m = MagicMock()
    m.build = MagicMock(return_value={"total_balance": 10000, "exposure": 0.0})
    return m


# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------


def test_build_demo_execution_decision_shape():
    """Happy path: risk approved, no existing position → open."""
    bundle = _make_bundle()
    decision = asyncio.run(build_demo_execution_decision(
        bundle=bundle,
        risk_manager=_mock_risk_manager(approved=True),
        position_manager=_mock_position_manager(action="no_position"),
        portfolio_context_builder=_mock_portfolio_context_builder(),
        open_positions=[],
        portfolio_stats={"total_balance": 10000},
        current_prices={"BTCUSDT": 68000.0},
        execution_mode="execute_all",
    ))

    assert isinstance(decision, DemoExecutionDecision)
    assert_eq(decision.approved, True)
    assert_eq(decision.action, "open")
    assert_eq(decision.risk_level, "low")
    assert_eq(decision.execution_mode, "execute_all")
    assert isinstance(decision.final_signal, AgentResult)
    assert_eq(len(decision.analyst_signals), 5)
    assert isinstance(decision.risk_decision, dict)


def test_risk_rejected_returns_skip():
    """Risk manager rejects → approved=False, action=skip."""
    bundle = _make_bundle()
    decision = asyncio.run(build_demo_execution_decision(
        bundle=bundle,
        risk_manager=_mock_risk_manager(approved=False, risk_level="high"),
        position_manager=_mock_position_manager(action="no_position"),
        portfolio_context_builder=_mock_portfolio_context_builder(),
        open_positions=[],
        portfolio_stats={"total_balance": 10000},
        current_prices={"BTCUSDT": 68000.0},
        execution_mode="execute_close_only",
    ))

    assert_eq(decision.approved, False)
    assert_eq(decision.action, "skip")
    assert_eq(decision.risk_level, "high")
    assert_true("too risky" in decision.reason)


def test_neutral_signal_returns_skip():
    """Neutral direction → skip without calling risk manager."""
    bundle = _make_bundle(
        direction=SignalDirection.NEUTRAL,
        action="HOLD",
        confidence=0.30,
        hold_reason="conflicting signals",
    )
    decision = asyncio.run(build_demo_execution_decision(
        bundle=bundle,
        risk_manager=_mock_risk_manager(approved=True),
        position_manager=_mock_position_manager(action="no_position"),
        portfolio_context_builder=_mock_portfolio_context_builder(),
        open_positions=[],
        portfolio_stats={"total_balance": 10000},
        current_prices={"BTCUSDT": 68000.0},
        execution_mode="execute_all",
    ))

    assert_eq(decision.approved, False)
    assert_eq(decision.action, "skip")
    assert_true("conflicting signals" in decision.reason)


def test_existing_position_close_action():
    """Position manager returns close_position → route to position action."""
    bundle = _make_bundle()
    decision = asyncio.run(build_demo_execution_decision(
        bundle=bundle,
        risk_manager=_mock_risk_manager(approved=True),
        position_manager=_mock_position_manager(action="close_position"),
        portfolio_context_builder=_mock_portfolio_context_builder(),
        open_positions=[],
        portfolio_stats={"total_balance": 10000},
        current_prices={"BTCUSDT": 68000.0},
        execution_mode="execute_all",
    ))

    assert_eq(decision.approved, True)
    assert_eq(decision.action, "close_position")
    assert isinstance(decision.position_decision, dict)


def test_existing_position_hold_action_does_not_open_new_trade():
    """hold_position must be terminal, not fall through to new-entry execution."""
    bundle = _make_bundle()
    decision = asyncio.run(build_demo_execution_decision(
        bundle=bundle,
        risk_manager=_mock_risk_manager(approved=True),
        position_manager=_mock_position_manager(action="hold_position"),
        portfolio_context_builder=_mock_portfolio_context_builder(),
        open_positions=[{"symbol": "BTCUSDT", "side": "LONG"}],
        portfolio_stats={"total_balance": 10000},
        current_prices={"BTCUSDT": 68000.0},
        execution_mode="execute_all",
    ))

    assert_eq(decision.approved, False)
    assert_eq(decision.action, "hold")
    assert isinstance(decision.position_decision, dict)
    assert isinstance(decision.risk_decision, dict)


def test_position_manager_receives_approved_risk_for_reverse():
    """Risk is evaluated before PositionManager so real reverse_position is reachable."""
    bundle = _make_bundle(confidence=0.90)
    risk_manager = _mock_risk_manager(approved=True)
    position_manager = MagicMock()

    async def _evaluate(**kwargs):
        risk_decision = kwargs.get("risk_decision")
        if risk_decision and risk_decision.get("approved"):
            return {
                "action": "reverse_position",
                "reason": "approved reverse",
                "position": {"trade_id": "BTC_SHORT_123"},
            }
        return {"action": "close_position", "reason": "risk missing", "position": {}}

    position_manager.evaluate = AsyncMock(side_effect=_evaluate)
    decision = asyncio.run(build_demo_execution_decision(
        bundle=bundle,
        risk_manager=risk_manager,
        position_manager=position_manager,
        portfolio_context_builder=_mock_portfolio_context_builder(),
        open_positions=[{"symbol": "BTCUSDT", "side": "SHORT"}],
        portfolio_stats={"total_balance": 10000},
        current_prices={"BTCUSDT": 68000.0},
        execution_mode="execute_all",
    ))

    assert_eq(decision.approved, True)
    assert_eq(decision.action, "reverse_position")
    assert isinstance(decision.risk_decision, dict)


def test_draft_signal_passthrough():
    """Bundle.raw_draft is passed through to DemoExecutionDecision."""
    bundle = _make_bundle()
    decision = asyncio.run(build_demo_execution_decision(
        bundle=bundle,
        risk_manager=_mock_risk_manager(approved=True),
        position_manager=_mock_position_manager(action="no_position"),
        portfolio_context_builder=_mock_portfolio_context_builder(),
        open_positions=[],
        portfolio_stats={"total_balance": 10000},
        current_prices={"BTCUSDT": 68000.0},
        execution_mode="execute_all",
    ))

    assert isinstance(decision.draft_signal, AgentResult)
    assert_eq(decision.draft_signal.agent_name, "TraderAgent")


# ── Guarded reverse planner tests (pure functions, no mocks needed) ──


def test_reverse_disabled_recommend_only():
    """reverse_enabled=False → should_close=False, get recommend status."""
    plan = plan_guarded_reverse(
        reverse_enabled=False,
        execution_mode="execute_all",
        final_confidence=0.85,
        min_confidence_to_open_reverse=0.80,
        position_decision={"position": {"trade_id": "abc"}},
        rerun_risk_after_close=True,
    )
    assert_eq(plan.should_close, False)
    assert_eq(plan.should_rerun_risk, False)
    assert_eq(plan.should_open_reverse, False)


def test_execution_mode_not_execute_all_recommend_only():
    """execution_mode != execute_all → no close, recommend status."""
    plan = plan_guarded_reverse(
        reverse_enabled=True,
        execution_mode="execute_close_only",
        final_confidence=0.85,
        min_confidence_to_open_reverse=0.80,
        position_decision={"position": {"trade_id": "abc"}},
        rerun_risk_after_close=True,
    )
    assert_eq(plan.should_close, False)
    assert_eq(plan.should_open_reverse, False)


def test_low_confidence_close_only():
    """confidence below threshold (with valid trade_id) → close but no rerun, no open."""
    plan = plan_guarded_reverse(
        reverse_enabled=True,
        execution_mode="execute_all",
        final_confidence=0.55,
        min_confidence_to_open_reverse=0.80,
        position_decision={"position": {"trade_id": "BTC_SHORT_456"}},
        rerun_risk_after_close=True,
    )
    assert_eq(plan.should_close, True)
    assert_eq(plan.should_rerun_risk, False)
    assert_eq(plan.should_open_reverse, False)
    assert_eq(plan.trade_id, "BTC_SHORT_456")


def test_missing_trade_id_fail_before_close():
    """No trade_id → should_close=False."""
    plan = plan_guarded_reverse(
        reverse_enabled=True,
        execution_mode="execute_all",
        final_confidence=0.85,
        min_confidence_to_open_reverse=0.80,
        position_decision={"position": {}},
        rerun_risk_after_close=True,
    )
    assert_eq(plan.should_close, False)
    assert_eq(plan.trade_id, None)


def test_low_confidence_missing_trade_id_fail_safe():
    """Missing trade_id takes priority over low confidence — no close."""
    plan = plan_guarded_reverse(
        reverse_enabled=True,
        execution_mode="execute_all",
        final_confidence=0.70,
        min_confidence_to_open_reverse=0.80,
        position_decision={"position": {}},
        rerun_risk_after_close=True,
    )
    assert_eq(plan.should_close, False)
    assert_eq(plan.should_rerun_risk, False)
    assert_eq(plan.should_open_reverse, False)
    assert_eq(plan.trade_id, None)


def test_valid_reverse_with_rerun_risk():
    """Happy path: close + rerun risk + open reverse."""
    plan = plan_guarded_reverse(
        reverse_enabled=True,
        execution_mode="execute_all",
        final_confidence=0.85,
        min_confidence_to_open_reverse=0.80,
        position_decision={"position": {"trade_id": "BTC_SHORT_123"}},
        rerun_risk_after_close=True,
    )
    assert_eq(plan.should_close, True)
    assert_eq(plan.should_rerun_risk, True)
    assert_eq(plan.should_open_reverse, True)
    assert_eq(plan.trade_id, "BTC_SHORT_123")


def test_valid_reverse_rerun_disabled_close_only():
    """rerun_risk_after_close=False → close only, no open."""
    plan = plan_guarded_reverse(
        reverse_enabled=True,
        execution_mode="execute_all",
        final_confidence=0.85,
        min_confidence_to_open_reverse=0.80,
        position_decision={"position": {"trade_id": "BTC_SHORT_123"}},
        rerun_risk_after_close=False,
    )
    assert_eq(plan.should_close, True)
    assert_eq(plan.should_rerun_risk, False)
    assert_eq(plan.should_open_reverse, False)
    assert_eq(plan.trade_id, "BTC_SHORT_123")


def run_tests():
    tests = [
        ("build_demo_execution_decision_shape", test_build_demo_execution_decision_shape),
        ("risk_rejected_returns_skip", test_risk_rejected_returns_skip),
        ("neutral_signal_returns_skip", test_neutral_signal_returns_skip),
        ("existing_position_close_action", test_existing_position_close_action),
        ("existing_position_hold_action_does_not_open_new_trade", test_existing_position_hold_action_does_not_open_new_trade),
        ("position_manager_receives_approved_risk_for_reverse", test_position_manager_receives_approved_risk_for_reverse),
        ("draft_signal_passthrough", test_draft_signal_passthrough),
        ("reverse_disabled_recommend_only", test_reverse_disabled_recommend_only),
        ("execution_mode_not_execute_all_recommend_only", test_execution_mode_not_execute_all_recommend_only),
        ("low_confidence_close_only", test_low_confidence_close_only),
        ("missing_trade_id_fail_before_close", test_missing_trade_id_fail_before_close),
        ("low_confidence_missing_trade_id_fail_safe", test_low_confidence_missing_trade_id_fail_safe),
        ("valid_reverse_with_rerun_risk", test_valid_reverse_with_rerun_risk),
        ("valid_reverse_rerun_disabled_close_only", test_valid_reverse_rerun_disabled_close_only),
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
