#!/usr/bin/env python3
"""Tests for policies/manual_report.py — no execution deps required."""
import asyncio
import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from orchestration.contracts import FinalAnalysis, AnalystSignalSummary
from policies.manual_report import (
    ManualTradeReportItem,
    _UNKNOWN,
    final_analysis_to_report_item,
    render_markdown_report,
)


ERRORS = []


def assert_true(cond, msg=""):
    if not cond:
        msg = msg or "assertion failed"
        ERRORS.append(msg)


def assert_eq(a, b, msg=""):
    if a != b:
        msg = msg or f"expected {b!r}, got {a!r}"
        ERRORS.append(msg)


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------


def _make_analyst_signals(**overrides):
    """Build a dict of AnalystSignalSummary with sensible defaults."""
    defaults = {
        "technical": AnalystSignalSummary(
            direction="bullish", score=0.75, confidence=0.70,
            reasoning="RSI bullish, MACD crossover on 1h",
        ),
        "news": AnalystSignalSummary(
            direction="neutral", score=0.50, confidence=0.40,
            reasoning="no significant news in past 24h",
        ),
        "sentiment": AnalystSignalSummary(
            direction="bullish", score=0.65, confidence=0.55,
            reasoning="Fear & Greed neutral, Polymarket odds rising",
        ),
        "fundamentals": AnalystSignalSummary(
            direction="neutral", score=0.52, confidence=0.45,
            reasoning="FDV/market cap ratio moderate",
        ),
        "derivatives": AnalystSignalSummary(
            direction="bullish", score=0.68, confidence=0.60,
            reasoning="funding neutral, OI rising with price",
        ),
    }
    defaults.update(overrides)
    return defaults


def _make_final_analysis(**overrides) -> FinalAnalysis:
    defaults = {
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "price": 68000.0,
        "timestamp": datetime.now().isoformat(),
        "analyst_signals": _make_analyst_signals(),
        "draft_signal": AnalystSignalSummary(
            direction="bullish", score=0.72, confidence=0.62,
            reasoning="draft: strong bullish consensus",
        ),
        "research_debate": {
            "consensus": "aligned",
            "confidence_adjustment": 0.05,
            "winner": "bull",
        },
        "final_signal": AnalystSignalSummary(
            direction="bullish", score=0.74, confidence=0.67,
            reasoning="final: confirmed bullish",
        ),
        "market_snapshot": {
            "timeframe": "1h", "ohlcv_candles": 200,
            "last_close": 68000.0, "ticker_price": 68000.0,
            "atr": 1500.0, "fundamentals_available": True,
        },
        "direction": "bullish",
        "confidence": 0.67,
        "action": "BUY",
        "hold_reason": None,
        "risk_notes": ["ATR elevated — consider smaller position"],
        "metadata": {"mode": "full"},
    }
    defaults.update(overrides)
    return FinalAnalysis(**defaults)


def _make_strategy_signal(**overrides):
    signal = {
        "strategy_id": "trend_following",
        "family": "trend_following",
        "action": "long",
        "confidence": 0.68,
        "setup": "EMA20 > EMA50 and price above trend stack",
        "trigger": "Close held above EMA20",
        "invalidation": "Close below EMA50",
        "sizing_hint": "Half size until replay attribution validates edge",
        "exit_plan": "Exit on invalidation or momentum rollover",
        "no_trade_reason": None,
        "risk_notes": ["Observational only; not execution approval."],
        "attribution": {
            "registry": True,
            "evaluated": [
                {"strategy_id": "volatility_skip", "action": "hold", "confidence": 0.90},
                {"strategy_id": "trend_following", "action": "long", "confidence": 0.68},
            ],
        },
    }
    signal.update(overrides)
    return signal


# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------


