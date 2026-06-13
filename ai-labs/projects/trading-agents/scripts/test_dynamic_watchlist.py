#!/usr/bin/env python3
"""Test Phase 8B: Dynamic Watchlist Updater."""
import json
import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.update_dynamic_watchlist import (
    RATING_RANK,
    _load_json,
    _resolve,
    _load_screening,
    _normalize_candidates,
    _filter_candidates,
    _build_proposal,
    _render_markdown,
)


def _make_screening(candidates, symbols_scanned=None, min_score=60, top_n=5):
    return {
        "generated_at": "2026-06-08T12:00:00",
        "symbols_scanned": symbols_scanned or len(candidates),
        "min_score": min_score,
        "top_n": top_n,
        "candidates": candidates,
    }


def _cand(symbol, score, rating, rank=None, warnings=None):
    return {
        "symbol": symbol,
        "rank": rank if rank is not None else 0,
        "score": score,
        "rating": rating,
        "recommended_action": "consider_watchlist" if rating in ("strong_candidate", "candidate") else "monitor_only",
        "liquidity_score": 80,
        "volatility_score": 80,
        "technical_score": 80,
        "news_score": 50,
        "risk_score": 100,
        "reasons": [],
        "warnings": warnings or [],
    }


# ---------------------------------------------------------------------------
# JSON load / resolve
# ---------------------------------------------------------------------------

def test_load_json_missing():
    assert _load_json(Path("/nonexistent.json")) is None
    print("PASS test_load_json_missing")


def test_load_json_valid():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"a": 1}, f)
        path = Path(f.name)
    assert _load_json(path) == {"a": 1}
    path.unlink()
    print("PASS test_load_json_valid")


def test_resolve_relative():
    p = _resolve("foo/bar.json", project_root)
    assert p == project_root / "foo/bar.json"
    print("PASS test_resolve_relative")


def test_resolve_absolute():
    abs_path = "/tmp/abs_test.json"
    p = _resolve(abs_path, project_root)
    assert str(p) == abs_path
    print("PASS test_resolve_absolute")


# ---------------------------------------------------------------------------
# Normalize candidates
# ---------------------------------------------------------------------------

def test_normalize_candidates_basic():
    screening = _make_screening([
        _cand("BTCUSDT", 75.0, "strong_candidate", rank=1),
        _cand("ETHUSDT", 65.0, "candidate", rank=2),
    ])
    cands = _normalize_candidates(screening)
    assert len(cands) == 2
    assert cands[0]["symbol"] == "BTCUSDT"
    assert cands[0]["score"] == 75.0
    print("PASS test_normalize_candidates_basic")


def test_normalize_candidates_empty():
    assert _normalize_candidates({}) == []
    print("PASS test_normalize_candidates_empty")


# ---------------------------------------------------------------------------
# Filter candidates
# ---------------------------------------------------------------------------

def test_filter_preserves_base():
    candidates = [
        _cand("BTCUSDT", 70, "candidate", rank=1),
        _cand("ETHUSDT", 65, "candidate", rank=2),
        _cand("SOLUSDT", 80, "strong_candidate", rank=3),
    ]
    rules = {"max_symbols": 6, "min_score": 60, "min_rating": "candidate",
             "preserve_base_watchlist": True, "exclude_avoid_rating": True}
    base = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    allowed = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    selected, excluded = _filter_candidates(candidates, rules, base, allowed)
    syms = [s["symbol"] for s in selected]
    assert syms == ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    print("PASS test_filter_preserves_base")


def test_filter_drops_avoid():
    candidates = [
        _cand("AAAUSDT", 90, "strong_candidate", rank=1),
        _cand("BBBUSDT", 30, "avoid", rank=2),
    ]
    rules = {"max_symbols": 6, "min_score": 60, "min_rating": "candidate",
             "preserve_base_watchlist": False, "exclude_avoid_rating": True}
    selected, excluded = _filter_candidates(candidates, rules, [], [])
    assert "AAAUSDT" in [s["symbol"] for s in selected]
    assert "BBBUSDT" not in [s["symbol"] for s in selected]
    excl = {e["symbol"] for e in excluded}
    assert "BBBUSDT" in excl
    print("PASS test_filter_drops_avoid")


def test_filter_drops_low_score():
    candidates = [
        _cand("AAAUSDT", 80, "candidate", rank=1),
        _cand("BBBUSDT", 50, "candidate", rank=2),
    ]
    rules = {"max_symbols": 6, "min_score": 60, "min_rating": "candidate",
             "preserve_base_watchlist": False, "exclude_avoid_rating": True}
    selected, excluded = _filter_candidates(candidates, rules, [], [])
    syms = [s["symbol"] for s in selected]
    assert "AAAUSDT" in syms
    assert "BBBUSDT" not in syms
    print("PASS test_filter_drops_low_score")


