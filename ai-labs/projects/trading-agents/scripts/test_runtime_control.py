#!/usr/bin/env python3
"""Test Phase 9A.3: Runtime Control CLI."""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time as _t
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.runtime_control import (
    resolve_status,
    format_status_text,
    cmd_status,
    cmd_start,
    cmd_stop,
    cmd_restart,
    _resolve,
    _resolve_lock_path,
    _resolve_health_path,
    _read_health_file,
)


# ---------------------------------------------------------------------------
# resolve_status
# ---------------------------------------------------------------------------

def test_status_never_started(tmp_root, cfg_patcher):
    cfg_patcher.set({
        "runtime": {
            "lock_file": str(tmp_root / "no.lock"),
            "health_file": str(tmp_root / "no.json"),
        }
    })
    state = resolve_status()
    assert state["status"] == "never_started"
    assert state["lock_pid"] is None
    assert state["health"] == {}
    print("PASS test_status_never_started")


def test_status_stopped(tmp_root, cfg_patcher):
    h = tmp_root / "h.json"
    h.write_text(json.dumps({
        "status": "stopped",
        "started_at": "2026-01-01T00:00:00",
        "stopped_at": "2026-01-01T00:10:00",
        "stop_reason": "graceful",
        "cycle_count": 5,
    }), encoding="utf-8")
    cfg_patcher.set({
        "runtime": {
            "lock_file": str(tmp_root / "no.lock"),
            "health_file": str(h),
        }
    })
    state = resolve_status()
    assert state["status"] == "stopped"
    assert state["health"]["cycle_count"] == 5
    print("PASS test_status_stopped")


def test_status_stale_lock(tmp_root, cfg_patcher):
    lock = tmp_root / "l.lock"
    lock.write_text(json.dumps({
        "pid": 99999999,
        "name": "dead",
        "started_at": "2026-01-01T00:00:00",
    }), encoding="utf-8")
    cfg_patcher.set({
        "runtime": {
            "lock_file": str(lock),
            "health_file": str(tmp_root / "no.json"),
        }
    })
    state = resolve_status()
    assert state["status"] == "stale_lock"
    assert state["lock_pid"] == 99999999
    assert state["lock_pid_alive"] is False
    print("PASS test_status_stale_lock")


def test_status_running_live_lock(tmp_root, cfg_patcher):
    lock = tmp_root / "l.lock"
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
        lock.write_text(json.dumps({
            "pid": sleeper.pid,
            "name": "test",
            "started_at": "2026-01-01T00:00:00",
        }), encoding="utf-8")
        cfg_patcher.set({
            "runtime": {
                "lock_file": str(lock),
                "health_file": str(tmp_root / "no.json"),
            }
        })
        state = resolve_status()
        assert state["status"] == "running"
        assert state["lock_pid"] == sleeper.pid
        assert state["lock_pid_alive"] is True
    finally:
        try:
            sleeper.kill()
            sleeper.wait(timeout=5)
        except Exception:
            pass
    print("PASS test_status_running_live_lock")


def test_status_running_no_lock(tmp_root, cfg_patcher):
    h = tmp_root / "h.json"
    h.write_text(json.dumps({"status": "running"}), encoding="utf-8")
    cfg_patcher.set({
        "runtime": {
            "lock_file": str(tmp_root / "no.lock"),
            "health_file": str(h),
        }
    })
    state = resolve_status()
    assert state["status"] == "running_no_lock"
    print("PASS test_status_running_no_lock")


# ---------------------------------------------------------------------------
# _read_health_file
# ---------------------------------------------------------------------------

def test_read_health_file_missing():
    result = _read_health_file(str(Path("/nonexistent/runtime_health.json")))
    assert result == {}
    print("PASS test_read_health_file_missing")


