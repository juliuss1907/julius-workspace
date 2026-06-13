#!/usr/bin/env python3
"""Test Phase 9A.2: Log Rotation."""
import os
import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.log_rotation import (
    should_rotate,
    rotate_file,
    rotate_all,
    _is_safe_path,
    _resolve,
)


# ---------------------------------------------------------------------------
# should_rotate
# ---------------------------------------------------------------------------

def test_should_rotate_missing(tmp_root):
    p = tmp_root / "missing.log"
    assert should_rotate(p, max_bytes=10) is False
    print("PASS test_should_rotate_missing")


def test_should_rotate_below(tmp_root):
    p = tmp_root / "log.log"
    p.write_text("a" * 5, encoding="utf-8")
    assert should_rotate(p, max_bytes=10) is False
    print("PASS test_should_rotate_below")


def test_should_rotate_at(tmp_root):
    """At exactly max_bytes: not greater, so no rotation."""
    p = tmp_root / "log.log"
    p.write_text("a" * 10, encoding="utf-8")
    assert should_rotate(p, max_bytes=10) is False
    print("PASS test_should_rotate_at")


def test_should_rotate_above(tmp_root):
    p = tmp_root / "log.log"
    p.write_text("a" * 20, encoding="utf-8")
    assert should_rotate(p, max_bytes=10) is True
    print("PASS test_should_rotate_above")


# ---------------------------------------------------------------------------
# rotate_file basic
# ---------------------------------------------------------------------------

def test_rotate_file_missing(tmp_root):
    p = tmp_root / "missing.log"
    result = rotate_file(p, project_root=tmp_root)
    assert result["skipped"] is True
    assert result["reason"] == "file_missing"
    assert result["rotated"] is False
    print("PASS test_rotate_file_missing")


def test_rotate_file_below_threshold(tmp_root):
    p = tmp_root / "log.log"
    p.write_text("a" * 5, encoding="utf-8")
    result = rotate_file(p, max_bytes=10, project_root=tmp_root)
    assert result["skipped"] is True
    assert result["reason"] == "below_threshold"
    assert result["rotated"] is False
    print("PASS test_rotate_file_below_threshold")


def test_rotate_file_rotates(tmp_root):
    p = tmp_root / "log.log"
    p.write_text("a" * 100, encoding="utf-8")
    result = rotate_file(p, max_bytes=10, keep_files=3, project_root=tmp_root)
    assert result["rotated"] is True
    backup = p.with_suffix(p.suffix + ".1")
    assert backup.exists()
    assert p.exists()
    assert p.stat().st_size == 0
    assert "a" * 100 in backup.read_text(encoding="utf-8")
    print("PASS test_rotate_file_rotates")


def test_rotate_file_keeps_max(tmp_root):
    """After keep_files+1 rotations, only the last `keep_files` backups exist."""
    p = tmp_root / "log.log"
    p.write_text("a" * 100, encoding="utf-8")
    keep = 3
    for i in range(5):
        p.write_text(f"iter{i}-" + "a" * 100, encoding="utf-8")
        rotate_file(p, max_bytes=10, keep_files=keep, project_root=tmp_root)
    for n in range(1, keep + 1):
        bk = p.with_suffix(p.suffix + f".{n}")
        assert bk.exists(), f"missing .bak.{n}"
    over = p.with_suffix(p.suffix + f".{keep+1}")
    assert not over.exists()
    print("PASS test_rotate_file_keeps_max")


def test_rotate_file_shifts_numbered(tmp_root):
    """After two rotations, .2 should exist with older content than .1."""
    p = tmp_root / "log.log"
    p.write_text("first" + "a" * 100, encoding="utf-8")
    rotate_file(p, max_bytes=10, keep_files=3, project_root=tmp_root)
    p.write_text("second" + "a" * 100, encoding="utf-8")
    rotate_file(p, max_bytes=10, keep_files=3, project_root=tmp_root)
    one = p.with_suffix(p.suffix + ".1").read_text(encoding="utf-8")
    two = p.with_suffix(p.suffix + ".2").read_text(encoding="utf-8")
    assert "second" in one
    assert "first" in two
    print("PASS test_rotate_file_shifts_numbered")


def test_rotate_file_rejects_outside_root(tmp_root):
    outside = Path("/tmp/log_rotation_outside.log")
    if outside.exists():
        outside.unlink()
    outside.write_text("a" * 100, encoding="utf-8")
    try:
        result = rotate_file(outside, max_bytes=10, keep_files=3,
                             project_root=tmp_root)
        assert result["skipped"] is True
        assert "outside" in result["reason"]
    finally:
        if outside.exists():
            outside.unlink()
    print("PASS test_rotate_file_rejects_outside_root")


