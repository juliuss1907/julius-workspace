# Batch 5H — Safe Test Subset Expansion Audit

## Summary

Batch 5H audited the test files in the source-of-truth repo and identified a conservative safe shortlist for possible CI expansion.

- Source repo: `/home/julius/julius-workspace/ai-labs/projects/the-trading-guy`
- Test files discovered/classified: `67`
- Baseline safe test result: `returncode=0`
- Full test suite executed: `no`
- New dependencies installed: `no`
- Source repo changed: `no`

## Preflight

Source repo status:

```text
## main...origin/main
```

HEAD / origin / remote:

```text
HEAD:        b83fb38292a24f260f7372ab557326b2ba50093d
origin/main: b83fb38292a24f260f7372ab557326b2ba50093d
remote main: b83fb38292a24f260f7372ab557326b2ba50093d
```

Existing baseline safe test:

```text
returncode=0
....                                                                     [100%]
4 passed in 0.02s

```

## Classification Counts

```json
{
  "needs_mocking_or_refactor": 15,
  "unsafe_deferred": 40,
  "safe_now_candidate": 4,
  "needs_dependency_or_fixture": 8
}
```

## Safe Shortlist for CI Review

Existing CI test plus new candidates:

```text
scripts/test_candidate_level_attribution.py
scripts/test_strategy_attribution.py
scripts/test_strategy_contracts.py
scripts/test_strategy_playbooks.py
```

New safe candidates found in Batch 5H:

```text
scripts/test_strategy_attribution.py
scripts/test_strategy_contracts.py
scripts/test_strategy_playbooks.py
```

These are pure strategy/contract unit-style tests that passed targeted local pytest and do not require `.env`, network, exchange clients, live trading, replay jobs, or additional dependencies.

## Targeted Execution Results

Only explicit target files were run. The full test suite was not run.

| File | Return code | First output line |
|---|---:|---|
| `scripts/test_strategy_contracts.py` | 0 | `......                                                                   [100%]` |
| `scripts/test_strategy_attribution.py` | 0 | `....                                                                     [100%]` |
| `scripts/test_strategy_playbooks.py` | 0 | `..................                                                       [100%]` |
| `scripts/test_strategy_registry.py` | 1 | `............F                                                            [100%]` |
| `scripts/test_execution_modes.py` | 2 | `==================================== ERRORS ====================================` |
| `scripts/test_technical_config.py` | 2 | `==================================== ERRORS ====================================` |
| `scripts/test_risk_manager.py` | 2 | `==================================== ERRORS ====================================` |

Key findings:

- `scripts/test_strategy_contracts.py` passed.
- `scripts/test_strategy_attribution.py` passed.
- `scripts/test_strategy_playbooks.py` passed.
- `scripts/test_strategy_registry.py` is mostly safe but currently fails one test because `PyYAML` is not in `requirements-dev.txt`.
- Several agent/risk/config tests are likely not CI-ready under minimal dev dependencies because they require `yaml` or `numpy`.

## Full Classification Table

