#!/usr/bin/env json
"""Test Phase 9A.4: Runtime Supervisor / Heartbeat Monitor."""
import argparse
import json
import logging
import os
import subprocess
import sys
import tempfile
import time as _t
from datetime import datetime, timedelta
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.runtime_supervisor import (
    classify_health,
    should_restart,
    build_decision,
    record_restart,
    count_recent_restarts,
    _load_state,
    _prune_old_events,
    _within_budget,
    RuntimeSupervisor,
    _now,
    _iso,
    _parse_iso,
)
import scripts.runtime_supervisor as sup_mod


# ---------------------------------------------------------------------------
# _parse_iso / _now / _iso
# ---------------------------------------------------------------------------

def test_parse_iso_valid():
    dt = _parse_iso("2026-06-08T19:00:00.000000")
    assert dt is not None
    assert dt.year == 2026
    print("PASS test_parse_iso_valid")


def test_parse_iso_empty():
    assert _parse_iso("") is None
    assert _parse_iso("not a date") is None
    print("PASS test_parse_iso_empty")


def test_now_and_iso_roundtrip():
    s = _iso(_now())
    dt = _parse_iso(s)
    assert dt is not None
    print("PASS test_now_and_iso_roundtrip")


# ---------------------------------------------------------------------------
# classify_health
# ---------------------------------------------------------------------------

def test_classify_health_never_started():
    s = {}
    assert classify_health(s, _now(), 900) == "never_started"
    print("PASS test_classify_health_never_started")


def test_classify_health_fresh_running():
    now = _now()
    s = {
        "health": {
            "status": "running",
            "last_cycle_at": _iso(now - timedelta(seconds=60)),
            "started_at": _iso(now - timedelta(seconds=120)),
        }
    }
    assert classify_health(s, now, 900) == "fresh_running"
    print("PASS test_classify_health_fresh_running")


def test_classify_health_stale_running():
    now = _now()
    s = {
        "health": {
            "status": "running",
            "last_cycle_at": _iso(now - timedelta(seconds=2000)),
            "started_at": _iso(now - timedelta(seconds=3000)),
        }
    }
    assert classify_health(s, now, 900) == "stale_running"
    print("PASS test_classify_health_stale_running")


def test_classify_health_running_no_cycle_uses_started_at():
    now = _now()
    s = {
        "health": {
            "status": "running",
            "started_at": _iso(now - timedelta(seconds=5000)),
        }
    }
    assert classify_health(s, now, 900) == "stale_running"
    print("PASS test_classify_health_running_no_cycle_uses_started_at")


def test_classify_health_stopped():
    s = {"health": {"status": "stopped"}}
    assert classify_health(s, _now(), 900) == "stopped"
    print("PASS test_classify_health_stopped")


def test_classify_health_stale_lock():
    s = {
        "lock_pid": 99999999,
        "lock_pid_alive": False,
        "lock_holder": {"pid": 99999999, "name": "dead"},
        "health": {"status": "stopped"},
    }
    assert classify_health(s, _now(), 900) == "stale_lock"
    print("PASS test_classify_health_stale_lock")


def test_classify_health_running_no_lock():
    s = {
        "lock_pid": None,
        "lock_pid_alive": False,
        "lock_holder": None,
        "health": {"status": "running"},
    }
    assert classify_health(s, _now(), 900) == "running_no_lock"
    print("PASS test_classify_health_running_no_lock")


def test_classify_health_malformed():
    """State with no health and no lock_holder classifies as never_started."""
    s = {"lock_pid_alive": False}
    assert classify_health(s, _now(), 900) == "never_started"
    print("PASS test_classify_health_malformed")


# ---------------------------------------------------------------------------
# should_restart
# ---------------------------------------------------------------------------

def test_should_restart_monitor_only_never_restarts():
    for c in ("stale_running", "stale_lock", "running_no_lock",
              "never_started", "stopped", "fresh_running"):
        assert should_restart(c, "monitor_only") is False, c
    print("PASS test_should_restart_monitor_only_never_restarts")


def test_should_restart_auto_restart_targets():
    assert should_restart("stale_running", "auto_restart") is True
    assert should_restart("stale_lock", "auto_restart") is True
    assert should_restart("running_no_lock", "auto_restart") is True
    assert should_restart("never_started", "auto_restart") is True
    print("PASS test_should_restart_auto_restart_targets")


