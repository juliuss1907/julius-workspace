"""
Pure reverse planner — zero side effects, zero heavy dependencies.

Extracted from policies/demo_execution.py so that the guarded-reverse
decision logic is importable without pulling the full analysis stack
(dataflows, agents, etc.).

Imports only stdlib.  No RiskManager, PositionManager, OrderManager,
data_manager, or Telegram dependencies.
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class GuardedReversePlan:
    """Pure-policy plan for a guarded reverse execution.

    Produced by plan_guarded_reverse().  The runtime layer must still
    perform all side effects: close, risk rerun, ticker fetch,
    execute_signal, notification, signal recording.
    """
    should_close: bool
    should_rerun_risk: bool
    should_open_reverse: bool
    trade_id: Optional[str] = None
    pre_close_status: Optional[str] = None
    post_close_status: Optional[str] = None
    reason: str = ""


def plan_guarded_reverse(
    reverse_enabled: bool,
    execution_mode: str,
    final_confidence: float,
    min_confidence_to_open_reverse: float,
    position_decision: Dict[str, Any],
    rerun_risk_after_close: bool,
) -> GuardedReversePlan:
    """Decide what a guarded reverse *should* do — no side effects.

    The runtime uses the returned plan to gate execution; if the plan
    says ``should_close=False`` the runtime returns early without
    touching the order manager.

    Checks are ordered so that missing-trade-id (which would make
    ``close_position(None)`` unsafe) takes priority over the confidence
    gate.  This way low confidence with a valid trade_id still closes,
    but low confidence *without* a trade_id returns a fail-safe plan.
    """
    if not reverse_enabled or execution_mode != "execute_all":
        return GuardedReversePlan(
            should_close=False,
            should_rerun_risk=False,
            should_open_reverse=False,
            reason="reverse disabled or execution_mode != execute_all",
        )

    trade_id = (position_decision or {}).get("position", {}).get("trade_id")
    if not trade_id:
        return GuardedReversePlan(
            should_close=False,
            should_rerun_risk=False,
            should_open_reverse=False,
            reason="no trade_id in position_decision",
        )

    if final_confidence < min_confidence_to_open_reverse:
        return GuardedReversePlan(
            should_close=True,
            should_rerun_risk=False,
            should_open_reverse=False,
            trade_id=trade_id,
            reason="confidence below reverse threshold — close only",
        )

    if not rerun_risk_after_close:
        return GuardedReversePlan(
            should_close=True,
            should_rerun_risk=False,
            should_open_reverse=False,
            trade_id=trade_id,
            reason="rerun_risk disabled — close only",
        )

    return GuardedReversePlan(
        should_close=True,
        should_rerun_risk=True,
        should_open_reverse=True,
        trade_id=trade_id,
        reason="full reverse requested",
    )