def test_bullish_analysis_produces_report_item():
    fa = _make_final_analysis()
    item = final_analysis_to_report_item(fa)

    assert isinstance(item, ManualTradeReportItem)
    assert_eq(item.symbol, "BTCUSDT")
    assert_eq(item.direction, "bullish")
    assert_eq(item.confidence, 0.67)
    assert_true(item.setup_quality in ("A", "B", "C", "avoid"))
    assert_true(len(item.thesis) > 0)
    assert isinstance(item.supporting_factors, list)
    assert isinstance(item.conflicts, list)
    assert_true(len(item.supporting_factors) > 0)
    assert_true(item.is_actionable)

    # New analysis blocks must be populated
    assert isinstance(item.news_analysis, dict)
    assert_true(len(item.news_analysis) > 0, "news_analysis should be populated")
    assert isinstance(item.technical_analysis, dict)
    assert_true(len(item.technical_analysis) > 0, "technical_analysis should be populated")
    assert isinstance(item.sentiment_analysis, dict)
    assert_true(len(item.sentiment_analysis) > 0, "sentiment_analysis should be populated")
    assert isinstance(item.fundamental_thesis, dict)
    assert_true(len(item.fundamental_thesis) > 0, "fundamental_thesis should be populated")
    assert isinstance(item.trading_plan, dict)
    assert_true(len(item.trading_plan) > 0, "trading_plan should be populated")


def test_bearish_analysis_produces_report_item():
    bearish_signals = _make_analyst_signals(
        technical=AnalystSignalSummary(
            direction="bearish", score=0.28, confidence=0.70,
            reasoning="RSI overbought, bearish divergence",
        ),
        derivatives=AnalystSignalSummary(
            direction="bearish", score=0.32, confidence=0.60,
            reasoning="funding very positive — long crowded",
        ),
        sentiment=AnalystSignalSummary(
            direction="bearish", score=0.35, confidence=0.50,
            reasoning="Extreme greed reading",
        ),
    )
    fa = _make_final_analysis(
        direction="bearish",
        action="SELL",
        confidence=0.72,
        analyst_signals=bearish_signals,
        final_signal=AnalystSignalSummary(
            direction="bearish", score=0.28, confidence=0.72,
            reasoning="final: confirmed bearish",
        ),
        draft_signal=AnalystSignalSummary(
            direction="bearish", score=0.30, confidence=0.70,
            reasoning="draft: bearish",
        ),
    )
    item = final_analysis_to_report_item(fa)

    assert_eq(item.direction, "bearish")
    assert_eq(item.setup_quality, "B")
    assert_true(len(item.supporting_factors) >= 1)
    assert_true(item.is_actionable)
    assert_true("resistance" in item.invalidation.lower() or "reclaims" in item.invalidation.lower())


def test_neutral_analysis_gets_avoid():
    fa = _make_final_analysis(
        direction="neutral",
        action="HOLD",
        confidence=0.35,
        hold_reason="conflicting analyst directions",
        analyst_signals=_make_analyst_signals(
            technical=AnalystSignalSummary(
                direction="bullish", score=0.60, confidence=0.55,
                reasoning="slightly bullish",
            ),
            derivatives=AnalystSignalSummary(
                direction="bearish", score=0.35, confidence=0.50,
                reasoning="slightly bearish",
            ),
        ),
        final_signal=AnalystSignalSummary(
            direction="neutral", score=0.48, confidence=0.35,
            reasoning="conflicting signals",
        ),
        draft_signal=AnalystSignalSummary(
            direction="neutral", score=0.50, confidence=0.30,
            reasoning="no clear direction",
        ),
        research_debate={"consensus": "balanced", "confidence_adjustment": 0.0,
                         "winner": "balanced"},
    )
    item = final_analysis_to_report_item(fa)

    assert_eq(item.setup_quality, "avoid")
    assert_eq(item.is_actionable, False)
    assert_eq(item.direction, "neutral")
    assert_eq(item.hold_reason, "conflicting analyst directions")


def test_high_confidence_no_conflicts_gets_a():
    aligned = _make_analyst_signals(
        technical=AnalystSignalSummary(
            direction="bullish", score=0.85, confidence=0.80,
            reasoning="strong multi-timeframe alignment",
        ),
    )
    fa = _make_final_analysis(
        direction="bullish",
        action="BUY",
        confidence=0.85,
        analyst_signals=aligned,
        final_signal=AnalystSignalSummary(
            direction="bullish", score=0.85, confidence=0.85,
            reasoning="strong bull thesis",
        ),
    )
    item = final_analysis_to_report_item(fa)

    assert_eq(item.setup_quality, "A")
    assert_eq(item.confidence, 0.85)
    assert_true(len(item.conflicts) == 0)