def test_should_restart_auto_restart_skips_healthy():
    assert should_restart("fresh_running", "auto_restart") is False
    assert should_restart("stopped", "auto_restart") is False
    assert should_restart("malformed", "auto_restart") is False
    print("PASS test_should_restart_auto_restart_skips_healthy")


def test_should_restart_unknown_mode():
    assert should_restart("stale_running", "weird_mode") is False
    print("PASS test_should_restart_unknown_mode")


# ---------------------------------------------------------------------------
# Restart budget
# ---------------------------------------------------------------------------

def test_prune_old_events(tmp_root):
    now = _now()
    events = [
        {"at": _iso(now - timedelta(hours=3)), "reason": "old"},
        {"at": _iso(now - timedelta(minutes=10)), "reason": "recent"},
        {"at": "garbage", "reason": "broken"},
    ]
    pruned = _prune_old_events(events, now, timedelta(hours=1))
    assert len(pruned) == 1
    assert pruned[0]["reason"] == "recent"
    print("PASS test_prune_old_events")


def test_within_budget_true(tmp_root):
    state = {"restart_events": [
        {"at": _iso(_now() - timedelta(minutes=10)), "reason": "x"},
    ]}
    assert _within_budget(state, _now(), max_per_hour=2) is True
    print("PASS test_within_budget_true")


def test_within_budget_false(tmp_root):
    state = {"restart_events": [
        {"at": _iso(_now() - timedelta(minutes=5)), "reason": "a"},
        {"at": _iso(_now() - timedelta(minutes=10)), "reason": "b"},
        {"at": _iso(_now() - timedelta(minutes=20)), "reason": "c"},
    ]}
    assert _within_budget(state, _now(), max_per_hour=2) is False
    print("PASS test_within_budget_false")


def test_record_restart(tmp_root):
    state_file = tmp_root / "sup_state.json"
    record_restart(state_file, reason="stale_running")
    record_restart(state_file, reason="stale_lock")
    data = _load_state(state_file)
    assert len(data["restart_events"]) == 2
    assert data["restart_events"][0]["reason"] == "stale_running"
    print("PASS test_record_restart")


def test_count_recent_restarts(tmp_root):
    state_file = tmp_root / "count_sup_state.json"
    record_restart(state_file, reason="x")
    record_restart(state_file, reason="y")
    assert count_recent_restarts(state_file) == 2
    print("PASS test_count_recent_restarts")


# ---------------------------------------------------------------------------
# build_decision
# ---------------------------------------------------------------------------

def _default_sup_cfg(tmp_root, **overrides):
    cfg = {
        "stale_after_seconds": 900,
        "mode": "monitor_only",
        "max_restarts_per_hour": 2,
        "state_file": str(tmp_root / "sup_state.json"),
    }
    cfg.update(overrides)
    return cfg


def test_build_decision_fresh_running_no_restart(tmp_root):
    now = _now()
    state = {
        "lock_pid": os.getpid(),
        "lock_pid_alive": True,
        "lock_holder": {"pid": os.getpid(), "name": "test"},
        "health": {
            "status": "running",
            "last_cycle_at": _iso(now - timedelta(seconds=60)),
        },
    }
    d = build_decision(state, now, _default_sup_cfg(
        tmp_root, mode="auto_restart",
        state_file=str(tmp_root / "fresh_running_test.json"),
    ))
    assert d.classification == "fresh_running"
    assert d.would_restart is False
    print("PASS test_build_decision_fresh_running_no_restart")


def test_build_decision_stale_running_restart(tmp_root):
    now = _now()
    state = {
        "lock_pid": os.getpid(),
        "lock_pid_alive": True,
        "lock_holder": {"pid": os.getpid(), "name": "test"},
        "health": {
            "status": "running",
            "last_cycle_at": _iso(now - timedelta(seconds=2000)),
        },
    }
    d = build_decision(state, now, _default_sup_cfg(
        tmp_root, mode="auto_restart",
        state_file=str(tmp_root / "stale_running_test.json"),
    ))
    assert d.classification == "stale_running"
    assert d.would_restart is True
    assert d.blocked_by_budget is False
    print("PASS test_build_decision_stale_running_restart")


def test_build_decision_stale_lock_restart(tmp_root):
    state = {
        "lock_pid": 99999999,
        "lock_pid_alive": False,
        "lock_holder": {"pid": 99999999, "name": "dead"},
        "health": {"status": "stopped"},
    }
    d = build_decision(state, _now(), _default_sup_cfg(
        tmp_root, mode="auto_restart",
        state_file=str(tmp_root / "stale_lock_test.json"),
    ))
    assert d.classification == "stale_lock"
    assert d.would_restart is True
    print("PASS test_build_decision_stale_lock_restart")