def test_filter_drops_weak_rating():
    candidates = [
        _cand("AAAUSDT", 80, "candidate", rank=1),
        _cand("BBBUSDT", 80, "watch_only", rank=2),
    ]
    rules = {"max_symbols": 6, "min_score": 60, "min_rating": "candidate",
             "preserve_base_watchlist": False, "exclude_avoid_rating": True}
    selected, _ = _filter_candidates(candidates, rules, [], [])
    syms = [s["symbol"] for s in selected]
    assert "AAAUSDT" in syms
    assert "BBBUSDT" not in syms
    print("PASS test_filter_drops_weak_rating")


def test_filter_caps_to_max_symbols():
    candidates = [_cand(f"X{i}USDT", 80, "candidate", rank=i+1) for i in range(10)]
    rules = {"max_symbols": 3, "min_score": 60, "min_rating": "candidate",
             "preserve_base_watchlist": False, "exclude_avoid_rating": True}
    selected, _ = _filter_candidates(candidates, rules, [], [])
    assert len(selected) == 3
    print("PASS test_filter_caps_to_max_symbols")


def test_filter_respects_allowlist():
    candidates = [
        _cand("AAAUSDT", 80, "candidate", rank=1),
        _cand("OUTSIDEUSDT", 80, "candidate", rank=2),
    ]
    rules = {"max_symbols": 6, "min_score": 60, "min_rating": "candidate",
             "preserve_base_watchlist": False, "exclude_avoid_rating": True}
    selected, excluded = _filter_candidates(
        candidates, rules, [], ["AAAUSDT"]
    )
    syms = [s["symbol"] for s in selected]
    assert "AAAUSDT" in syms
    assert "OUTSIDEUSDT" not in syms
    print("PASS test_filter_respects_allowlist")


def test_filter_preserves_base_even_with_low_score():
    candidates = [
        _cand("AAAUSDT", 80, "candidate", rank=1),
        _cand("BASEUSDT", 30, "avoid", rank=2),
    ]
    rules = {"max_symbols": 6, "min_score": 60, "min_rating": "candidate",
             "preserve_base_watchlist": True, "exclude_avoid_rating": True}
    selected, _ = _filter_candidates(candidates, rules, ["BASEUSDT"], [])
    syms = [s["symbol"] for s in selected]
    assert "BASEUSDT" in syms
    print("PASS test_filter_preserves_base_even_with_low_score")


def test_filter_no_preserve_base():
    candidates = [
        _cand("AAAUSDT", 80, "candidate", rank=1),
    ]
    rules = {"max_symbols": 6, "min_score": 60, "min_rating": "candidate",
             "preserve_base_watchlist": False, "exclude_avoid_rating": True}
    selected, _ = _filter_candidates(candidates, rules, ["NOTINCANDS"], [])
    syms = [s["symbol"] for s in selected]
    assert "NOTINCANDS" not in syms
    assert "AAAUSDT" in syms
    print("PASS test_filter_no_preserve_base")


# ---------------------------------------------------------------------------
# Build proposal
# ---------------------------------------------------------------------------

def test_build_proposal_structure():
    screening = _make_screening([
        _cand("BTCUSDT", 80, "strong_candidate", rank=1),
        _cand("ETHUSDT", 70, "candidate", rank=2),
    ])
    selected = [
        {"symbol": "BTCUSDT", "score": 80, "rating": "strong_candidate",
         "rank": 1, "recommended_action": "consider_watchlist",
         "reasons": [], "warnings": [], "from_base": True},
    ]
    excluded = [{"symbol": "XUSDT", "reason": "score_below_60"}]
    rules = {"max_symbols": 6, "min_score": 60, "min_rating": "candidate",
             "preserve_base_watchlist": True, "exclude_avoid_rating": True,
             "require_manual_approval": True}

    proposal = _build_proposal(
        screening=screening, selected=selected, excluded=excluded,
        rules=rules, base_symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        source_report="reports/screening/latest-screening.json",
    )
    assert proposal["status"] == "manual_review_required"
    assert proposal["enabled_for_runtime"] is False
    assert "BTCUSDT" in proposal["selected_symbols"]
    assert proposal["source_report"] == "reports/screening/latest-screening.json"
    assert proposal["source_metrics"]["symbols_scanned"] == 2
    print("PASS test_build_proposal_structure")


