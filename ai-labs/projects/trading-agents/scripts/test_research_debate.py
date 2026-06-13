#!/usr/bin/env python3
"""Synthetic tests for Phase 3B ResearchDebate."""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.base_agent import AgentResult, SignalDirection
from agents.research_debate import ResearchDebate
from utils import setup_logging


setup_logging("INFO")


def make_signal(name: str, symbol: str, direction: SignalDirection, score: float, confidence: float) -> AgentResult:
    return AgentResult(
        agent_name=name,
        symbol=symbol,
        timestamp=datetime.now(),
        direction=direction,
        sub_score=score,
        confidence=confidence,
        analysis={},
        reasoning=f"synthetic {name} {direction.value}",
        metadata={},
    )


async def run_case(label: str, final_direction: SignalDirection, signals, expected: str):
    symbol = "BTCUSDT"
    final_score = 0.7 if final_direction == SignalDirection.BULLISH else 0.3 if final_direction == SignalDirection.BEARISH else 0.5
    final_signal = make_signal("TraderAgent", symbol, final_direction, final_score, 0.75)
    debate = ResearchDebate()
    result = await debate.debate(symbol, signals, final_signal)
    await debate.close()

    print(
        f"{label}: consensus={result['consensus']} adjustment={result['confidence_adjustment']:+.2f} "
        f"winner={result['winner']} bull={result['bull_score']:.3f} bear={result['bear_score']:.3f}"
    )
    assert result["consensus"] == expected, f"{label}: expected {expected}, got {result['consensus']}"


async def main():
    symbol = "BTCUSDT"

    bull_signals = {
        "technical": make_signal("TechnicalAnalyst", symbol, SignalDirection.BULLISH, 0.72, 0.85),
        "news": make_signal("NewsAnalyst", symbol, SignalDirection.BULLISH, 0.66, 0.70),
        "sentiment": make_signal("SentimentAnalyst", symbol, SignalDirection.BULLISH, 0.64, 0.75),
        "fundamentals": make_signal("FundamentalsAnalyst", symbol, SignalDirection.BULLISH, 0.68, 0.80),
        "derivatives": make_signal("DerivativesAnalyst", symbol, SignalDirection.NEUTRAL, 0.52, 0.65),
    }
    await run_case("bull aligned", SignalDirection.BULLISH, bull_signals, "aligned")

    bear_signals = {
        "technical": make_signal("TechnicalAnalyst", symbol, SignalDirection.BEARISH, 0.28, 0.85),
        "news": make_signal("NewsAnalyst", symbol, SignalDirection.BEARISH, 0.34, 0.70),
        "sentiment": make_signal("SentimentAnalyst", symbol, SignalDirection.BEARISH, 0.36, 0.75),
        "fundamentals": make_signal("FundamentalsAnalyst", symbol, SignalDirection.NEUTRAL, 0.50, 0.60),
        "derivatives": make_signal("DerivativesAnalyst", symbol, SignalDirection.BEARISH, 0.30, 0.80),
    }
    await run_case("bear aligned", SignalDirection.BEARISH, bear_signals, "aligned")

    opposite_signals = {
        "technical": make_signal("TechnicalAnalyst", symbol, SignalDirection.BEARISH, 0.25, 0.90),
        "news": make_signal("NewsAnalyst", symbol, SignalDirection.BEARISH, 0.32, 0.80),
        "sentiment": make_signal("SentimentAnalyst", symbol, SignalDirection.NEUTRAL, 0.50, 0.60),
        "fundamentals": make_signal("FundamentalsAnalyst", symbol, SignalDirection.BEARISH, 0.38, 0.70),
        "derivatives": make_signal("DerivativesAnalyst", symbol, SignalDirection.BEARISH, 0.30, 0.85),
    }
    await run_case("opposite", SignalDirection.BULLISH, opposite_signals, "opposite")

    balanced_signals = {
        "technical": make_signal("TechnicalAnalyst", symbol, SignalDirection.BULLISH, 0.58, 0.70),
        "news": make_signal("NewsAnalyst", symbol, SignalDirection.BEARISH, 0.42, 0.65),
        "sentiment": make_signal("SentimentAnalyst", symbol, SignalDirection.NEUTRAL, 0.50, 0.60),
        "fundamentals": make_signal("FundamentalsAnalyst", symbol, SignalDirection.BULLISH, 0.56, 0.65),
        "derivatives": make_signal("DerivativesAnalyst", symbol, SignalDirection.BEARISH, 0.44, 0.65),
    }
    await run_case("balanced", SignalDirection.NEUTRAL, balanced_signals, "balanced")

    print("ResearchDebate synthetic tests passed")


if __name__ == "__main__":
    asyncio.run(main())
