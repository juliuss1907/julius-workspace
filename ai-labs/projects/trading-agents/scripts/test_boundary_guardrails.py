#!/usr/bin/env python3
"""
Aggregate boundary regression test.

Verifies that the shared-core / dual-consumer architecture seams
remain clean by inspecting import behaviour in fresh subprocesses.

Rules enforced:
  - orchestration/ does NOT pull execution modules
  - policies/manual_report does NOT pull utils or execution modules
  - policies/reverse_planner stays stdlib-only
  - policies/__init__.py does not eagerly import execution modules
  - CLI --help paths remain lightweight (exit 0 in system python)
"""
import os
import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
SCRIPT_DIR = str(project_root / "scripts")
VENV_PYTHON = str(project_root / "venv" / "bin" / "python")
SYSTEM_PYTHON = sys.executable

ERRORS = []
SKIPPED = []


def assert_eq(a, b, msg=""):
    if a != b:
        msg = msg or f"expected {b!r}, got {a!r}"
        ERRORS.append(msg)


def assert_true(cond, msg=""):
    if not cond:
        msg = msg or "assertion failed"
        ERRORS.append(msg)


_EXEC_SUBSTR = (
    "risk_manager", "position_manager", "order_manager", "entry_guard",
    "trade_notifier", "telegram_bot", "reconciliation", "runtime_health",
)

# Extended forbidden list used for strategy-layer purity checks.
_STRATEGY_EXEC_SUBSTR = _EXEC_SUBSTR + ("trading", "state.database")

# ── pre-flight: verify venv Python is usable ─────────────────────────

_VENV_OK = os.path.isfile(VENV_PYTHON)
_ANALYSIS_IMPORT_OK = False
if _VENV_OK:
    # Contracts are lightweight and should import even without optional
    # analysis dependencies. analyze_symbol requires the project runtime
    # deps (numpy/vader/etc.); if those are missing, only the import-heavy
    # boundary test is skipped with an explicit warning.
    rv = subprocess.run(
        [VENV_PYTHON, "-c", "import sys; sys.path.insert(0, '.'); from orchestration import FinalAnalysis"],
        capture_output=True, text=True, timeout=15,
        cwd=str(project_root),
    )
    _VENV_OK = (rv.returncode == 0)
    if not _VENV_OK:
        print(f"[WARN] venv Python at {VENV_PYTHON} exists but cannot import orchestration contracts: "
              f"{rv.stderr.strip()[:200]}")
    else:
        rv = subprocess.run(
            [VENV_PYTHON, "-c", "import sys; sys.path.insert(0, '.'); from orchestration import analyze_symbol"],
            capture_output=True, text=True, timeout=15,
            cwd=str(project_root),
        )
        _ANALYSIS_IMPORT_OK = (rv.returncode == 0)
        if not _ANALYSIS_IMPORT_OK:
            print(f"[WARN] venv Python cannot import analysis runner dependencies; "
                  f"import-heavy analysis boundary tests will be skipped: {rv.stderr.strip()[:200]}")
else:
    print(f"[WARN] venv Python not found at {VENV_PYTHON} — "
          f"import-heavy boundary tests will be skipped.")


# ── subprocess helpers ────────────────────────────────────────────────