# ---------------------------------------------------------------------------
# rotate_all
# ---------------------------------------------------------------------------

def test_rotate_all_disabled(tmp_root):
    cfg = {"runtime": {"log_rotation": {"enabled": False, "files": ["a.log"]}}}
    out = rotate_all(cfg, project_root=tmp_root)
    assert out == []
    print("PASS test_rotate_all_disabled")


def test_rotate_all_no_config(tmp_root):
    out = rotate_all(None, project_root=tmp_root)
    assert out == []
    print("PASS test_rotate_all_no_config")


def test_rotate_all_handles_multiple_files(tmp_root):
    a = tmp_root / "a.log"
    b = tmp_root / "b.log"
    a.write_text("a" * 100, encoding="utf-8")
    b.write_text("b" * 100, encoding="utf-8")

    cfg = {
        "runtime": {
            "log_rotation": {
                "enabled": True,
                "max_bytes": 10,
                "keep_files": 3,
                "files": [str(a), str(b)],
            }
        }
    }
    out = rotate_all(cfg, project_root=tmp_root)
    assert len(out) == 2
    assert all(r["rotated"] for r in out)
    a1 = a.with_suffix(a.suffix + ".1")
    b1 = b.with_suffix(b.suffix + ".1")
    assert a1.exists() and b1.exists()
    print("PASS test_rotate_all_handles_multiple_files")


def test_rotate_all_mixed_paths(tmp_root):
    """Files outside project root should be skipped, not rotated."""
    inside = tmp_root / "inside.log"
    outside = Path("/tmp/log_rotation_mixed_outside.log")
    if outside.exists():
        outside.unlink()
    inside.write_text("a" * 100, encoding="utf-8")
    outside.write_text("b" * 100, encoding="utf-8")
    try:
        cfg = {
            "runtime": {
                "log_rotation": {
                    "enabled": True,
                    "max_bytes": 10,
                    "keep_files": 3,
                    "files": [str(inside), str(outside)],
                }
            }
        }
        out = rotate_all(cfg, project_root=tmp_root)
        assert len(out) == 2
        assert out[0]["rotated"] is True
        assert out[1]["skipped"] is True
    finally:
        if outside.exists():
            outside.unlink()
    print("PASS test_rotate_all_mixed_paths")


def test_rotate_all_small_files_noop(tmp_root):
    a = tmp_root / "a.log"
    a.write_text("tiny", encoding="utf-8")
    cfg = {
        "runtime": {
            "log_rotation": {
                "enabled": True,
                "max_bytes": 1000,
                "keep_files": 3,
                "files": [str(a)],
            }
        }
    }
    out = rotate_all(cfg, project_root=tmp_root)
    assert len(out) == 1
    assert out[0]["skipped"] is True
    assert out[0]["reason"] == "below_threshold"
    print("PASS test_rotate_all_small_files_noop")


# ---------------------------------------------------------------------------
# _is_safe_path / _resolve
# ---------------------------------------------------------------------------

def test_is_safe_path_under_root(tmp_root):
    p = tmp_root / "logs" / "a.log"
    assert _is_safe_path(p, tmp_root) is True
    print("PASS test_is_safe_path_under_root")


def test_is_safe_path_outside_root():
    p = Path("/tmp/log_rotation_safety_test.log")
    if p.exists():
        p.unlink()
    p.touch()
    try:
        assert _is_safe_path(p, Path("/home/julius/julius-workspace/ai-labs")) is False
    finally:
        if p.exists():
            p.unlink()
    print("PASS test_is_safe_path_outside_root")


def test_resolve_relative(tmp_root):
    p = _resolve("logs/a.log", tmp_root)
    assert p == tmp_root / "logs" / "a.log"
    print("PASS test_resolve_relative")


def test_resolve_absolute():
    abs_path = "/tmp/log_rotation_resolve_test.log"
    p = _resolve(abs_path, Path("/home/julius/julius-workspace/ai-labs"))
    assert str(p) == abs_path
    print("PASS test_resolve_absolute")


def run_all():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)

        tests = [
            test_should_rotate_missing, test_should_rotate_below,
            test_should_rotate_at, test_should_rotate_above,
            test_rotate_file_missing, test_rotate_file_below_threshold,
            test_rotate_file_rotates, test_rotate_file_keeps_max,
            test_rotate_file_shifts_numbered, test_rotate_file_rejects_outside_root,
            test_rotate_all_disabled, test_rotate_all_no_config,
            test_rotate_all_handles_multiple_files, test_rotate_all_mixed_paths,
            test_rotate_all_small_files_noop,
            test_is_safe_path_under_root, test_is_safe_path_outside_root,
            test_resolve_relative, test_resolve_absolute,
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
