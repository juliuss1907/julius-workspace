#!/usr/bin/env python3
"""Test Phase 9A.2: Health CLI."""
import json
import os
import subprocess
import sys
import tempfile
import time as _t
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.check_runtime_health import _resolve, _print_health


# ---------------------------------------------------------------------------
# _resolve helper
# ---------------------------------------------------------------------------

def test_resolve_relative(tmp_root):
    p = _resolve("logs/h.json")
    assert p == project_root / "logs" / "h.json"
    print("PASS test_resolve_relative")


def test_resolve_absolute():
    p = _resolve("/tmp/abs.json")
    assert str(p) == "/tmp/abs.json"
    print("PASS test_resolve_absolute")


# ---------------------------------------------------------------------------
# _print_health does not crash
# ---------------------------------------------------------------------------

def test_print_health_running(tmp_root, capsys=None):
    health = {
        "name": "trading-runtime",
        "status": "running",
        "mode": "single_cycle",
        "started_at": "2026-06-08T19:00:00",
        "cycle_count": 5,
        "last_cycle_at": "2026-06-08T19:30:00",
        "last_cycle_status": "success",
        "last_cycle_duration_sec": 1.23,
        "last_symbols_processed": 3,
        "watchlist": ["BTCUSDT", "ETHUSDT"],
        "errors": [{"at": "2026-06-08T19:00:00", "message": "test"}],
        "pid": 12345,
        "host": "testhost",
    }
    _print_health(health, lock_info=None)
    print("PASS test_print_health_running")


def test_print_health_stopped():
    health = {
        "name": "trading-runtime",
        "status": "stopped",
        "started_at": "2026-06-08T19:00:00",
        "stopped_at": "2026-06-08T19:30:00",
        "stop_reason": "single_cycle_complete",
        "cycle_count": 1,
        "errors": [],
    }
    _print_health(health, lock_info=None)
    print("PASS test_print_health_stopped")


def test_print_health_with_lock():
    health = {
        "name": "trading-runtime",
        "status": "running",
        "pid": 12345,
        "started_at": "2026-06-08T19:00:00",
    }
    lock_info = {
        "_path": "/tmp/x.lock",
        "pid": 99999,
        "pid_alive": False,
        "stale": True,
        "started_at": "2026-06-01T00:00:00",
    }
    _print_health(health, lock_info=lock_info)
    print("PASS test_print_health_with_lock")


def test_print_health_with_many_errors():
    health = {
        "name": "trading-runtime",
        "status": "running",
        "pid": 12345,
        "started_at": "2026-06-08T19:00:00",
        "errors": [{"at": f"2026-06-08T19:00:0{i}", "message": f"err{i}"} for i in range(10)],
    }
    _print_health(health, lock_info=None)
    print("PASS test_print_health_with_many_errors")


# ---------------------------------------------------------------------------
# CLI end-to-end
# ---------------------------------------------------------------------------

def test_cli_no_health_file(tmp_root):
    """CLI should exit 1 when no health file exists."""
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts/check_runtime_health.py"),
         "--path", str(tmp_root / "no.json")],
        capture_output=True, text=True, timeout=15,
        cwd=str(project_root),
    )
    assert result.returncode == 1
    assert "No runtime health file" in result.stdout
    print("PASS test_cli_no_health_file")


def test_cli_text_output(tmp_root):
    p = tmp_root / "h.json"
    p.write_text(json.dumps({
        "name": "trading-runtime",
        "status": "running",
        "mode": "continuous",
        "started_at": "2026-06-08T19:00:00",
        "cycle_count": 3,
        "last_cycle_status": "success",
        "pid": 12345,
        "host": "testhost",
        "errors": [],
    }), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts/check_runtime_health.py"),
         "--path", str(p)],
        capture_output=True, text=True, timeout=15,
        cwd=str(project_root),
    )
    assert result.returncode == 0
    assert "Runtime Health" in result.stdout
    assert "running" in result.stdout
    assert "12345" in result.stdout
    print("PASS test_cli_text_output")


def test_cli_json_output(tmp_root):
    p = tmp_root / "h.json"
    p.write_text(json.dumps({
        "name": "trading-runtime",
        "status": "stopped",
        "started_at": "2026-06-08T19:00:00",
        "stopped_at": "2026-06-08T19:30:00",
        "stop_reason": "graceful",
        "cycle_count": 5,
        "errors": [],
    }), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts/check_runtime_health.py"),
         "--path", str(p),
         "--json"],
        capture_output=True, text=True, timeout=15,
        cwd=str(project_root),
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["available"] is True
    assert data["health"]["status"] == "stopped"
    print("PASS test_cli_json_output")


def test_cli_check_lock_with_live_pid(tmp_root):
    p = tmp_root / "h.json"
    p.write_text(json.dumps({"status": "running"}), encoding="utf-8")
    real_lock = project_root / "logs" / "run_paper_trading.lock"
    real_lock.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    if real_lock.exists():
        backup = real_lock.read_text(encoding="utf-8")

    sleeper = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"],
    )
    try:
        for _ in range(20):
            try:
                os.kill(sleeper.pid, 0)
                break
            except OSError:
                _t.sleep(0.05)
        real_lock.write_text(json.dumps({
            "pid": sleeper.pid,
            "name": "x",
            "started_at": "2026-06-01T00:00:00",
        }), encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(project_root / "scripts/check_runtime_health.py"),
             "--path", str(p),
             "--check-lock"],
            capture_output=True, text=True, timeout=15,
            cwd=str(project_root),
        )
        assert result.returncode == 0
        assert "Lock info" in result.stdout
        assert f"pid:         {sleeper.pid}" in result.stdout
    finally:
        try:
            sleeper.kill()
            sleeper.wait(timeout=5)
        except Exception:
            pass
        if backup is not None:
            real_lock.write_text(backup, encoding="utf-8")
        elif real_lock.exists():
            real_lock.unlink()
    print("PASS test_cli_check_lock_with_live_pid")


def test_cli_malformed_health(tmp_root):
    p = tmp_root / "h.json"
    p.write_text("not json", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts/check_runtime_health.py"),
         "--path", str(p)],
        capture_output=True, text=True, timeout=15,
        cwd=str(project_root),
    )
    assert result.returncode == 1
    assert "No runtime health file" in result.stdout
    print("PASS test_cli_malformed_health")


def test_cli_json_unavailable(tmp_root):
    p = tmp_root / "no.json"
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts/check_runtime_health.py"),
         "--path", str(p),
         "--json"],
        capture_output=True, text=True, timeout=15,
        cwd=str(project_root),
    )
    assert result.returncode == 1
    data = json.loads(result.stdout)
    assert data["available"] is False
    print("PASS test_cli_json_unavailable")


def run_all():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)

        tests = [
            test_resolve_relative, test_resolve_absolute,
            test_print_health_running, test_print_health_stopped,
            test_print_health_with_lock, test_print_health_with_many_errors,
            test_cli_no_health_file, test_cli_text_output, test_cli_json_output,
            test_cli_check_lock_with_live_pid,
            test_cli_malformed_health, test_cli_json_unavailable,
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
