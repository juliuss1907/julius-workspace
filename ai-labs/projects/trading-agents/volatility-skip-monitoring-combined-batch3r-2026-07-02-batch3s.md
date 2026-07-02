# Batch 3O — Volatility-Skip Post-Implementation Monitoring

## Executive Summary

- Mode: post_implementation_monitoring
- Status: watch
- Runtime/default config change performed in Batch 3O: false
- Monitoring inputs: logs/replay_signals-batch3f-2026-06-28.jsonl, logs/replay_signals-batch3g-2026-06-28.jsonl, logs/replay_signals-batch3r-2026-07-02-batch3s-core.jsonl
- Recommendation: Monitoring watch; keep variant-d but collect broader replay data before further runtime expansion.

## Current Config Verification

| Key | Expected | Actual | Matches |
|---|---|---|---|
| regime_strategy_order.volatile | ['volatility_skip', 'trend_following', 'breakout'] | ['volatility_skip', 'trend_following', 'breakout'] | true |
| volatility_skip.volatile_confidence_floor | 0.75 | 0.75 | true |
| volatility_skip.high_atr_pct | 0.1 | 0.1 | true |
| trend_following.allow_volatile_trend_up | True | True | true |
| trend_following.allow_volatile_trend_down | True | True | true |
| trend_following.min_regime_confidence | 0.5 | 0.5 | true |
| selection.min_action_confidence | 0.5 | 0.5 | true |
| breakout.allow_volatile | False | False | true |

## Aggregate Monitoring Metrics

| Metric | Value |
|---|---:|
| total_records | 296 |
| hard_conflict_count | 0 |
| volatile_trend_following_selected_count | 3 |
| volatile_breakout_selected_count | 0 |
| fallback_or_missing_state_count | 0 |
| attribution_coverage_rate | 100.0% |
| directional_strategy_coverage_rate | 12.8% |
| skip_during_trader_action_rate | 0.0% |
| volatility_skip_direct_block_rate | 0.0% |

## Alerts

| Level | Metric | Message |
|---|---|---|
| watch | volatility_skip_direct_block_rate | Volatility-skip direct block rate is 0.0%; continue watching for over-relaxation. |

## Per-Window Summary

| Window | Records | Hard conflicts | Volatile trend-following | Volatile breakout | Vol-skip block rate | Directional rate |
|---|---:|---:|---:|---:|---:|---:|
| replay_signals-batch3f-2026-06-28 | 15 | 0 | 0 | 0 | 0.0% | 6.7% |
| replay_signals-batch3g-2026-06-28 | 140 | 0 | 1 | 0 | 0.0% | 10.7% |
| replay_signals-batch3r-2026-07-02-batch3s-core | 141 | 0 | 2 | 0 | 0.0% | 15.6% |

## Boundary Confirmation

- No runtime/default config changes were made by Batch 3O.
- No live trading, order placement, or StrategySignal-to-order mapping was introduced.
- Raw replay logs remain local/ignored and were not committed.

## Recommendation

- Outcome: Monitoring watch; keep variant-d but collect broader replay data before further runtime expansion.
- Next batch: Batch 3P — collect broader replay dataset and review watch alerts.

## Decision Block

~~~text
Batch 3O Decision:
- Runtime/default config change performed in Batch 3O: false
- Current config matches variant-d: true
- Volatile breakout selected count: 0
- Hard conflict count: 0
- Monitoring status: watch
- Recommendation: Monitoring watch; keep variant-d but collect broader replay data before further runtime expansion.
- Next batch: Batch 3P — collect broader replay dataset and review watch alerts.
~~~
