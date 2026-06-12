"""
Shared analysis orchestration layer.

Provides the normalized FinalAnalysis contract and a reusable
analyze_symbol() runner that produces analysis outputs without
touching order execution.
"""
from .contracts import FinalAnalysis, AnalystSignalSummary


def _lazy_import_analysis_runner():
    from .analysis_runner import analyze_symbol, AnalysisBundle
    return analyze_symbol, AnalysisBundle


def __getattr__(name):
    if name in ("analyze_symbol", "AnalysisBundle"):
        items = _lazy_import_analysis_runner()
        idx = 0 if name == "analyze_symbol" else 1
        value = items[idx]
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "FinalAnalysis",
    "AnalystSignalSummary",
    "AnalysisBundle",
    "analyze_symbol",
]