def test_low_confidence_gets_avoid():
    fa = _make_final_analysis(
        direction="bullish",
        action="BUY",
        confidence=0.52,
        analyst_signals=_make_analyst_signals(
            technical=AnalystSignalSummary(
                direction="bullish", score=0.55, confidence=0.52,
                reasoning="weak signal",
            ),
        ),
        final_signal=AnalystSignalSummary(
            direction="bullish", score=0.55, confidence=0.52,
            reasoning="marginal bullish",
        ),
    )
    item = final_analysis_to_report_item(fa)

    assert_eq(item.setup_quality, "avoid")


def test_report_item_serialization():
    fa = _make_final_analysis()
    item = final_analysis_to_report_item(fa)

    d = item.to_dict()
    assert isinstance(d, dict)
    assert_eq(d["symbol"], "BTCUSDT")
    assert_eq(d["direction"], "bullish")
    assert isinstance(d["supporting_factors"], list)
    assert isinstance(d["conflicts"], list)

    import json
    json_str = json.dumps(d)
    restored = json.loads(json_str)
    assert_eq(restored["symbol"], "BTCUSDT")
    assert_eq(restored["setup_quality"], item.setup_quality)


def test_manual_report_item_preserves_strategy_signal():
    strategy_signal = _make_strategy_signal()
    fa = _make_final_analysis(
        action="BUY",
        metadata={"mode": "full", "strategy_signal": strategy_signal},
    )

    item = final_analysis_to_report_item(fa)

    assert_true(isinstance(item.strategy_signal, dict), "strategy_signal should be copied")
    assert_eq(item.strategy_signal["strategy_id"], "trend_following")
    assert_eq(item.strategy_signal["action"], "long")
    assert_eq(item.strategy_signal["confidence"], 0.68)
    assert_eq(fa.action, "BUY", "strategy attribution must not alter FinalAnalysis.action")


def test_manual_report_item_strategy_signal_defaults_to_empty_dict():
    fa = _make_final_analysis(metadata={"mode": "full"})
    item = final_analysis_to_report_item(fa)

    assert_true(isinstance(item.strategy_signal, dict))
    assert_eq(item.strategy_signal, {})


def test_report_item_serialization_includes_strategy_signal():
    strategy_signal = _make_strategy_signal()
    fa = _make_final_analysis(
        metadata={"mode": "full", "strategy_signal": strategy_signal},
    )
    item = final_analysis_to_report_item(fa)

    d = item.to_dict()

    assert_true("strategy_signal" in d)
    assert_eq(d["strategy_signal"]["strategy_id"], "trend_following")
    assert_eq(d["strategy_signal"]["action"], "long")


def test_markdown_renderer_produces_output():
    fa1 = _make_final_analysis()
    item1 = final_analysis_to_report_item(fa1)

    fa2 = _make_final_analysis(
        symbol="ETHUSDT", price=3200.0, direction="bearish",
        action="SELL", confidence=0.62,
        analyst_signals=_make_analyst_signals(
            technical=AnalystSignalSummary(
                direction="bearish", score=0.35, confidence=0.62,
                reasoning="RSI bearish divergence",
            ),
        ),
        final_signal=AnalystSignalSummary(
            direction="bearish", score=0.35, confidence=0.62,
            reasoning="bearish thesis",
        ),
        draft_signal=AnalystSignalSummary(
            direction="bearish", score=0.38, confidence=0.60,
            reasoning="draft bearish",
        ),
    )
    item2 = final_analysis_to_report_item(fa2)

    md = render_markdown_report([item1, item2])
    assert_true(isinstance(md, str))
    assert_true(len(md) > 200)
    assert_true("BTCUSDT" in md)
    assert_true("ETHUSDT" in md)
    assert_true("Xu hướng Tăng" in md)
    assert_true("Xu hướng Giảm" in md)
    assert_true("---\n---" not in md, "renderer should not produce duplicate horizontal rules")


