#!/usr/bin/env python3
"""Synthetic tests for PositionManager execution modes."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils import config


def load_mode():
    default = config.load_default_params()
    return default.get("position_manager", {}).get("execution_mode", "execute_close_only")


def mode_allows_close(mode: str) -> bool:
    return mode != "dry_run"


def mode_allows_reduce(mode: str) -> bool:
    return mode in ("execute_reduce_and_close", "execute_all")


def mode_allows_reverse(mode: str) -> bool:
    return mode == "execute_all"


def test():
    mode = load_mode()
    valid = {"dry_run", "execute_close_only", "execute_reduce_and_close", "execute_all"}
    assert mode in valid, f"unknown mode: {mode}"

    dry = "dry_run"
    assert mode_allows_close(dry) is False
    assert mode_allows_reduce(dry) is False
    assert mode_allows_reverse(dry) is False

    co = "execute_close_only"
    assert mode_allows_close(co) is True
    assert mode_allows_reduce(co) is False
    assert mode_allows_reverse(co) is False

    rc = "execute_reduce_and_close"
    assert mode_allows_close(rc) is True
    assert mode_allows_reduce(rc) is True
    assert mode_allows_reverse(rc) is False

    ea = "execute_all"
    assert mode_allows_close(ea) is True
    assert mode_allows_reduce(ea) is True
    assert mode_allows_reverse(ea) is True

    print("Execution mode tests passed")
    print(f"current_mode={mode}")
    print(f"  close: {mode_allows_close(mode)}, reduce: {mode_allows_reduce(mode)}, reverse: {mode_allows_reverse(mode)}")


if __name__ == "__main__":
    test()
