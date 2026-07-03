# Batch 3U — Manual Cadence Run #2 Evidence Pack

**Date tag:** `manual-2026-07-03-0917-batch3u`
**Status:** `watch`
**Mode:** Option A — manual-on-demand only

## Summary

Batch 3U executed the second manual read-only monitoring cadence after Batch 3T selected manual-on-demand operation. The cadence remained read-only and scheduler-disabled.

## Safety Boundaries

- No live trading.
- No order placement.
- No simulate-live execution.
- No StrategySignal-to-order mapping.
- No runtime/default config change.
- No cron/systemd/scheduler enablement.
- Raw replay log is local-only and must not be committed.

## Dependency Readiness

- Command: `venv/bin/python scripts/check_replay_dependency_readiness.py`
- Result: `pass`

## Cadence Execution

- Dry-run executed first: `true`
- Explicit `--run` executed: `true`
- Symbols: `BTCUSDT ETHUSDT SOLUSDT`
- Days/window/step: `14 / 200 / 4`
- Raw replay log: `logs/replay_signals-batch3r-manual-2026-07-03-0917-batch3u-core.jsonl`
- Raw replay records: `141`
- Raw replay policy: **do not stage, commit, or push**

## Fresh Monitoring

- `status`: `watch`
- `windows`: `1`
- `total_records`: `141`
- `hard_conflict_count`: `0`
- `volatile_breakout_selected_count`: `0`
- `volatile_trend_following_selected_count`: `2`
- `fallback_or_missing_state_count`: `0`
- `alignment_rate`: `0.5603`
- `attribution_coverage_rate`: `1.0000`
- `conflict_rate`: `0.0000`
- `directional_strategy_coverage_rate`: `0.1560`
- `skip_during_trader_action_rate`: `0.0000`
- `volatility_skip_direct_block_rate`: `0.0000`
- `current_config_matches_variant_d`: `True`

## Combined Monitoring

- `status`: `watch`
- `windows`: `3`
- `total_records`: `296`
- `hard_conflict_count`: `0`
- `volatile_breakout_selected_count`: `0`
- `volatile_trend_following_selected_count`: `3`
- `fallback_or_missing_state_count`: `0`
- `alignment_rate`: `0.5304`
- `attribution_coverage_rate`: `1.0000`
- `conflict_rate`: `0.0000`
- `directional_strategy_coverage_rate`: `0.1284`
- `skip_during_trader_action_rate`: `0.0000`
- `volatility_skip_direct_block_rate`: `0.0000`
- `current_config_matches_variant_d`: `True`

## Comparison

- Batch 3Q Retry: fresh 141 records; combined 296 records; status watch; hard conflicts 0; volatile breakout selected 0.
- Batch 3S: fresh 141 records; combined 296 records; status watch; hard conflicts 0; volatile breakout selected 0.
- Batch 3U matches the same clean hard-safety profile and remains a manual evidence point, not a scheduler approval.

## Watch Reasons

- fresh: volatility_skip_direct_block_rate == 0.0
- fresh: volatility_skip_direct_block_rate — Volatility-skip direct block rate is 0.0%; continue watching for over-relaxation.
- combined: volatility_skip_direct_block_rate == 0.0
- combined: volatility_skip_direct_block_rate — Volatility-skip direct block rate is 0.0%; continue watching for over-relaxation.

## Scheduler State

Scheduler remains disabled:

- `scheduler_enabled`: `false`
- `cron_enabled`: `false`
- `systemd_timer_enabled`: `false`

Future scheduler work still requires explicit Julius approval:

```text
Approve scheduled read-only monitoring cadence for trading-agents.
```

## Local-Only Raw Log Policy

Do not stage or commit `logs/replay_signals-batch3r-manual-2026-07-03-0917-batch3u-core.jsonl`.