def test_markdown_renderer_includes_strategy_layer_observational_section():
    strategy_signal = _make_strategy_signal()
    fa = _make_final_analysis(
        metadata={"mode": "full", "strategy_signal": strategy_signal},
    )
    item = final_analysis_to_report_item(fa)

    md = render_markdown_report([item])

    assert_true("Strategy Layer (Observational)" in md, "missing strategy section")
    assert_true("trend_following" in md, "missing selected strategy id")
    assert_true("long" in md, "missing strategy action")
    assert_true("68%" in md or "0.68" in md, "missing strategy confidence")
    assert_true("volatility_skip:hold@0.90" in md, "missing evaluated attribution")
    assert_true("trend_following:long@0.68" in md, "missing evaluated attribution")
    assert_true(
        "does not override FinalAnalysis.action" in md,
        "strategy section must state observational-only semantics",
    )


def test_markdown_renderer_omits_strategy_section_when_absent():
    fa = _make_final_analysis(metadata={"mode": "full"})
    item = final_analysis_to_report_item(fa)

    md = render_markdown_report([item])

    assert_true("Strategy Layer (Observational)" not in md)


def test_markdown_renderer_sorts_section_by_quality_and_confidence():
    """Best setups should appear first inside each directional section."""
    low = final_analysis_to_report_item(_make_final_analysis(
        symbol="LOWUSDT",
        direction="bullish",
        confidence=0.62,
        final_signal=AnalystSignalSummary(
            direction="bullish", score=0.62, confidence=0.62,
            reasoning="low confidence bullish",
        ),
    ))
    high = final_analysis_to_report_item(_make_final_analysis(
        symbol="HIGHUSDT",
        direction="bullish",
        confidence=0.86,
        analyst_signals=_make_analyst_signals(
            technical=AnalystSignalSummary(
                direction="bullish", score=0.86, confidence=0.86,
                reasoning="strong bullish setup",
            ),
            sentiment=AnalystSignalSummary(
                direction="bullish", score=0.80, confidence=0.80,
                reasoning="aligned sentiment",
            ),
            derivatives=AnalystSignalSummary(
                direction="bullish", score=0.82, confidence=0.82,
                reasoning="aligned derivatives",
            ),
        ),
        final_signal=AnalystSignalSummary(
            direction="bullish", score=0.86, confidence=0.86,
            reasoning="high confidence bullish",
        ),
    ))

    md = render_markdown_report([low, high])
    assert_true(md.index("HIGHUSDT") < md.index("LOWUSDT"),
                "higher-quality bullish setup should render first")


def test_policy_imports_no_execution_modules():
    """Manual report policy must not load execution-side modules."""
    before = set(sys.modules.keys())

    from policies.manual_report import final_analysis_to_report_item
    _ = final_analysis_to_report_item

    after = set(sys.modules.keys())
    new = after - before
    exec_keywords = (
        "risk_manager", "position_manager", "order_manager",
        "entry_guard", "trade_notifier", "telegram_bot",
        "reconciliation", "runtime_health", "trading.",
    )
    leaked = [m for m in new for kw in exec_keywords if kw in m]
    assert_true(not leaked, f"Execution modules leaked: {leaked}")


def test_cli_help_exits_zero():
    """python generate_manual_trade_report.py --help must exit 0 without importing heavy deps."""
    script = str(project_root / "scripts" / "generate_manual_trade_report.py")
    result = subprocess.run(
        [sys.executable, script, "--help"],
        capture_output=True, text=True, timeout=15,
    )
    assert_eq(result.returncode, 0, f"--help exit code: {result.returncode}")
    assert_true("usage:" in result.stdout.lower() or "--help" in result.stdout.lower(),
                "help output should contain usage info")


def test_policy_module_no_utils_import():
    """policies.manual_report must not import from utils in a fresh process."""
    code = (
        "import sys; sys.path.insert(0, '.'); "
        "from policies.manual_report import ManualTradeReportItem; "
        "assert 'utils' not in [m for m in sys.modules if 'policies.manual_report' in m], 'utils leaked!'; "
        "print('OK')"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=10,
        cwd=str(project_root),
    )
    assert_eq(result.returncode, 0,
              f"import failed: {result.stderr.strip()}")
    assert_true("OK" in result.stdout)


