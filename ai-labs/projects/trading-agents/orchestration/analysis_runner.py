"""
Shared analysis runner.

Provides analyze_symbol() — the reusable function that runs the full
analysis pipeline (data fetch → analysts → debate → final signal) and
returns an AnalysisBundle containing both normalized FinalAnalysis and
raw AgentResult objects needed by policy layers.

This module intentionally does NOT import OrderManager, Telegram bot,
EntryGuard, RiskManager, PositionManager, or any execution concern.
"""
import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from agents.technical_analyst import TechnicalAnalyst
from agents.news_analyst import NewsAnalyst
from agents.sentiment_analyst import SentimentAnalyst
from agents.fundamentals_analyst import FundamentalsAnalyst
from agents.derivatives_analyst import DerivativesAnalyst
from agents.trader_agent import TraderAgent
from agents.research_debate import ResearchDebate
from agents.base_agent import AgentResult, SignalDirection
from dataflows import data_manager as dm
from orchestration.contracts import FinalAnalysis, AnalystSignalSummary
from strategies.contracts import MarketState, StrategySignal, TechnicalState
from strategies.registry import StrategyRegistry
from utils import get_logger


logger = get_logger(__name__)


@dataclass
class AnalysisBundle:
    """Container returned by analyze_symbol().

    Holds both the normalized (serialization-friendly) FinalAnalysis
    and the raw AgentResult objects needed by demo-policy layers
    (PositionManager, RiskManager) for continued analysis.
    """
    final: FinalAnalysis
    raw_signals: Dict[str, Optional[AgentResult]]
    raw_draft: AgentResult
    raw_final: AgentResult


def _signal_summary(sig: Optional[AgentResult]) -> AnalystSignalSummary:
    """Convert an AgentResult (or None) to a normalized summary."""
    if not sig:
        return AnalystSignalSummary(
            direction="N/A",
            score=0.0,
            confidence=0.0,
            reasoning="analyst unavailable",
        )
    return AnalystSignalSummary(
        direction=sig.direction.value,
        score=round(sig.sub_score, 4),
        confidence=round(sig.confidence, 4),
        reasoning=sig.reasoning,
    )


def _derive_direction_and_action(
    final_signal: AnalystSignalSummary,
    trader_analysis: dict,
    final_sig: AgentResult,
) -> tuple:
    """Return (direction, action, hold_reason) from final signal."""
    direction = final_sig.direction.value
    action = trader_analysis.get("action", final_sig.metadata.get("final_action", "HOLD"))
    hold_reason = trader_analysis.get("hold_reason")
    return direction, action, hold_reason


def _fallback_strategy_signal(reason: str) -> Dict:
    """Return serialized observational skip when strategy layer cannot run."""
    return StrategySignal(
        strategy_id="registry",
        family="registry",
        action="skip",
        confidence=0.0,
        setup="strategy layer unavailable",
        trigger=reason,
        invalidation="n/a",
        sizing_hint="no position",
        exit_plan="n/a",
        no_trade_reason=(
            "Strategy layer skipped because technical_state or market_state is missing"
        ),
        risk_notes=["Strategy layer unavailable; FinalAnalysis.action was not changed."],
        attribution={"registry": False, "evaluated": []},
    ).to_dict()


def _load_strategy_layer_config() -> Dict:
    """Load strategy_layer config best-effort; never block analysis."""
    try:
        from utils.config_loader import config
        default_config = config.load_default_params() or {}
        if not isinstance(default_config, dict):
            return {}
        strategy_config = default_config.get("strategy_layer", {}) or {}
        if not isinstance(strategy_config, dict):
            return {}
        return strategy_config
    except Exception as exc:
        logger.warning(f"Strategy layer config unavailable: {exc}")
        return {}


def _build_strategy_signal(
    technical_analysis: dict,
    strategy_config: Optional[Dict] = None,
) -> Dict:
    """Build serialized StrategySignal from technical analyst state snapshots.

    Observational only: this function never returns execution actions and never
    modifies FinalAnalysis.action.
    """
    if strategy_config and strategy_config.get("enabled") is False:
        fallback = _fallback_strategy_signal("strategy layer disabled")
        fallback["no_trade_reason"] = "Strategy layer disabled by config"
        return fallback

    technical_state_raw = technical_analysis.get("technical_state")
    market_state_raw = technical_analysis.get("market_state")

    if not isinstance(technical_state_raw, dict) or not isinstance(market_state_raw, dict):
        return _fallback_strategy_signal("missing technical_state or market_state")

    try:
        technical_state = TechnicalState(**technical_state_raw)
        market_state = MarketState(**market_state_raw)
        signal = StrategyRegistry(strategy_config or {}).select(
            technical_state,
            market_state,
            context={"source": "analysis_runner"},
        )
        return signal.to_dict()
    except Exception as exc:
        fallback = _fallback_strategy_signal(f"strategy layer error: {exc}")
        fallback["no_trade_reason"] = "Strategy layer skipped because strategy selection failed"
        fallback["risk_notes"].append("Strategy layer raised during serialization seam.")
        return fallback


