"""
Demo execution policy adapter.

Consumes a shared AnalysisBundle and translates it into the inputs
needed by RiskManager / PositionManager / the execution path.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from agents.base_agent import AgentResult
from agents.risk_manager import RiskManager
from agents.position_manager import PositionManager
from state.portfolio_context import PortfolioContextBuilder
from orchestration.analysis_runner import AnalysisBundle
from policies.reverse_planner import GuardedReversePlan, plan_guarded_reverse  # noqa: F401 — re-exported for convenience
from utils import get_logger


logger = get_logger(__name__)


# ── Demo execution decision ───────────────────────────────────────────


@dataclass
class DemoExecutionDecision:
    """Normalized output of the demo-policy evaluation.

    Wraps the combined outputs from PositionManager and RiskManager
    so the execution layer can act without rebuilding context.
    """
    approved: bool
    action: str                          # "open" | "hold" | "reduce" | "close" | "reverse" | "skip"
    reason: str
    risk_level: str                      # "low" | "medium" | "high" | "blocked"
    execution_mode: str

    # Raw policy-layer outputs preserved for the execution path
    position_decision: Optional[Dict] = None
    risk_decision: Optional[Dict] = None
    position_size_multiplier: float = 1.0
    max_leverage: int = 1

    # Passthrough from the analysis bundle for execution use
    final_signal: Optional[AgentResult] = None
    analyst_signals: Dict[str, Optional[AgentResult]] = field(default_factory=dict)
    research_debate: Optional[Dict] = None
    draft_signal: Optional[AgentResult] = None
    market_snapshot: Dict = field(default_factory=dict)


async def build_demo_execution_decision(
    bundle: AnalysisBundle,
    risk_manager: RiskManager,
    position_manager: PositionManager,
    portfolio_context_builder: PortfolioContextBuilder,
    open_positions: List[Dict],
    portfolio_stats: Dict,
    current_prices: Dict[str, Optional[float]],
    execution_mode: str,
) -> DemoExecutionDecision:
    """Evaluate the shared analysis through demo-policy gates.

    Evaluates risk first for non-neutral signals, then calls PositionManager
    with that risk context, and returns a single DemoExecutionDecision for
    the execution layer to act on.

    Args:
        bundle: Shared analysis output from orchestration.
        risk_manager: Pre-initialized RiskManager instance.
        position_manager: Pre-initialized PositionManager instance.
        portfolio_context_builder: Builder for portfolio context.
        open_positions: List of current open positions from the DB.
        portfolio_stats: Portfolio stats dict from the DB.
        current_prices: Dict mapping symbol → current price.
        execution_mode: The runtime execution mode string.

    Returns:
        DemoExecutionDecision ready for the execution layer.
    """
    analysis = bundle.final
    symbol = analysis.symbol
    final_signal = bundle.raw_final
    analyst_signals = bundle.raw_signals
    research_debate = analysis.research_debate
    market_snapshot = dict(analysis.market_snapshot)
    price = analysis.price

    portfolio_context = portfolio_context_builder.build(
        open_positions=open_positions,
        portfolio_stats=portfolio_stats,
        current_prices=current_prices,
    )

    risk_decision = None
    if final_signal.direction.value != "neutral":
        risk_decision = await risk_manager.evaluate(
            symbol=symbol,
            final_signal=final_signal,
            analyst_signals=analyst_signals,
            research_debate=research_debate,
            market_snapshot=market_snapshot,
            open_positions=open_positions,
            portfolio_stats=portfolio_stats,
            portfolio_context=portfolio_context,
        )

        logger.info(
            f"{symbol}: Risk approved={risk_decision['approved']} "
            f"level={risk_decision['risk_level']} "
            f"mult={risk_decision['position_size_multiplier']:.2f} "
            f"reason={risk_decision['reason']}"
        )

    position_decision = await position_manager.evaluate(
        symbol=symbol,
        final_signal=final_signal,
        analyst_signals=analyst_signals,
        research_debate=research_debate,
        risk_decision=risk_decision,
        portfolio_context=portfolio_context,
        open_positions=open_positions,
        market_snapshot=market_snapshot,
    )

    position_action = position_decision.get("action", "no_position")

    if position_action == "hold_position":
        return DemoExecutionDecision(
            approved=False,
            action="hold",
            reason=position_decision.get("reason", "position held"),
            risk_level=(risk_decision or {}).get("risk_level", "low"),
            execution_mode=execution_mode,
            position_decision=position_decision,
            risk_decision=risk_decision,
            final_signal=final_signal,
            analyst_signals=analyst_signals,
            research_debate=research_debate,
            draft_signal=bundle.raw_draft,
            market_snapshot=market_snapshot,
        )

    if position_action in ("close_position", "reduce_position", "reverse_position"):
        return DemoExecutionDecision(
            approved=True,
            action=position_action,
            reason=position_decision.get("reason", ""),
            risk_level=(risk_decision or {}).get("risk_level", "medium"),
            execution_mode=execution_mode,
            position_decision=position_decision,
            risk_decision=risk_decision,
            final_signal=final_signal,
            analyst_signals=analyst_signals,
            research_debate=research_debate,
            draft_signal=bundle.raw_draft,
            market_snapshot=market_snapshot,
        )

    if final_signal.direction.value == "neutral":
        return DemoExecutionDecision(
            approved=False,
            action="skip",
            reason=analysis.hold_reason or "neutral signal",
            risk_level="low",
            execution_mode=execution_mode,
            position_decision=position_decision,
            final_signal=final_signal,
            analyst_signals=analyst_signals,
            research_debate=research_debate,
            market_snapshot=market_snapshot,
        )

    assert risk_decision is not None

    if not risk_decision["approved"]:
        return DemoExecutionDecision(
            approved=False,
            action="skip",
            reason=risk_decision["reason"],
            risk_level=risk_decision["risk_level"],
            execution_mode=execution_mode,
            risk_decision=risk_decision,
            final_signal=final_signal,
            analyst_signals=analyst_signals,
            research_debate=research_debate,
            market_snapshot=market_snapshot,
        )

    return DemoExecutionDecision(
        approved=True,
        action="open",
        reason=risk_decision.get("reason", "approved"),
        risk_level=risk_decision["risk_level"],
        execution_mode=execution_mode,
        position_decision=position_decision,
        risk_decision=risk_decision,
        position_size_multiplier=risk_decision.get("position_size_multiplier", 1.0),
        max_leverage=risk_decision.get("max_leverage", 1),
        final_signal=final_signal,
        analyst_signals=analyst_signals,
        research_debate=research_debate,
        draft_signal=bundle.raw_draft,
        market_snapshot=market_snapshot,
    )
