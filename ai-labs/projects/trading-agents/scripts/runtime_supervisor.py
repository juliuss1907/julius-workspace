#!/usr/bin/env python3
"""
Runtime Supervisor — Phase 9A.4.

Reads `runtime_health.json` + lock state and decides whether the
trading runtime is healthy. Optional auto-restart, with a per-hour
budget to prevent restart loops.

Defaults to `enabled: false` and `mode: monitor_only`. The supervisor
NEVER force-kills and NEVER mutates trading config.

Public API:
  - RuntimeSupervisor(config, project_root) -> supervisor object
  - supervisor.check_once()                   -> decision dict
  - supervisor.run_loop()                     -> never returns
  - classify_health(state, now, stale_after)  -> status string
  - should_restart(decision, mode)            -> bool
  - record_restart(state_file, reason)        -> state dict

CLI:
  ./venv/bin/python scripts/runtime_supervisor.py --once
  ./venv/bin/python scripts/runtime_supervisor.py --loop
  ./venv/bin/python scripts/runtime_supervisor.py --mode auto_restart
  ./venv/bin/python scripts/runtime_supervisor.py --dry-run
"""
import argparse
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.process_lock import ProcessLock
from state.runtime_health import read_health
import scripts.runtime_control as rc


DEFAULT_LOGGER_NAME = "runtime_supervisor"


def _now() -> datetime:
    return datetime.now()


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _parse_iso(s: str) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def classify_health(state: dict, now: datetime, stale_after_seconds: int) -> str:
    """Classify runtime health for the supervisor.

    Returns one of:
      - "fresh_running"
      - "stale_running"
      - "stopped"
      - "stale_lock"
      - "running_no_lock"
      - "never_started"
      - "malformed"
    """
    if not state:
        return "never_started"

    health = state.get("health") or {}
    holder = state.get("lock_holder") or None
    has_holder = holder is not None
    pid_alive = bool(state.get("lock_pid_alive"))

    if not health and not has_holder:
        return "never_started"

    if has_holder and not pid_alive:
        return "stale_lock"

    status = health.get("status")
    lock_checked = "lock_holder" in state
    has_live_lock = bool(has_holder and pid_alive)

    if status == "running" and lock_checked and not has_live_lock:
        return "running_no_lock"

    if status == "running" and not health.get("last_cycle_at"):
        started = _parse_iso(health.get("started_at", ""))
        if started:
            age = (now - started).total_seconds()
            if age > stale_after_seconds * 2:
                return "stale_running"
        return "fresh_running"

    if status == "running":
        last_at = _parse_iso(health.get("last_cycle_at", ""))
        if not last_at:
            return "fresh_running"
        age = (now - last_at).total_seconds()
        if age > stale_after_seconds:
            return "stale_running"
        return "fresh_running"

    if status == "stopped":
        return "stopped"

    if status is None:
        return "malformed"

    return "malformed"


# ---------------------------------------------------------------------------
# Decision + restart budget
# ---------------------------------------------------------------------------

def should_restart(classification: str, mode: str) -> bool:
    """Return True if the supervisor should attempt a restart."""
    if mode not in ("monitor_only", "auto_restart"):
        return False
    if mode == "monitor_only":
        return False
    if classification in ("stale_running", "stale_lock",
                          "running_no_lock", "never_started"):
        return True
    return False


def _load_state(path: Path) -> dict:
    if not path.exists():
        return {"restart_events": []}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {"restart_events": []}
        if not isinstance(data.get("restart_events"), list):
            data["restart_events"] = []
        return data
    except Exception:
        return {"restart_events": []}


def _save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=True)
    os.replace(tmp, path)


def _prune_old_events(events: list, now: datetime, window: timedelta) -> list:
    cutoff = now - window
    pruned = []
    for e in events:
        at = _parse_iso(e.get("at", ""))
        if at and at >= cutoff:
            pruned.append(e)
    return pruned


def _within_budget(state: dict, now: datetime, max_per_hour: int) -> bool:
    if max_per_hour <= 0:
        return False
    events = _prune_old_events(state.get("restart_events", []), now, timedelta(hours=1))
    return len(events) < max_per_hour


