#!/usr/bin/env python3
"""
Runtime Control CLI — Phase 9A.3.

Manages the trading runtime safely via the existing ProcessLock +
RuntimeHealth primitives.

Commands:
  status    - report lock + health state
  start     - launch run_paper_trading.py in background
  stop      - SIGTERM the process holding the lock
  restart   - stop then start

Safety rules:
  - Only kills PIDs read from the lock file
  - Never sends SIGKILL by default
  - Stale locks do not block start (let runtime reclaim)
  - start refuses if a live lock exists
  - stop is a no-op when no live lock exists

Usage:
  ./venv/bin/python scripts/runtime_control.py status
  ./venv/bin/python scripts/runtime_control.py start
  ./venv/bin/python scripts/runtime_control.py start --mode single-cycle
  ./venv/bin/python scripts/runtime_control.py stop
  ./venv/bin/python scripts/runtime_control.py restart
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.process_lock import ProcessLock


PYTHON = sys.executable


def _read_health_file(path: str) -> dict:
    """Read runtime health JSON using stdlib only.

    Returns {} if the file is missing, unreadable, corrupt, or not a dict.
    This keeps runtime_control lightweight and independent of aiosqlite.
    """
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def _resolve_lock_path() -> str:
    """Resolve runtime lock path from config, falling back to default."""
    try:
        from utils import config as cfg_loader
        cfg = cfg_loader.load_default_params()
        runtime_cfg = (cfg or {}).get("runtime", {}) or {}
        return runtime_cfg.get("lock_file", "logs/run_paper_trading.lock")
    except Exception:
        return "logs/run_paper_trading.lock"


def _resolve_health_path() -> str:
    try:
        from utils import config as cfg_loader
        cfg = cfg_loader.load_default_params()
        runtime_cfg = (cfg or {}).get("runtime", {}) or {}
        return runtime_cfg.get("health_file", "logs/runtime_health.json")
    except Exception:
        return "logs/runtime_health.json"


def _resolve(path_str: str) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        p = project_root / p
    return p


def resolve_status() -> dict:
    """Inspect lock + health, return a structured status."""
    lock_path = _resolve(_resolve_lock_path())
    health_path = _resolve(_resolve_health_path())

    lock = ProcessLock(path=str(lock_path), name="trading-runtime")
    info = lock.lock_info()
    health = _read_health_file(str(health_path))

    pid_alive = bool(info and info.get("pid_alive"))
    lock_pid = info.get("pid") if info else None

    if info and pid_alive:
        status = "running"
    elif info and not pid_alive:
        status = "stale_lock"
    elif health and health.get("status") == "stopped":
        status = "stopped"
    elif health and health.get("status") == "running":
        status = "running_no_lock"
    else:
        status = "never_started"

    return {
        "status": status,
        "lock_path": str(lock_path),
        "health_path": str(health_path),
        "lock_pid": lock_pid,
        "lock_pid_alive": pid_alive,
        "lock_holder": info or None,
        "health": health or {},
    }


def format_status_text(state: dict) -> str:
    lines = []
    lines.append(f"Runtime status: {state['status']}")
    lines.append(f"Lock:   {state['lock_path']}")
    lines.append(f"Health: {state['health_path']}")
    if state["lock_pid"] is not None:
        lines.append(
            f"Lock PID: {state['lock_pid']} (alive={state['lock_pid_alive']})"
        )
    health = state.get("health") or {}
    if health:
        last_at = health.get("last_cycle_at")
        last_status = health.get("last_cycle_status")
        cycle_count = health.get("cycle_count")
        if last_at:
            lines.append(f"Last cycle at:    {last_at}")
        if last_status:
            lines.append(f"Last cycle:       {last_status}")
        if cycle_count is not None:
            lines.append(f"Cycle count:      {cycle_count}")
        stop_reason = health.get("stop_reason")
        if stop_reason:
            lines.append(f"Stop reason:      {stop_reason}")
    return "\n".join(lines)


def cmd_status(args) -> int:
    state = resolve_status()
    if args.json:
        import json
        print(json.dumps(state, indent=2, ensure_ascii=True))
    else:
        print(format_status_text(state))
    status = state["status"]
    if status in ("running", "stopped", "never_started", "stale_lock", "running_no_lock"):
        return 0
    return 1


def cmd_start(args) -> int:
    lock_path = _resolve(_resolve_lock_path())
    lock = ProcessLock(path=str(lock_path), name="trading-runtime")

    info = lock.lock_info()
    if info and info.get("pid_alive"):
        pid = info.get("pid")
        print(f"Refusing to start: lock already held by live PID {pid}")
        return 1

    script = project_root / "scripts" / "run_paper_trading.py"
    if not script.exists():
        print(f"Error: trading script not found at {script}")
        return 1

    log_path = project_root / "logs" / "runtime_control.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [PYTHON, str(script)]
    if args.mode == "single-cycle":
        cmd.append("--single-cycle")

    if args.dry_run:
        print(f"[DRY-RUN] would launch: {' '.join(cmd)}")
        print(f"[DRY-RUN] log: {log_path}")
        return 0

    log_fp = open(log_path, "a", encoding="utf-8")
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=log_fp,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            cwd=str(project_root),
        )
    finally:
        log_fp.close()

    print(f"Started trading runtime (PID {proc.pid})")
    print(f"Log: {log_path}")
    return 0


def cmd_stop(args) -> int:
    lock_path = _resolve(_resolve_lock_path())
    lock = ProcessLock(path=str(lock_path), name="trading-runtime")

    info = lock.lock_info()
    if not info:
        print("No lock file; nothing to stop.")
        return 0

    if not info.get("pid_alive"):
        print(
            f"Lock exists but PID {info.get('pid')} is not alive. "
            f"Cleaning up stale lock."
        )
        # Stale lock — process is dead, so safe to remove the file
        # regardless of which PID wrote it.
        try:
            lock_path_obj = Path(lock_path)
            if lock_path_obj.exists():
                lock_path_obj.unlink()
        except OSError as e:
            print(f"Warning: could not remove stale lock: {e}")
        return 0

    pid = info.get("pid")
    if args.dry_run:
        print(f"[DRY-RUN] would SIGTERM PID {pid}")
        return 0

    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        print(f"PID {pid} already gone. Cleaning up lock.")
        lock.release()
        return 0
    except PermissionError:
        print(f"Permission denied sending SIGTERM to PID {pid}")
        return 1
    except OSError as e:
        print(f"Failed to send SIGTERM to PID {pid}: {e}")
        return 1

    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
            time.sleep(0.2)
        except ProcessLookupError:
            print(f"PID {pid} stopped.")
            # Process is dead; safe to remove lock regardless of which
            # PID wrote it.
            try:
                if lock_path.exists():
                    lock_path.unlink()
            except OSError as e:
                print(f"Warning: could not remove lock: {e}")
            return 0
        except PermissionError:
            time.sleep(0.2)

    try:
        os.kill(pid, 0)
        still_alive = True
    except ProcessLookupError:
        still_alive = False

    if still_alive:
        print(
            f"PID {pid} still alive after {args.timeout}s. "
            f"Refusing to force-kill. Re-run with --timeout or use OS tools."
        )
        return 2

    print(f"PID {pid} stopped. Cleaning up lock.")
    lock.release()
    return 0


def cmd_restart(args) -> int:
    if args.dry_run:
        print("[DRY-RUN] would stop then start")
        print("[DRY-RUN] stop:")
        rc_stop = cmd_stop(argparse.Namespace(timeout=args.timeout, dry_run=True))
        print(f"[DRY-RUN] stop returned {rc_stop}")
        print("[DRY-RUN] start:")
        rc_start = cmd_start(argparse.Namespace(mode=args.mode, dry_run=True))
        print(f"[DRY-RUN] start returned {rc_start}")
        return 0

    print("Stopping...")
    rc_stop = cmd_stop(argparse.Namespace(timeout=args.timeout, dry_run=False))
    print(f"Stop exit: {rc_stop}")
    if rc_stop not in (0, 1):
        print(f"Stop failed (rc={rc_stop}); aborting restart.")
        return rc_stop

    time.sleep(1.0)
    print("Starting...")
    rc_start = cmd_start(argparse.Namespace(mode=args.mode, dry_run=False))
    print(f"Start exit: {rc_start}")
    return rc_start


def main():
    parser = argparse.ArgumentParser(description="Trading runtime control")
    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Show runtime status")
    p_status.add_argument("--json", action="store_true")

    p_start = sub.add_parser("start", help="Start trading runtime")
    p_start.add_argument("--mode", choices=["continuous", "single-cycle"],
                        default="continuous")
    p_start.add_argument("--dry-run", action="store_true")

    p_stop = sub.add_parser("stop", help="Stop trading runtime")
    p_stop.add_argument("--timeout", type=float, default=15.0,
                        help="Seconds to wait for graceful stop")
    p_stop.add_argument("--dry-run", action="store_true")

    p_restart = sub.add_parser("restart", help="Restart trading runtime")
    p_restart.add_argument("--mode", choices=["continuous", "single-cycle"],
                          default="continuous")
    p_restart.add_argument("--timeout", type=float, default=15.0)
    p_restart.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if args.command == "status":
        return cmd_status(args)
    if args.command == "start":
        return cmd_start(args)
    if args.command == "stop":
        return cmd_stop(args)
    if args.command == "restart":
        return cmd_restart(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