def test_read_health_file_valid(tmp_root):
    h = tmp_root / "h.json"
    h.write_text(json.dumps({"status": "running", "cycle_count": 3}), encoding="utf-8")
    result = _read_health_file(str(h))
    assert result == {"status": "running", "cycle_count": 3}
    print("PASS test_read_health_file_valid")


def test_read_health_file_corrupt(tmp_root):
    h = tmp_root / "h.json"
    h.write_text("not valid json", encoding="utf-8")
    result = _read_health_file(str(h))
    assert result == {}
    print("PASS test_read_health_file_corrupt")


def test_read_health_file_not_dict(tmp_root):
    h = tmp_root / "h.json"
    h.write_text(json.dumps(["list", "not", "dict"]), encoding="utf-8")
    result = _read_health_file(str(h))
    assert result == {}
    print("PASS test_read_health_file_not_dict")


# ---------------------------------------------------------------------------
# format_status_text
# ---------------------------------------------------------------------------

def test_format_status_text_never_started():
    s = format_status_text({
        "status": "never_started",
        "lock_path": "/tmp/x.lock",
        "health_path": "/tmp/x.json",
        "lock_pid": None,
        "lock_pid_alive": False,
        "lock_holder": None,
        "health": {},
    })
    assert "Runtime status: never_started" in s
    assert "Lock:   /tmp/x.lock" in s
    print("PASS test_format_status_text_never_started")


def test_format_status_text_with_health():
    s = format_status_text({
        "status": "stopped",
        "lock_path": "/tmp/x.lock",
        "health_path": "/tmp/x.json",
        "lock_pid": None,
        "lock_pid_alive": False,
        "lock_holder": None,
        "health": {
            "cycle_count": 3,
            "last_cycle_at": "2026-01-01T00:05:00",
            "last_cycle_status": "success",
            "stop_reason": "graceful",
        },
    })
    assert "Cycle count:      3" in s
    assert "Last cycle:       success" in s
    assert "Stop reason:      graceful" in s
    print("PASS test_format_status_text_with_health")


# ---------------------------------------------------------------------------
# cmd_start
# ---------------------------------------------------------------------------

def test_cmd_start_dry_run(tmp_root, cfg_patcher):
    cfg_patcher.set({
        "runtime": {
            "lock_file": str(tmp_root / "x.lock"),
            "health_file": str(tmp_root / "x.json"),
        }
    })
    rc = cmd_start(argparse.Namespace(mode="continuous", dry_run=True))
    assert rc == 0
    assert not (tmp_root / "x.lock").exists()
    print("PASS test_cmd_start_dry_run")


def test_cmd_start_refuses_when_live_lock(tmp_root, cfg_patcher):
    lock = tmp_root / "l.lock"
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
        lock.write_text(json.dumps({
            "pid": sleeper.pid,
            "name": "test",
            "started_at": "2026-01-01T00:00:00",
        }), encoding="utf-8")
        cfg_patcher.set({
            "runtime": {
                "lock_file": str(lock),
                "health_file": str(tmp_root / "x.json"),
            }
        })
        rc = cmd_start(argparse.Namespace(mode="continuous", dry_run=False))
        assert rc == 1
    finally:
        try:
            sleeper.kill()
            sleeper.wait(timeout=5)
        except Exception:
            pass
    print("PASS test_cmd_start_refuses_when_live_lock")


# ---------------------------------------------------------------------------
# cmd_stop
# ---------------------------------------------------------------------------

def test_cmd_stop_no_lock(tmp_root, cfg_patcher):
    cfg_patcher.set({
        "runtime": {
            "lock_file": str(tmp_root / "no.lock"),
            "health_file": str(tmp_root / "x.json"),
        }
    })
    rc = cmd_stop(argparse.Namespace(timeout=5.0, dry_run=False))
    assert rc == 0
    print("PASS test_cmd_stop_no_lock")


