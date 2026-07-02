# Batch 3Q-A — Replay Import-Safety and Dependency Readiness

## Executive Summary

- Mode: replay_import_safety_dependency_readiness
- Status: **pass**
- Dependency installed: **false**
- Runtime/default config changed: **false**
- Live trading / order placement / simulate-live: **false**
- Recommendation: Retry Batch 3Q fresh non-variant replay collection for BTCUSDT/ETHUSDT/SOLUSDT.

## Pre-Patch Blocker

Before Batch 3Q-A, replay CLI readiness failed before fresh replay collection:

```text
python3 scripts/replay_signals.py --help
→ ModuleNotFoundError: No module named 'telethon'
```

A first narrow optional-Telegram isolation then exposed the broader package-level issue:

```text
ModuleNotFoundError: No module named 'feedparser'
```

Root cause:

```text
dataflows/__init__.py eagerly imported optional scraper/fetcher modules,
and scripts/replay_signals.py loaded runtime dependencies before argparse
could handle --help and exit.
```

## Patch Applied

Used a two-part import-safety patch:

1. `dataflows/__init__.py`
   - eagerly loads only `DataSource`,
   - lazy-loads concrete clients/scrapers via `__getattr__`,
   - keeps optional dependencies isolated until the specific optional component is used.

2. `scripts/replay_signals.py`
   - defers `dotenv`, `state`, `agents`, `dataflows`, and strategy attribution imports until actual replay execution,
   - keeps `--help` lightweight and import-safe,
   - does not alter replay strategy semantics.

3. `scripts/test_boundary_guardrails.py`
   - adds `replay_signals_cli_help_exits_zero_lightweight`.

## Validation

| Command | Status | Notes |
|---|---|---|
| `python3 -m py_compile scripts/replay_signals.py dataflows/__init__.py scripts/test_boundary_guardrails.py` | pass | rc=0 |
| `python3 scripts/replay_signals.py --help` | pass | rc=0 |
| `python3 scripts/run_volatility_skip_monitoring.py --help` | pass | rc=0 |
| `python3 scripts/test_boundary_guardrails.py` | pass | rc=0 |
| `python3 scripts/test_volatility_skip_monitoring.py` | pass | rc=0 |

## Boundary Confirmation

- No runtime/default config changes were made.
- No strategy thresholds were changed.
- No live trading, order placement, or simulate-live execution was run.
- No StrategySignal-to-order mapping was introduced.
- No dependencies were installed.
- `.env` contents were not read or printed.
- No raw replay logs were created, staged, or committed.

## Decision Block

```text
Batch 3Q-A Decision:
- Status: pass
- replay_signals.py --help readiness: pass
- dependency installed: false
- runtime/default config changed: false
- fresh replay retry recommended: true
- next step: Retry Batch 3Q fresh non-variant replay collection for BTCUSDT/ETHUSDT/SOLUSDT.
```
