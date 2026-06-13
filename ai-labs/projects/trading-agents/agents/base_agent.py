"""
Base Agent - Abstract base class for all agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SignalDirection(Enum):
    """Signal direction"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


@dataclass
class AgentResult:
    """Result from an agent analysis"""
    agent_name: str
    symbol: str
    timestamp: datetime
    direction: SignalDirection
    sub_score: float
    confidence: float
    analysis: Dict[str, Any]
    reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "agent_name": self.agent_name,
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "direction": self.direction.value,
            "sub_score": self.sub_score,
            "confidence": self.confidence,
            "analysis": self.analysis,
            "reasoning": self.reasoning,
            "metadata": self.metadata
        }


class BaseAgent(ABC):
    """Abstract base class for all trading agents"""
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        self.name = name
        self.config = config or {}
        self._initialized = False
    
    @abstractmethod
    async def analyze(self, symbol: str, data: Dict) -> AgentResult:
        """
        Perform analysis on the given data
        
        Args:
            symbol: Trading pair symbol
            data: Market data dictionary
        
        Returns:
            AgentResult with analysis
        """
        pass
    
    @abstractmethod
    async def initialize(self):
        """Initialize the agent (load models, connect to services, etc.)"""
        pass
    
    async def close(self):
        """Clean up resources"""
        pass
    
    def _clamp_score(self, score: float) -> float:
        """Clamp score to [0.0, 1.0] range"""
        return max(0.0, min(1.0, score))
    
    def _determine_direction(self, score: float) -> SignalDirection:
        """
        Determine signal direction from score
        
        Args:
            score: Sub-score in [0.0, 1.0]
        
        Returns:
            SignalDirection
        """
        if score >= 0.6:
            return SignalDirection.BULLISH
        elif score <= 0.4:
            return SignalDirection.BEARISH
        else:
            return SignalDirection.NEUTRAL
