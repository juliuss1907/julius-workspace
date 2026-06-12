"""
Manual real-money report policy.

Consumes normalized FinalAnalysis and produces human-centric
ManualTradeReportItem objects optimized for discretionary trading
decisions — not execution semantics.

This module intentionally imports zero execution-side dependencies
(no OrderManager, RiskManager, PositionManager, Telegram, EntryGuard,
or trading modules).  It also avoids utils and logging deps to stay
maximally lightweight.
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from typing import Dict, List, Optional

from orchestration.contracts import FinalAnalysis, AnalystSignalSummary

_DIRECTION_LABEL = {
    "bullish": "🟢 Tăng",
    "bearish": "🔴 Giảm",
    "neutral": "⚪ Trung tính",
}

_DIRECTION_VI = {
    "bullish": "tăng",
    "bearish": "giảm",
    "neutral": "trung tính",
}

_SETUP_QUALITY_THRESHOLDS = {
    "A": 0.80,
    "B": 0.70,
    "C": 0.60,
}

_UNKNOWN = "Chưa có dữ liệu trong pipeline hiện tại"
_NA = "Không áp dụng"

_SETUP_EMOJI = {"A": "🟢", "B": "🟡", "C": "🟠", "avoid": "🔴"}


@dataclass
class ManualTradeReportItem:
    """Human-centric trade idea for discretionary review.

    Optimized for clarity, caveats, and decision support —
    NOT for execution automation.
    """
    symbol: str
    direction: str
    confidence: float
    setup_quality: str                         # "A" | "B" | "C" | "avoid"
    thesis: str
    entry_idea: Optional[str] = None
    trigger: Optional[str] = None
    invalidation: Optional[str] = None
    risk_notes: List[str] = field(default_factory=list)
    supporting_factors: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    market_snapshot: Dict = field(default_factory=dict)
    source_summary: Dict[str, AnalystSignalSummary] = field(default_factory=dict)
    hold_reason: Optional[str] = None
    research_debate: Optional[Dict] = None

    news_analysis: Dict = field(default_factory=dict)
    technical_analysis: Dict = field(default_factory=dict)
    sentiment_analysis: Dict = field(default_factory=dict)
    fundamental_thesis: Dict = field(default_factory=dict)
    trading_plan: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)

    @property
    def direction_label(self) -> str:
        return _DIRECTION_LABEL.get(self.direction, self.direction)

    @property
    def direction_vi(self) -> str:
        return _DIRECTION_VI.get(self.direction, self.direction)

    @property
    def is_actionable(self) -> bool:
        return self.setup_quality != "avoid"


# -------------------------------------------------------------------
# Quality / alignment helpers (unchanged)
# -------------------------------------------------------------------


def _classify_setup_quality(direction: str, confidence: float,
                            conflicts: List[str]) -> str:
    if direction == "neutral":
        return "avoid"
    if confidence >= _SETUP_QUALITY_THRESHOLDS["A"] and not conflicts:
        return "A"
    if confidence >= _SETUP_QUALITY_THRESHOLDS["B"]:
        return "B"
    if confidence >= _SETUP_QUALITY_THRESHOLDS["C"]:
        return "C"
    return "avoid"


def _collect_alignment(analyst_signals: Dict[str, AnalystSignalSummary],
                       final_direction: str) -> tuple:
    """Return (supporting_factors, conflicts) lists."""
    supporting = []
    conflicting = []
    for name, sig in analyst_signals.items():
        if sig.direction == "N/A":
            continue
        if sig.direction == final_direction:
            supporting.append(f"{name}: {sig.reasoning}")
        elif sig.direction != "neutral" and final_direction != "neutral":
            conflicting.append(f"{name} ({sig.direction}): {sig.reasoning}")
    return supporting, conflicting


def _build_thesis(analysis: FinalAnalysis,
                  supporting: List[str]) -> str:
    """Build a concise thesis from aligned analyst reasoning."""
    parts = []
    debate = analysis.research_debate or {}
    consensus = debate.get("consensus")
    if consensus == "aligned":
        parts.append("Research debate aligns with signal.")
    elif consensus == "opposite":
        parts.append("Research debate opposes signal — elevated caution.")
    else:
        parts.append("Research debate balanced.")

    if supporting:
        parts.append("Supporting evidence:")
        for s in supporting[:3]:
            parts.append(f"  - {s}")
    else:
        parts.append("No strong analyst consensus in this direction.")

    if analysis.hold_reason:
        parts.append(f"HOLD: {analysis.hold_reason}")

    return "\n".join(parts)


def _build_invalidation(direction: str, conflicts: List[str],
                        price: Optional[float]) -> str:
    """Describe what would invalidate the thesis."""
    inval = []
    if direction == "bullish":
        inval.append("Price breaks below key support levels.")
    elif direction == "bearish":
        inval.append("Price reclaims above resistance levels.")
    else:
        return "Direction unclear — no actionable invalidation."

    if conflicts:
        inval.append("Conflicting signals to monitor:")
        for c in conflicts[:2]:
            inval.append(f"  - {c}")

    if price:
        inval.append(f"Current price: ${price:,.2f}")
    return "\n".join(inval)


def _build_entry_idea(analysis: FinalAnalysis) -> Optional[str]:
    """Derive a rough entry zone from market snapshot data."""
    ms = analysis.market_snapshot or {}
    price = analysis.price
    atr = ms.get("atr", 0)
    if not price or not atr:
        return None
    if analysis.direction == "bullish":
        return (f"Consider entry zone near ${price - atr * 0.5:,.2f} "
                f"(current: ${price:,.2f}, ATR: {atr:,.2f})")
    if analysis.direction == "bearish":
        return (f"Consider entry zone near ${price + atr * 0.5:,.2f} "
                f"(current: ${price:,.2f}, ATR: {atr:,.2f})")
    return None


# -------------------------------------------------------------------
# Analysis block builders (new)
# -------------------------------------------------------------------


def _sig_reason(signals: Dict[str, AnalystSignalSummary], name: str) -> str:
    """Get reasoning from an analyst signal, or 'N/A'."""
    sig = signals.get(name)
    if sig and sig.direction != "N/A":
        return sig.reasoning
    return _UNKNOWN


def _build_news_analysis(analysis: FinalAnalysis) -> Dict:
    signals = analysis.analyst_signals
    news_reason = _sig_reason(signals, "news")

    return {
        "tom_tat": news_reason,
        "ngay_7": _UNKNOWN,
        "ngay_30": _UNKNOWN,
        "catalyst_chinh": _UNKNOWN,
        "rui_ro_tin_tuc": _UNKNOWN,
    }


def _build_technical_analysis(analysis: FinalAnalysis) -> Dict:
    signals = analysis.analyst_signals
    tech_reason = _sig_reason(signals, "technical")
    deriv_reason = _sig_reason(signals, "derivatives")
    ms = analysis.market_snapshot or {}
    atr = ms.get("atr", 0)
    price = analysis.price

    # Try to pull partial info from reasoning
    rsi_info = _UNKNOWN
    macd_info = _UNKNOWN
    support_info = _UNKNOWN
    resistance_info = _UNKNOWN

    if tech_reason != _UNKNOWN:
        lower = tech_reason.lower()
        if "rsi" in lower:
            rsi_info = tech_reason
        if "macd" in lower:
            macd_info = tech_reason
        if "support" in lower:
            support_info = tech_reason
        if "resistance" in lower:
            resistance_info = tech_reason

    return {
        "xu_huong": tech_reason if tech_reason != _UNKNOWN else _UNKNOWN,
        "cau_truc_gia": _UNKNOWN,
        "volume": _UNKNOWN,
        "vung_ho_tro": support_info,
        "vung_khang_cu": resistance_info,
        "chi_bao": tech_reason if tech_reason != _UNKNOWN else _UNKNOWN,
        "rsi": rsi_info,
        "macd": macd_info,
        "atr": f"{atr:,.2f}" if atr else _UNKNOWN,
        "gia_hien_tai": f"${price:,.2f}" if price else _UNKNOWN,
        "derivatives": {
            "tom_tat": deriv_reason if deriv_reason != _UNKNOWN else _UNKNOWN,
            "funding_rate": _UNKNOWN,
            "open_interest": _UNKNOWN,
            "long_short_bias": _UNKNOWN,
        },
    }


def _build_sentiment_analysis(analysis: FinalAnalysis) -> Dict:
    signals = analysis.analyst_signals
    sent_reason = _sig_reason(signals, "sentiment")
    deriv_reason = _sig_reason(signals, "derivatives")

    market = {
        "tom_tat": sent_reason if sent_reason != _UNKNOWN else _UNKNOWN,
        "fear_greed": (
            sent_reason if "fear" in sent_reason.lower() or "greed" in sent_reason.lower()
            else _UNKNOWN
        ),
        "funding": (
            deriv_reason if deriv_reason != _UNKNOWN and "funding" in deriv_reason.lower()
            else _UNKNOWN
        ),
        "open_interest": (
            deriv_reason if deriv_reason != _UNKNOWN and "OI" in deriv_reason.upper()
            else _UNKNOWN
        ),
        "liquidation_heatmap": _UNKNOWN,
    }

    return {
        "market_sentiment": market,
        "social_sentiment": {
            "ct_vibe": _UNKNOWN,
            "mentions": _UNKNOWN,
            "community": _UNKNOWN,
        },
        "onchain_sentiment": {
            "holder_behavior": _UNKNOWN,
            "exchange_flows": _UNKNOWN,
            "active_addresses": _UNKNOWN,
            "staking_lockup": _UNKNOWN,
        },
        "narrative_sentiment": {
            "narrative": _UNKNOWN,
            "narrative_heat": _UNKNOWN,
            "do_ben_attention": _UNKNOWN,
        },
    }


def _build_fundamental_thesis(analysis: FinalAnalysis) -> Dict:
    signals = analysis.analyst_signals
    fund_reason = _sig_reason(signals, "fundamentals")

    return {
        "value_proposition": fund_reason if fund_reason != _UNKNOWN else _UNKNOWN,
        "vi_sao_can_blockchain": _UNKNOWN,
        "nguoi_dung_that": _UNKNOWN,
        "token_utility": _UNKNOWN,
        "value_capture": _UNKNOWN,
        "supply_unlock_risk": _UNKNOWN,
        "moat": _UNKNOWN,
        "market_opportunity": _UNKNOWN,
        "team_execution": _UNKNOWN,
        "backers": _UNKNOWN,
    }


def _build_trading_plan(analysis: FinalAnalysis) -> Dict:
    ms = analysis.market_snapshot or {}
    price = analysis.price
    atr = ms.get("atr", 0)
    direction = analysis.direction
    risk_notes = list(analysis.risk_notes)

    if direction == "bullish":
        entry = f"${price:,.2f}" if price else _UNKNOWN
        target_1 = f"${price + atr:,.2f}" if price and atr else _UNKNOWN
        target_2 = f"${price + atr * 2:,.2f}" if price and atr else _UNKNOWN
        stoploss = f"${price - atr:,.2f}" if price and atr else _UNKNOWN
        return {
            "position": "Spot ưu tiên, Futures chỉ khi quản trị rủi ro tốt",
            "setup": "Buy / Long",
            "entry": entry,
            "target_1": target_1,
            "target_2": target_2,
            "stoploss": stoploss,
            "setup_that_bai_khi": "Mất hỗ trợ chính, direction đảo chiều, confidence giảm mạnh.",
            "risk_notes": risk_notes,
        }

    if direction == "bearish":
        entry = f"${price:,.2f}" if price else _UNKNOWN
        target_1 = f"${price - atr:,.2f}" if price and atr else _UNKNOWN
        target_2 = f"${price - atr * 2:,.2f}" if price and atr else _UNKNOWN
        stoploss = f"${price + atr:,.2f}" if price and atr else _UNKNOWN
        return {
            "position": "Futures",
            "setup": "Sell / Short",
            "entry": entry,
            "target_1": target_1,
            "target_2": target_2,
            "stoploss": stoploss,
            "setup_that_bai_khi": "Giá reclaim trên kháng cự, direction đảo chiều, confidence giảm mạnh.",
            "risk_notes": risk_notes,
        }

    return {
        "position": "Không giao dịch",
        "setup": "Tránh",
        "entry": _NA,
        "target_1": _NA,
        "target_2": _NA,
        "stoploss": _NA,
        "setup_that_bai_khi": (
            "Chỉ xem xét lại khi có breakout hoặc tín hiệu rõ ràng."
        ),
        "risk_notes": risk_notes or ["Không có rủi ro đặc biệt — đang trong vùng tránh."],
    }


# -------------------------------------------------------------------
# Main conversion function
# -------------------------------------------------------------------


def final_analysis_to_report_item(
    analysis: FinalAnalysis,
) -> ManualTradeReportItem:
    """Convert a shared FinalAnalysis into a manual-trading report item.

    This is a pure function — no I/O, no execution state, no side effects.
    """
    supporting, conflicts = _collect_alignment(
        analysis.analyst_signals, analysis.direction,
    )

    setup_quality = _classify_setup_quality(
        analysis.direction, analysis.confidence, conflicts,
    )

    return ManualTradeReportItem(
        symbol=analysis.symbol,
        direction=analysis.direction,
        confidence=analysis.confidence,
        setup_quality=setup_quality,
        thesis=_build_thesis(analysis, supporting),
        entry_idea=_build_entry_idea(analysis),
        trigger=None,
        invalidation=_build_invalidation(
            analysis.direction, conflicts, analysis.price,
        ),
        risk_notes=list(analysis.risk_notes),
        supporting_factors=supporting,
        conflicts=conflicts,
        market_snapshot=dict(analysis.market_snapshot),
        source_summary=dict(analysis.analyst_signals),
        hold_reason=analysis.hold_reason,
        research_debate=analysis.research_debate,

        news_analysis=_build_news_analysis(analysis),
        technical_analysis=_build_technical_analysis(analysis),
        sentiment_analysis=_build_sentiment_analysis(analysis),
        fundamental_thesis=_build_fundamental_thesis(analysis),
        trading_plan=_build_trading_plan(analysis),
    )


# -------------------------------------------------------------------
# Markdown rendering — Vietnamese
# -------------------------------------------------------------------

_REPORT_HEADER = """# 📊 Báo cáo Giao dịch Thủ công — {date}

