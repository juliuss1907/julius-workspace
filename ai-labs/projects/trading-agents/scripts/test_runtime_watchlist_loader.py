#!/usr/bin/env python3
"""Test Phase 8C: Guarded Runtime Watchlist Loader."""
import json
import logging
import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.watchlist import (
    _normalize_symbol,
    _normalize_list,
    _read_json,
    _resolve_path,
    evaluate_dynamic_watchlist,
    load_runtime_watchlist,
)


def _write_dynamic(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _base_config(overrides=None):
    cfg = {
        "watchlist": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        "dynamic_watchlist": {
            "enabled": False,
            "output_json": "watchlist/dynamic-watchlist.json",
            "allowed_symbols": [
                "BTCUSDT", "ETHUSDT", "SOLUSDT",
                "BNBUSDT", "HYPEUSDT", "ZECUSDT",
            ],
        },
    }
    if overrides:
        cfg.update(overrides)
    return cfg


# ---------------------------------------------------------------------------
# Normalize helpers
# ---------------------------------------------------------------------------

def test_normalize_symbol_uppercase():
    assert _normalize_symbol("btcusdt") == "BTCUSDT"
    print("PASS test_normalize_symbol_uppercase")


def test_normalize_symbol_add_suffix():
    assert _normalize_symbol("BTC") == "BTCUSDT"
    print("PASS test_normalize_symbol_add_suffix")


def test_normalize_symbol_empty():
    assert _normalize_symbol("") == ""
    assert _normalize_symbol(None) == ""
    print("PASS test_normalize_symbol_empty")


def test_normalize_list_dedup_preserves_order():
    out = _normalize_list(["BTCUSDT", "btcusdt", "ETH", "BTCUSDT"])
    assert out == ["BTCUSDT", "ETHUSDT"]
    print("PASS test_normalize_list_dedup_preserves_order")


def test_normalize_list_skips_empty():
    out = _normalize_list(["BTC", "", None, "ETH"])
    assert out == ["BTCUSDT", "ETHUSDT"]
    print("PASS test_normalize_list_skips_empty")


# ---------------------------------------------------------------------------
# _read_json
# ---------------------------------------------------------------------------

def test_read_json_missing():
    assert _read_json(Path("/nonexistent/foo.json")) is None
    print("PASS test_read_json_missing")


def test_read_json_valid():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"a": 1}, f)
        p = Path(f.name)
    assert _read_json(p) == {"a": 1}
    p.unlink()
    print("PASS test_read_json_valid")


def test_read_json_malformed():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("not json")
        p = Path(f.name)
    assert _read_json(p) is None
    p.unlink()
    print("PASS test_read_json_malformed")


# ---------------------------------------------------------------------------
# _resolve_path
# ---------------------------------------------------------------------------

def test_resolve_path_relative():
    p = _resolve_path("foo/bar.json", project_root)
    assert p == project_root / "foo/bar.json"
    print("PASS test_resolve_path_relative")


def test_resolve_path_absolute():
    p = _resolve_path("/tmp/abs.json", project_root)
    assert str(p) == "/tmp/abs.json"
    print("PASS test_resolve_path_absolute")


# ---------------------------------------------------------------------------
# evaluate_dynamic_watchlist
# ---------------------------------------------------------------------------

def test_evaluate_disabled_in_config(tmp_root):
    cfg = _base_config()
    symbols, reason = evaluate_dynamic_watchlist(cfg, project_root=tmp_root)
    assert symbols is None
    assert "disabled" in reason
    print("PASS test_evaluate_disabled_in_config")


def test_evaluate_missing_file(tmp_root):
    cfg = _base_config({"dynamic_watchlist": {
        "enabled": True,
        "output_json": "watchlist/does-not-exist.json",
    }})
    symbols, reason = evaluate_dynamic_watchlist(cfg, project_root=tmp_root)
    assert symbols is None
    assert "missing" in reason
    print("PASS test_evaluate_missing_file")


def test_evaluate_malformed_file(tmp_root):
    p = tmp_root / "watchlist" / "dynamic-watchlist.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("not json", encoding="utf-8")
    cfg = _base_config({"dynamic_watchlist": {
        "enabled": True, "output_json": str(p),
    }})
    symbols, reason = evaluate_dynamic_watchlist(cfg, project_root=tmp_root)
    assert symbols is None
    assert "missing" in reason
    print("PASS test_evaluate_malformed_file")


def test_evaluate_status_manual_review(tmp_root):
    p = tmp_root / "watchlist" / "dynamic-watchlist.json"
    _write_dynamic(p, {
        "status": "manual_review_required",
        "enabled_for_runtime": True,
        "selected_symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
    })
    cfg = _base_config({"dynamic_watchlist": {
        "enabled": True, "output_json": str(p),
    }})
    symbols, reason = evaluate_dynamic_watchlist(cfg, project_root=tmp_root)
    assert symbols is None
    assert "not_approved" in reason
    print("PASS test_evaluate_status_manual_review")


