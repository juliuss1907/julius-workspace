#!/usr/bin/env python3
"""Test Phase 9A.1: Runtime Health."""
import json
import os
import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from state.runtime_health import RuntimeHealth, read_health


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# read_health
# ---------------------------------------------------------------------------

def test_read_health_missing():
    assert read_health("/nonexistent/health.json") is None
    print("PASS test_read_health_missing")


def test_read_health_valid(tmp_root):
    p = tmp_root / "h.json"
    p.write_text(json.dumps({"status": "running"}), encoding="utf-8")
    assert read_health(str(p)) == {"status": "running"}
    print("PASS test_read_health_valid")


def test_read_health_malformed(tmp_root):
    p = tmp_root / "h.json"
    p.write_text("not json", encoding="utf-8")
    assert read_health(str(p)) is None
    print("PASS test_read_health_malformed")


# ---------------------------------------------------------------------------
# mark_running
# ---------------------------------------------------------------------------

def test_mark_running_writes_file(tmp_root):
    p = tmp_root / "h.json"
    h = RuntimeHealth(path=str(p), name="test")
    payload = h.mark_running(watchlist=["BTCUSDT", "ETHUSDT"], mode="single_cycle")
    assert p.exists()
    data = _read(p)
    assert data["status"] == "running"
    assert data["mode"] == "single_cycle"
    assert data["name"] == "test"
    assert data["watchlist"] == ["BTCUSDT", "ETHUSDT"]
    assert data["started_at"] is not None
    assert data["cycle_count"] == 0
    assert data["last_cycle_at"] is None
    assert payload["status"] == "running"
    print("PASS test_mark_running_writes_file")


def test_mark_running_creates_parent_dir(tmp_root):
    p = tmp_root / "deep" / "nested" / "h.json"
    h = RuntimeHealth(path=str(p), name="test")
    h.mark_running()
    assert p.exists()
    print("PASS test_mark_running_creates_parent_dir")


def test_mark_running_no_watchlist(tmp_root):
    p = tmp_root / "h.json"
    h = RuntimeHealth(path=str(p), name="test")
    h.mark_running(mode="continuous")
    data = _read(p)
    assert "watchlist" not in data
    print("PASS test_mark_running_no_watchlist")


# ---------------------------------------------------------------------------
# record_cycle
# ---------------------------------------------------------------------------

def test_record_cycle_success(tmp_root):
    p = tmp_root / "h.json"
    h = RuntimeHealth(path=str(p), name="test")
    h.mark_running()
    payload = h.record_cycle(status="success", duration_sec=1.23, symbols_processed=3)
    data = _read(p)
    assert data["status"] == "running"
    assert data["last_cycle_status"] == "success"
    assert data["last_cycle_duration_sec"] == 1.23
    assert data["last_symbols_processed"] == 3
    assert data["cycle_count"] == 1
    assert data["last_cycle_at"] is not None
    assert payload["cycle_count"] == 1
    print("PASS test_record_cycle_success")


def test_record_cycle_multiple_increments(tmp_root):
    p = tmp_root / "h.json"
    h = RuntimeHealth(path=str(p), name="test")
    h.mark_running()
    for i in range(5):
        h.record_cycle(status="success", duration_sec=0.5, symbols_processed=2)
    data = _read(p)
    assert data["cycle_count"] == 5
    print("PASS test_record_cycle_multiple_increments")


def test_record_cycle_with_error(tmp_root):
    p = tmp_root / "h.json"
    h = RuntimeHealth(path=str(p), name="test")
    h.mark_running()
    h.record_cycle(status="failed", duration_sec=0.1, symbols_processed=0,
                   error="something went wrong")
    data = _read(p)
    assert data["last_cycle_status"] == "failed"
    assert len(data["errors"]) == 1
    assert data["errors"][0]["message"] == "something went wrong"
    print("PASS test_record_cycle_with_error")


def test_record_cycle_keeps_recent_errors(tmp_root):
    p = tmp_root / "h.json"
    h = RuntimeHealth(path=str(p), name="test")
    h.mark_running()
    for i in range(25):
        h.record_cycle(status="failed", duration_sec=0.1, symbols_processed=0,
                       error=f"err_{i}")
    data = _read(p)
    assert len(data["errors"]) == 20
    assert data["errors"][0]["message"] == "err_5"
    print("PASS test_record_cycle_keeps_recent_errors")


