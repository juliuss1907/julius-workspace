#!/usr/bin/env python3
"""Test Phase 9A.2: Scheduler Guard (skip-on-live-lock + log rotation hook)."""
import json
import logging
import os
import subprocess
import sys
import tempfile
import time as _t
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.trading_scheduler import TradingScheduler
from utils.process_lock import ProcessLock


# ---------------------------------------------------------------------------
# _full_runtime_active
# ---------------------------------------------------------------------------

def test_full_runtime_active_no_lock(tmp_root):
    """When no lock exists, scheduler should report not-active."""
    cfg = {
        "scheduler": {
            "full_mode_time": "07:00",
            "lite_mode_enabled": False,
            "report_time": "23:00",
        },
        "runtime": {
            "prevent_duplicate_instances": True,
            "lock_file": str(tmp_root / "missing.lock"),
        },
    }
    import importlib
    utils_config = importlib.import_module("utils")
    real_loader = utils_config.config.load_default_params

    def fake_loader():
        return cfg
    utils_config.config.load_default_params = fake_loader
    try:
        sch = TradingScheduler()
        active, holder = sch._full_runtime_active()
        assert active is False
    finally:
        utils_config.config.load_default_params = real_loader
    print("PASS test_full_runtime_active_no_lock")


def test_full_runtime_active_stale_lock(tmp_root):
    """Stale lock should not be reported as active."""
    lock = tmp_root / "stale.lock"
    lock.write_text(json.dumps({
        "pid": 99999999, "name": "dead", "started_at": "2026-01-01T00:00:00",
    }), encoding="utf-8")
    cfg = {
        "scheduler": {"full_mode_time": "07:00", "lite_mode_enabled": False, "report_time": "23:00"},
        "runtime": {"prevent_duplicate_instances": True, "lock_file": str(lock)},
    }
    import importlib
    utils_config = importlib.import_module("utils")
    real_loader = utils_config.config.load_default_params
    utils_config.config.load_default_params = lambda: cfg
    try:
        sch = TradingScheduler()
        active, _ = sch._full_runtime_active()
        assert active is False
    finally:
        utils_config.config.load_default_params = real_loader
    print("PASS test_full_runtime_active_stale_lock")


def test_full_runtime_active_live_lock(tmp_root):
    """Live lock should be reported as active."""
    lock = tmp_root / "live.lock"

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

        cfg = {
            "scheduler": {"full_mode_time": "07:00", "lite_mode_enabled": False, "report_time": "23:00"},
            "runtime": {"prevent_duplicate_instances": True, "lock_file": str(lock)},
        }
        import importlib
        utils_config = importlib.import_module("utils")
        real_loader = utils_config.config.load_default_params
        utils_config.config.load_default_params = lambda: cfg
        try:
            sch = TradingScheduler()
            active, holder = sch._full_runtime_active()
            assert active is True
            assert holder["pid"] == sleeper.pid
        finally:
            utils_config.config.load_default_params = real_loader
    finally:
        try:
            sleeper.kill()
            sleeper.wait(timeout=5)
        except Exception:
            pass
    print("PASS test_full_runtime_active_live_lock")


def test_full_runtime_active_disabled_in_config(tmp_root):
    """If prevent_duplicate_instances is false, always report not-active."""
    cfg = {
        "scheduler": {"full_mode_time": "07:00", "lite_mode_enabled": False, "report_time": "23:00"},
        "runtime": {"prevent_duplicate_instances": False, "lock_file": str(tmp_root / "x.lock")},
    }
    import importlib
    utils_config = importlib.import_module("utils")
    real_loader = utils_config.config.load_default_params
    utils_config.config.load_default_params = lambda: cfg
    try:
        sch = TradingScheduler()
        active, _ = sch._full_runtime_active()
        assert active is False
    finally:
        utils_config.config.load_default_params = real_loader
    print("PASS test_full_runtime_active_disabled_in_config")


# ---------------------------------------------------------------------------
# run_full_mode skip on live lock
# ---------------------------------------------------------------------------

def test_run_full_mode_skips_when_live_lock(tmp_root):
    """run_full_mode should return None and not start a process when live lock exists."""
    lock = tmp_root / "live.lock"
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

        cfg = {
            "scheduler": {"full_mode_time": "07:00", "lite_mode_enabled": False, "report_time": "23:00"},
            "runtime": {"prevent_duplicate_instances": True, "lock_file": str(lock)},
        }
        import importlib
        utils_config = importlib.import_module("utils")
        real_loader = utils_config.config.load_default_params
        utils_config.config.load_default_params = lambda: cfg
        try:
            sch = TradingScheduler()
            sch.last_full_run = None
            sch.last_full_skipped = None
            result = sch.run_full_mode()
            assert result is None
            assert sch.last_full_skipped is not None
        finally:
            utils_config.config.load_default_params = real_loader
    finally:
        try:
            sleeper.kill()
            sleeper.wait(timeout=5)
        except Exception:
            pass
    print("PASS test_run_full_mode_skips_when_live_lock")


# ---------------------------------------------------------------------------
# _rotate_logs (uses real log_rotation)
# ---------------------------------------------------------------------------

def test_rotate_logs_handles_missing_config(tmp_root):
    cfg = {
        "scheduler": {"full_mode_time": "07:00", "lite_mode_enabled": False, "report_time": "23:00"},
        "runtime": {},
    }
    import importlib
    utils_config = importlib.import_module("utils")
    real_loader = utils_config.config.load_default_params
    utils_config.config.load_default_params = lambda: cfg
    try:
        sch = TradingScheduler()
        sch._rotate_logs()  # should not raise
    finally:
        utils_config.config.load_default_params = real_loader
    print("PASS test_rotate_logs_handles_missing_config")


def test_rotate_logs_with_real_file(tmp_root):
    # The scheduler uses project_root as the safety boundary.
    # Use a project-relative path so the safety check passes.
    log_rel = "logs/test_scheduler_rotation_temp.log"
    abs_log = project_root / log_rel
    abs_log.parent.mkdir(parents=True, exist_ok=True)
    backup_log = abs_log.with_suffix(abs_log.suffix + ".1")
    if backup_log.exists():
        backup_log.unlink()
    if abs_log.exists():
        abs_log.unlink()
    abs_log.write_text("a" * 200, encoding="utf-8")

    try:
        cfg = {
            "scheduler": {"full_mode_time": "07:00", "lite_mode_enabled": False, "report_time": "23:00"},
            "runtime": {
                "prevent_duplicate_instances": True,
                "lock_file": str(tmp_root / "x.lock"),
                "log_rotation": {
                    "enabled": True,
                    "max_bytes": 100,
                    "keep_files": 3,
                    "files": [log_rel],
                },
            },
        }
        import importlib
        utils_config = importlib.import_module("utils")
        real_loader = utils_config.config.load_default_params
        utils_config.config.load_default_params = lambda: cfg
        try:
            sch = TradingScheduler()
            sch._rotate_logs()
            assert backup_log.exists(), f"expected backup at {backup_log}"
        finally:
            utils_config.config.load_default_params = real_loader
    finally:
        if abs_log.exists():
            abs_log.unlink()
        if backup_log.exists():
            backup_log.unlink()
    print("PASS test_rotate_logs_with_real_file")


def run_all():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)

        tests = [
            test_full_runtime_active_no_lock,
            test_full_runtime_active_stale_lock,
            test_full_runtime_active_live_lock,
            test_full_runtime_active_disabled_in_config,
            test_run_full_mode_skips_when_live_lock,
            test_rotate_logs_handles_missing_config,
            test_rotate_logs_with_real_file,
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