def test_build_decision_blocked_by_budget(tmp_root):
    state_file = tmp_root / "blocked_budget_test.json"
    for _ in range(2):
        record_restart(state_file, reason="x")
    now = _now()
    state = {
        "lock_pid": os.getpid(),
        "lock_pid_alive": True,
        "lock_holder": {"pid": os.getpid(), "name": "test"},
        "health": {
            "status": "running",
            "last_cycle_at": _iso(now - timedelta(seconds=2000)),
        },
    }
    d = build_decision(state, now, _default_sup_cfg(
        tmp_root, mode="auto_restart", max_restarts_per_hour=2,
        state_file=str(state_file),
    ))
    assert d.classification == "stale_running"
    assert d.would_restart is False
    assert d.blocked_by_budget is True
    assert d.recent_restarts == 2
    print("PASS test_build_decision_blocked_by_budget")


def test_build_decision_monitor_only_never_restarts(tmp_root):
    now = _now()
    state = {
        "lock_pid": os.getpid(),
        "lock_pid_alive": True,
        "lock_holder": {"pid": os.getpid(), "name": "test"},
        "health": {
            "status": "running",
            "last_cycle_at": _iso(now - timedelta(seconds=2000)),
        },
    }
    d = build_decision(state, now, _default_sup_cfg(
        tmp_root, mode="monitor_only",
        state_file=str(tmp_root / "monitor_only_test.json"),
    ))
    assert d.would_restart is False
    print("PASS test_build_decision_monitor_only_never_restarts")


def test_build_decision_stopped_no_restart(tmp_root):
    state = {"health": {"status": "stopped"}}
    d = build_decision(state, _now(),
                       _default_sup_cfg(tmp_root, mode="auto_restart"))
    assert d.classification == "stopped"
    assert d.would_restart is False
    print("PASS test_build_decision_stopped_no_restart")


# ---------------------------------------------------------------------------
# RuntimeSupervisor
# ---------------------------------------------------------------------------

def test_supervisor_check_once_dry_run(tmp_root):
    cfg = _default_sup_cfg(
        tmp_root, mode="auto_restart",
        lock_file=str(tmp_root / "no.lock"),
        health_file=str(tmp_root / "no.json"),
        state_file=str(tmp_root / "dry_run_test.json"),
    )
    sup = RuntimeSupervisor(cfg, project_root=tmp_root)
    record = sup.check_once(dry_run=True)
    assert record["dry_run"] is True
    assert record["decision"]["classification"] == "never_started"
    assert record["action"] == "would_restart"
    print("PASS test_supervisor_check_once_dry_run")


def test_supervisor_check_once_monitor_only(tmp_root):
    cfg = _default_sup_cfg(
        tmp_root, mode="monitor_only",
        lock_file=str(tmp_root / "no.lock"),
        health_file=str(tmp_root / "no.json"),
    )
    sup = RuntimeSupervisor(cfg, project_root=tmp_root)
    record = sup.check_once(dry_run=False)
    assert record["action"] == "none"
    assert record["decision"]["would_restart"] is False
    print("PASS test_supervisor_check_once_monitor_only")


def test_supervisor_no_force_kill_in_perform(tmp_root):
    """Ensure _perform_restart uses cmd_stop and cmd_start, never SIGKILL."""
    import scripts.runtime_supervisor as sup_mod
    calls = {"stop": 0, "start": 0}

    def fake_stop(ns):
        calls["stop"] += 1
        return 0

    def fake_start(ns):
        calls["start"] += 1
        return 0

    real_stop = sup_mod.rc.cmd_stop
    real_start = sup_mod.rc.cmd_start
    sup_mod.rc.cmd_stop = fake_stop
    sup_mod.rc.cmd_start = fake_start
    try:
        cfg = _default_sup_cfg(
            tmp_root, mode="auto_restart",
            lock_file=str(tmp_root / "no.lock"),
            health_file=str(tmp_root / "no.json"),
            state_file=str(tmp_root / "sup_state.json"),
        )
        sup = RuntimeSupervisor(cfg, project_root=tmp_root)
        state_file = tmp_root / "sup_state.json"
        state_file.write_text(json.dumps({"restart_events": []}), encoding="utf-8")
        d = sup_mod.Decision(
            classification="stale_running", reason="test",
            would_restart=True, blocked_by_budget=False, recent_restarts=0,
        )
        action = sup._perform_restart(d)
        assert calls["stop"] == 1
        assert calls["start"] == 1
        assert "restarted" in action
        assert _load_state(state_file)["restart_events"], "restart event should be recorded"
    finally:
        sup_mod.rc.cmd_stop = real_stop
        sup_mod.rc.cmd_start = real_start
    print("PASS test_supervisor_no_force_kill_in_perform")


