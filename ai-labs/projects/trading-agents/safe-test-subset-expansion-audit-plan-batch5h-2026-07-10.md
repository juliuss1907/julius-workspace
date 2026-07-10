# Batch 5H — Safe Test Subset Expansion Audit Plan

## Goal

Audit test files in the source-of-truth repo and identify additional pytest files that may be safe to add to CI after review.

Source repo:

```text
/home/julius/julius-workspace/ai-labs/projects/the-trading-guy
```

Remote:

```text
git@github.com:juliuss1907/the-trading-guy.git
```

## Non-Goal

Batch 5H does **not** modify CI, source code, runtime config, requirements, or test logic. It is an audit/classification batch first.

## Current Preflight Snapshot

Source repo status:

```text
## main...origin/main
```

Source repo HEAD / origin / remote:

```text
HEAD:        b83fb38292a24f260f7372ab557326b2ba50093d
origin/main: b83fb38292a24f260f7372ab557326b2ba50093d
remote main: b83fb38292a24f260f7372ab557326b2ba50093d
```

Local venv Python:

```text
returncode=0
Python 3.14.3
```

Workspace ahead count:

```text
0
```

## Read-Only Test Discovery Snapshot

This plan performed read-only discovery only. It did not execute the full suite.

- Test files discovered: `67`
- Files with no static risk keyword hits: `13`
- Files with at least one static risk keyword hit: `54`

