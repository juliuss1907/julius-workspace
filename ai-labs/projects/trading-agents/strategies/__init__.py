"""
Strategy layer package.

Provides pure, execution-free strategy policies that translate
TechnicalState + MarketState into StrategySignal objects.

The strategy layer must not import execution, runtime, order, position,
or notification modules. It sits between the analysis layer and the
downstream policy/execution consumers.
"""
from strategies.contracts import (
    StrategyAction,
    StrategyFamily,
    TechnicalState,
    MarketState,
    StrategySignal,
)
from strategies.base import StrategyPolicy
from strategies.volatility_skip import VolatilitySkipStrategy

__all__ = [
    "StrategyAction",
    "StrategyFamily",
    "TechnicalState",
    "MarketState",
    "StrategySignal",
    "StrategyPolicy",
    "VolatilitySkipStrategy",
]