def test_evaluate_enabled_for_runtime_false(tmp_root):
    p = tmp_root / "watchlist" / "dynamic-watchlist.json"
    _write_dynamic(p, {
        "status": "approved",
        "enabled_for_runtime": False,
        "selected_symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
    })
    cfg = _base_config({"dynamic_watchlist": {
        "enabled": True, "output_json": str(p),
    }})
    symbols, reason = evaluate_dynamic_watchlist(cfg, project_root=tmp_root)
    assert symbols is None
    assert "enabled_for_runtime_false" in reason
    print("PASS test_evaluate_enabled_for_runtime_false")


def test_evaluate_empty_selection(tmp_root):
    p = tmp_root / "watchlist" / "dynamic-watchlist.json"
    _write_dynamic(p, {
        "status": "approved",
        "enabled_for_runtime": True,
        "selected_symbols": [],
    })
    cfg = _base_config({"dynamic_watchlist": {
        "enabled": True, "output_json": str(p),
    }})
    symbols, reason = evaluate_dynamic_watchlist(cfg, project_root=tmp_root)
    assert symbols is None
    assert "empty" in reason
    print("PASS test_evaluate_empty_selection")


def test_evaluate_success(tmp_root):
    p = tmp_root / "watchlist" / "dynamic-watchlist.json"
    _write_dynamic(p, {
        "status": "approved",
        "enabled_for_runtime": True,
        "selected_symbols": ["BTC", "ETH", "SOL", "BNB"],
    })
    cfg = _base_config({"dynamic_watchlist": {
        "enabled": True, "output_json": str(p),
    }})
    symbols, reason = evaluate_dynamic_watchlist(cfg, project_root=tmp_root)
    assert symbols == ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
    assert reason == "dynamic_active"
    print("PASS test_evaluate_success")


def test_evaluate_allowlist_filters(tmp_root):
    p = tmp_root / "watchlist" / "dynamic-watchlist.json"
    _write_dynamic(p, {
        "status": "approved",
        "enabled_for_runtime": True,
        "selected_symbols": ["BTC", "ETH", "UNKNOWNCOIN"],
    })
    cfg = _base_config({"dynamic_watchlist": {
        "enabled": True, "output_json": str(p),
        "allowed_symbols": ["BTC", "ETH"],
    }})
    symbols, reason = evaluate_dynamic_watchlist(cfg, project_root=tmp_root)
    assert "UNKNOWNCOINUSDT" not in symbols
    assert "BTCUSDT" in symbols
    assert "ETHUSDT" in symbols
    assert "filtered" in reason
    print("PASS test_evaluate_allowlist_filters")


def test_evaluate_all_filtered_returns_none(tmp_root):
    p = tmp_root / "watchlist" / "dynamic-watchlist.json"
    _write_dynamic(p, {
        "status": "approved",
        "enabled_for_runtime": True,
        "selected_symbols": ["XRP", "DOGE"],
    })
    cfg = _base_config({"dynamic_watchlist": {
        "enabled": True, "output_json": str(p),
        "allowed_symbols": ["BTC", "ETH"],
    }})
    symbols, reason = evaluate_dynamic_watchlist(cfg, project_root=tmp_root)
    assert symbols is None
    assert "filtered" in reason
    print("PASS test_evaluate_all_filtered_returns_none")


def test_evaluate_no_config():
    symbols, reason = evaluate_dynamic_watchlist(None, project_root=project_root)
    assert symbols is None
    assert "config_missing" in reason
    print("PASS test_evaluate_no_config")


# ---------------------------------------------------------------------------
# load_runtime_watchlist
# ---------------------------------------------------------------------------

def test_loader_default_disabled_uses_static(tmp_root):
    cfg = _base_config()
    out = load_runtime_watchlist(cfg, project_root=tmp_root, logger=_NullLogger())
    assert out == ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    print("PASS test_loader_default_disabled_uses_static")


def test_loader_enabled_but_no_file_uses_static(tmp_root):
    cfg = _base_config({"dynamic_watchlist": {
        "enabled": True,
        "output_json": "watchlist/missing.json",
    }})
    out = load_runtime_watchlist(cfg, project_root=tmp_root, logger=_NullLogger())
    assert out == ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    print("PASS test_loader_enabled_but_no_file_uses_static")


