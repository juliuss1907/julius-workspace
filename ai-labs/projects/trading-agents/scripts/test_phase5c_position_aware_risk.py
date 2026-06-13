#!/usr/bin/env python3
"""Synthetic tests for Phase 5C: Position-Aware Risk Manager gates."""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.base_agent import AgentResult, SignalDirection
from agents.risk_manager import RiskManager
from utils import setup_logging


setup_logging("INFO")


def make_signal(name: str, direction: SignalDirection, score: float, confidence: float, funding_avg=None, atr=100.0):
    analysis = {"indicators": {"atr": atr}}
    if name == "DerivativesAnalyst":
        analysis["funding"] = {"average": funding_avg}
    return AgentResult(
        agent_name=name,
        symbol="BTCUSDT",
        timestamp=datetime.now(),
        direction=direction,
        sub_score=score,
        confidence=confidence,
        analysis=analysis,
        reasoning=f"synthetic {name} {direction.value}",
        metadata={},
    )


BASE_RISK = {
    "demo_trading": {"auto_execute": {"min_confidence": 0.60}},
    "risk_management": {"max_open_positions": 5},
    "risk_manager": {
        "max_open_positions": 5,
        "block_duplicate_symbol": False,  # let pyramiding handle this
        "pyramiding": {
            "allow_pyramiding": False,
            "max_same_symbol_positions": 1,
            "same_symbol_exposure_warning_pct": 0.20,
            "max_same_symbol_exposure_pct": 0.30,
            "same_symbol_warning_multiplier": 0.50,
        },
        "directional_exposure": {
            "directional_exposure_warning_pct": 0.60,
            "max_directional_exposure_pct": 0.75,
            "directional_exposure_warning_multiplier": 0.70,
        },
        "drawdown": {
            "daily_drawdown_warning_pct": -0.03,
            "daily_drawdown_block_pct": -0.05,
            "total_drawdown_warning_pct": -0.08,
            "total_drawdown_block_pct": -0.12,
            "drawdown_warning_multiplier": 0.50,
        },
    },
    "futures": {"max_acceptable_funding": 0.001, "funding_warning_threshold": 0.0005},
}


def pc(side_exposure_pct: dict):
    """Build a minimal portfolio context with side exposure."""
    return {
        "total_balance": 10000.0,
        "total_exposure_pct": sum(side_exposure_pct.values()),
        "side_exposure_pct": side_exposure_pct,
        "symbol_exposure_pct": {"BTCUSDT": side_exposure_pct.get("LONG", 0.0) + side_exposure_pct.get("SHORT", 0.0)},
        "correlated_exposure_pct": {},
    }


FIN_BULL = make_signal("TraderAgent", SignalDirection.BULLISH, 0.68, 0.75)
FIN_BEAR = make_signal("TraderAgent", SignalDirection.BEARISH, 0.32, 0.75)
SIG_BULL = {
    "technical": make_signal("TechnicalAnalyst", SignalDirection.BULLISH, 0.66, 0.80),
    "derivatives": make_signal("DerivativesAnalyst", SignalDirection.NEUTRAL, 0.52, 0.70, funding_avg=0.0001),
}
SIG_BEAR = {
    "technical": make_signal("TechnicalAnalyst", SignalDirection.BEARISH, 0.34, 0.80),
    "derivatives": make_signal("DerivativesAnalyst", SignalDirection.NEUTRAL, 0.52, 0.70, funding_avg=0.0001),
}