def test_build_proposal_always_manual():
    screening = _make_screening([_cand("AAAUSDT", 80, "candidate")])
    rules = {"max_symbols": 6, "min_score": 60, "min_rating": "candidate"}
    proposal = _build_proposal(
        screening=screening, selected=[], excluded=[],
        rules=rules, base_symbols=[], source_report="x.json",
    )
    assert proposal["status"] == "manual_review_required"
    assert proposal["enabled_for_runtime"] is False
    print("PASS test_build_proposal_always_manual")


# ---------------------------------------------------------------------------
# Markdown render
# ---------------------------------------------------------------------------

def test_render_markdown_sections():
    proposal = {
        "generated_at": "2026-06-08T12:00:00",
        "source_report": "reports/screening/latest-screening.json",
        "status": "manual_review_required",
        "enabled_for_runtime": False,
        "base_symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        "selected_symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        "selection": [
            {"symbol": "BTCUSDT", "score": 80, "rating": "strong_candidate",
             "from_base": True},
            {"symbol": "ETHUSDT", "score": 70, "rating": "candidate",
             "from_base": True},
        ],
        "excluded": [{"symbol": "XUSDT", "reason": "score_below_60"}],
        "selection_rules": {
            "max_symbols": 6, "min_score": 60, "min_rating": "candidate",
            "preserve_base_watchlist": True, "exclude_avoid_rating": True,
            "require_manual_approval": True,
        },
        "source_metrics": {"symbols_scanned": 6, "min_score_threshold": 60},
    }
    md = _render_markdown(proposal)
    assert "# Dynamic Watchlist Proposal" in md
    assert "manual_review_required" in md
    assert "Selected Symbols" in md
    assert "Selection Rules" in md
    assert "Excluded Symbols" in md
    assert "Manual Review Checklist" in md
    assert "NOT active for runtime" in md
    assert "(base)" in md
    print("PASS test_render_markdown_sections")


def test_render_markdown_empty_selection():
    proposal = {
        "generated_at": "2026-06-08T12:00:00",
        "source_report": "x.json",
        "status": "manual_review_required",
        "enabled_for_runtime": False,
        "base_symbols": [],
        "selected_symbols": [],
        "selection": [],
        "excluded": [],
        "selection_rules": {},
        "source_metrics": {},
    }
    md = _render_markdown(proposal)
    assert "(none)" in md
    print("PASS test_render_markdown_empty_selection")


# ---------------------------------------------------------------------------
# Integration / CLI
# ---------------------------------------------------------------------------

def test_main_missing_source():
    """Test that running with missing source returns 2."""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts/update_dynamic_watchlist.py"),
         "--source", "/nonexistent/screening.json"],
        capture_output=True, text=True, timeout=30,
        cwd=str(project_root),
    )
    assert result.returncode == 2
    print("PASS test_main_missing_source")


def test_main_dry_run_with_fixture():
    """Test that dry-run with a synthetic screening report works."""
    import subprocess
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        screening_path = tmp_path / "screening.json"
        screening_path.write_text(json.dumps(_make_screening([
            _cand("BTCUSDT", 80, "strong_candidate", rank=1),
            _cand("ETHUSDT", 70, "candidate", rank=2),
            _cand("SOLUSDT", 75, "strong_candidate", rank=3),
            _cand("BNBUSDT", 65, "candidate", rank=4),
            _cand("AVOIDUSDT", 30, "avoid", rank=5),
        ])), encoding="utf-8")

        out_json = tmp_path / "dyn.json"
        out_md = tmp_path / "dyn.md"

        result = subprocess.run(
            [sys.executable, str(project_root / "scripts/update_dynamic_watchlist.py"),
             "--source", str(screening_path),
             "--output-json", str(out_json),
             "--output-md", str(out_md),
             "--dry-run"],
            capture_output=True, text=True, timeout=30,
            cwd=str(project_root),
        )
        assert result.returncode == 0, f"exit {result.returncode}\n{result.stdout}\n{result.stderr}"
        assert not out_json.exists(), "dry-run should not write files"
    print("PASS test_main_dry_run_with_fixture")


