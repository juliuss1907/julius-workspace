"""
Process Lock — Phase 9A.1.

Prevents multiple instances of the trading system from running at once.
Stores PID + metadata in a small JSON file. Detects stale locks (PID
no longer alive) and reclaims them safely.

Public API:
  - ProcessLock(path)         : lock manager object
  - ProcessLock.acquire()     : acquire lock, raises LockHeldError if active
  - ProcessLock.release()     : release lock if held by this process
  - ProcessLock.is_held()     : check if lock is currently held
  - ProcessLock.lock_info()   : return dict with holder info (or None)
  - lock_or_exit(path, ...)   : convenience: acquire or sys.exit(1)

Always safe to call release() even if not held.
"""
import errno
import json
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional


class LockHeldError(RuntimeError):
    """Raised when attempting to acquire a lock already held by another live process."""

    def __init__(self, message, holder=None):
        super().__init__(message)
        self.holder = holder or {}


def _pid_alive(pid: int) -> bool:
    """Return True if a process with this PID appears to be running."""
    if pid is None or pid <= 0:
        return False
    if pid == os.getpid():
        return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError as e:
        if e.errno == errno.EPERM:
            return True
        return False
    return True


def _read_lock(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None
        return data
    except (json.JSONDecodeError, OSError):
        return None


def _atomic_write_json(path: Path, payload: dict):
    """Write JSON atomically via temp + rename to avoid torn writes."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)
    os.replace(tmp, path)


class ProcessLock:
    """File-based PID lock with stale detection."""

    def __init__(self, path: str = "logs/run_paper_trading.lock",
                 name: str = "trading-runtime",
                 reclaim_stale: bool = True):
        self.path = Path(path)
        self.name = name
        self.reclaim_stale = reclaim_stale
        self._held = False

    def is_held(self) -> bool:
        info = self.lock_info()
        return bool(info and info.get("pid_alive"))

    def lock_info(self) -> Optional[dict]:
        data = _read_lock(self.path)
        if not data:
            return None
        pid = data.get("pid")
        pid_alive = _pid_alive(pid) if pid else False
        return {
            **data,
            "pid_alive": pid_alive,
            "stale": not pid_alive,
        }

    def acquire(self, force: bool = False) -> dict:
        """Acquire the lock. Returns the lock payload.

        Raises LockHeldError if another live process holds the lock.
        If `force=True` is passed and the existing lock is stale (PID dead),
        the stale lock will be replaced.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)

        existing = self.lock_info()
        if existing and existing.get("pid_alive"):
            if not force:
                raise LockHeldError(
                    f"Lock already held by PID {existing.get('pid')} "
                    f"(name={existing.get('name')}, "
                    f"started={existing.get('started_at')})",
                    holder=existing,
                )
            else:
                raise LockHeldError(
                    f"Lock held by PID {existing.get('pid')} (force=True refused)",
                    holder=existing,
                )

        payload = {
            "pid": os.getpid(),
            "name": self.name,
            "started_at": datetime.now().isoformat(),
            "host": os.uname().nodename if hasattr(os, "uname") else "unknown",
            "python": sys.version.split()[0],
        }
        try:
            _atomic_write_json(self.path, payload)
        except OSError as e:
            raise LockHeldError(f"Failed to write lock file: {e}")

        self._held = True
        return payload

    def release(self):
        """Release the lock if held. Safe to call multiple times."""
        if not self.path.exists():
            self._held = False
            return
        try:
            data = _read_lock(self.path)
            if data and data.get("pid") == os.getpid():
                try:
                    self.path.unlink()
                except OSError:
                    pass
        except Exception:
            pass
        self._held = False

    def __enter__(self) -> "ProcessLock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()
        return False


def lock_or_exit(path: str = "logs/run_paper_trading.lock",
                 name: str = "trading-runtime",
                 reclaim_stale: bool = True,
                 logger=None) -> ProcessLock:
    """Acquire lock; if held, print reason and sys.exit(1). Returns ProcessLock."""
    lock = ProcessLock(path=path, name=name, reclaim_stale=reclaim_stale)
    try:
        lock.acquire()
    except LockHeldError as e:
        holder = e.holder or {}
        msg = (
            f"Runtime lock active: PID {holder.get('pid')} already running "
            f"(name={holder.get('name')}, started={holder.get('started_at')}). "
            f"Refusing to start duplicate trading process."
        )
        if logger:
            logger.error(msg)
        else:
            print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)
    return lock