| Test file | Category | Static risk hits | Targeted execution |
|---|---|---|---|
| `scripts/test_analysis_runner.py` | `needs_mocking_or_refactor` | binance, ccxt, order, telegram | not_run |
| `scripts/test_backtest_dashboard.py` | `unsafe_deferred` | .jsonl, replay, simulate | not_run |
| `scripts/test_binance_futures_history.py` | `needs_mocking_or_refactor` | .env, api_key, binance, dotenv, order, secret | not_run |
| `scripts/test_boundary_guardrails.py` | `unsafe_deferred` | .env, dotenv, open(, order, os.environ, replay, subprocess | not_run |
| `scripts/test_calibration_workflow.py` | `unsafe_deferred` | .jsonl, replay, simulate, subprocess | not_run |
| `scripts/test_candidate_level_attribution.py` | `safe_now_candidate` | order | rc=0; ....                                                                     [100%] / 4 passed in 0.02s |
| `scripts/test_coingecko.py` | `needs_mocking_or_refactor` | binance | not_run |
| `scripts/test_data_fetchers.py` | `needs_mocking_or_refactor` | api_key, binance, dotenv, order, secret | not_run |
| `scripts/test_demo_execution_policy.py` | `needs_mocking_or_refactor` | binance, order, telegram | not_run |
| `scripts/test_derivatives_analyst.py` | `needs_mocking_or_refactor` | dotenv | not_run |
| `scripts/test_dynamic_watchlist.py` | `unsafe_deferred` | default_params.yaml, subprocess | not_run |
| `scripts/test_entry_guard.py` | `needs_mocking_or_refactor` | open( | not_run |
| `scripts/test_execution_mode_gate.py` | `unsafe_deferred` | order | not_run |
| `scripts/test_execution_modes.py` | `needs_dependency_or_fixture` | none | rc=2; ==================================== ERRORS ==================================== / _______________ ERROR collecting scripts/test_execution_modes.py _______________ / ImportError while importing test module '/home/julius/julius-workspace/ai-labs/projects/the-trading-guy/scripts/test_execution_modes.py'. |
| `scripts/test_final_analysis_contract.py` | `unsafe_deferred` | replay | not_run |
| `scripts/test_guarded_reverse_flow.py` | `unsafe_deferred` | order | not_run |
| `scripts/test_health_cli.py` | `unsafe_deferred` | live, logs/, open(, subprocess | not_run |
| `scripts/test_log_rotation.py` | `unsafe_deferred` | logs/ | not_run |
| `scripts/test_manual_report_policy.py` | `unsafe_deferred` | order, replay, simulate, subprocess, telegram | not_run |
| `scripts/test_news_analyst.py` | `needs_mocking_or_refactor` | dotenv, telegram | not_run |
| `scripts/test_order_manager_close_notify.py` | `unsafe_deferred` | binance, order | not_run |
| `scripts/test_paper_trading.py` | `unsafe_deferred` | binance, dotenv, order, telegram | not_run |
| `scripts/test_parameter_recommendations.py` | `unsafe_deferred` | default_params.yaml, logs/, replay, simulate | not_run |
| `scripts/test_parameter_sweep.py` | `unsafe_deferred` | .jsonl, open(, replay, simulate | not_run |
| `scripts/test_phase4b_risk_gate.py` | `unsafe_deferred` | .jsonl, order | not_run |
| `scripts/test_phase5c_position_aware_risk.py` | `needs_dependency_or_fixture` | none | not_run |
| `scripts/test_portfolio_context.py` | `needs_dependency_or_fixture` | none | not_run |
| `scripts/test_position_event_analytics.py` | `unsafe_deferred` | .jsonl | not_run |
| `scripts/test_position_group_close.py` | `unsafe_deferred` | order | not_run |
| `scripts/test_position_manager.py` | `needs_dependency_or_fixture` | none | not_run |
| `scripts/test_position_notifications.py` | `unsafe_deferred` | telegram | not_run |
| `scripts/test_position_reduce.py` | `unsafe_deferred` | order | not_run |
| `scripts/test_process_lock.py` | `unsafe_deferred` | live, open(, subprocess | not_run |
| `scripts/test_readonly_analyzer_cli.py` | `unsafe_deferred` | replay | not_run |
| `scripts/test_readonly_monitoring_cadence.py` | `unsafe_deferred` | .jsonl, logs/, replay, subprocess | not_run |
| `scripts/test_reconciliation.py` | `unsafe_deferred` | binance, order | not_run |
| `scripts/test_replay_attribution_analyzer.py` | `unsafe_deferred` | .jsonl, replay, subprocess | not_run |
| `scripts/test_replay_parameter_sweep.py` | `unsafe_deferred` | open(, replay, simulate | not_run |
| `scripts/test_replay_strategy_attribution.py` | `unsafe_deferred` | order, replay | not_run |
| `scripts/test_research_debate.py` | `needs_dependency_or_fixture` | none | not_run |
| `scripts/test_risk_manager.py` | `needs_dependency_or_fixture` | none | rc=2; ==================================== ERRORS ==================================== / ________________ ERROR collecting scripts/test_risk_manager.py _________________ / ImportError while importing test module '/home/julius/julius-workspace/ai-labs/projects/the-trading-guy/scripts/test_risk_manager.py'. |
| `scripts/test_rss_fetcher.py` | `needs_mocking_or_refactor` | none | not_run |
| `scripts/test_run_paper_trading_dry_run.py` | `needs_mocking_or_refactor` | open(, order, telegram | not_run |
| `scripts/test_runtime_control.py` | `unsafe_deferred` | live, logs/, open(, subprocess | not_run |
| `scripts/test_runtime_health.py` | `unsafe_deferred` | subprocess | not_run |
| `scripts/test_runtime_supervisor.py` | `unsafe_deferred` | live, subprocess | not_run |
| `scripts/test_runtime_watchlist_loader.py` | `unsafe_deferred` | order, subprocess | not_run |
| `scripts/test_scheduler_guard.py` | `unsafe_deferred` | live, logs/, open(, scheduler, subprocess | not_run |
| `scripts/test_screening_agent.py` | `needs_mocking_or_refactor` | subprocess | not_run |
| `scripts/test_sentiment_classifier.py` | `needs_mocking_or_refactor` | exchange | not_run |
| `scripts/test_signal_recorder_strategy_signal.py` | `unsafe_deferred` | .jsonl, order, replay | not_run |
| `scripts/test_spot_close_balance_cap.py` | `unsafe_deferred` | order, place_order | not_run |
| `scripts/test_spot_futures_notifications.py` | `unsafe_deferred` | telegram | not_run |
| `scripts/test_storage.py` | `needs_mocking_or_refactor` | none | not_run |
| `scripts/test_strategy_attribution.py` | `safe_now_candidate` | none | rc=0; ....                                                                     [100%] / 4 passed in 0.01s |
| `scripts/test_strategy_contracts.py` | `safe_now_candidate` | none | rc=0; ......                                                                   [100%] / 6 passed in 0.02s |
| `scripts/test_strategy_playbooks.py` | `safe_now_candidate` | none | rc=0; ..................                                                       [100%] / 18 passed in 0.03s |
| `scripts/test_strategy_registry.py` | `needs_dependency_or_fixture` | order | rc=1; ............F                                                            [100%] / =================================== FAILURES =================================== / ____ test_default_params_strategy_layer_matches_approved_variant_d_surface _____ |
| `scripts/test_strategy_vs_trader_evaluator.py` | `unsafe_deferred` | .jsonl, replay, subprocess | not_run |
| `scripts/test_technical_analyst.py` | `needs_mocking_or_refactor` | none | not_run |
| `scripts/test_technical_config.py` | `needs_dependency_or_fixture` | none | rc=2; ==================================== ERRORS ==================================== / ______________ ERROR collecting scripts/test_technical_config.py _______________ / ImportError while importing test module '/home/julius/julius-workspace/ai-labs/projects/the-trading-guy/scripts/test_technical_config.py'. |
| `scripts/test_telegram_scraper.py` | `needs_mocking_or_refactor` | dotenv, telegram | not_run |
| `scripts/test_trade_simulation.py` | `unsafe_deferred` | .jsonl, open(, replay, simulate | not_run |
| `scripts/test_volatility_skip_broader_validation.py` | `unsafe_deferred` | .jsonl, logs/, replay | not_run |
| `scripts/test_volatility_skip_calibration.py` | `unsafe_deferred` | order, replay, subprocess | not_run |
| `scripts/test_volatility_skip_monitoring.py` | `unsafe_deferred` | .jsonl, order, subprocess | not_run |
| `scripts/test_volatility_skip_zero_blocks.py` | `unsafe_deferred` | .jsonl | not_run |

## Recommendation

For **Batch 5I — Add Expanded Safe Pytest Subset to CI**, the conservative recommendation is to add these three new files alongside the existing candidate-level attribution test:

```bash
python -m pytest -q -p no:cacheprovider   scripts/test_candidate_level_attribution.py   scripts/test_strategy_contracts.py   scripts/test_strategy_attribution.py   scripts/test_strategy_playbooks.py
```

Do **not** add `scripts/test_strategy_registry.py` yet unless Batch 5I also explicitly reviews dev dependencies or splits/removes the `PyYAML`-dependent default-config test from the CI subset.

## Deferred Buckets

- `needs_dependency_or_fixture`: mostly requires `PyYAML`, `numpy`, or isolated state/data fixtures.
- `needs_mocking_or_refactor`: external data, Telegram, Binance/exchange, or integration-adjacent paths that need stronger mocks before CI.
- `unsafe_deferred`: replay/log/output/scheduler/live/order/credential-adjacent tests or scripts; not appropriate for current safe CI subset.

## Post-Checks

Source repo status after targeted execution:

```text
## main...origin/main
```

Tracked local/generated files:

```text
<none>
```

Ignored local artifacts:

```text
!! .venv/
```

## Safety Boundary Confirmation

- No live trading executed.
- No order placement executed.
- No simulate-live execution.
- No StrategySignal-to-order bridge work.
- No runtime/default config mutation.
- No `.env` files read, printed, or committed.
- No global package install.
- No new dependency install in Batch 5H.
- No full test suite execution.
- No replay or monitoring jobs executed.
- No raw replay logs staged or committed.
- No scheduler/cron/systemd enablement.
- No source repo changes committed.
- No push executed.

## Next Step

If Julius approves the shortlist, build:

```text
Batch 5I — Add Expanded Safe Pytest Subset to CI
```