def test_cmd_stop_stale_lock(tmp_root, cfg_patcher):
    lock = tmp_root / "l.lock"
    lock.write_text(json.dumps({
        "pid": 99999999, "name": "dead", "started_at": "2026-01-01T00:00:00",
    }), encoding="utf-8")
    cfg_patcher.set({
        "runtime": {
            "lock_file": str(lock),
            "health_file": str(tmp_root / "x.json"),
        }
    })
    rc = cmd_stop(argparse.Namespace(timeout=5.0, dry_run=False))
    assert rc == 0
    assert not lock.exists()
    print("PASS test_cmd_stop_stale_lock")


def test_cmd_stop_dry_run(tmp_root, cfg_patcher):
    lock = tmp_root / "l.lock"
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
        lock.write_text(json.dumps({
            "pid": sleeper.pid, "name": "test", "started_at": "2026-01-01T00:00:00",
        }), encoding="utf-8")
        cfg_patcher.set({
            "runtime": {
                "lock_file": str(lock),
                "health_file": str(tmp_root / "x.json"),
            }
        })
        rc = cmd_stop(argparse.Namespace(timeout=5.0, dry_run=True))
        assert rc == 0
        try:
            os.kill(sleeper.pid, 0)
            still_alive = True
        except ProcessLookupError:
            still_alive = False
        assert still_alive is True
        assert lock.exists()
    finally:
        try:
            sleeper.kill()
            sleeper.wait(timeout=5)
        except Exception:
            pass
    print("PASS test_cmd_stop_dry_run")


def test_cmd_stop_signals_live_pid(tmp_root, cfg_patcher):
    """Start a sleeper as the runtime, write its PID to lock, then call stop.
    Process should exit cleanly and lock should be released."""
    lock = tmp_root / "l.lock"
    sleeper_script = (
        "import json, time, os; "
        f"open(r'{lock}', 'w').write(json.dumps({{'pid': os.getpid(), 'name': 't', 'started_at': 'x'}})); "
        "time.sleep(60)"
    )
    sleeper = subprocess.Popen(
        [sys.executable, "-c", sleeper_script],
    )
    try:
        for _ in range(40):
            if lock.exists():
                break
            _t.sleep(0.05)
        assert lock.exists(), "lock file was never created"

        cfg_patcher.set({
            "runtime": {
                "lock_file": str(lock),
                "health_file": str(tmp_root / "x.json"),
            }
        })
        rc = cmd_stop(argparse.Namespace(timeout=10.0, dry_run=False))
        assert rc == 0
        assert not lock.exists()
    finally:
        try:
            if sleeper.poll() is None:
                sleeper.kill()
            sleeper.wait(timeout=5)
        except Exception:
            pass
    print("PASS test_cmd_stop_signals_live_pid")


# ---------------------------------------------------------------------------
# cmd_restart
# ---------------------------------------------------------------------------

def test_cmd_restart_dry_run(tmp_root, cfg_patcher):
    cfg_patcher.set({
        "runtime": {
            "lock_file": str(tmp_root / "no.lock"),
            "health_file": str(tmp_root / "no.json"),
        }
    })
    rc = cmd_restart(argparse.Namespace(
        mode="continuous", timeout=5.0, dry_run=True,
    ))
    assert rc == 0
    print("PASS test_cmd_restart_dry_run")


# ---------------------------------------------------------------------------
# _resolve helpers
# ---------------------------------------------------------------------------

def test_resolve_relative():
    p = _resolve("logs/x.lock")
    assert p == project_root / "logs" / "x.lock"
    print("PASS test_resolve_relative")


def test_resolve_absolute():
    p = _resolve("/tmp/abs.lock")
    assert str(p) == "/tmp/abs.lock"
    print("PASS test_resolve_absolute")


def test_resolve_lock_path_returns_string():
    s = _resolve_lock_path()
    assert isinstance(s, str)
    print("PASS test_resolve_lock_path_returns_string")


def test_resolve_health_path_returns_string():
    s = _resolve_health_path()
    assert isinstance(s, str)
    print("PASS test_resolve_health_path_returns_string")