def test_manual_report_default_output_is_flat():
    """Default manual report output should be one flat artifact under reports/."""
    from scripts.generate_manual_trade_report import _default_output_path

    out_path = _default_output_path("2026-06-12")
    assert_eq(out_path.parent, project_root / "reports")
    assert_eq(out_path.name, "manual-trade-report-2026-06-12.md")
    assert_true("manual" not in out_path.relative_to(project_root).parts[:-1],
                f"default output should not create nested manual dir: {out_path}")


def test_cli_help_mentions_flat_default_path():
    """--help must mention the flat default path but NOT the old nested path."""
    script = str(project_root / "scripts" / "generate_manual_trade_report.py")
    result = subprocess.run(
        [sys.executable, script, "--help"],
        capture_output=True, text=True, timeout=15,
    )
    assert_eq(result.returncode, 0, f"--help exit code: {result.returncode}")
    # argparse wraps long help lines — collapse whitespace for substring checks
    flat = result.stdout.replace("\n", " ").replace("  ", " ")
    assert_true("reports/manual-trade-" in flat,
                f"--help should mention flat default path prefix.  Got: {flat[:400]}")
    assert_true("reports/manual/manual-trade-report" not in flat,
                f"--help must NOT mention old nested manual/ dir.  Got: {flat[:400]}")


def test_custom_output_creates_parent_dirs():
    """Custom --output path must mkdir parents before writing."""
    import tempfile

    from scripts.generate_manual_trade_report import _write_output

    with tempfile.TemporaryDirectory() as tmp:
        nested = Path(tmp) / "sub" / "deep" / "report.md"
        assert_true(not nested.parent.exists(),
                    "parent should NOT exist before write")
        _write_output(nested, "hello")
        assert_true(nested.exists(), "output file must exist after write")
        assert_eq(nested.read_text(), "hello")


def test_manual_report_batch_continues_when_one_symbol_fails():
    """Batch analysis continues past individual symbol failures."""
    from scripts.generate_manual_trade_report import _analyze_symbols

    class _FakeBundle:
        def __init__(self, final):
            self.final = final

    async def _fake_analyze(symbol, mode="full"):
        if symbol == "BADUSDT":
            raise ValueError("bad fixture")
        fa = _make_final_analysis(symbol=symbol)
        return _FakeBundle(fa)

    def _fake_log_warning(msg, *args, **kwargs):
        pass

    def _fake_log_info(msg, *args, **kwargs):
        pass

    class _FakeLogger:
        def info(self, msg, *args, **kwargs):
            pass
        def warning(self, msg, *args, **kwargs):
            pass

    items = asyncio.run(_analyze_symbols(
        ["BTCUSDT", "BADUSDT", "ETHUSDT"],
        mode="quick",
        analyze_symbol_fn=_fake_analyze,
        final_analysis_to_report_item_fn=final_analysis_to_report_item,
        manual_item_cls=ManualTradeReportItem,
        logger=_FakeLogger(),
    ))

    assert_eq(len(items), 3, f"expected 3 items, got {len(items)}")
    assert_eq(items[0].symbol, "BTCUSDT")
    assert_true(items[0].is_actionable,
                f"BTCUSDT should be actionable, got {items[0].setup_quality}")
    assert_eq(items[1].symbol, "BADUSDT")
    assert_eq(items[1].setup_quality, "avoid")
    assert_eq(items[1].confidence, 0.0)
    assert_eq(items[1].direction, "neutral")
    assert_true("Analysis unavailable" in items[1].thesis,
                f"thesis should mention unavailability: {items[1].thesis}")
    assert_true(len(items[1].risk_notes) >= 1,
                f"expected at least 1 risk note, got {len(items[1].risk_notes)}")
    assert_true("ValueError" in items[1].risk_notes[0],
                f"risk_note should contain ValueError: {items[1].risk_notes[0]}")
    assert_true("bad fixture" in items[1].risk_notes[0],
                f"risk_note should contain error message: {items[1].risk_notes[0]}")
    assert_eq(items[2].symbol, "ETHUSDT")
    assert_true(items[2].is_actionable,
                f"ETHUSDT should be actionable, got {items[2].setup_quality}")