async def analyze_symbol(
    symbol: str,
    timeframe: str = "1h",
    mode: str = "full",
    _data_manager=None,
) -> AnalysisBundle:
    """Run the full analysis pipeline for one symbol.

    Does NOT touch order execution, position management, or risk gates.
    Returns an AnalysisBundle with both normalized FinalAnalysis and
    raw AgentResult objects for downstream consumers.

    Args:
        symbol: Trading pair symbol (e.g. "BTCUSDT").
        timeframe: OHLCV timeframe (e.g. "1h", "4h", "1d").
        mode: Analysis mode ("full" or "quick").
        _data_manager: Optional shared DataManager. If None, the
            module-level singleton is initialized/closed internally.

    Returns:
        AnalysisBundle containing .final (FinalAnalysis),
        .raw_signals (Dict[str, AgentResult]), .raw_draft (AgentResult),
        and .raw_final (AgentResult).

    Raises:
        RuntimeError: if the TechnicalAnalyst (required) fails.
    """
    coin = symbol.replace("USDT", "")

    shared_dm = _data_manager
    own_dm = shared_dm is None

    technical = TechnicalAnalyst()
    news = NewsAnalyst()
    sentiment = SentimentAnalyst()
    fundamentals_agent = FundamentalsAnalyst()
    derivatives = DerivativesAnalyst()
    trader = TraderAgent()
    debate = ResearchDebate()

    try:
        if own_dm:
            await dm.initialize()
        await technical.initialize()
        await news.initialize()
        await sentiment.initialize()
        await fundamentals_agent.initialize()
        await derivatives.initialize()
        await trader.initialize()
        await debate.initialize()

        ohlcv = await (shared_dm or dm).fetch_and_store_ohlcv(symbol, timeframe, limit=200)
        ticker = await (shared_dm or dm).get_ticker(symbol)
        fundamentals = await (shared_dm or dm).get_fundamentals(coin)

        if not ohlcv:
            raise RuntimeError(f"No OHLCV data for {symbol}")
        if not ticker:
            raise RuntimeError(f"No ticker data for {symbol}")

        price = ticker.get("price")

        data = {"ohlcv": ohlcv, "timeframe": timeframe, "fundamentals": fundamentals}
        results = await asyncio.gather(
            technical.analyze(symbol, data),
            news.analyze(symbol, {"coin": coin, "hours": 24}),
            sentiment.analyze(symbol, {"coin": coin}),
            fundamentals_agent.analyze(symbol, {"coin": coin, "fundamentals": fundamentals}),
            derivatives.analyze(symbol, {"coin": coin, "ohlcv": ohlcv}),
            return_exceptions=True,
        )

        analyst_names = ["technical", "news", "sentiment", "fundamentals", "derivatives"]
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                name = analyst_names[i]
                if name == "technical":
                    raise RuntimeError(
                        f"TechnicalAnalyst failed for {symbol}",
                    ) from r
                logger.warning(f"{name.title()}Analyst failed for {symbol}: {r}")
                results[i] = None

        tech, news_sig, sent_sig, fund_sig, deriv_sig = results

        if not tech:
            raise RuntimeError(
                f"TechnicalAnalyst returned no result for {symbol}"
            )

        analyst_signals_raw = {
            "technical": tech,
            "news": news_sig,
            "sentiment": sent_sig,
            "fundamentals": fund_sig,
            "derivatives": deriv_sig,
        }

        analyst_summaries = {
            name: _signal_summary(sig)
            for name, sig in analyst_signals_raw.items()
        }

        draft_signal = await trader.analyze(
            symbol, {"mode": mode, "signals": analyst_signals_raw}
        )
        research_debate = await debate.debate(symbol, analyst_signals_raw, draft_signal)
        final_signal = await trader.analyze(
            symbol,
            {"mode": mode, "signals": analyst_signals_raw, "research_debate": research_debate},
        )

        trader_analysis = final_signal.analysis.get("trader", {})
        direction, action, hold_reason = _derive_direction_and_action(
            _signal_summary(final_signal), trader_analysis, final_signal,
        )

        market_snapshot = {
            "timeframe": timeframe,
            "ohlcv_candles": len(ohlcv),
            "last_close": ohlcv[-1].get("close") if ohlcv else None,
            "ticker_price": price,
            "atr": final_signal.analysis.get("indicators", {}).get("atr", 0),
            "fundamentals_available": bool(fundamentals),
        }

        strategy_signal = _build_strategy_signal(
            technical_analysis=tech.analysis,
            strategy_config=_load_strategy_layer_config(),
        )

        normalized = FinalAnalysis(
            symbol=symbol,
            timeframe=timeframe,
            price=price,
            timestamp=datetime.now().isoformat(),
            analyst_signals=analyst_summaries,
            draft_signal=_signal_summary(draft_signal),
            research_debate=research_debate,
            final_signal=_signal_summary(final_signal),
            market_snapshot=market_snapshot,
            direction=direction,
            confidence=round(final_signal.confidence, 4),
            action=action,
            hold_reason=hold_reason,
            risk_notes=[],
            metadata={
                "mode": mode,
                "analysis_timeframe": timeframe,
                "strategy_signal": strategy_signal,
            },
        )

        return AnalysisBundle(
            final=normalized,
            raw_signals=analyst_signals_raw,
            raw_draft=draft_signal,
            raw_final=final_signal,
        )
    finally:
        await technical.close()
        await news.close()
        await sentiment.close()
        await fundamentals_agent.close()
        await derivatives.close()
        await trader.close()
        await debate.close()
        if own_dm:
            await dm.close()