def record_restart(state_file: Path, reason: str, now: Optional[datetime] = None) -> dict:
    now = now or _now()
    state = _load_state(state_file)
    state.setdefault("restart_events", []).append({
        "at": _iso(now),
        "reason": reason,
    })
    state["restart_events"] = _prune_old_events(
        state["restart_events"], now, timedelta(hours=24),
    )
    _save_state(state_file, state)
    return state


def count_recent_restarts(state_file: Path, now: Optional[datetime] = None) -> int:
    now = now or _now()
    state = _load_state(state_file)
    return len(_prune_old_events(state.get("restart_events", []), now, timedelta(hours=1)))


# ---------------------------------------------------------------------------
# Decision builder
# ---------------------------------------------------------------------------

@dataclass
class Decision:
    classification: str
    reason: str
    would_restart: bool
    blocked_by_budget: bool
    recent_restarts: int

    def to_dict(self) -> dict:
        return {
            "classification": self.classification,
            "reason": self.reason,
            "would_restart": self.would_restart,
            "blocked_by_budget": self.blocked_by_budget,
            "recent_restarts": self.recent_restarts,
        }


def build_decision(
    state: dict,
    now: datetime,
    sup_cfg: dict,
) -> Decision:
    stale_after = int(sup_cfg.get("stale_after_seconds", 900))
    mode = sup_cfg.get("mode", "monitor_only")
    max_per_hour = int(sup_cfg.get("max_restarts_per_hour", 2))
    state_file = Path(sup_cfg.get("state_file", "logs/runtime_supervisor_state.json"))
    if not state_file.is_absolute():
        state_file = project_root / state_file

    classification = classify_health(state, now, stale_after)
    recent = count_recent_restarts(state_file, now=now)

    reason = ""
    if classification == "fresh_running":
        reason = "runtime reports running and last cycle is recent"
    elif classification == "stale_running":
        last = (state.get("health") or {}).get("last_cycle_at", "?")
        reason = f"last_cycle_at={last} older than {stale_after}s"
    elif classification == "stale_lock":
        pid = (state.get("lock_holder") or {}).get("pid")
        reason = f"lock PID {pid} no longer alive"
    elif classification == "stopped":
        reason = "health file shows status=stopped"
    elif classification == "running_no_lock":
        reason = "health says running but no active lock"
    elif classification == "never_started":
        reason = "no health and no lock"
    elif classification == "malformed":
        reason = "state data could not be classified"

    would_restart = should_restart(classification, mode)
    blocked = False
    if would_restart:
        if not _within_budget(_load_state(state_file), now, max_per_hour):
            would_restart = False
            blocked = True

    return Decision(
        classification=classification,
        reason=reason,
        would_restart=would_restart,
        blocked_by_budget=blocked,
        recent_restarts=recent,
    )


# ---------------------------------------------------------------------------
# Runtime supervisor
# ---------------------------------------------------------------------------