def test_manual_report_batch_preserves_symbol_order():
    """Output symbols order matches input order even with one failure."""
    from scripts.generate_manual_trade_report import _analyze_symbols

    class _FakeBundle:
        def __init__(self, final):
            self.final = final

    call_order = []

    async def _fake_analyze(symbol, mode="full"):
        call_order.append(symbol)
        if symbol == "FAILUSDT":
            raise RuntimeError("simulated crash")
        fa = _make_final_analysis(symbol=symbol)
        return _FakeBundle(fa)

    class _FakeLogger:
        def info(self, msg, *args, **kwargs):
            pass
        def warning(self, msg, *args, **kwargs):
            pass

    symbols_in = ["ETHUSDT", "FAILUSDT", "BTCUSDT", "SOLUSDT"]
    items = asyncio.run(_analyze_symbols(
        symbols_in,
        mode="quick",
        analyze_symbol_fn=_fake_analyze,
        final_analysis_to_report_item_fn=final_analysis_to_report_item,
        manual_item_cls=ManualTradeReportItem,
        logger=_FakeLogger(),
    ))

    assert_eq(len(items), 4)
    for i, sym in enumerate(symbols_in):
        assert_eq(items[i].symbol, sym,
                  f"position {i}: expected {sym}, got {items[i].symbol}")


def test_manual_report_batch_reuses_shared_data_manager():
    """Real batch path should initialize one DataManager and pass it through all symbols."""
    from scripts.generate_manual_trade_report import _analyze_symbols

    class _FakeBundle:
        def __init__(self, final):
            self.final = final

    class _FakeDataManager:
        def __init__(self):
            self.initialize_calls = 0
            self.close_calls = 0

        async def initialize(self):
            self.initialize_calls += 1

        async def close(self):
            self.close_calls += 1

    class _FakeLogger:
        def info(self, msg, *args, **kwargs):
            pass
        def warning(self, msg, *args, **kwargs):
            pass

    fake_dm = _FakeDataManager()
    seen_data_managers = []

    async def _fake_analyze(symbol, mode="full", _data_manager=None):
        seen_data_managers.append(_data_manager)
        return _FakeBundle(_make_final_analysis(symbol=symbol))

    items = asyncio.run(_analyze_symbols(
        ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        mode="quick",
        analyze_symbol_fn=_fake_analyze,
        final_analysis_to_report_item_fn=final_analysis_to_report_item,
        manual_item_cls=ManualTradeReportItem,
        logger=_FakeLogger(),
        data_manager=fake_dm,
    ))

    assert_eq(len(items), 3)
    assert_eq(fake_dm.initialize_calls, 1)
    assert_eq(fake_dm.close_calls, 1)
    assert_eq(seen_data_managers, [fake_dm, fake_dm, fake_dm])


def test_vietnamese_markdown_has_required_sections():
    """Report markdown must contain all 6 Vietnamese section headings."""
    fa = _make_final_analysis()
    item = final_analysis_to_report_item(fa)
    md = render_markdown_report([item])

    assert_true("Tóm tắt nhanh" in md, "missing Tóm tắt nhanh")
    assert_true("Tin tức & catalyst" in md, "missing Tin tức & catalyst")
    assert_true("Phân tích kỹ thuật" in md, "missing Phân tích kỹ thuật")
    assert_true("Sentiment" in md, "missing Sentiment")
    assert_true("Thesis cơ bản" in md, "missing Thesis cơ bản")
    assert_true("Kế hoạch giao dịch" in md, "missing Kế hoạch giao dịch")


