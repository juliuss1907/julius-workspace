#!/usr/bin/env python3
"""
Runtime Health CLI — Phase 9A.2.

Read-only inspection of `logs/runtime_health.json`. Useful for ops to
quickly check whether the trading system is alive, last cycle status,
PID, and recent errors.

Usage:
  ./venv/bin/python scripts/check_runtime_health.py
  ./venv/bin/python scripts/check_runtime_health.py --json
  ./venv/bin/python scripts/check_runtime_health.py --path logs/runtime_health.json
"""
import argparse
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils import config as cfg_loader
from state.runtime_health import read_health, DEFAULT_PATH
from utils.process_lock import ProcessLock, _pid_alive


def _resolve(path_str: str) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        p = project_root / p
    return p


def _resolve_lock(path_str: str) -> Path:
    return _resolve(path_str)


def _print_health(health: dict, lock_info: dict | None) -> None:
    status = health.get("status", "unknown")
    name = health.get("name", "?")
    pid = health.get("pid", "?")
    host = health.get("host", "?")

    print("Runtime Health")
    print("=" * 40)
    print(f"  name:    {name}")
    print(f"  status:  {status}")
    print(f"  pid:     {pid}")
    print(f"  host:    {host}")

    mode = health.get("mode")
    if mode:
        print(f"  mode:    {mode}")

    started_at = health.get("started_at")
    if started_at:
        print(f"  started: {started_at}")

    stopped_at = health.get("stopped_at")
    if stopped_at:
        print(f"  stopped: {stopped_at}")

    stop_reason = health.get("stop_reason")
    if stop_reason:
        print(f"  reason:  {stop_reason}")

    cycle_count = health.get("cycle_count")
    if cycle_count is not None:
        print(f"  cycles:  {cycle_count}")

    last_at = health.get("last_cycle_at")
    last_status = health.get("last_cycle_status")
    last_dur = health.get("last_cycle_duration_sec")
    last_syms = health.get("last_symbols_processed")
    if last_at:
        print(f"  last_cycle_at:    {last_at}")
    if last_status:
        print(f"  last_cycle:       {last_status}")
    if last_dur is not None:
        print(f"  last_duration:    {last_dur}s")
    if last_syms is not None:
        print(f"  last_symbols:     {last_syms}")

    watchlist = health.get("watchlist")
    if watchlist:
        print(f"  watchlist:        {', '.join(watchlist)}")

    errors = health.get("errors") or []
    if errors:
        print(f"\nRecent errors (last {len(errors)}):")
        for e in errors[-5:]:
            msg = e.get("message", "")
            at = e.get("at", "")
            print(f"  - {at}  {msg}")

    if lock_info:
        print()
        print("Lock info:")
        print(f"  path:        {lock_info.get('_path', '?')}")
        print(f"  pid:         {lock_info.get('pid', '?')}")
        print(f"  pid_alive:   {lock_info.get('pid_alive')}")
        print(f"  stale:       {lock_info.get('stale')}")
        print(f"  started_at:  {lock_info.get('started_at', '?')}")


def main():
    parser = argparse.ArgumentParser(description="Inspect runtime health")
    parser.add_argument("--path", default=None,
                        help="Path to health JSON (default from config)")
    parser.add_argument("--json", action="store_true",
                        help="Print raw JSON instead of formatted text")
    parser.add_argument("--check-lock", action="store_true",
                        help="Also include lock info")
    args = parser.parse_args()

    if args.path:
        path = _resolve(args.path)
    else:
        cfg = cfg_loader.load_default_params()
        runtime_cfg = cfg.get("runtime", {}) or {}
        path = _resolve(runtime_cfg.get("health_file", DEFAULT_PATH))

    health = read_health(str(path))

    lock_info = None
    if args.check_lock:
        cfg = cfg_loader.load_default_params()
        runtime_cfg = cfg.get("runtime", {}) or {}
        lock_path = runtime_cfg.get("lock_file", "logs/run_paper_trading.lock")
        lk = ProcessLock(path=str(_resolve_lock(lock_path)))
        info = lk.lock_info() or {}
        if info:
            info["_path"] = str(_resolve_lock(lock_path))
        lock_info = info

    if health is None:
        if args.json:
            print(json.dumps({
                "health_file": str(path),
                "available": False,
                "lock": lock_info,
            }, indent=2, ensure_ascii=True))
        else:
            print(f"No runtime health file at {path}")
            print("(system has not run yet, or file was removed)")
        return 1

    if args.json:
        payload = {
            "available": True,
            "health_file": str(path),
            "health": health,
        }
        if lock_info is not None:
            payload["lock"] = lock_info
        print(json.dumps(payload, indent=2, ensure_ascii=True))
    else:
        _print_health(health, lock_info)

    status = health.get("status")
    if status == "running":
        return 0
    if status == "stopped":
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
