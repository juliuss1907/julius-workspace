"""
Trader Agent v1

Aggregates analyst outputs into a final AgentResult that remains compatible
with the existing OrderManager execution interface.
"""
from copy import deepcopy
from datetime import datetime
from typing import Dict, Optional

from agents.base_agent import BaseAgent, AgentResult, SignalDirection
from utils import get_logger, config


logger = get_logger(__name__)


class TraderAgent(BaseAgent):
    """Final signal aggregator for paper trading execution."""

    def __init__(self, config_override: Optional[Dict] = None):
        super().__init__("TraderAgent", config_override)
        default_config = config.load_default_params()
        self.config = {**default_config, **(config_override or {})}
        self.default_mode = self.config.get("default_mode", "full")
        thresholds = self.config.get("analyst_weights", {}).get("direction_thresholds", {})
        self.bullish_above = thresholds.get("bullish_above", 0.60)
        self.bearish_below = thresholds.get("bearish_below", 0.40)
        self.hold_confidence_cap = thresholds.get("hold_confidence_cap", 0.55)

    async def initialize(self):
        if self._initialized:
            return
        logger.info("TraderAgent initialized")
        self._initialized = True

    async def analyze(self, symbol: str, data: Dict) -> AgentResult:
        if not self._initialized:
            await self.initialize()

        signals = data.get("signals", {})
        mode = data.get("mode", self.default_mode)
        research_debate = data.get("research_debate")
        technical = signals.get("technical")

        if not technical:
            return self._neutral_result(symbol, "Technical signal missing; final decision is HOLD")

        available = {name: signal for name, signal in signals.items() if signal is not None}
        weights = self._active_weights(mode, available)
        final_score = self._weighted_metric(available, weights, "sub_score", default=0.5)
        raw_confidence = self._weighted_metric(available, weights, "confidence", default=0.0)
        adjusted_confidence = self._apply_alignment_adjustment(raw_confidence, available)
        final_direction = self._determine_direction(final_score)
        action = self._action_from_direction(final_direction)
        hold_reason = self._hold_reason(final_score, available) if final_direction == SignalDirection.NEUTRAL else None
        research_adjustment = self._research_adjustment(research_debate, final_direction)
        research_adjusted_confidence = self._clamp_score(adjusted_confidence + research_adjustment)
        final_confidence = self._actionability_confidence(research_adjusted_confidence, final_direction)

        analysis = deepcopy(technical.analysis) if technical.analysis else {}
        analysis["trader"] = {
            "mode": mode,
            "action": action,
            "hold_reason": hold_reason,
            "weights": weights,
            "final_score": final_score,
            "raw_confidence": raw_confidence,
            "adjusted_confidence": adjusted_confidence,
            "research_adjustment": research_adjustment,
            "research_adjusted_confidence": research_adjusted_confidence,
            "research_debate": research_debate,
            "final_confidence": final_confidence,
            "directional_margin": abs(final_score - 0.5),
            "signals": self._signal_summary(available),
            "missing_signals": [name for name in self._configured_weights(mode).keys() if name not in available],
        }

        metadata = dict(technical.metadata or {})
        metadata.update(
            {
                "mode": mode,
                "final_action": action,
                "hold_reason": hold_reason,
                "research_consensus": research_debate.get("consensus") if research_debate else None,
                "research_adjustment": research_adjustment,
                "aggregated_agents": list(available.keys()),
                "weights": weights,
            }
        )

        return AgentResult(
            agent_name=self.name,
            symbol=symbol,
            timestamp=datetime.now(),
            direction=final_direction,
            sub_score=final_score,
            confidence=final_confidence,
            analysis=analysis,
            reasoning=self._generate_reasoning(
                available,
                weights,
                action,
                final_score,
                final_confidence,
                hold_reason,
                research_debate,
                research_adjustment,
            ),
            metadata=metadata,
        )

    def _configured_weights(self, mode: str) -> Dict[str, float]:
        weights_by_mode = self.config.get("analyst_weights", {})
        weights = weights_by_mode.get(mode) or weights_by_mode.get("full") or {}
        if not weights:
            return {
                "technical": 0.60,
                "news": 0.10,
                "fundamentals": 0.10,
                "sentiment": 0.05,
                "derivatives": 0.15,
            }
        return weights

    def _active_weights(self, mode: str, available: Dict[str, AgentResult]) -> Dict[str, float]:
        configured = self._configured_weights(mode)
        active = {name: weight for name, weight in configured.items() if name in available and weight > 0}
        total = sum(active.values())
        if total <= 0:
            return {"technical": 1.0} if "technical" in available else {}
        return {name: weight / total for name, weight in active.items()}

    def _weighted_metric(self, signals: Dict[str, AgentResult], weights: Dict[str, float], metric: str, default: float) -> float:
        if not weights:
            return default
        total = 0.0
        for name, weight in weights.items():
            total += getattr(signals[name], metric, default) * weight
        return self._clamp_score(total)

    def _apply_alignment_adjustment(self, confidence: float, signals: Dict[str, AgentResult]) -> float:
        non_neutral = [s for s in signals.values() if s.direction != SignalDirection.NEUTRAL]
        if len(non_neutral) < 2:
            return self._clamp_score(confidence)

        bullish = sum(1 for s in non_neutral if s.direction == SignalDirection.BULLISH)
        bearish = sum(1 for s in non_neutral if s.direction == SignalDirection.BEARISH)
        if bullish and bearish:
            confidence -= min(bullish, bearish) * 0.03
        elif len(non_neutral) >= 3:
            confidence += 0.03
        return self._clamp_score(confidence)

    def _actionability_confidence(self, confidence: float, direction: SignalDirection) -> float:
        """Cap confidence for HOLD so it does not pass execution thresholds."""
        if direction == SignalDirection.NEUTRAL:
            return min(self._clamp_score(confidence), self.hold_confidence_cap)
        return self._clamp_score(confidence)

    def _determine_direction(self, score: float) -> SignalDirection:
        if score >= self.bullish_above:
            return SignalDirection.BULLISH
        if score <= self.bearish_below:
            return SignalDirection.BEARISH
        return SignalDirection.NEUTRAL

    def _research_adjustment(self, research_debate: Optional[Dict], direction: SignalDirection) -> float:
        if not research_debate or direction == SignalDirection.NEUTRAL:
            return 0.0
        return float(research_debate.get("confidence_adjustment") or 0.0)

    def _hold_reason(self, score: float, signals: Dict[str, AgentResult]) -> str:
        non_neutral = [signal for signal in signals.values() if signal.direction != SignalDirection.NEUTRAL]
        bullish = sum(1 for signal in non_neutral if signal.direction == SignalDirection.BULLISH)
        bearish = sum(1 for signal in non_neutral if signal.direction == SignalDirection.BEARISH)

        if bullish and bearish:
            return "conflicting analyst directions"
        if 0.45 <= score <= 0.55:
            return "weighted score near neutral midpoint"
        if score < 0.60 and score > 0.50:
            return "bullish evidence below action threshold"
        if score > 0.40 and score < 0.50:
            return "bearish evidence below action threshold"
        return "final score within neutral band"

    def _signal_summary(self, signals: Dict[str, AgentResult]) -> Dict:
        return {
            name: {
                "direction": signal.direction.value,
                "sub_score": signal.sub_score,
                "confidence": signal.confidence,
                "reasoning": signal.reasoning,
            }
            for name, signal in signals.items()
        }

    def _action_from_direction(self, direction: SignalDirection) -> str:
        if direction == SignalDirection.BULLISH:
            return "BUY"
        if direction == SignalDirection.BEARISH:
            return "SELL"
        return "HOLD"

    def _generate_reasoning(
        self,
        signals: Dict[str, AgentResult],
        weights: Dict[str, float],
        action: str,
        score: float,
        confidence: float,
        hold_reason: Optional[str] = None,
        research_debate: Optional[Dict] = None,
        research_adjustment: float = 0.0,
    ) -> str:
        parts = []
        for name in weights.keys():
            signal = signals[name]
            parts.append(
                f"{name} {signal.direction.value} S:{signal.sub_score:.3f} C:{signal.confidence:.3f} W:{weights[name]:.2f}"
            )
        final = f"final {action} S:{score:.3f} C:{confidence:.3f}"
        if hold_reason:
            final += f" ({hold_reason})"
        if research_debate:
            final += f" research={research_debate.get('consensus')} {research_adjustment:+.2f}"
        parts.append(final)
        return " | ".join(parts)

    def _neutral_result(self, symbol: str, reason: str) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            symbol=symbol,
            timestamp=datetime.now(),
            direction=SignalDirection.NEUTRAL,
            sub_score=0.5,
            confidence=0.0,
            analysis={"trader": {"action": "HOLD", "reason": reason}},
            reasoning=reason,
            metadata={"final_action": "HOLD"},
        )