def test_vietnamese_markdown_trading_plan_labels():
    """Trading plan section must contain all required labels."""
    fa = _make_final_analysis()
    item = final_analysis_to_report_item(fa)
    md = render_markdown_report([item])

    assert_true("Position:" in md, "missing Position")
    assert_true("Setup:" in md, "missing Setup")
    assert_true("Entry:" in md, "missing Entry")
    assert_true("Target 1:" in md, "missing Target 1")
    assert_true("Target 2:" in md, "missing Target 2")
    assert_true("Stoploss:" in md, "missing Stoploss")
    assert_true("Setup thất bại khi:" in md, "missing Setup thất bại khi")


def test_vietnamese_markdown_has_unavailable_markers():
    """Fields without source data must show the unknown marker."""
    fa = _make_final_analysis()
    item = final_analysis_to_report_item(fa)
    md = render_markdown_report([item])

    assert_true("Chưa có dữ liệu trong pipeline hiện tại" in md,
                "must have unknown-data markers")


def test_vietnamese_report_header_is_vietnamese():
    """Report header must be Vietnamese."""
    fa = _make_final_analysis()
    item = final_analysis_to_report_item(fa)
    md = render_markdown_report([item])

    assert_true("Báo cáo Giao dịch Thủ công" in md,
                "header should be Vietnamese")


def test_trading_plan_for_neutral_is_avoid():
    """Neutral/avoid items must have Không giao dịch and Tránh setup."""
    fa = _make_final_analysis(
        direction="neutral",
        action="HOLD",
        confidence=0.35,
    )
    item = final_analysis_to_report_item(fa)
    tp = item.trading_plan

    assert_eq(tp["position"], "Không giao dịch")
    assert_eq(tp["setup"], "Tránh")
    assert_eq(tp["entry"], "Không áp dụng")
    assert_eq(tp["target_1"], "Không áp dụng")
    assert_eq(tp["target_2"], "Không áp dụng")
    assert_eq(tp["stoploss"], "Không áp dụng")


def test_trading_plan_for_bullish_has_targets():
    """Bullish trading plan must derive entry/target/stoploss from price+ATR."""
    fa = _make_final_analysis(price=68000.0)
    item = final_analysis_to_report_item(fa)
    tp = item.trading_plan

    assert_true("$" in tp["entry"], f"entry should contain dollar amount: {tp['entry']}")
    assert_true("$" in tp["target_1"], f"target_1 should contain dollar amount: {tp['target_1']}")
    assert_true("$" in tp["target_2"], f"target_2 should contain dollar amount: {tp['target_2']}")
    assert_true("$" in tp["stoploss"], f"stoploss should contain dollar amount: {tp['stoploss']}")


def test_manual_report_item_backward_compat():
    """ManualTradeReportItem can be constructed without new analysis fields."""
    item = ManualTradeReportItem(
        symbol="MINUSDT",
        direction="bullish",
        confidence=0.65,
        setup_quality="B",
        thesis="simple thesis",
    )
    assert_eq(item.symbol, "MINUSDT")
    assert_eq(item.direction, "bullish")
    assert isinstance(item.news_analysis, dict)
    assert isinstance(item.technical_analysis, dict)
    assert isinstance(item.sentiment_analysis, dict)
    assert isinstance(item.fundamental_thesis, dict)
    assert isinstance(item.trading_plan, dict)


def test_all_na_signals_produces_only_unknown_markers():
    """When ALL analyst signals are N/A, every user-facing field must
    render 'Chưa có dữ liệu trong pipeline hiện tại' — no other fallbacks."""
    na_signal = AnalystSignalSummary(
        direction="N/A", score=0.0, confidence=0.0,
        reasoning="analyst unavailable",
    )
    na_signals = {
        "technical": na_signal,
        "news": na_signal,
        "sentiment": na_signal,
        "fundamentals": na_signal,
        "derivatives": na_signal,
    }
    fa = _make_final_analysis(
        analyst_signals=na_signals,
        direction="neutral",
        action="HOLD",
        confidence=0.0,
        final_signal=AnalystSignalSummary(
            direction="neutral", score=0.0, confidence=0.0,
            reasoning="no signals",
        ),
        draft_signal=AnalystSignalSummary(
            direction="neutral", score=0.0, confidence=0.0,
            reasoning="no draft",
        ),
        price=None,
        market_snapshot={},
    )
    item = final_analysis_to_report_item(fa)
    md = render_markdown_report([item])

    assert_true(_UNKNOWN in md,
                f"must contain '{_UNKNOWN}' when all signals are N/A")

    bad_fallbacks = [
        "Không có tin tức đáng chú ý",
        "Dữ liệu hạn chế từ pipeline hiện tại",
        "N/A",
    ]
    for bad in bad_fallbacks:
        assert_true(bad not in md,
                    f"must NOT contain fallback '{bad}' when signals are N/A")