def test_dry_run_does_not_spawn_runtime(tmp_root):
    """dry-run must not actually invoke cmd_stop / cmd_start."""
    import scripts.runtime_supervisor as sup_mod
    calls = {"stop": 0, "start": 0}

    def fake_stop(ns):
        calls["stop"] += 1
        return 0

    def fake_start(ns):
        calls["start"] += 1
        return 0

    real_stop = sup_mod.rc.cmd_stop
    real_start = sup_mod.rc.cmd_start
    sup_mod.rc.cmd_stop = fake_stop
    sup_mod.rc.cmd_start = fake_start
    try:
        cfg = _default_sup_cfg(
            tmp_root, mode="auto_restart",
            lock_file=str(tmp_root / "no.lock"),
            health_file=str(tmp_root / "no.json"),
            state_file=str(tmp_root / "sup_state.json"),
        )
        sup = RuntimeSupervisor(cfg, project_root=tmp_root)
        record = sup.check_once(dry_run=True)
        assert record["action"] == "would_restart"
        assert calls["stop"] == 0
        assert calls["start"] == 0
    finally:
        sup_mod.rc.cmd_stop = real_stop
        sup_mod.rc.cmd_start = real_start
    print("PASS test_dry_run_does_not_spawn_runtime")


# ---------------------------------------------------------------------------
# CLI smoke
# ---------------------------------------------------------------------------

def test_cli_once_dry_run_monitor_only():
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts/runtime_supervisor.py"),
         "--once", "--dry-run", "--mode", "monitor_only", "--json"],
        capture_output=True, text=True, timeout=30,
        cwd=str(project_root),
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "decision" in data
    assert "classification" in data["decision"]
    print("PASS test_cli_once_dry_run_monitor_only")


def test_cli_once_dry_run_auto_restart():
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts/runtime_supervisor.py"),
         "--once", "--dry-run", "--mode", "auto_restart", "--json"],
        capture_output=True, text=True, timeout=30,
        cwd=str(project_root),
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["decision"]["would_restart"] in (True, False)
    print("PASS test_cli_once_dry_run_auto_restart")


def test_cli_help():
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts/runtime_supervisor.py"), "--help"],
        capture_output=True, text=True, timeout=15,
        cwd=str(project_root),
    )
    assert result.returncode == 0
    assert "supervisor" in result.stdout.lower()
    print("PASS test_cli_help")


# ---------------------------------------------------------------------------
# Integration: dry-run auto-restart path (see test_dry_run_does_not_spawn_runtime above)
# ---------------------------------------------------------------------------


def run_all():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)

        tests = [
            test_parse_iso_valid, test_parse_iso_empty,
            test_now_and_iso_roundtrip,
            test_classify_health_never_started,
            test_classify_health_fresh_running,
            test_classify_health_stale_running,
            test_classify_health_running_no_cycle_uses_started_at,
            test_classify_health_stopped,
            test_classify_health_stale_lock,
            test_classify_health_running_no_lock,
            test_classify_health_malformed,
            test_should_restart_monitor_only_never_restarts,
            test_should_restart_auto_restart_targets,
            test_should_restart_auto_restart_skips_healthy,
            test_should_restart_unknown_mode,
            test_prune_old_events,
            test_within_budget_true,
            test_within_budget_false,
            test_record_restart,
            test_count_recent_restarts,
            test_build_decision_fresh_running_no_restart,
            test_build_decision_stale_running_restart,
            test_build_decision_stale_lock_restart,
            test_build_decision_blocked_by_budget,
            test_build_decision_monitor_only_never_restarts,
            test_build_decision_stopped_no_restart,
            test_supervisor_check_once_dry_run,
            test_supervisor_check_once_monitor_only,
            test_supervisor_no_force_kill_in_perform,
            test_cli_once_dry_run_monitor_only,
            test_cli_once_dry_run_auto_restart,
            test_cli_help,
            test_dry_run_does_not_spawn_runtime,
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