| Test file | LOC | Imports | Static risk keyword hits |
|---|---:|---:|---|
| `scripts/test_analysis_runner.py` | 551 | 8 | binance, ccxt, order, telegram |
| `scripts/test_backtest_dashboard.py` | 332 | 5 | .jsonl, replay, simulate |
| `scripts/test_binance_futures_history.py` | 79 | 7 | .env, api_key, binance, dotenv, order, secret |
| `scripts/test_boundary_guardrails.py` | 673 | 6 | .env, dotenv, open(, order, os.environ, replay, subprocess, telegram |
| `scripts/test_calibration_workflow.py` | 461 | 11 | .jsonl, replay, simulate, subprocess |
| `scripts/test_candidate_level_attribution.py` | 76 | 4 | order |
| `scripts/test_coingecko.py` | 161 | 5 | binance |
| `scripts/test_data_fetchers.py` | 203 | 7 | api_key, binance, dotenv, order, secret |
| `scripts/test_demo_execution_policy.py` | 522 | 10 | binance, order, telegram |
| `scripts/test_derivatives_analyst.py` | 43 | 7 | dotenv |
| `scripts/test_dynamic_watchlist.py` | 498 | 10 | default_params.yaml, subprocess |
| `scripts/test_entry_guard.py` | 192 | 5 | open( |
| `scripts/test_execution_mode_gate.py` | 198 | 13 | order |
| `scripts/test_execution_modes.py` | 60 | 3 | none |
| `scripts/test_final_analysis_contract.py` | 246 | 5 | replay |
| `scripts/test_guarded_reverse_flow.py` | 362 | 4 | order |
| `scripts/test_health_cli.py` | 280 | 8 | live, logs/, open(, subprocess |
| `scripts/test_log_rotation.py` | 299 | 5 | logs/ |
| `scripts/test_manual_report_policy.py` | 879 | 15 | order, replay, simulate, subprocess, telegram |
| `scripts/test_news_analyst.py` | 33 | 5 | dotenv, telegram |
| `scripts/test_order_manager_close_notify.py` | 320 | 12 | binance, order |
| `scripts/test_paper_trading.py` | 215 | 9 | binance, dotenv, order, telegram |
| `scripts/test_parameter_recommendations.py` | 426 | 5 | default_params.yaml, logs/, replay, simulate |
| `scripts/test_parameter_sweep.py` | 204 | 5 | .jsonl, open(, replay, simulate |
| `scripts/test_phase4b_risk_gate.py` | 179 | 12 | .jsonl, order |
| `scripts/test_phase5c_position_aware_risk.py` | 329 | 7 | none |
| `scripts/test_portfolio_context.py` | 111 | 8 | none |
| `scripts/test_position_event_analytics.py` | 430 | 6 | .jsonl |
| `scripts/test_position_group_close.py` | 113 | 7 | order |
| `scripts/test_position_manager.py` | 111 | 7 | none |
| `scripts/test_position_notifications.py` | 239 | 4 | telegram |
| `scripts/test_position_reduce.py` | 181 | 10 | order |
| `scripts/test_process_lock.py` | 399 | 8 | live, open(, subprocess |
| `scripts/test_readonly_analyzer_cli.py` | 173 | 5 | replay |
| `scripts/test_readonly_monitoring_cadence.py` | 107 | 5 | .jsonl, logs/, replay, subprocess |
| `scripts/test_reconciliation.py` | 357 | 11 | binance, order |
| `scripts/test_replay_attribution_analyzer.py` | 263 | 6 | .jsonl, replay, subprocess |
| `scripts/test_replay_parameter_sweep.py` | 218 | 6 | open(, replay, simulate |
| `scripts/test_replay_strategy_attribution.py` | 175 | 7 | order, replay |
| `scripts/test_research_debate.py` | 91 | 7 | none |
| `scripts/test_risk_manager.py` | 116 | 7 | none |
| `scripts/test_rss_fetcher.py` | 140 | 5 | none |
| `scripts/test_run_paper_trading_dry_run.py` | 380 | 6 | open(, order, telegram |
| `scripts/test_runtime_control.py` | 559 | 10 | live, logs/, open(, subprocess |
| `scripts/test_runtime_health.py` | 278 | 7 | subprocess |
| `scripts/test_runtime_supervisor.py` | 566 | 14 | live, subprocess |
| `scripts/test_runtime_watchlist_loader.py` | 430 | 7 | order, subprocess |
| `scripts/test_scheduler_guard.py` | 284 | 17 | live, logs/, open(, scheduler, subprocess |
| `scripts/test_screening_agent.py` | 523 | 9 | subprocess |
| `scripts/test_sentiment_classifier.py` | 142 | 6 | exchange |
| `scripts/test_signal_recorder_strategy_signal.py` | 138 | 7 | .jsonl, order, replay |
| `scripts/test_spot_close_balance_cap.py` | 121 | 6 | order, place_order |
| `scripts/test_spot_futures_notifications.py` | 269 | 6 | telegram |
| `scripts/test_storage.py` | 210 | 7 | none |
| `scripts/test_strategy_attribution.py` | 142 | 3 | none |
| `scripts/test_strategy_contracts.py` | 180 | 4 | none |
| `scripts/test_strategy_playbooks.py` | 332 | 7 | none |
| `scripts/test_strategy_registry.py` | 290 | 5 | order |
| `scripts/test_strategy_vs_trader_evaluator.py` | 262 | 6 | .jsonl, replay, subprocess |
| `scripts/test_technical_analyst.py` | 183 | 6 | none |
| `scripts/test_technical_config.py` | 209 | 4 | none |
| `scripts/test_telegram_scraper.py` | 123 | 6 | dotenv, telegram |
| `scripts/test_trade_simulation.py` | 537 | 5 | .jsonl, open(, replay, simulate |
| `scripts/test_volatility_skip_broader_validation.py` | 108 | 4 | .jsonl, logs/, replay |
| `scripts/test_volatility_skip_calibration.py` | 177 | 7 | order, replay, subprocess |
| `scripts/test_volatility_skip_monitoring.py` | 161 | 5 | .jsonl, order, subprocess |
| `scripts/test_volatility_skip_zero_blocks.py` | 116 | 4 | .jsonl |

Full discovery details are saved in the JSON plan file.

## Planned Phases

### 5H-A — Preflight

1. Verify source repo is clean and synced:

```bash
cd /home/julius/julius-workspace/ai-labs/projects/the-trading-guy
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git ls-remote origin refs/heads/main
```

2. Verify local `.venv` is available.
3. Run the existing baseline safe test only:

```bash
.venv/bin/python -m pytest -q -p no:cacheprovider scripts/test_candidate_level_attribution.py
```

### 5H-B — Test Discovery

Enumerate test files using filename and path conventions:

```text
test_*.py
*_test.py
*/tests/*.py
```

Capture:

- path
- LOC
- imports
- static risk keyword hits

### 5H-C — Static Safety Classification

Classify each file as one of:

| Category | Meaning |
|---|---|
| `safe_now_candidate` | Pure/local unit-style test, eligible for targeted execution and maybe CI. |
| `safe_local_only` | Probably safe but not ideal for CI yet. |
| `needs_dependency_or_fixture` | Requires missing package, fixture, path, or setup. |
| `needs_mocking_or_refactor` | Touches integration-like paths but may become safe with mocks. |
| `unsafe_deferred` | Mentions/invokes credentials, live trading, orders, simulate-live, broad replay/output, or config mutation. |

Risk signals include:

```text
.env, dotenv, os.environ, api_key, secret, ccxt, binance, bybit,
exchange, order, place_order, live, simulate-live, websocket,
requests, aiohttp, httpx, telegram, scheduler, cron, systemd,
replay, logs/, outputs/, .jsonl, default_params.yaml, subprocess
```

### 5H-D — Optional Targeted Execution

Only after classification, run safe candidates explicitly, not the full suite:

```bash
.venv/bin/python -m pytest -q -p no:cacheprovider <test_file>
```

Stop immediately if a file requires `.env`, network, exchange credentials, live/simulate-live execution, runtime mutation, or creates suspicious artifacts.

### 5H-E — Evidence Write-Up

Write audit evidence:

```text
ai-labs/projects/trading-agents/safe-test-subset-expansion-audit-batch5h-2026-07-10.md
ai-labs/projects/trading-agents/safe-test-subset-expansion-audit-batch5h-2026-07-10.json
```

Commit locally with:

```text
docs(trading-agents): add safe test subset expansion audit
```

No push without explicit approval.

## Safety Boundaries

- No live trading.
- No order placement.
- No simulate-live.
- No StrategySignal-to-order bridge work.
- No runtime/default config mutation.
- No `.env` file read, print, or commit.
- No global package install.
- No new dependency install in Batch 5H.
- No full test suite execution.
- No replay or monitoring jobs.
- No raw replay logs staged or committed.
- No scheduler/cron/systemd enablement.
- No source repo changes unless a later implementation batch is explicitly approved.
- No push without explicit approval.

## Expected Follow-Up

If Batch 5H finds a conservative safe shortlist, the next implementation batch can be:

```text
Batch 5I — Add Expanded Safe Pytest Subset to CI
```

Only after Julius approves the 5H shortlist.
