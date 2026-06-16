"""
Abstract base class for pure strategy policies.

Strategy policies are stateless, execution-free callables that decide
whether a valid setup exists for a given technical/market snapshot.
"""
from abc import ABC, abstractmethod
from typing import Optional

from strategies.contracts import MarketState, StrategySignal, TechnicalState


class StrategyPolicy(ABC):
    """Base interface for all strategy policies."""

    strategy_id: str = ""
    family: str = ""

    @abstractmethod
    def evaluate(
        self,
        technical_state: TechnicalState,
        market_state: MarketState,
        context: Optional[dict] = None,
    ) -> StrategySignal:
        """Return a StrategySignal for the given state snapshot."""
        ...
