#!/usr/bin/env python3
"""Tests for manual read-only monitoring cadence runner."""
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = PROJECT_ROOT / "scripts" / "run_readonly_monitoring_cadence.py"
ERRORS = []


def assert_true(cond, msg):
    if not cond:
        ERRORS.append(msg)


def assert_eq(a, b, msg):
    if a != b:
        ERRORS.append(f"{msg}: expected {b!r}, got {a!r}")


def load_module():
    spec = importlib.util.spec_from_file_location("cadence", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_help_exits_zero():
    rv = subprocess.run([sys.executable, str(SCRIPT), "--help"], cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=15)
    assert_eq(rv.returncode, 0, "--help rc")
    assert_true("--run" in rv.stdout and "--date-tag" in rv.stdout, "help missing expected flags")


def test_dry_run_exits_zero_and_does_not_create_files():
    tag = "test-dry-run-no-create"
    rv = subprocess.run([sys.executable, str(SCRIPT), "--date-tag", tag], cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=15)
    assert_eq(rv.returncode, 0, "dry-run rc")
    assert_true("DRY-RUN" in rv.stdout, "dry-run marker missing")
    assert_true(not (PROJECT_ROOT / f"logs/replay_signals-batch3r-{tag}-core.jsonl").exists(), "dry-run created raw replay log")


def test_build_paths_contains_date_tag():
    module = load_module()
    paths = module.build_paths("unit")
    assert_true(str(paths.raw_replay_log).endswith("logs/replay_signals-batch3r-unit-core.jsonl"), "raw path date tag mismatch")
    assert_true("batch3r-unit" in str(paths.fresh_json), "fresh report date tag missing")
    assert_eq(len(paths.committable_reports()), 4, "committable report count")


def test_run_not_default_and_commands_use_venv_python():
    module = load_module()
    args = module.parse_args(["--date-tag", "unit"])
    assert_true(not args.run, "--run should not be default")
    commands = module.build_commands(args, module.build_paths(args.date_tag))
    for name, command in commands.items():
        assert_eq(command[0], "venv/bin/python", f"{name} python")
    assert_true("scripts/replay_signals.py" in commands["replay"], "replay command missing script")
    assert_true("scripts/run_volatility_skip_monitoring.py" in commands["fresh_monitoring"], "fresh monitoring command missing script")


def test_refuses_overwrite_when_outputs_exist():
    module = load_module()
    with tempfile.TemporaryDirectory() as tmp:
        existing = Path(tmp) / "existing.jsonl"
        existing.write_text("x\n")
        paths = module.CadencePaths(existing, Path(tmp) / "fresh.md", Path(tmp) / "fresh.json", Path(tmp) / "combined.md", Path(tmp) / "combined.json")
        try:
            module.ensure_outputs_do_not_exist(paths, overwrite=False)
            ERRORS.append("expected FileExistsError")
        except FileExistsError:
            pass
        module.ensure_outputs_do_not_exist(paths, overwrite=True)


def run_tests():
    tests = [
        test_help_exits_zero,
        test_dry_run_exits_zero_and_does_not_create_files,
        test_build_paths_contains_date_tag,
        test_run_not_default_and_commands_use_venv_python,
        test_refuses_overwrite_when_outputs_exist,
    ]
    passed = 0
    all_errors = []
    for test in tests:
        ERRORS.clear()
        test()
        if ERRORS:
            all_errors.extend(f"{test.__name__}: {err}" for err in ERRORS)
        else:
            passed += 1
            print(f"PASS {test.__name__}")
    if all_errors:
        print("FAIL")
        for err in all_errors:
            print(err)
        return 1
    print(f"PASS {passed} readonly monitoring cadence tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_tests())
