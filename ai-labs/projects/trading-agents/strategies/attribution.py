"""
Pure strategy attribution builder.

Builds serialized StrategySignal dictionaries from TechnicalAnalyst analysis
state snapshots. This module is intentionally strategy-layer only: no runtime,
execution, order, DB, notifier, dataflow, or orchestration imports.
"""
from typing import Dict, Optional

from strategies.contracts import MarketState, StrategySignal, TechnicalState
from strategies.registry import StrategyRegistry


def fallback_strategy_signal(reason: str, *, source: str = "unknown") -> Dict:
    """Return serialized observational skip when strategy layer cannot run."""
    return StrategySignal(
        strategy_id="registry",
        family="registry",
        action="skip",
        confidence=0.0,
        setup="strategy layer unavailable",
        trigger=reason,
        invalidation="n/a",
        sizing_hint="no position",
        exit_plan="n/a",
        no_trade_reason=(
            "Strategy layer skipped because technical_state or market_state is missing"
        ),
        risk_notes=["Strategy layer unavailable; downstream action was not changed."],
        attribution={"registry": False, "evaluated": [], "source": source},
    ).to_dict()


def build_strategy_signal(
    technical_analysis: dict,
    strategy_config: Optional[Dict] = None,
    *,
    source: str = "unknown",
) -> Dict:
    """Build serialized StrategySignal from technical analyst state snapshots.

    Observational only: this helper never returns execution actions and never
    modifies downstream TraderAgent / FinalAnalysis action semantics.
    """
    strategy_config = strategy_config or {}

    if strategy_config.get("enabled") is False:
        fallback = fallback_strategy_signal("strategy layer disabled", source=source)
        fallback["no_trade_reason"] = "Strategy layer disabled by config"
        return fallback

    if not isinstance(technical_analysis, dict):
        return fallback_strategy_signal("missing technical_state or market_state", source=source)

    technical_state_raw = technical_analysis.get("technical_state")
    market_state_raw = technical_analysis.get("market_state")

    if not isinstance(technical_state_raw, dict) or not isinstance(market_state_raw, dict):
        return fallback_strategy_signal("missing technical_state or market_state", source=source)

    try:
        technical_state = TechnicalState(**technical_state_raw)
        market_state = MarketState(**market_state_raw)
        signal = StrategyRegistry(strategy_config).select(
            technical_state,
            market_state,
            context={"source": source},
        )
        serialized = signal.to_dict()
        attribution = serialized.get("attribution", {}) or {}
        attribution["source"] = source
        serialized["attribution"] = attribution
        return serialized
    except Exception as exc:
        fallback = fallback_strategy_signal(f"strategy layer error: {exc}", source=source)
        fallback["no_trade_reason"] = "Strategy layer skipped because strategy selection failed"
        fallback["risk_notes"].append("Strategy layer raised during serialization seam.")
        return fallback
