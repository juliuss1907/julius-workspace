"""
Runtime Health — Phase 9A.1.

Writes a small JSON file with runtime state. Updated:
  - on startup (status=running)
  - after each cycle (last_cycle_*)
  - on shutdown (status=stopped)

File: logs/runtime_health.json

Public API:
  - RuntimeHealth(path)   : manager object
  - mark_running()        : writes initial running state
  - record_cycle(...)     : updates last_cycle_* fields
  - mark_stopped(...)     : writes stopped state
  - snapshot()            : returns current state dict
  - read_health(path)     : read-only helper for ops/monitoring
"""
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional


DEFAULT_PATH = "logs/runtime_health.json"


def _atomic_write_json(path: Path, payload: dict):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)
    os.replace(tmp, path)


def _now_iso() -> str:
    return datetime.now().isoformat()


def _host_info() -> dict:
    info = {"pid": os.getpid()}
    try:
        if hasattr(os, "uname"):
            info["host"] = os.uname().nodename
    except Exception:
        pass
    return info


def read_health(path: str = DEFAULT_PATH) -> Optional[dict]:
    p = Path(path)
    if not p.exists():
        return None
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


class RuntimeHealth:
    def __init__(self, path: str = DEFAULT_PATH, name: str = "trading-runtime"):
        self.path = Path(path)
        self.name = name
        self._started_at: Optional[str] = None
        self.cycle_count = 0
        self.errors: list = []

    def mark_running(self, watchlist: Optional[list] = None,
                     mode: Optional[str] = None) -> dict:
        self._started_at = _now_iso()
        payload = {
            "name": self.name,
            "status": "running",
            "mode": mode or "unknown",
            "started_at": self._started_at,
            "last_cycle_at": None,
            "last_cycle_status": None,
            "last_cycle_duration_sec": None,
            "last_symbols_processed": None,
            "cycle_count": 0,
            "errors": [],
            **_host_info(),
        }
        if watchlist is not None:
            payload["watchlist"] = list(watchlist)
        self._write(payload)
        return payload

    def record_cycle(self, status: str = "success", duration_sec: float = 0.0,
                     symbols_processed: int = 0, error: Optional[str] = None) -> dict:
        self.cycle_count += 1
        if error:
            self.errors.append({
                "at": _now_iso(),
                "message": error,
            })
            self.errors = self.errors[-20:]
        payload = {
            "name": self.name,
            "status": "running",
            "started_at": self._started_at or _now_iso(),
            "last_cycle_at": _now_iso(),
            "last_cycle_status": status,
            "last_cycle_duration_sec": round(float(duration_sec), 3),
            "last_symbols_processed": int(symbols_processed),
            "cycle_count": self.cycle_count,
            "errors": self.errors,
            **_host_info(),
        }
        self._write(payload)
        return payload

    def mark_stopped(self, reason: str = "graceful") -> dict:
        payload = {
            "name": self.name,
            "status": "stopped",
            "stopped_at": _now_iso(),
            "started_at": self._started_at,
            "stop_reason": reason,
            "cycle_count": self.cycle_count,
            "errors": self.errors,
            **_host_info(),
        }
        self._write(payload)
        return payload

    def snapshot(self) -> dict:
        return read_health(str(self.path)) or {}

    def _write(self, payload: dict):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write_json(self.path, payload)