async def main():
    risk = RiskManager(BASE_RISK)

    # ── 1. Pyramiding disabled blocks same symbol ─────────────────────────
    r = await risk.evaluate(
        "BTCUSDT", FIN_BULL, SIG_BULL,
        open_positions=[{"symbol": "BTCUSDT", "side": "LONG"}],
        portfolio_context=pc({"LONG": 0.20}),
    )
    assert r["approved"] is False, f"expected blocked, got approved: {r}"
    assert "pyramiding disabled" in r["reason"], f"reason: {r['reason']}"
    assert r["checks"]["pyramiding"]["blocked"] is True
    print("PASS pyramiding_disabled_blocks")

    # ── 2. Pyramiding enabled, max same-symbol exceeded ───────────────────
    risk2 = RiskManager({
        **BASE_RISK,
        "risk_manager": {
            **BASE_RISK["risk_manager"],
            "pyramiding": {
                "allow_pyramiding": True,
                "max_same_symbol_positions": 1,
                "same_symbol_exposure_warning_pct": 0.20,
                "max_same_symbol_exposure_pct": 0.30,
            },
        },
    })
    r = await risk2.evaluate(
        "BTCUSDT", FIN_BULL, SIG_BULL,
        open_positions=[{"symbol": "BTCUSDT", "side": "LONG"}],
        portfolio_context=pc({"LONG": 0.15}),
    )
    assert r["approved"] is False, f"expected blocked, got: {r}"
    assert "max same-symbol positions reached" in r["reason"], f"reason: {r['reason']}"
    print("PASS pyramiding_max_same_symbol")

    # ── 3. Pyramiding enabled, exposure warning ───────────────────────────
    r = await risk2.evaluate(
        "BTCUSDT", FIN_BULL, SIG_BULL,
        open_positions=[],  # not same symbol
        portfolio_context=pc({"LONG": 0.25}),
    )
    assert r["approved"] is True, f"expected approved, got: {r}"
    assert r["checks"]["pyramiding"]["warning"] is False
    print("PASS pyramiding_no_block_different_symbol")

    # Now with 0 positions => pyramiding pass
    r = await risk2.evaluate(
        "BTCUSDT", FIN_BULL, SIG_BULL,
        open_positions=[], portfolio_context=pc({}),
    )
    assert r["approved"] is True
    print("PASS pyramiding_pass_empty")

    # ── 4. Same-side LONG warning ────────────────────────────────────────
    r = await risk.evaluate(
        "ETHUSDT", FIN_BULL, SIG_BULL,
        open_positions=[{"symbol": "BTCUSDT", "side": "LONG"}, {"symbol": "SOLUSDT", "side": "LONG"}],
        portfolio_context=pc({"LONG": 0.65, "SHORT": 0.0}),
    )
    assert r["approved"] is True, f"expected approved, got: {r}"
    assert r["position_size_multiplier"] < 1.0, f"expected reduced multiplier: {r}"
    de = r["checks"]["directional_exposure"]
    assert de["warning"] is True, f"expected warning: {de}"
    assert "same-side LONG exposure elevated" in de["reason"], f"reason: {de['reason']}"
    print("PASS directional_LONG_warning")

    # ── 5. Same-side LONG block ──────────────────────────────────────────
    r = await risk.evaluate(
        "SOLUSDT", FIN_BULL, SIG_BULL,
        open_positions=[{"symbol": "BTCUSDT", "side": "LONG"}],
        portfolio_context=pc({"LONG": 0.80, "SHORT": 0.0}),
    )
    assert r["approved"] is False, f"expected blocked, got: {r}"
    de = r["checks"]["directional_exposure"]
    assert de["blocked"] is True
    assert "same-side LONG exposure too high" in r["reason"], f"reason: {r['reason']}"
    print("PASS directional_LONG_block")

    # ── 6. LONG-heavy but BEARISH signal allowed (hedge) ─────────────────
    r = await risk.evaluate(
        "BTCUSDT", FIN_BEAR, SIG_BEAR,
        open_positions=[{"symbol": "SOLUSDT", "side": "LONG"}],
        portfolio_context=pc({"LONG": 0.75, "SHORT": 0.0}),
    )
    assert r["approved"] is True, f"expected approved, got: {r}"
    de = r["checks"]["directional_exposure"]
    assert de["blocked"] is False, f"should NOT be blocked: {de}"
    assert de.get("warning") is False, f"should not warn for opposite side: {de}"
    assert "acceptable" in de["reason"], f"reason: {de['reason']}"
    print("PASS hedge_LONG_heavy_bearish_allowed")

    # ── 7. SHORT-heavy but BULLISH signal allowed (hedge) ────────────────
    r = await risk.evaluate(
        "BTCUSDT", FIN_BULL, SIG_BULL,
        open_positions=[{"symbol": "SOLUSDT", "side": "SHORT"}],
        portfolio_context=pc({"LONG": 0.0, "SHORT": 0.70}),
    )
    assert r["approved"] is True, f"expected approved, got: {r}"
    de = r["checks"]["directional_exposure"]
    assert de["blocked"] is False
    assert de.get("warning") is False
    print("PASS hedge_SHORT_heavy_bullish_allowed")

    # ── 8. SHORT-heavy BULLISH requires normal checks (not boosted) ──────
    r = await risk.evaluate(
        "BTCUSDT", FIN_BULL, SIG_BULL,
        open_positions=[],
        portfolio_context=pc({"LONG": 0.0, "SHORT": 0.70}),
    )
    assert r["approved"] is True
    assert r["position_size_multiplier"] == 1.0, f"hedge should not boost: {r['position_size_multiplier']}"
    print("PASS hedge_no_boost")

    # ── 9. Same-side SHORT warning ───────────────────────────────────────
    r = await risk.evaluate(
        "ETHUSDT", FIN_BEAR, SIG_BEAR,
        open_positions=[],
        portfolio_context=pc({"LONG": 0.0, "SHORT": 0.65}),
    )
    assert r["approved"] is True
    assert r["position_size_multiplier"] < 1.0
    de = r["checks"]["directional_exposure"]
    assert de["warning"] is True
    print("PASS directional_SHORT_warning")

    # ── 10. Daily drawdown warning ───────────────────────────────────────
    r = await risk.evaluate(
        "BTCUSDT", FIN_BULL, SIG_BULL,
        open_positions=[], portfolio_context=pc({}),
        portfolio_stats={"latest_snapshot": {"daily_pnl": -400, "total_equity": 10000, "total_pnl": 500, "total_pnl_pct": 5.0}},
    )
    assert r["approved"] is True
    dd = r["checks"]["drawdown"]
    assert dd["warning"] is True, f"expected drawdown warning: {dd}"
    assert r["position_size_multiplier"] < 1.0
    print("PASS drawdown_daily_warning")

    # ── 11. Daily drawdown block ─────────────────────────────────────────
    r = await risk.evaluate(
        "BTCUSDT", FIN_BULL, SIG_BULL,
        open_positions=[], portfolio_context=pc({}),
        portfolio_stats={"latest_snapshot": {"daily_pnl": -600, "total_equity": 10000, "total_pnl": 500, "total_pnl_pct": 5.0}},
    )
    assert r["approved"] is False
    dd = r["checks"]["drawdown"]
    assert dd["blocked"] is True
    assert "daily drawdown limit" in r["reason"]
    print("PASS drawdown_daily_block")

    # ── 12. Total drawdown block ─────────────────────────────────────────
    r = await risk.evaluate(
        "BTCUSDT", FIN_BULL, SIG_BULL,
        open_positions=[], portfolio_context=pc({}),
        portfolio_stats={"latest_snapshot": {"daily_pnl": 10, "total_equity": 10000, "total_pnl": -300, "total_pnl_pct": -15.0}},
    )
    assert r["approved"] is False
    dd = r["checks"]["drawdown"]
    assert dd["blocked"] is True
    assert "total drawdown limit" in r["reason"], f"reason: {r['reason']}"
    print("PASS drawdown_total_block")

    # ── 13. Total drawdown warning ───────────────────────────────────────
    r = await risk.evaluate(
        "BTCUSDT", FIN_BULL, SIG_BULL,
        open_positions=[], portfolio_context=pc({}),
        portfolio_stats={"latest_snapshot": {"daily_pnl": 10, "total_equity": 10000, "total_pnl": -50, "total_pnl_pct": -10.0}},
    )
    assert r["approved"] is True
    dd = r["checks"]["drawdown"]
    assert dd["warning"] is True, f"expected total drawdown warning: {dd}"
    assert r["position_size_multiplier"] < 1.0
    print("PASS drawdown_total_warning")

    # ── 14. Drawdown unavailable ─────────────────────────────────────────
    r = await risk.evaluate(
        "BTCUSDT", FIN_BULL, SIG_BULL,
        open_positions=[], portfolio_context=pc({}),
        portfolio_stats={},
    )
    assert r["approved"] is True
    dd = r["checks"]["drawdown"]
    assert dd["available"] is False
    assert dd["blocked"] is False
    print("PASS drawdown_unavailable_ok")

    # ── 15. Directional exposure unavailable ─────────────────────────────
    r = await risk.evaluate(
        "BTCUSDT", FIN_BULL, SIG_BULL,
        open_positions=[], portfolio_context={},
    )
    assert r["approved"] is True
    de = r["checks"]["directional_exposure"]
    assert de["available"] is False
    print("PASS directional_exposure_unavailable_ok")

    # ── 16. Neutral signal passes directional check (no side) ────────────
    neutral_sig = make_signal("TraderAgent", SignalDirection.NEUTRAL, 0.50, 0.55)
    r = await risk.evaluate(
        "BTCUSDT", neutral_sig, SIG_BULL,
        open_positions=[], portfolio_context=pc({"LONG": 0.70}),
    )
    assert r["approved"] is False  # neutral blocked by actionable_direction, not by directional check
    de = r["checks"]["directional_exposure"]
    assert de["available"] is False  # no signal side = unavailable
    print("PASS neutral_signal_directional_unavailable")

    # ── 17. No open positions + no context = clean approval ──────────────
    r = await risk.evaluate(
        "BTCUSDT", FIN_BULL, SIG_BULL,
        open_positions=[], portfolio_context={}, portfolio_stats={},
    )
    assert r["approved"] is True
    assert r["risk_level"] == "low"
    assert r["position_size_multiplier"] == 1.0
    assert r["checks"]["pyramiding"]["blocked"] is False
    assert r["checks"]["directional_exposure"]["available"] is False
    assert r["checks"]["drawdown"]["available"] is False
    print("PASS clean_approval_all_missing_context")

    # ── 18. Same-symbol exposure too high (pyramiding enabled) ───────────
    r = await risk2.evaluate(
        "BTCUSDT", FIN_BULL, SIG_BULL,
        open_positions=[{"symbol": "BTCUSDT", "side": "LONG"}],
        portfolio_context={
            "total_balance": 10000.0,
            "total_exposure_pct": 0.40,
            "side_exposure_pct": {"LONG": 0.40},
            "symbol_exposure_pct": {"BTCUSDT": 0.40},
            "correlated_exposure_pct": {},
        },
    )
    assert r["approved"] is False, f"expected blocked: {r}"
    assert "same-symbol" in r["reason"], f"reason: {r['reason']}"
    print("PASS pyramiding_exposure_block")

    print("\nAll Phase 5C risk tests passed.")


if __name__ == "__main__":
    asyncio.run(main())