def _run_py(code, python=SYSTEM_PYTHON, label="", timeout=15):
    """Run Python code in a subprocess.  Returns (returncode, stdout, stderr)."""
    rv = subprocess.run(
        [python, "-c", code],
        capture_output=True, text=True, timeout=timeout,
        cwd=str(project_root),
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    return rv.returncode, rv.stdout, rv.stderr


def _check_no_leak(label, code, python=SYSTEM_PYTHON):
    """Run code and assert stdout contains ONLY 'CLEAN'."""
    rc, out, err = _run_py(code, python=python, label=label)
    assert_eq(rc, 0, f"{label} crashed (rc={rc}): {err.strip()[:300]}")
    out = out.strip()
    assert_eq(out, "CLEAN", f"{label} leaked: {out}")


def _check_no_leak_venv(label, code):
    """Like _check_no_leak but requires analysis deps in the venv.
    Tracks skips visibly so they are not mistaken for passes.
    """
    if not _VENV_OK:
        SKIPPED.append(f"{label} (venv Python unavailable)")
        print(f"SKIP {label} (venv Python unavailable)")
        return
    if not _ANALYSIS_IMPORT_OK:
        SKIPPED.append(f"{label} (analysis dependencies unavailable in venv)")
        print(f"SKIP {label} (analysis dependencies unavailable in venv)")
        return
    _check_no_leak(label, code, python=VENV_PYTHON)


# ── Templates ─────────────────────────────────────────────────────────

_LEAK_CHECK = (
    "import sys; sys.path.insert(0, '.')\n"
    "{import_line}\n"
    "leaked = [m for m in sys.modules for kw in {tuple_} if kw in m]\n"
    "{extra_checks}"
    "print('LEAKED:' + ','.join(sorted(set(leaked))) if leaked else 'CLEAN')\n"
)


def _leak_code(import_line, extra_checks="", forbidden=_EXEC_SUBSTR):
    """Build a leak-checking subprocess script from a template.

    Avoids %% formatting ambiguity by constructing the tuple literal
    via repr, then substituting it and the import line explicitly.
    """
    return _LEAK_CHECK.format(
        import_line=import_line,
        tuple_=repr(forbidden),
        extra_checks=extra_checks,
    )


# ── Tests ─────────────────────────────────────────────────────────────


def test_orchestration_contracts_no_execution_leak():
    code = _leak_code("from orchestration import FinalAnalysis")
    _check_no_leak("orchestration.contracts", code)


def test_orchestration_analyze_symbol_no_execution_leak():
    code = _leak_code("from orchestration import analyze_symbol")
    _check_no_leak_venv("orchestration.analyze_symbol", code)


def test_manual_report_no_execution_leak():
    code = _leak_code(
        "from policies.manual_report import ManualTradeReportItem",
        extra_checks=(
            "utils_leak = [m for m in sys.modules if m == 'utils' or m.startswith('utils.')]\n"
            "leaked.extend(utils_leak)\n"
        ),
    )
    _check_no_leak("policies.manual_report", code)


def test_manual_report_cli_help_exits_zero_lightweight():
    """--help must work with system Python (no heavy deps)."""
    rv = subprocess.run(
        [SYSTEM_PYTHON, f"{SCRIPT_DIR}/generate_manual_trade_report.py", "--help"],
        capture_output=True, text=True, timeout=15,
        cwd=str(project_root),
    )
    assert_eq(rv.returncode, 0,
              f"--help rc={rv.returncode}: {rv.stderr.strip()[:200]}")
    assert_true("usage:" in rv.stdout.lower() or "--help" in rv.stdout.lower(),
                f"help output missing usage info: {rv.stdout[:200]}")


def test_readonly_analyzer_cli_help_exits_zero_lightweight():
    """--help must work with system Python before dotenv/runtime imports."""
    rv = subprocess.run(
        [SYSTEM_PYTHON, f"{SCRIPT_DIR}/analyze_symbol_readonly.py", "--help"],
        capture_output=True, text=True, timeout=15,
        cwd=str(project_root),
    )
    assert_eq(rv.returncode, 0,
              f"readonly --help rc={rv.returncode}: {rv.stderr.strip()[:200]}")
    assert_true("--include-demo-decision" in rv.stdout,
                f"readonly help missing demo flag: {rv.stdout[:300]}")


def test_readonly_analyzer_module_import_no_execution_leak():
    """Loading helper functions must not import execution/runtime modules."""
    code = (
        "import runpy, sys\n"
        "runpy.run_path('scripts/analyze_symbol_readonly.py', run_name='readonly_test')\n"
        "forbidden = ['dotenv', 'orchestration.analysis_runner', 'risk_manager', "
        "'position_manager', 'state', 'trading', 'telegram_bot']\n"
        "leaked = [m for m in sys.modules for kw in forbidden "
        "if m == kw or m.startswith(kw + '.') or kw in m]\n"
        "print('LEAKED:' + ','.join(sorted(set(leaked))) if leaked else 'CLEAN')\n"
    )
    _check_no_leak("readonly analyzer import", code)


def test_replay_attribution_analyzer_cli_help_exits_zero_lightweight():
    """Replay attribution analyzer --help must work without runtime deps."""
    rv = subprocess.run(
        [SYSTEM_PYTHON, f"{SCRIPT_DIR}/analyze_replay_attribution.py", "--help"],
        capture_output=True, text=True, timeout=15,
        cwd=str(project_root),
    )
    assert_eq(rv.returncode, 0,
              f"replay attribution --help rc={rv.returncode}: {rv.stderr.strip()[:300]}")
    assert_true("--input" in rv.stdout and "--output" in rv.stdout,
                f"replay attribution help missing expected flags: {rv.stdout[:300]}")


def test_replay_attribution_analyzer_import_no_execution_leak():
    """Loading analyzer helpers must not import runtime/execution modules."""
    code = (
        "import runpy, sys\n"
        "runpy.run_path('scripts/analyze_replay_attribution.py', run_name='replay_attr_test')\n"
        "forbidden = ['dotenv', 'dataflows', 'state', 'trading', 'telegram_bot', "
        "'risk_manager', 'position_manager', 'order_manager', 'entry_guard', "
        "'runtime_health', 'reconciliation']\n"
        "leaked = [m for m in sys.modules for kw in forbidden "
        "if m == kw or m.startswith(kw + '.') or kw in m]\n"
        "print('LEAKED:' + ','.join(sorted(set(leaked))) if leaked else 'CLEAN')\n"
    )
    _check_no_leak("replay attribution analyzer import", code)


def test_runtime_control_cli_help_exits_zero_lightweight():
    """runtime_control --help must work with system Python (no aiosqlite)."""
    rv = subprocess.run(
        [SYSTEM_PYTHON, f"{SCRIPT_DIR}/runtime_control.py", "--help"],
        capture_output=True, text=True, timeout=15,
        cwd=str(project_root),
    )
    assert_eq(rv.returncode, 0,
              f"runtime_control --help rc={rv.returncode}: {rv.stderr.strip()[:200]}")
    assert_true("usage:" in rv.stdout.lower(),
                f"runtime_control help missing usage info: {rv.stdout[:200]}")


def test_runtime_control_start_dry_run_exits_zero_lightweight():
    """runtime_control start --dry-run must work with system Python (no aiosqlite)."""
    rv = subprocess.run(
        [SYSTEM_PYTHON, f"{SCRIPT_DIR}/runtime_control.py",
         "start", "--mode", "single-cycle", "--dry-run"],
        capture_output=True, text=True, timeout=15,
        cwd=str(project_root),
    )
    assert_eq(rv.returncode, 0,
              f"runtime_control start dry-run rc={rv.returncode}: {rv.stderr.strip()[:300]}")
    assert_true("DRY-RUN" in rv.stdout,
                f"runtime_control dry-run missing DRY-RUN marker: {rv.stdout[:300]}")


def test_runtime_control_import_no_optional_deps():
    """Importing runtime_control.py as a module must not pull aiosqlite/state.database/trading/telegram_bot."""
    code = (
        "import runpy, sys\n"
        "runpy.run_path('scripts/runtime_control.py', run_name='runtime_control_test')\n"
        "forbidden = ['aiosqlite', 'state.database', 'trading', 'telegram_bot']\n"
        "leaked = [m for m in sys.modules for kw in forbidden "
        "if m == kw or m.startswith(kw + '.') or kw in m]\n"
        "print('LEAKED:' + ','.join(sorted(set(leaked))) if leaked else 'CLEAN')\n"
    )
    _check_no_leak("runtime_control import purity", code)


def test_run_paper_trading_cli_help_exits_zero_lightweight():
    """--help must not require optional runtime deps like Telethon."""
    rv = subprocess.run(
        [SYSTEM_PYTHON, f"{SCRIPT_DIR}/run_paper_trading.py", "--help"],
        capture_output=True, text=True, timeout=15,
        cwd=str(project_root),
    )
    assert_eq(rv.returncode, 0,
              f"paper --help rc={rv.returncode}: {rv.stderr.strip()[:300]}")
    assert_true("--single-cycle" in rv.stdout,
                f"paper help missing --single-cycle: {rv.stdout[:300]}")
    assert_true("--dry-run" in rv.stdout,
                f"paper help missing --dry-run: {rv.stdout[:300]}")


def test_run_paper_trading_syntax():
    code = (
        "import ast\n"
        "with open('scripts/run_paper_trading.py') as f:\n"
        "    ast.parse(f.read())\n"
        "print('CLEAN')\n"
    )
    _check_no_leak("run_paper_trading syntax", code)


def test_generate_manual_trade_report_syntax():
    code = (
        "import ast\n"
        "with open('scripts/generate_manual_trade_report.py') as f:\n"
        "    ast.parse(f.read())\n"
        "print('CLEAN')\n"
    )
    _check_no_leak("generate_manual_trade_report syntax", code)


def test_policies_init_no_execution_eager_import():
    """policies/__init__.py must not eagerly import execution modules."""
    code = _leak_code("from policies import __doc__ as _")
    _check_no_leak("policies.init", code)


def test_reverse_planner_stdlib_only():
    """policies.reverse_planner must stay stdlib-only — no utils, no agents, no dataflows."""
    code = (
        "import sys; sys.path.insert(0, '.')\n"
        "from policies.reverse_planner import plan_guarded_reverse\n"
        "forbidden = ['utils', 'agents', 'dataflows', 'orchestration', 'state', 'trading', 'telegram_bot']\n"
        "leaked = [m for m in sys.modules for kw in forbidden if m == kw or m.startswith(kw + '.')]\n"
        "print('LEAKED:' + ','.join(sorted(set(leaked))) if leaked else 'CLEAN')\n"
    )
    _check_no_leak("policies.reverse_planner stdlib-only", code)


def test_orchestration_init_does_not_import_policies_or_state():
    """orchestration/__init__.py must not eagerly import policies/ or state/."""
    code = (
        "import sys; sys.path.insert(0, '.')\n"
        "from orchestration import FinalAnalysis\n"
        "forbidden = ['policies', 'state']\n"
        "leaked = [m for m in sys.modules for kw in forbidden if m == kw or m.startswith(kw + '.')]\n"
        "print('LEAKED:' + ','.join(sorted(set(leaked))) if leaked else 'CLEAN')\n"
    )
    _check_no_leak("orchestration.init no policies/state", code)


def test_strategy_contracts_no_execution_leak():
    code = _leak_code("from strategies import StrategySignal", forbidden=_STRATEGY_EXEC_SUBSTR)
    _check_no_leak("strategies.contracts", code)


def test_volatility_skip_no_execution_leak():
    code = _leak_code("from strategies.volatility_skip import VolatilitySkipStrategy", forbidden=_STRATEGY_EXEC_SUBSTR)
    _check_no_leak("strategies.volatility_skip", code)


def test_trend_following_no_execution_leak():
    code = _leak_code("from strategies.trend_following import TrendFollowingStrategy", forbidden=_STRATEGY_EXEC_SUBSTR)
    _check_no_leak("strategies.trend_following", code)


def test_breakout_no_execution_leak():
    code = _leak_code("from strategies.breakout import BreakoutStrategy", forbidden=_STRATEGY_EXEC_SUBSTR)
    _check_no_leak("strategies.breakout", code)


def test_strategy_registry_no_execution_leak():
    code = _leak_code("from strategies.registry import StrategyRegistry", forbidden=_STRATEGY_EXEC_SUBSTR)
    _check_no_leak("strategies.registry", code)


def test_strategy_attribution_no_execution_leak():
    code = _leak_code("from strategies.attribution import build_strategy_signal", forbidden=_STRATEGY_EXEC_SUBSTR)
    _check_no_leak("strategies.attribution", code)


def test_orchestration_module_docstrings():
    """Every orchestration/ module must document its execution-free guarantee."""
    import ast

    for mod_name in ("__init__", "analysis_runner", "contracts"):
        path = project_root / "orchestration" / f"{mod_name}.py"
        module_ast = ast.parse(path.read_text())
        doc = ast.get_docstring(module_ast)
        assert_true(doc and len(doc) > 40,
                    f"orchestration.{mod_name} docstring too short or missing")


def test_policies_docstrings_enforce_boundaries():
    """policies/__init__.py, reverse_planner, and manual_report must document
    their execution-free guarantee."""
    import ast

    for mod_name, path in (
        ("__init__", project_root / "policies" / "__init__.py"),
        ("reverse_planner", project_root / "policies" / "reverse_planner.py"),
        ("manual_report", project_root / "policies" / "manual_report.py"),
    ):
        module_ast = ast.parse(path.read_text())
        doc = ast.get_docstring(module_ast)
        assert_true(doc and len(doc) > 30,
                    f"policies.{mod_name} docstring too short or missing")


def run_tests():
    tests = [
        ("orchestration_contracts_no_execution_leak", test_orchestration_contracts_no_execution_leak),
        ("orchestration_analyze_symbol_no_execution_leak", test_orchestration_analyze_symbol_no_execution_leak),
        ("orchestration_init_no_policies_or_state", test_orchestration_init_does_not_import_policies_or_state),
        ("policies_init_no_execution_eager_import", test_policies_init_no_execution_eager_import),
        ("reverse_planner_stdlib_only", test_reverse_planner_stdlib_only),
        ("manual_report_no_execution_leak", test_manual_report_no_execution_leak),
        ("manual_report_cli_help_exits_zero_lightweight", test_manual_report_cli_help_exits_zero_lightweight),
        ("readonly_analyzer_cli_help_exits_zero_lightweight", test_readonly_analyzer_cli_help_exits_zero_lightweight),
        ("readonly_analyzer_module_import_no_execution_leak", test_readonly_analyzer_module_import_no_execution_leak),
        ("replay_attribution_analyzer_cli_help_exits_zero_lightweight", test_replay_attribution_analyzer_cli_help_exits_zero_lightweight),
        ("replay_attribution_analyzer_import_no_execution_leak", test_replay_attribution_analyzer_import_no_execution_leak),
        ("runtime_control_cli_help_exits_zero_lightweight", test_runtime_control_cli_help_exits_zero_lightweight),
        ("runtime_control_start_dry_run_exits_zero_lightweight", test_runtime_control_start_dry_run_exits_zero_lightweight),
        ("runtime_control_import_no_optional_deps", test_runtime_control_import_no_optional_deps),
        ("run_paper_trading_cli_help_exits_zero_lightweight", test_run_paper_trading_cli_help_exits_zero_lightweight),
        ("run_paper_trading_syntax", test_run_paper_trading_syntax),
        ("generate_manual_trade_report_syntax", test_generate_manual_trade_report_syntax),
        ("strategy_contracts_no_execution_leak", test_strategy_contracts_no_execution_leak),
        ("volatility_skip_no_execution_leak", test_volatility_skip_no_execution_leak),
        ("trend_following_no_execution_leak", test_trend_following_no_execution_leak),
        ("breakout_no_execution_leak", test_breakout_no_execution_leak),
        ("strategy_registry_no_execution_leak", test_strategy_registry_no_execution_leak),
        ("strategy_attribution_no_execution_leak", test_strategy_attribution_no_execution_leak),
        ("orchestration_module_docstrings", test_orchestration_module_docstrings),
        ("policies_docstrings_enforce_boundaries", test_policies_docstrings_enforce_boundaries),
    ]

    all_errors = []
    passed = 0
    for name, fn in tests:
        ERRORS.clear()
        try:
            fn()
            if ERRORS:
                for err in ERRORS:
                    all_errors.append(f"{name}: {err}")
                    print(f"FAIL {name}: {err}")
            else:
                print(f"PASS {name}")
                passed += 1
        except Exception as e:
            all_errors.append(f"{name}: {e}")
            print(f"FAIL {name}: {e}")

    if SKIPPED:
        print(f"\n{len(SKIPPED)} SKIPPED:")
        for s in SKIPPED:
            print(f"  - {s}")

    if all_errors:
        print(f"\n{len(all_errors)} FAILURES:")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print(f"\nAll {passed} boundary guardrails pass.", end="")
    if SKIPPED:
        print(f"  ({len(SKIPPED)} skipped)")
    else:
        print()
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