def test_loader_enabled_and_approved_uses_dynamic(tmp_root):
    p = tmp_root / "watchlist" / "dynamic-watchlist.json"
    _write_dynamic(p, {
        "status": "approved",
        "enabled_for_runtime": True,
        "selected_symbols": ["BTC", "ETH", "BNB"],
    })
    cfg = _base_config({"dynamic_watchlist": {
        "enabled": True, "output_json": str(p),
    }})
    out = load_runtime_watchlist(cfg, project_root=tmp_root, logger=_NullLogger())
    assert out == ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    print("PASS test_loader_enabled_and_approved_uses_dynamic")


def test_loader_enabled_but_manual_review_uses_static(tmp_root):
    p = tmp_root / "watchlist" / "dynamic-watchlist.json"
    _write_dynamic(p, {
        "status": "manual_review_required",
        "enabled_for_runtime": True,
        "selected_symbols": ["BTC", "ETH", "BNB"],
    })
    cfg = _base_config({"dynamic_watchlist": {
        "enabled": True, "output_json": str(p),
    }})
    out = load_runtime_watchlist(cfg, project_root=tmp_root, logger=_NullLogger())
    assert out == ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    print("PASS test_loader_enabled_but_manual_review_uses_static")


def test_loader_static_normalizes_partial_list(tmp_root):
    cfg = _base_config()
    cfg["watchlist"] = ["btc", "eth", "sol"]
    out = load_runtime_watchlist(cfg, project_root=tmp_root, logger=_NullLogger())
    assert out == ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    print("PASS test_loader_static_normalizes_partial_list")


def test_loader_static_fallback_when_dynamic_empty(tmp_root):
    p = tmp_root / "watchlist" / "dynamic-watchlist.json"
    _write_dynamic(p, {
        "status": "approved",
        "enabled_for_runtime": True,
        "selected_symbols": [],
    })
    cfg = _base_config({"dynamic_watchlist": {
        "enabled": True, "output_json": str(p),
    }})
    out = load_runtime_watchlist(cfg, project_root=tmp_root, logger=_NullLogger())
    assert out == ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    print("PASS test_loader_static_fallback_when_dynamic_empty")


def test_loader_handles_missing_config_key():
    cfg = {}
    out = load_runtime_watchlist(cfg, project_root=project_root, logger=_NullLogger())
    assert out == ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    print("PASS test_loader_handles_missing_config_key")


def test_loader_handles_no_dynamic_block():
    cfg = {"watchlist": ["BTC", "ETH"]}
    out = load_runtime_watchlist(cfg, project_root=project_root, logger=_NullLogger())
    assert out == ["BTCUSDT", "ETHUSDT"]
    print("PASS test_loader_handles_no_dynamic_block")


# ---------------------------------------------------------------------------
# Logger helper
# ---------------------------------------------------------------------------

class _NullLogger:
    def info(self, *a, **kw): pass
    def warning(self, *a, **kw): pass
    def error(self, *a, **kw): pass


# ---------------------------------------------------------------------------
# Runner integration smoke
# ---------------------------------------------------------------------------

def test_run_paper_trading_single_cycle_still_works():
    """Make sure wiring the loader into run_paper_trading did not break it."""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts/run_paper_trading.py"),
         "--single-cycle"],
        capture_output=True, text=True, timeout=120,
        cwd=str(project_root),
    )
    assert result.returncode == 0
    assert "Trading cycle completed" in result.stdout or "Trading cycle completed" in result.stderr
    print("PASS test_run_paper_trading_single_cycle_still_works")


def run_all():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)

        tests = [
            test_normalize_symbol_uppercase, test_normalize_symbol_add_suffix,
            test_normalize_symbol_empty, test_normalize_list_dedup_preserves_order,
            test_normalize_list_skips_empty,
            test_read_json_missing, test_read_json_valid, test_read_json_malformed,
            test_resolve_path_relative, test_resolve_path_absolute,
            test_evaluate_disabled_in_config,
            test_evaluate_missing_file,
            test_evaluate_malformed_file,
            test_evaluate_status_manual_review,
            test_evaluate_enabled_for_runtime_false,
            test_evaluate_empty_selection,
            test_evaluate_success,
            test_evaluate_allowlist_filters,
            test_evaluate_all_filtered_returns_none,
            test_evaluate_no_config,
            test_loader_default_disabled_uses_static,
            test_loader_enabled_but_no_file_uses_static,
            test_loader_enabled_and_approved_uses_dynamic,
            test_loader_enabled_but_manual_review_uses_static,
            test_loader_static_normalizes_partial_list,
            test_loader_static_fallback_when_dynamic_empty,
            test_loader_handles_missing_config_key,
            test_loader_handles_no_dynamic_block,
            test_run_paper_trading_single_cycle_still_works,
        ]

        failures = 0
        for t in tests:
            try:
                if "tmp_root" in t.__code__.co_varnames:
                    t(tmp_root=tmp_root)
                else:
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
