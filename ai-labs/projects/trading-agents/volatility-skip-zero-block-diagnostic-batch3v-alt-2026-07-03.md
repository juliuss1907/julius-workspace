# Batch 3V-alt — Volatility-Skip Zero-Block Diagnostic

**Status:** `watch`
**Mode:** read-only diagnostic, no runtime/default config changes

## Question

Why does `volatility_skip_direct_block_rate == 0.0` keep appearing across monitoring batches?

## Short Answer

- No explicit volatile regime records were detectable in replay JSONL schema; zero direct blocks may be sample/schema visibility driven.
- Detected 650 records with numeric pct/ratio volatility candidates >= 0.10; inspect examples before changing config.
- Action-oriented strategies are selected in some records; with prefer_action_over_hold=true, HOLD-like skip candidates may be less likely to become selected when action confidence is available.
- Existing monitoring reports show hard_conflict_count=0 and volatile_breakout_selected_count=0, so zero-block is a watch item rather than an execution-safety failure.

## Current Config Check

- `enabled`: `True`
- `matches_variant_d_core_expectations`: `True`
- `volatility_skip_high_atr_pct`: `0.1`
- `volatility_skip_volatile_confidence_floor`: `0.75`
- `breakout_allow_volatile`: `False`
- `prefer_action_over_hold`: `True`
- `regime_strategy_order`: `{'trend_up': ['volatility_skip', 'trend_following', 'breakout'], 'trend_down': ['volatility_skip', 'trend_following', 'breakout'], 'ranging': ['volatility_skip', 'breakout'], 'volatile': ['volatility_skip', 'trend_following', 'breakout']}`

## Record Diagnostic

- `total_records`: `650`
- `parse_error_count`: `0`
- `records_with_strategy_signal`: `578`
- `records_with_strategy_attribution_text`: `578`
- `records_with_market_state`: `0`
- `volatile_regime_records`: `0`
- `records_with_atr_or_volatility_numeric_fields`: `650`
- `records_with_any_high_atr_pct_candidate_ge_config_threshold`: `650`
- `selected_volatility_skip_records`: `498`
- `selected_trend_following_records`: `74`
- `selected_breakout_records`: `6`
- `final_action_records`: `0`
- `final_hold_records`: `0`
- `final_buy_sell_records`: `0`

## Selected Strategy Counts

- `volatility_skip`: `498`
- `trend_following`: `74`
- `unknown`: `72`
- `breakout`: `6`

## Regime Counts

- `unknown`: `650`

## Monitoring Report Summaries

- `volatility-skip-monitoring-cadence-batch3r-manual-2026-07-03-0917-batch3u.json`: status=`watch`, records=`141`, hard_conflicts=`0`, volatile_breakout_selected=`0`, volatile_trend_following_selected=`2`, direct_block_rate=`0.0`
- `volatility-skip-monitoring-combined-batch3r-manual-2026-07-03-0917-batch3u.json`: status=`watch`, records=`296`, hard_conflicts=`0`, volatile_breakout_selected=`0`, volatile_trend_following_selected=`3`, direct_block_rate=`0.0`
- `volatility-skip-monitoring-cadence-batch3r-2026-07-02-batch3s.json`: status=`watch`, records=`141`, hard_conflicts=`0`, volatile_breakout_selected=`0`, volatile_trend_following_selected=`2`, direct_block_rate=`0.0`
- `volatility-skip-monitoring-combined-batch3r-2026-07-02-batch3s.json`: status=`watch`, records=`296`, hard_conflicts=`0`, volatile_breakout_selected=`0`, volatile_trend_following_selected=`3`, direct_block_rate=`0.0`
- `volatility-skip-monitoring-cadence-batch3q-retry-2026-07-02.json`: status=`watch`, records=`141`, hard_conflicts=`0`, volatile_breakout_selected=`0`, volatile_trend_following_selected=`2`, direct_block_rate=`0.0`
- `volatility-skip-monitoring-combined-batch3q-retry-2026-07-02.json`: status=`watch`, records=`296`, hard_conflicts=`0`, volatile_breakout_selected=`0`, volatile_trend_following_selected=`3`, direct_block_rate=`0.0`

## Interpretation

The current replay/monitoring artifacts are enough to confirm the repeated zero direct-block observation, but they do not expose every intermediate candidate that the strategy registry considered. Therefore this diagnostic should not be used to loosen or tighten config by itself.

The safest interpretation is: **zero direct blocks are a watch signal, not a hard failure**, because hard conflicts remain zero, volatile breakout selections remain zero, and approved variant-D core config is intact.

## Safety Confirmation

- No live trading.
- No order placement.
- No simulate-live execution.
- No StrategySignal-to-order mapping.
- No runtime/default config mutation.
- No scheduler/cron/systemd enablement.
- Raw replay logs remain local-only.

## Recommendation

Proceed to Batch 3V manual cadence run #3 only after committing this diagnostic. Keep scheduler disabled. If deeper causality is required, plan a separate candidate-level attribution instrumentation batch.
