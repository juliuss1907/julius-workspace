#!/usr/bin/env python3
"""Test Phase 9A.1: Process Lock."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.process_lock import ProcessLock, LockHeldError, lock_or_exit, _pid_alive


# ---------------------------------------------------------------------------
# _pid_alive
# ---------------------------------------------------------------------------

def test_pid_alive_self():
    assert _pid_alive(os.getpid()) is True
    print("PASS test_pid_alive_self")


def test_pid_alive_zero():
    assert _pid_alive(0) is False
    assert _pid_alive(-1) is False
    assert _pid_alive(None) is False
    print("PASS test_pid_alive_zero")


def test_pid_alive_nonexistent():
    """A very high PID should not be alive."""
    assert _pid_alive(99999999) is False
    print("PASS test_pid_alive_nonexistent")


# ---------------------------------------------------------------------------
# ProcessLock basic
# ---------------------------------------------------------------------------

def _write_lock(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def test_lock_acquire_success(tmp_root):
    p = tmp_root / "test.lock"
    lock = ProcessLock(path=str(p), name="test")
    payload = lock.acquire()
    assert payload["pid"] == os.getpid()
    assert p.exists()
    lock.release()
    print("PASS test_lock_acquire_success")


def test_lock_release_removes_file(tmp_root):
    p = tmp_root / "test.lock"
    lock = ProcessLock(path=str(p), name="test")
    lock.acquire()
    assert p.exists()
    lock.release()
    assert not p.exists()
    print("PASS test_lock_release_removes_file")


def test_lock_acquire_when_held_raises(tmp_root):
    p = tmp_root / "test.lock"
    lock1 = ProcessLock(path=str(p), name="test")
    lock2 = ProcessLock(path=str(p), name="test")
    lock1.acquire()
    try:
        lock2.acquire()
        assert False, "should have raised"
    except LockHeldError as e:
        assert e.holder["pid"] == os.getpid()
    finally:
        lock1.release()
    print("PASS test_lock_acquire_when_held_raises")


def test_lock_force_raises_when_held(tmp_root):
    p = tmp_root / "test.lock"
    lock1 = ProcessLock(path=str(p), name="test")
    lock2 = ProcessLock(path=str(p), name="test")
    lock1.acquire()
    try:
        try:
            lock2.acquire(force=True)
            assert False, "should have raised"
        except LockHeldError:
            pass
    finally:
        lock1.release()
    print("PASS test_lock_force_raises_when_held")


def test_lock_releases_only_own(tmp_root):
    """A lock with a different PID should not be removed on release()."""
    p = tmp_root / "test.lock"
    _write_lock(p, {
        "pid": 99999999,
        "name": "other",
        "started_at": "2026-01-01T00:00:00",
    })
    lock = ProcessLock(path=str(p), name="test")
    lock.release()
    assert p.exists()
    p.unlink()
    print("PASS test_lock_releases_only_own")


# ---------------------------------------------------------------------------
# Stale lock detection
# ---------------------------------------------------------------------------

def test_stale_lock_can_be_reclaimed(tmp_root):
    p = tmp_root / "test.lock"
    _write_lock(p, {
        "pid": 99999999,
        "name": "dead-process",
        "started_at": "2026-01-01T00:00:00",
    })
    lock = ProcessLock(path=str(p), name="new")
    payload = lock.acquire()
    assert payload["pid"] == os.getpid()
    assert payload["name"] == "new"
    lock.release()
    print("PASS test_stale_lock_can_be_reclaimed")


def test_is_held_with_dead_pid(tmp_root):
    p = tmp_root / "test.lock"
    _write_lock(p, {
        "pid": 99999999,
        "name": "dead",
        "started_at": "2026-01-01T00:00:00",
    })
    lock = ProcessLock(path=str(p), name="test")
    assert lock.is_held() is False
    lock.acquire()
    assert lock.is_held() is True
    lock.release()
    print("PASS test_is_held_with_dead_pid")


def test_is_held_with_live_pid(tmp_root):
    p = tmp_root / "test.lock"
    lock = ProcessLock(path=str(p), name="test")
    lock.acquire()
    try:
        other = ProcessLock(path=str(p), name="other")
        assert other.is_held() is True
    finally:
        lock.release()
    print("PASS test_is_held_with_live_pid")


# ---------------------------------------------------------------------------
# lock_info
# ---------------------------------------------------------------------------

def test_lock_info_missing(tmp_root):
    p = tmp_root / "missing.lock"
    lock = ProcessLock(path=str(p), name="test")
    assert lock.lock_info() is None
    print("PASS test_lock_info_missing")


def test_lock_info_stale_marker(tmp_root):
    p = tmp_root / "test.lock"
    _write_lock(p, {
        "pid": 99999999,
        "name": "dead",
        "started_at": "2026-01-01T00:00:00",
    })
    lock = ProcessLock(path=str(p), name="test")
    info = lock.lock_info()
    assert info["pid_alive"] is False
    assert info["stale"] is True
    p.unlink()
    print("PASS test_lock_info_stale_marker")


def test_lock_info_live_marker(tmp_root):
    p = tmp_root / "test.lock"
    lock = ProcessLock(path=str(p), name="test")
    lock.acquire()
    try:
        info = lock.lock_info()
        assert info["pid_alive"] is True
        assert info["stale"] is False
    finally:
        lock.release()
    print("PASS test_lock_info_live_marker")


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------

def test_context_manager_acquire_release(tmp_root):
    p = tmp_root / "test.lock"
    with ProcessLock(path=str(p), name="ctx") as lock:
        assert p.exists()
    assert not p.exists()
    print("PASS test_context_manager_acquire_release")


def test_context_manager_releases_on_exception(tmp_root):
    p = tmp_root / "test.lock"
    try:
        with ProcessLock(path=str(p), name="ctx") as lock:
            assert p.exists()
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    assert not p.exists()
    print("PASS test_context_manager_releases_on_exception")


# ---------------------------------------------------------------------------
# Malformed lock file
# ---------------------------------------------------------------------------

def test_malformed_lock_file_handled(tmp_root):
    p = tmp_root / "test.lock"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("not json at all", encoding="utf-8")
    lock = ProcessLock(path=str(p), name="test")
    info = lock.lock_info()
    assert info is None
    payload = lock.acquire()
    assert payload["pid"] == os.getpid()
    lock.release()
    print("PASS test_malformed_lock_file_handled")


def test_empty_lock_file_handled(tmp_root):
    p = tmp_root / "test.lock"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("", encoding="utf-8")
    lock = ProcessLock(path=str(p), name="test")
    info = lock.lock_info()
    assert info is None
    payload = lock.acquire()
    lock.release()
    print("PASS test_empty_lock_file_handled")


# ---------------------------------------------------------------------------
# lock_or_exit
# ---------------------------------------------------------------------------

def test_lock_or_exit_exits_when_held(tmp_root):
    p = tmp_root / "test.lock"
    lock = ProcessLock(path=str(p), name="first")
    lock.acquire()
    try:
        result = subprocess.run(
            [sys.executable, "-c",
             f"import sys; sys.path.insert(0, '{project_root}'); "
             f"from utils.process_lock import lock_or_exit; "
             f"lock_or_exit(path='{p}', name='dup')"],
            capture_output=True, text=True, timeout=15,
            cwd=str(project_root),
        )
        assert result.returncode == 1
        assert "Runtime lock active" in result.stderr or "Runtime lock active" in result.stdout
    finally:
        lock.release()
    print("PASS test_lock_or_exit_exits_when_held")


def test_lock_or_exit_succeeds_when_free(tmp_root):
    p = tmp_root / "test.lock"
    script = (
        f"import sys, os; "
        f"sys.path.insert(0, '{project_root}'); "
        f"from utils.process_lock import lock_or_exit; "
        f"lock = lock_or_exit(path='{p}', name='solo'); "
        f"print('PID', os.getpid(), 'acquired'); "
        f"lock.release(); "
        f"print('released')"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True, timeout=15,
        cwd=str(project_root),
    )
    assert result.returncode == 0
    assert "acquired" in result.stdout
    assert "released" in result.stdout
    print("PASS test_lock_or_exit_succeeds_when_free")


# ---------------------------------------------------------------------------
# Integration: run_paper_trading refuses duplicate
# ---------------------------------------------------------------------------

def test_run_paper_trading_refuses_duplicate(tmp_root):
    """Spawn a long-running sleeper holding the lock file, then attempt
    to run the real script. It should exit 1 with the lock message."""
    import time as _t
    real_lock = project_root / "logs" / "run_paper_trading.lock"
    real_lock.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    if real_lock.exists():
        backup = real_lock.read_text(encoding="utf-8")

    sleeper = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"],
    )
    try:
        # Wait briefly for sleeper to start
        for _ in range(20):
            if sleeper.poll() is not None:
                raise RuntimeError("sleeper exited prematurely")
            try:
                os.kill(sleeper.pid, 0)
                break
            except OSError:
                _t.sleep(0.05)

        real_lock.write_text(json.dumps({
            "pid": sleeper.pid,
            "name": "test_sleeper",
            "started_at": "2026-01-01T00:00:00",
        }), encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(project_root / "scripts/run_paper_trading.py"),
             "--single-cycle"],
            capture_output=True, text=True, timeout=30,
            cwd=str(project_root),
        )
        assert result.returncode == 1
        combined = result.stdout + result.stderr
        assert "Runtime lock active" in combined
    finally:
        try:
            sleeper.kill()
            sleeper.wait(timeout=5)
        except Exception:
            try:
                sleeper.kill()
            except Exception:
                pass
        if backup is not None:
            real_lock.write_text(backup, encoding="utf-8")
        elif real_lock.exists():
            real_lock.unlink()
    print("PASS test_run_paper_trading_refuses_duplicate")


def run_all():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)

        tests = [
            test_pid_alive_self, test_pid_alive_zero, test_pid_alive_nonexistent,
            test_lock_acquire_success, test_lock_release_removes_file,
            test_lock_acquire_when_held_raises, test_lock_force_raises_when_held,
            test_lock_releases_only_own,
            test_stale_lock_can_be_reclaimed,
            test_is_held_with_dead_pid, test_is_held_with_live_pid,
            test_lock_info_missing, test_lock_info_stale_marker,
            test_lock_info_live_marker,
            test_context_manager_acquire_release,
            test_context_manager_releases_on_exception,
            test_malformed_lock_file_handled, test_empty_lock_file_handled,
            test_lock_or_exit_exits_when_held,
            test_lock_or_exit_succeeds_when_free,
            test_run_paper_trading_refuses_duplicate,
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