def run_tests():
    tests = [
        ("bullish_analysis_produces_report_item", test_bullish_analysis_produces_report_item),
        ("bearish_analysis_produces_report_item", test_bearish_analysis_produces_report_item),
        ("neutral_analysis_gets_avoid", test_neutral_analysis_gets_avoid),
        ("high_confidence_no_conflicts_gets_a", test_high_confidence_no_conflicts_gets_a),
        ("low_confidence_gets_avoid", test_low_confidence_gets_avoid),
        ("report_item_serialization", test_report_item_serialization),
        ("manual_report_item_preserves_strategy_signal", test_manual_report_item_preserves_strategy_signal),
        ("manual_report_item_strategy_signal_defaults_to_empty_dict", test_manual_report_item_strategy_signal_defaults_to_empty_dict),
        ("report_item_serialization_includes_strategy_signal", test_report_item_serialization_includes_strategy_signal),
        ("markdown_renderer_produces_output", test_markdown_renderer_produces_output),
        ("markdown_renderer_includes_strategy_layer_observational_section", test_markdown_renderer_includes_strategy_layer_observational_section),
        ("markdown_renderer_omits_strategy_section_when_absent", test_markdown_renderer_omits_strategy_section_when_absent),
        ("markdown_renderer_sorts_section_by_quality_and_confidence", test_markdown_renderer_sorts_section_by_quality_and_confidence),
        ("vietnamese_markdown_has_required_sections", test_vietnamese_markdown_has_required_sections),
        ("vietnamese_markdown_trading_plan_labels", test_vietnamese_markdown_trading_plan_labels),
        ("vietnamese_markdown_has_unavailable_markers", test_vietnamese_markdown_has_unavailable_markers),
        ("vietnamese_report_header_is_vietnamese", test_vietnamese_report_header_is_vietnamese),
        ("trading_plan_for_neutral_is_avoid", test_trading_plan_for_neutral_is_avoid),
        ("trading_plan_for_bullish_has_targets", test_trading_plan_for_bullish_has_targets),
        ("manual_report_item_backward_compat", test_manual_report_item_backward_compat),
        ("all_na_signals_produces_only_unknown_markers", test_all_na_signals_produces_only_unknown_markers),
        ("policy_imports_no_execution_modules", test_policy_imports_no_execution_modules),
        ("cli_help_exits_zero", test_cli_help_exits_zero),
        ("policy_module_no_utils_import", test_policy_module_no_utils_import),
        ("manual_report_default_output_is_flat", test_manual_report_default_output_is_flat),
        ("cli_help_mentions_flat_default_path", test_cli_help_mentions_flat_default_path),
        ("custom_output_creates_parent_dirs", test_custom_output_creates_parent_dirs),
        ("batch_continues_when_one_symbol_fails", test_manual_report_batch_continues_when_one_symbol_fails),
        ("batch_preserves_symbol_order", test_manual_report_batch_preserves_symbol_order),
        ("batch_reuses_shared_data_manager", test_manual_report_batch_reuses_shared_data_manager),
    ]

    all_errors = []
    passed = 0
    for name, fn in tests:
        ERRORS.clear()
        try:
            fn()
            if ERRORS:
                for err in ERRORS:
                    all_errors.append(f"{name}: {err}")
                    print(f"FAIL {name}: {err}")
            else:
                print(f"PASS {name}")
                passed += 1
        except Exception as e:
            all_errors.append(f"{name}: {e}")
            print(f"FAIL {name}: {e}")

    if all_errors:
        print(f"\n{len(all_errors)} FAILURES:")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print(f"\nAll {passed} tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
