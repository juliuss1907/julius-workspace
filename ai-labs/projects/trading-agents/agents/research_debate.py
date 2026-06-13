"""
Research Debate Agent

Runs BullResearcher and BearResearcher, then maps the result to a confidence
adjustment for TraderAgent.
"""
import asyncio
from datetime import datetime
from typing import Dict, Optional

from agents.base_agent import AgentResult, SignalDirection
from agents.bull_researcher import BullResearcher
from agents.bear_researcher import BearResearcher
from utils import get_logger, config


logger = get_logger(__name__)


class ResearchDebate:
    """Compares bull and bear theses against the draft final signal."""

    def __init__(self, config_override: Optional[Dict] = None):
        default_config = config.load_default_params()
        confidence_config = default_config.get("confidence", {}).get("researcher_adjustment", {})
        self.config = {**confidence_config, **(config_override or {})}
        self.name = "ResearchDebate"
        self.bull_researcher = BullResearcher()
        self.bear_researcher = BearResearcher()
        self.aligned_adjustment = self.config.get("aligned", 0.05)
        self.opposite_adjustment = self.config.get("opposite", -0.10)
        self.neutral_adjustment = self.config.get("neutral", 0.0)
        self.min_margin = self.config.get("min_margin", 0.08)
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        await self.bull_researcher.initialize()
        await self.bear_researcher.initialize()
        logger.info("ResearchDebate initialized")
        self._initialized = True

    async def debate(self, symbol: str, signals: Dict[str, Optional[AgentResult]], final_signal: AgentResult) -> Dict:
        if not self._initialized:
            await self.initialize()

        bull_task = self.bull_researcher.research(symbol, signals, final_signal)
        bear_task = self.bear_researcher.research(symbol, signals, final_signal)
        bull_case, bear_case = await asyncio.gather(bull_task, bear_task)

        bull_score = bull_case["score"] * bull_case["confidence"]
        bear_score = bear_case["score"] * bear_case["confidence"]
        margin = abs(bull_score - bear_score)
        winner = "bull" if bull_score > bear_score else "bear" if bear_score > bull_score else "balanced"
        consensus = self._consensus(winner, margin, final_signal.direction)
        adjustment = self._adjustment(consensus)

        return {
            "agent_name": self.name,
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "consensus": consensus,
            "confidence_adjustment": adjustment,
            "winner": winner,
            "margin": margin,
            "bull_score": bull_case["score"],
            "bear_score": bear_case["score"],
            "bull_weighted_score": bull_score,
            "bear_weighted_score": bear_score,
            "bull_case": bull_case,
            "bear_case": bear_case,
            "summary": self._summary(consensus, winner, adjustment, bull_case, bear_case),
        }

    def _consensus(self, winner: str, margin: float, direction: SignalDirection) -> str:
        if direction == SignalDirection.NEUTRAL or winner == "balanced" or margin < self.min_margin:
            return "balanced"
        if direction == SignalDirection.BULLISH:
            return "aligned" if winner == "bull" else "opposite"
        if direction == SignalDirection.BEARISH:
            return "aligned" if winner == "bear" else "opposite"
        return "balanced"

    def _adjustment(self, consensus: str) -> float:
        if consensus == "aligned":
            return self.aligned_adjustment
        if consensus == "opposite":
            return self.opposite_adjustment
        return self.neutral_adjustment

    def _summary(self, consensus: str, winner: str, adjustment: float, bull_case: Dict, bear_case: Dict) -> str:
        return (
            f"research {consensus}; winner={winner}; adjustment={adjustment:+.2f}; "
            f"bull={bull_case['score']:.3f}; bear={bear_case['score']:.3f}"
        )

    async def close(self):
        await self.bull_researcher.close()
        await self.bear_researcher.close()