**Thời gian tạo:** {timestamp}
**Chế độ phân tích:** {mode}
**Số symbols đã phân tích:** {symbol_count}

---

"""


def _render_quick_summary(item: ManualTradeReportItem) -> str:
    emoji = _SETUP_EMOJI.get(item.setup_quality, "⚪")
    dir_vi = item.direction_vi.capitalize()

    if item.direction == "bullish":
        phu_hop = "Trader chủ động, ưa thích momentum tăng"
    elif item.direction == "bearish":
        phu_hop = "Trader phòng thủ, muốn hedge hoặc short"
    else:
        phu_hop = "Không phù hợp giao dịch hiện tại"

    # Extract a short "why" from thesis
    ly_do = item.supporting_factors[0] if item.supporting_factors else "Không có tín hiệu rõ ràng"

    return f"""### 1. Tóm tắt nhanh

- **Bias:** {dir_vi}
- **Độ tin cậy:** {item.confidence:.0%}
- **Chất lượng setup:** {emoji} {item.setup_quality}
- **Phù hợp với:** {phu_hop}
- **Lý do chính:** {ly_do}
"""


def _render_news_section(news: Dict) -> str:
    lines = ["### 2. Tin tức & catalyst", ""]
    lines.append(f"- **Tóm tắt:** {news.get('tom_tat', _UNKNOWN)}")
    lines.append(f"- **7 ngày qua:** {news.get('ngay_7', _UNKNOWN)}")
    lines.append(f"- **30 ngày qua:** {news.get('ngay_30', _UNKNOWN)}")
    lines.append(f"- **Catalyst chính:** {news.get('catalyst_chinh', _UNKNOWN)}")
    lines.append(f"- **Rủi ro từ tin tức:** {news.get('rui_ro_tin_tuc', _UNKNOWN)}")
    lines.append("")
    return "\n".join(lines)


def _render_technical_section(tech: Dict) -> str:
    lines = ["### 3. Phân tích kỹ thuật", ""]
    lines.append(f"- **Xu hướng:** {tech.get('xu_huong', _UNKNOWN)}")
    lines.append(f"- **Cấu trúc giá:** {tech.get('cau_truc_gia', _UNKNOWN)}")
    lines.append(f"- **Volume:** {tech.get('volume', _UNKNOWN)}")
    lines.append(f"- **Vùng hỗ trợ:** {tech.get('vung_ho_tro', _UNKNOWN)}")
    lines.append(f"- **Vùng kháng cự:** {tech.get('vung_khang_cu', _UNKNOWN)}")
    lines.append("")

    lines.append("**Chỉ báo:**")
    lines.append(f"- **RSI:** {tech.get('rsi', _UNKNOWN)}")
    lines.append(f"- **MACD:** {tech.get('macd', _UNKNOWN)}")
    lines.append(f"- **ATR:** {tech.get('atr', _UNKNOWN)}")
    lines.append(f"- **Giá hiện tại:** {tech.get('gia_hien_tai', _UNKNOWN)}")
    lines.append("")

    deriv = tech.get("derivatives", {})
    lines.append("**Derivatives:**")
    lines.append(f"- **Tóm tắt:** {deriv.get('tom_tat', _UNKNOWN)}")
    lines.append(f"- **Funding rate:** {deriv.get('funding_rate', _UNKNOWN)}")
    lines.append(f"- **Open Interest:** {deriv.get('open_interest', _UNKNOWN)}")
    lines.append(f"- **Long/short bias:** {deriv.get('long_short_bias', _UNKNOWN)}")
    lines.append("")
    return "\n".join(lines)


def _render_sentiment_section(sent: Dict) -> str:
    lines = ["### 4. Sentiment", ""]

    ms = sent.get("market_sentiment", {})
    lines.append("**Market sentiment:**")
    lines.append(f"- **Tóm tắt:** {ms.get('tom_tat', _UNKNOWN)}")
    lines.append(f"- **Fear & Greed:** {ms.get('fear_greed', _UNKNOWN)}")
    lines.append(f"- **Funding:** {ms.get('funding', _UNKNOWN)}")
    lines.append(f"- **Open Interest:** {ms.get('open_interest', _UNKNOWN)}")
    lines.append(f"- **Liquidation heatmap:** {ms.get('liquidation_heatmap', _UNKNOWN)}")
    lines.append("")

    ss = sent.get("social_sentiment", {})
    lines.append("**Social sentiment:**")
    lines.append(f"- **CT vibe:** {ss.get('ct_vibe', _UNKNOWN)}")
    lines.append(f"- **Mentions:** {ss.get('mentions', _UNKNOWN)}")
    lines.append(f"- **Community:** {ss.get('community', _UNKNOWN)}")
    lines.append("")

    os_ = sent.get("onchain_sentiment", {})
    lines.append("**On-chain sentiment:**")
    lines.append(f"- **Holder behavior:** {os_.get('holder_behavior', _UNKNOWN)}")
    lines.append(f"- **Exchange flows:** {os_.get('exchange_flows', _UNKNOWN)}")
    lines.append(f"- **Active addresses:** {os_.get('active_addresses', _UNKNOWN)}")
    lines.append(f"- **Staking/lock-up:** {os_.get('staking_lockup', _UNKNOWN)}")
    lines.append("")

    ns = sent.get("narrative_sentiment", {})
    lines.append("**Narrative sentiment:**")
    lines.append(f"- **Narrative:** {ns.get('narrative', _UNKNOWN)}")
    lines.append(f"- **Narrative heat:** {ns.get('narrative_heat', _UNKNOWN)}")
    lines.append(f"- **Độ bền attention:** {ns.get('do_ben_attention', _UNKNOWN)}")
    lines.append("")
    return "\n".join(lines)


def _render_fundamental_section(fund: Dict) -> str:
    lines = ["### 5. Thesis cơ bản", ""]
    lines.append(f"- **Value proposition:** {fund.get('value_proposition', _UNKNOWN)}")
    lines.append(f"- **Vì sao cần blockchain:** {fund.get('vi_sao_can_blockchain', _UNKNOWN)}")
    lines.append(f"- **Người dùng thật:** {fund.get('nguoi_dung_that', _UNKNOWN)}")
    lines.append(f"- **Token utility:** {fund.get('token_utility', _UNKNOWN)}")
    lines.append(f"- **Value capture:** {fund.get('value_capture', _UNKNOWN)}")
    lines.append(f"- **Supply / unlock risk:** {fund.get('supply_unlock_risk', _UNKNOWN)}")
    lines.append(f"- **Moat:** {fund.get('moat', _UNKNOWN)}")
    lines.append(f"- **Market opportunity:** {fund.get('market_opportunity', _UNKNOWN)}")
    lines.append(f"- **Team & execution:** {fund.get('team_execution', _UNKNOWN)}")
    lines.append(f"- **Backers:** {fund.get('backers', _UNKNOWN)}")
    lines.append("")
    return "\n".join(lines)


def _render_trading_plan_section(tp: Dict) -> str:
    lines = ["### 6. Kế hoạch giao dịch", ""]
    lines.append(f"- **Position:** {tp.get('position', _UNKNOWN)}")
    lines.append(f"- **Setup:** {tp.get('setup', _UNKNOWN)}")
    lines.append(f"- **Entry:** {tp.get('entry', _UNKNOWN)}")
    lines.append(f"- **Target 1:** {tp.get('target_1', _UNKNOWN)}")
    lines.append(f"- **Target 2:** {tp.get('target_2', _UNKNOWN)}")
    lines.append(f"- **Stoploss:** {tp.get('stoploss', _UNKNOWN)}")
    lines.append(f"- **Setup thất bại khi:** {tp.get('setup_that_bai_khi', _UNKNOWN)}")

    risk = tp.get("risk_notes", [])
    if risk:
        lines.append("- **Risk notes:**")
        for r in risk:
            lines.append(f"  - {r}")
    lines.append("")
    return "\n".join(lines)


def _render_trade_card(item: ManualTradeReportItem) -> str:
    direction_icon = {"bullish": "📈", "bearish": "📉", "neutral": "➖"}.get(
        item.direction, "❓",
    )
    emoji = _SETUP_EMOJI.get(item.setup_quality, "⚪")
    heading = (
        f"## {direction_icon} {item.symbol} — "
        f"Xu hướng {item.direction_vi.capitalize()} / Setup {emoji} {item.setup_quality}"
    )

    lines = [heading, ""]
    lines.append(_render_quick_summary(item))
    lines.append(_render_news_section(item.news_analysis))
    lines.append(_render_technical_section(item.technical_analysis))
    lines.append(_render_sentiment_section(item.sentiment_analysis))
    lines.append(_render_fundamental_section(item.fundamental_thesis))
    lines.append(_render_trading_plan_section(item.trading_plan))
    lines.append("")
    return "\n".join(lines)


def _render_section(title: str, items: List[ManualTradeReportItem]) -> str:
    if not items:
        return ""
    lines = [f"## {title}", "", f"_{len(items)} setup(s)_", ""]
    for item in items:
        lines.append(_render_trade_card(item))
    return "\n".join(lines)


def _sort_setups(items: List[ManualTradeReportItem]) -> List[ManualTradeReportItem]:
    """Sort report sections by trader usefulness: quality first, confidence second."""
    quality_rank = {"A": 0, "B": 1, "C": 2, "avoid": 3}
    return sorted(
        items,
        key=lambda item: (
            quality_rank.get(item.setup_quality, 4),
            -item.confidence,
            item.symbol,
        ),
    )


def _append_final_footer(report: str) -> str:
    """Append the footer without creating duplicate horizontal rules."""
    if report.rstrip().endswith("---"):
        return report.rstrip() + "\n\n*Báo cáo được tạo bởi trading-agents manual path. Chỉ dùng để tham khảo.*\n"
    return report + "---\n\n*Báo cáo được tạo bởi trading-agents manual path. Chỉ dùng để tham khảo.*\n"


def render_markdown_report(
    items: List[ManualTradeReportItem],
    mode: str = "full",
) -> str:
    """Render a flat markdown report string from a list of report items."""
    today = date.today().isoformat()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = _REPORT_HEADER.format(
        date=today, timestamp=now, mode=mode, symbol_count=len(items),
    )

    bullish = _sort_setups([
        i for i in items if i.direction == "bullish" and i.is_actionable
    ])
    bearish = _sort_setups([
        i for i in items if i.direction == "bearish" and i.is_actionable
    ])
    neutral = _sort_setups([
        i for i in items if i.direction == "neutral" or not i.is_actionable
    ])

    report += _render_section("🟢 Xu hướng Tăng", bullish)
    report += _render_section("🔴 Xu hướng Giảm", bearish)
    if neutral:
        report += _render_section("⚪ Trung tính / Tránh / Xung đột cao", neutral)

    all_risk_notes = []
    for item in items:
        all_risk_notes.extend(item.risk_notes)
    if all_risk_notes:
        report += "## ⚠️ Ghi chú Rủi ro Phiên\n\n"
        for rn in all_risk_notes:
            report += f"- {rn}\n"
        report += "\n"

    return _append_final_footer(report)
