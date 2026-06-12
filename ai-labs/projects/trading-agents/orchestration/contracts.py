"""
Shared orchestration contracts.

Dataclasses that define the normalized output of the analysis pipeline.
Both the demo-execution and manual-report paths consume these contracts.
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional


@dataclass
class AnalystSignalSummary:
    """Normalized summary of a single analyst AgentResult.

    Mirrors the existing sig_summary() helper shape in readonly scripts.
    """
    direction: str          # "bullish" | "bearish" | "neutral" | "N/A"
    score: float            # sub_score from AgentResult
    confidence: float       # confidence from AgentResult
    reasoning: str          # human-readable reasoning text


@dataclass
class FinalAnalysis:
    """Normalized output of the full analysis pipeline.

    This is the shared contract between the analysis layer and all
    downstream consumers (demo execution, manual reports, debug CLI).

    Contains only primitive/serializable types — no AgentResult objects,
    no datetime instances, no execution-side dependencies.
    """
    symbol: str
    timeframe: str
    price: Optional[float]
    timestamp: str                                          # ISO-8601
    analyst_signals: Dict[str, AnalystSignalSummary]
    draft_signal: AnalystSignalSummary
    research_debate: Optional[Dict]                         # dict from ResearchDebate.debate()
    final_signal: AnalystSignalSummary
    market_snapshot: Dict
    direction: str                                          # "bullish" | "bearish" | "neutral"
    confidence: float
    action: str                                             # "BUY" | "SELL" | "HOLD"
    hold_reason: Optional[str] = None
    risk_notes: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Serialize to a plain dict for JSON output."""
        return asdict(self)
