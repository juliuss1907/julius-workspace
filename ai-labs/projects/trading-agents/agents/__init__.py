"""
Agents Package

Only BaseAgent and AgentResult are eagerly loaded (stdlib-only deps).
All analyst, researcher, trader, and executive classes are lazy-loaded
via __getattr__ to prevent heavy transitive dependencies (numpy,
vaderSentiment, ccxt, etc.) from being pulled in at package-init time.
"""
from .base_agent import BaseAgent, AgentResult


_LAZY = {
    "FundamentalsAnalyst": ".fundamentals_analyst",
    "TechnicalAnalyst": ".technical_analyst",
    "NewsAnalyst": ".news_analyst",
    "SentimentAnalyst": ".sentiment_analyst",
    "DerivativesAnalyst": ".derivatives_analyst",
    "TraderAgent": ".trader_agent",
    "BullResearcher": ".bull_researcher",
    "BearResearcher": ".bear_researcher",
    "ResearchDebate": ".research_debate",
    "RiskManager": ".risk_manager",
    "PositionManager": ".position_manager",
}


def __getattr__(name):
    dotpath = _LAZY.get(name)
    if dotpath is not None:
        mod = __import__(f"agents{dotpath}", fromlist=[name])
        value = getattr(mod, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "BaseAgent",
    "AgentResult",
    "TechnicalAnalyst",
    "NewsAnalyst",
    "SentimentAnalyst",
    "FundamentalsAnalyst",
    "DerivativesAnalyst",
    "TraderAgent",
    "BullResearcher",
    "BearResearcher",
    "ResearchDebate",
    "RiskManager",
    "PositionManager",
]