def test_record_cycle_preserves_started_at(tmp_root):
    p = tmp_root / "h.json"
    h = RuntimeHealth(path=str(p), name="test")
    payload = h.mark_running()
    started = payload["started_at"]
    h.record_cycle(status="success", duration_sec=0.5, symbols_processed=2)
    data = _read(p)
    assert data["started_at"] == started
    print("PASS test_record_cycle_preserves_started_at")


# ---------------------------------------------------------------------------
# mark_stopped
# ---------------------------------------------------------------------------

def test_mark_stopped(tmp_root):
    p = tmp_root / "h.json"
    h = RuntimeHealth(path=str(p), name="test")
    h.mark_running()
    h.mark_stopped(reason="graceful")
    data = _read(p)
    assert data["status"] == "stopped"
    assert data["stopped_at"] is not None
    assert data["stop_reason"] == "graceful"
    assert data["started_at"] is not None
    print("PASS test_mark_stopped")


def test_mark_stopped_without_running(tmp_root):
    p = tmp_root / "h.json"
    h = RuntimeHealth(path=str(p), name="test")
    h.mark_stopped(reason="immediate")
    data = _read(p)
    assert data["status"] == "stopped"
    assert data["stop_reason"] == "immediate"
    print("PASS test_mark_stopped_without_running")


# ---------------------------------------------------------------------------
# snapshot
# ---------------------------------------------------------------------------

def test_snapshot_after_running(tmp_root):
    p = tmp_root / "h.json"
    h = RuntimeHealth(path=str(p), name="test")
    h.mark_running()
    h.record_cycle(status="success", duration_sec=0.4, symbols_processed=2)
    snap = h.snapshot()
    assert snap["status"] == "running"
    assert snap["last_cycle_status"] == "success"
    print("PASS test_snapshot_after_running")


def test_snapshot_empty(tmp_root):
    p = tmp_root / "snapshot_empty.json"
    h = RuntimeHealth(path=str(p), name="test")
    assert h.snapshot() == {}
    print("PASS test_snapshot_empty")


# ---------------------------------------------------------------------------
# Atomic write (no torn file on rapid succession)
# ---------------------------------------------------------------------------

def test_atomic_writes(tmp_root):
    p = tmp_root / "h.json"
    h = RuntimeHealth(path=str(p), name="test")
    h.mark_running()
    for i in range(20):
        h.record_cycle(status="success", duration_sec=0.01, symbols_processed=1)
    data = _read(p)
    assert data["cycle_count"] == 20
    assert data["status"] == "running"
    print("PASS test_atomic_writes")


# ---------------------------------------------------------------------------
# Integration: --single-cycle produces health file
# ---------------------------------------------------------------------------

def test_run_paper_trading_writes_health_file():
    import subprocess
    health_path = project_root / "logs" / "runtime_health.json"
    backup = None
    if health_path.exists():
        backup = health_path.read_text(encoding="utf-8")
    try:
        result = subprocess.run(
            [sys.executable, str(project_root / "scripts/run_paper_trading.py"),
             "--single-cycle"],
            capture_output=True, text=True, timeout=120,
            cwd=str(project_root),
        )
        assert result.returncode == 0
        assert health_path.exists()
        data = json.loads(health_path.read_text(encoding="utf-8"))
        assert "status" in data
    finally:
        if backup is not None:
            health_path.write_text(backup, encoding="utf-8")
    print("PASS test_run_paper_trading_writes_health_file")


def run_all():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)

        tests = [
            test_read_health_missing, test_read_health_valid, test_read_health_malformed,
            test_mark_running_writes_file, test_mark_running_creates_parent_dir,
            test_mark_running_no_watchlist,
            test_record_cycle_success, test_record_cycle_multiple_increments,
            test_record_cycle_with_error, test_record_cycle_keeps_recent_errors,
            test_record_cycle_preserves_started_at,
            test_mark_stopped, test_mark_stopped_without_running,
            test_snapshot_after_running, test_snapshot_empty,
            test_atomic_writes,
            test_run_paper_trading_writes_health_file,
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