def test_main_writes_proposal_with_fixture():
    """Test that real run writes proposal files."""
    import subprocess
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        screening_path = tmp_path / "screening.json"
        screening_path.write_text(json.dumps(_make_screening([
            _cand("BTCUSDT", 80, "strong_candidate", rank=1),
            _cand("ETHUSDT", 70, "candidate", rank=2),
            _cand("SOLUSDT", 75, "strong_candidate", rank=3),
            _cand("BNBUSDT", 65, "candidate", rank=4),
            _cand("HYPEUSDT", 70, "candidate", rank=5),
            _cand("ZECUSDT", 68, "candidate", rank=6),
            _cand("AVOIDUSDT", 30, "avoid", rank=7),
        ])), encoding="utf-8")

        out_json = tmp_path / "dyn.json"
        out_md = tmp_path / "dyn.md"

        result = subprocess.run(
            [sys.executable, str(project_root / "scripts/update_dynamic_watchlist.py"),
             "--source", str(screening_path),
             "--output-json", str(out_json),
             "--output-md", str(out_md),
             "--allowed-symbols", "BTCUSDT", "ETHUSDT", "SOLUSDT",
             "BNBUSDT", "HYPEUSDT", "ZECUSDT"],
            capture_output=True, text=True, timeout=30,
            cwd=str(project_root),
        )
        assert result.returncode == 0, f"exit {result.returncode}\n{result.stdout}\n{result.stderr}"
        assert out_json.exists()
        assert out_md.exists()
        data = json.loads(out_json.read_text(encoding="utf-8"))
        assert data["status"] == "manual_review_required"
        assert data["enabled_for_runtime"] is False
        assert "BTCUSDT" in data["selected_symbols"]
        assert "ETHUSDT" in data["selected_symbols"]
        assert "SOLUSDT" in data["selected_symbols"]
        excl_syms = [e["symbol"] for e in data["excluded"]]
        assert "AVOIDUSDT" in excl_syms
        md = out_md.read_text(encoding="utf-8")
        assert "NOT active for runtime" in md
    print("PASS test_main_writes_proposal_with_fixture")


def test_main_against_real_screening_report():
    """Run the script against the latest-screening.json that exists in the project."""
    import subprocess
    report = project_root / "reports/screening/latest-screening.json"
    if not report.exists():
        print("SKIP test_main_against_real_screening_report (no real report yet)")
        return
    with tempfile.TemporaryDirectory() as tmp:
        out_json = Path(tmp) / "dyn.json"
        out_md = Path(tmp) / "dyn.md"
        result = subprocess.run(
            [sys.executable, str(project_root / "scripts/update_dynamic_watchlist.py"),
             "--source", str(report),
             "--output-json", str(out_json),
             "--output-md", str(out_md)],
            capture_output=True, text=True, timeout=30,
            cwd=str(project_root),
        )
        assert result.returncode == 0
        assert out_json.exists()
        data = json.loads(out_json.read_text(encoding="utf-8"))
        assert data["enabled_for_runtime"] is False
    print("PASS test_main_against_real_screening_report")


def test_does_not_mutate_config():
    """Make sure the script doesn't touch default_params.yaml."""
    cfg_path = project_root / "config/default_params.yaml"
    if not cfg_path.exists():
        print("SKIP test_does_not_mutate_config (no config)")
        return
    original = cfg_path.read_text(encoding="utf-8")
    import subprocess
    with tempfile.TemporaryDirectory() as tmp:
        screening_path = Path(tmp) / "screening.json"
        screening_path.write_text(json.dumps(_make_screening([
            _cand("BTCUSDT", 80, "strong_candidate", rank=1),
        ])), encoding="utf-8")
        out_json = Path(tmp) / "dyn.json"
        out_md = Path(tmp) / "dyn.md"
        subprocess.run(
            [sys.executable, str(project_root / "scripts/update_dynamic_watchlist.py"),
             "--source", str(screening_path),
             "--output-json", str(out_json),
             "--output-md", str(out_md)],
            capture_output=True, text=True, timeout=30,
            cwd=str(project_root),
        )
    assert cfg_path.read_text(encoding="utf-8") == original
    print("PASS test_does_not_mutate_config")


def run_all():
    tests = [
        test_load_json_missing, test_load_json_valid,
        test_resolve_relative, test_resolve_absolute,
        test_normalize_candidates_basic, test_normalize_candidates_empty,
        test_filter_preserves_base,
        test_filter_drops_avoid, test_filter_drops_low_score,
        test_filter_drops_weak_rating, test_filter_caps_to_max_symbols,
        test_filter_respects_allowlist,
        test_filter_preserves_base_even_with_low_score,
        test_filter_no_preserve_base,
        test_build_proposal_structure, test_build_proposal_always_manual,
        test_render_markdown_sections, test_render_markdown_empty_selection,
        test_main_missing_source, test_main_dry_run_with_fixture,
        test_main_writes_proposal_with_fixture,
        test_main_against_real_screening_report,
        test_does_not_mutate_config,
    ]

    failures = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            print(f"FAIL {t.__name__}: {e}")
            failures += 1
        except Exception as e:
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
            failures += 1

    if failures:
        print(f"\n{failures} test(s) failed")
        sys.exit(1)
    print(f"\nAll {len(tests)} tests passed")


if __name__ == "__main__":
    run_all()
