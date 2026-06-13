"""
Bull Researcher Agent

Builds a lightweight long-side thesis from existing analyst outputs.
"""
from datetime import datetime
from typing import Dict, Optional

from agents.base_agent import AgentResult, SignalDirection
from utils import get_logger


logger = get_logger(__name__)


class BullResearcher:
    """Rule-based researcher that scores bullish evidence."""

    def __init__(self):
        self.name = "BullResearcher"
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        logger.info("BullResearcher initialized")
        self._initialized = True

    async def research(self, symbol: str, signals: Dict[str, Optional[AgentResult]], final_signal: AgentResult) -> Dict:
        if not self._initialized:
            await self.initialize()

        score = 0.35
        evidence = []
        risks = []

        for name, signal in signals.items():
            if not signal:
                continue

            contribution = self._bullish_contribution(name, signal)
            score += contribution["delta"]
            if contribution["delta"] > 0:
                evidence.append(contribution["reason"])
            elif contribution["delta"] < 0:
                risks.append(contribution["reason"])

        score = self._clamp(score)
        confidence = self._calculate_confidence(signals, score)
        thesis = self._build_thesis(symbol, score, evidence, risks)

        return {
            "researcher": self.name,
            "side": "bull",
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "score": score,
            "confidence": confidence,
            "thesis": thesis,
            "evidence": evidence[:6],
            "risks": risks[:6],
            "metadata": {
                "final_direction": final_signal.direction.value,
                "final_score": final_signal.sub_score,
                "signals_used": [name for name, signal in signals.items() if signal],
            },
        }

    def _bullish_contribution(self, name: str, signal: AgentResult) -> Dict:
        strength = signal.confidence * abs(signal.sub_score - 0.5)
        if signal.direction == SignalDirection.BULLISH:
            delta = 0.08 + strength * 0.35
            return {"delta": delta, "reason": f"{name} supports upside ({signal.reasoning})"}
        if signal.direction == SignalDirection.BEARISH:
            delta = -(0.08 + strength * 0.30)
            return {"delta": delta, "reason": f"{name} challenges bull case ({signal.reasoning})"}
        return {"delta": 0.01 if signal.sub_score > 0.52 else 0.0, "reason": f"{name} is neutral"}

    def _calculate_confidence(self, signals: Dict[str, Optional[AgentResult]], score: float) -> float:
        available = [signal for signal in signals.values() if signal]
        if not available:
            return 0.0
        avg_conf = sum(signal.confidence for signal in available) / len(available)
        conviction = abs(score - 0.5) * 0.5
        coverage = min(len(available) / 5, 1.0) * 0.15
        return self._clamp(avg_conf * 0.65 + conviction + coverage)

    def _build_thesis(self, symbol: str, score: float, evidence: list, risks: list) -> str:
        if score >= 0.65:
            stance = "strong bullish case"
        elif score >= 0.55:
            stance = "moderate bullish case"
        elif score >= 0.45:
            stance = "weak bullish case"
        else:
            stance = "bull case not supported"
        main = evidence[0] if evidence else "no decisive bullish evidence"
        risk = risks[0] if risks else "no major opposing evidence"
        return f"{symbol}: {stance}; main support: {main}; key risk: {risk}"

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, value))

    async def close(self):
        pass
