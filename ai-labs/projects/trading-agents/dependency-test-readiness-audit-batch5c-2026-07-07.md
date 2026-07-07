# Batch 5C — Dependency & Test Readiness Audit

Date: 2026-07-07

## Goal

Audit dependency and test readiness for the source-of-truth repo without installing dependencies or running unsafe scripts.

## Source Repo

- Path: `/home/julius/julius-workspace/ai-labs/projects/the-trading-guy`
- Remote: `git@github.com:juliuss1907/the-trading-guy.git`
- HEAD: `60eec5639f6fcb9c49eef70947908fb1803b449c`
- Log: `60eec56 ci: add repository safety checks`
- Commit count: `3`
- Remote main: `60eec5639f6fcb9c49eef70947908fb1803b449c`

## Existing CI Checks

```text
forbidden_files_check=ok
required_docs_check=ok
python_files_checked=181
syntax_check=ok
```

## Dependency Files

- requirements.txt: exists, pytest=True, api_lib_markers=True
- requirements-dev.txt: missing
- pyproject.toml: missing
- setup.py: missing
- setup.cfg: missing
- Pipfile: missing
- poetry.lock: missing

## Pytest Availability

- Available: `False`
- Exit code: `1`
- Output: `/usr/bin/python: No module named pytest`

## Tests Discovered

- Test count: `67`

Safe/CI-candidate tests:

```text
scripts/test_candidate_level_attribution.py
scripts/test_derivatives_analyst.py
scripts/test_entry_guard.py
scripts/test_execution_mode_gate.py
scripts/test_execution_modes.py
scripts/test_final_analysis_contract.py
scripts/test_guarded_reverse_flow.py
scripts/test_phase4b_risk_gate.py
scripts/test_portfolio_context.py
scripts/test_readonly_analyzer_cli.py
scripts/test_replay_strategy_attribution.py
scripts/test_research_debate.py
scripts/test_risk_manager.py
scripts/test_sentiment_classifier.py
scripts/test_storage.py
scripts/test_strategy_attribution.py
scripts/test_strategy_contracts.py
scripts/test_strategy_playbooks.py
scripts/test_strategy_registry.py
scripts/test_technical_analyst.py
scripts/test_technical_config.py
scripts/test_volatility_skip_calibration.py
```

Unsafe or needs-review tests:

```text
scripts/test_analysis_runner.py — requires_network
scripts/test_backtest_dashboard.py — mutates_state
scripts/test_binance_futures_history.py — requires_credentials, requires_network
scripts/test_boundary_guardrails.py — requires_credentials, requires_network
scripts/test_calibration_workflow.py — mutates_state
scripts/test_coingecko.py — requires_network
scripts/test_data_fetchers.py — requires_credentials, requires_network
scripts/test_demo_execution_policy.py — requires_network
scripts/test_dynamic_watchlist.py — mutates_state
scripts/test_health_cli.py — mutates_state
scripts/test_log_rotation.py — mutates_state
scripts/test_manual_report_policy.py — mutates_state, requires_network
scripts/test_news_analyst.py — requires_network
scripts/test_order_manager_close_notify.py — requires_network, trading_or_order_related
scripts/test_paper_trading.py — requires_network
scripts/test_parameter_recommendations.py — mutates_state
scripts/test_parameter_sweep.py — mutates_state
scripts/test_phase5c_position_aware_risk.py — trading_or_order_related
scripts/test_position_event_analytics.py — mutates_state, trading_or_order_related
scripts/test_position_group_close.py — mutates_state, trading_or_order_related
scripts/test_position_manager.py — trading_or_order_related
scripts/test_position_notifications.py — requires_network, trading_or_order_related
scripts/test_position_reduce.py — trading_or_order_related
scripts/test_process_lock.py — mutates_state
scripts/test_readonly_monitoring_cadence.py — mutates_state
scripts/test_reconciliation.py — mutates_state, requires_network, trading_or_order_related
scripts/test_replay_attribution_analyzer.py — mutates_state
scripts/test_replay_parameter_sweep.py — mutates_state
scripts/test_rss_fetcher.py — mutates_state
scripts/test_run_paper_trading_dry_run.py — requires_network, trading_or_order_related
scripts/test_runtime_control.py — mutates_state
scripts/test_runtime_health.py — mutates_state
scripts/test_runtime_supervisor.py — mutates_state
scripts/test_runtime_watchlist_loader.py — mutates_state
scripts/test_scheduler_guard.py — mutates_state
scripts/test_screening_agent.py — mutates_state
scripts/test_signal_recorder_strategy_signal.py — mutates_state, trading_or_order_related
scripts/test_spot_close_balance_cap.py — trading_or_order_related
scripts/test_spot_futures_notifications.py — requires_credentials, requires_network
scripts/test_strategy_vs_trader_evaluator.py — mutates_state, trading_or_order_related
scripts/test_telegram_scraper.py — mutates_state, requires_network
scripts/test_trade_simulation.py — mutates_state, trading_or_order_related
scripts/test_volatility_skip_broader_validation.py — mutates_state
scripts/test_volatility_skip_monitoring.py — mutates_state
scripts/test_volatility_skip_zero_blocks.py — mutates_state
```

## Candidate-Level Attribution Test

- Candidate: `scripts/test_candidate_level_attribution.py`
- Classified safe to run: `True`
- Run status: `skipped`
- Exit code: `skipped`

Output:

```text
pytest unavailable; skipped without installing dependencies
```

## Dependency Readiness Checker

- Path: `scripts/check_replay_dependency_readiness.py`
- Exists: `True`
- Static decision: `deferred_requires_dedicated_review`
- Run status: `skipped`
- Exit code: `skipped`

Output:

```text
checker missing or deferred after safety classification
```

## Post-Audit Hygiene

- Source repo status lines after audit: `0`
- Forbidden files after audit: `0`
- Dependency install executed: `false`
- Push executed: `false`

## Recommendations

- Add/approve a dev dependency strategy for pytest before enabling pytest in CI.
- Keep unsafe/unknown tests out of CI until refactored or explicitly marked.
- Dependency readiness checker remains deferred or missing; review separately before CI inclusion.

## Safety Boundaries

- Live trading: not executed
- Order placement: not executed
- Simulate-live: not executed
- StrategySignal-to-order mapping: not added
- Runtime/default config changes: not changed
- Dependency install: not executed
- External API calls: not executed
- Secrets printed: none
- `.env` files read/printed/committed: none
- Raw replay logs committed: none
- Scheduler/cron/systemd enabled: no
- Push: no

## Status

`passed`