# ---------------------------------------------------------------------------
# CLI smoke
# ---------------------------------------------------------------------------

def test_cli_status_no_state():
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts/runtime_control.py"), "status"],
        capture_output=True, text=True, timeout=15,
        cwd=str(project_root),
    )
    assert result.returncode in (0, 1)
    assert "Runtime status" in result.stdout
    print("PASS test_cli_status_no_state")


def test_cli_status_json():
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts/runtime_control.py"),
         "status", "--json"],
        capture_output=True, text=True, timeout=15,
        cwd=str(project_root),
    )
    assert result.returncode in (0, 1)
    data = json.loads(result.stdout)
    assert "status" in data
    assert "lock_path" in data
    print("PASS test_cli_status_json")


def test_cli_start_dry_run():
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts/runtime_control.py"),
         "start", "--dry-run"],
        capture_output=True, text=True, timeout=15,
        cwd=str(project_root),
    )
    assert result.returncode == 0
    assert "DRY-RUN" in result.stdout
    print("PASS test_cli_start_dry_run")


def test_cli_stop_when_no_lock():
    """No lock + no live process should be a clean no-op exit 0."""
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts/runtime_control.py"),
         "stop", "--timeout", "3"],
        capture_output=True, text=True, timeout=15,
        cwd=str(project_root),
    )
    assert result.returncode == 0
    print("PASS test_cli_stop_when_no_lock")


# ---------------------------------------------------------------------------
# Cfg patcher helper
# ---------------------------------------------------------------------------

class _CfgPatcher:
    """Monkey-patch the Config instance's load_default_params method."""
    def __init__(self):
        self._real_loader = None
        self._patched = False
        self._cfg_instance = None

    def set(self, cfg):
        from utils import config as cfg_instance
        if not self._patched:
            self._cfg_instance = cfg_instance
            self._real_loader = cfg_instance.load_default_params
            self._patched = True
        cfg_instance.load_default_params = lambda: cfg

    def restore(self):
        if self._patched and self._real_loader is not None and self._cfg_instance is not None:
            self._cfg_instance.load_default_params = self._real_loader
            self._patched = False


def run_all():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        patcher = _CfgPatcher()

        tests = [
            test_status_never_started,
            test_status_stopped,
            test_status_stale_lock,
            test_status_running_live_lock,
            test_status_running_no_lock,
            test_read_health_file_missing,
            test_read_health_file_valid,
            test_read_health_file_corrupt,
            test_read_health_file_not_dict,
            test_format_status_text_never_started,
            test_format_status_text_with_health,
            test_cmd_start_dry_run,
            test_cmd_start_refuses_when_live_lock,
            test_cmd_stop_no_lock,
            test_cmd_stop_stale_lock,
            test_cmd_stop_dry_run,
            test_cmd_stop_signals_live_pid,
            test_cmd_restart_dry_run,
            test_resolve_relative,
            test_resolve_absolute,
            test_resolve_lock_path_returns_string,
            test_resolve_health_path_returns_string,
            test_cli_status_no_state,
            test_cli_status_json,
            test_cli_start_dry_run,
            test_cli_stop_when_no_lock,
        ]

        failures = 0
        for t in tests:
            try:
                params = t.__code__.co_varnames
                if "tmp_root" in params and "cfg_patcher" in params:
                    t(tmp_root=tmp_root, cfg_patcher=patcher)
                elif "tmp_root" in params:
                    t(tmp_root=tmp_root)
                elif "cfg_patcher" in params:
                    t(cfg_patcher=patcher)
                else:
                    t()
            except AssertionError as e:
                print(f"FAIL {t.__name__}: {e}")
                failures += 1
            except Exception as e:
                print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
                failures += 1

        patcher.restore()

        if failures:
            print(f"\n{failures} test(s) failed")
            sys.exit(1)
        print(f"\nAll {len(tests)} tests passed")


if __name__ == "__main__":
    run_all()