class RuntimeSupervisor:
    def __init__(self, sup_cfg: dict, project_root: Optional[Path] = None,
                 logger: Optional[logging.Logger] = None):
        self.cfg = sup_cfg or {}
        self.root = project_root or Path(__file__).parent.parent
        self.logger = logger or logging.getLogger(DEFAULT_LOGGER_NAME)
        self.lock_path = self._resolve(self.cfg.get("lock_file",
                                                    "logs/run_paper_trading.lock"))
        self.health_path = self._resolve(self.cfg.get("health_file",
                                                      "logs/runtime_health.json"))
        self.state_path = self._resolve(self.cfg.get("state_file",
                                                     "logs/runtime_supervisor_state.json"))
        self.log_path = self._resolve(self.cfg.get("log_file",
                                                   "logs/runtime_supervisor.log"))

    def _resolve(self, path_str: str) -> Path:
        p = Path(path_str)
        if not p.is_absolute():
            p = self.root / p
        return p

    def _current_state(self) -> dict:
        lock = ProcessLock(path=str(self.lock_path), name="trading-runtime")
        info = lock.lock_info()
        health = read_health(str(self.health_path))
        return {
            "status": "inspected",
            "lock_path": str(self.lock_path),
            "health_path": str(self.health_path),
            "lock_pid": info.get("pid") if info else None,
            "lock_pid_alive": bool(info and info.get("pid_alive")),
            "lock_holder": info or None,
            "health": health or {},
        }

    def check_once(self, dry_run: bool = False) -> dict:
        state = self._current_state()
        now = _now()
        decision = build_decision(state, now, self.cfg)

        action = "none"
        if decision.would_restart and not dry_run:
            action = self._perform_restart(decision)
        elif decision.would_restart and dry_run:
            action = "would_restart"

        record = {
            "at": _iso(now),
            "decision": decision.to_dict(),
            "state": state,
            "dry_run": dry_run,
            "action": action,
        }
        return record

    def _perform_restart(self, decision: Decision) -> str:
        try:
            stop_rc = rc.cmd_stop(_ns(timeout=15.0, dry_run=False))
        except Exception as e:
            self.logger.error(f"supervisor stop failed: {e}")
            return f"stop_error:{e}"
        time.sleep(2.0)
        try:
            start_rc = rc.cmd_start(_ns(
                mode=self.cfg.get("restart_mode", "continuous"),
                dry_run=False,
            ))
        except Exception as e:
            self.logger.error(f"supervisor start failed: {e}")
            return f"start_error:{e}"

        record_restart(self.state_path, reason=decision.classification)
        return f"restarted: stop={stop_rc} start={start_rc}"

    def run_loop(self, dry_run: bool = False) -> None:
        interval = float(self.cfg.get("check_interval_seconds", 60))
        self.logger.info(
            f"supervisor loop start: mode={self.cfg.get('mode', 'monitor_only')}, "
            f"interval={interval}s, dry_run={dry_run}"
        )
        try:
            while True:
                try:
                    record = self.check_once(dry_run=dry_run)
                    self._log_record(record)
                except Exception as e:
                    self.logger.error(f"supervisor check error: {e}")
                time.sleep(interval)
        except KeyboardInterrupt:
            self.logger.info("supervisor loop interrupted")

    def _log_record(self, record: dict) -> None:
        d = record["decision"]
        self.logger.info(
            f"classification={d['classification']} action={record['action']} "
            f"reason={d['reason']} recent_restarts={d['recent_restarts']}"
        )


# ---------------------------------------------------------------------------
# Argparse namespace helper
# ---------------------------------------------------------------------------

def _ns(**kwargs):
    """Build a small argparse-like namespace for runtime_control helpers."""
    import argparse
    return argparse.Namespace(**kwargs)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _load_supervisor_cfg() -> dict:
    try:
        from utils import config as cfg_loader
        cfg = cfg_loader.load_default_params()
    except Exception:
        return {}
    return (cfg or {}).get("runtime", {}).get("supervisor", {}) or {}


def main():
    parser = argparse.ArgumentParser(description="Trading runtime supervisor")
    parser.add_argument("--once", action="store_true",
                        help="Run a single check then exit")
    parser.add_argument("--loop", action="store_true",
                        help="Run periodic checks until interrupted")
    parser.add_argument("--mode", default=None,
                        choices=["monitor_only", "auto_restart"],
                        help="Override supervisor mode")
    parser.add_argument("--dry-run", action="store_true",
                        help="Recommend actions without performing restarts")
    parser.add_argument("--json", action="store_true",
                        help="Print last record as JSON")
    args = parser.parse_args()

    cfg = _load_supervisor_cfg()
    if args.mode:
        cfg["mode"] = args.mode

    log_path = Path(cfg.get("log_file", "logs/runtime_supervisor.log"))
    if not log_path.is_absolute():
        log_path = project_root / log_path
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(str(log_path), encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    logger = logging.getLogger(DEFAULT_LOGGER_NAME)

    if not cfg.get("enabled", False):
        logger.warning(
            "supervisor is disabled in config (runtime.supervisor.enabled=false). "
            "Running one check anyway."
        )

    sup = RuntimeSupervisor(cfg, project_root=project_root, logger=logger)

    if args.loop:
        sup.run_loop(dry_run=args.dry_run)
        return 0

    record = sup.check_once(dry_run=args.dry_run)
    sup._log_record(record)
    if args.json:
        print(json.dumps(record, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
