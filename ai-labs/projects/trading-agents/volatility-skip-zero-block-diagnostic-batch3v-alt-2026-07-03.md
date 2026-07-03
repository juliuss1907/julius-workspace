# Batch 3V-alt — Volatility-Skip Zero-Block Diagnostic

**Status:** `watch`
**Mode:** read-only diagnostic, no runtime/default config changes

## Correction Note

This diagnostic uses `strategy_signal.strategy_id`, `strategy_signal.family`, and `strategy_signal.action` as the selected StrategySignal fields. It does not infer selected strategy from flattened attribution text.

## Short Answer

- Replay JSONL shows 0 records whose selected `strategy_signal.strategy_id` is `volatility_skip`, mostly HOLD/no-trade style signals.
- Monitoring direct block rate remains 0.0 because the monitor metric is narrower than selected volatility-skip count: it counts volatility-skip directly blocking a TraderAgent action, not every volatility-skip HOLD selection.
- All selected volatility-skip records are non-action/HOLD style; they do not create order intent and remain observational-only.
- Recent monitoring summaries still show hard_conflict_count=0 and volatile_breakout_selected_count=0, so this is a watch/interpretation issue rather than a hard safety failure.
- Replay JSONL does not expose a simple explicit regime field; deeper cause analysis would require candidate-level attribution instrumentation in a separately approved batch.

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
- `records_with_strategy_signal`: `578`
- `selected_volatility_skip_records`: `0`
- `selected_trend_following_records`: `0`
- `selected_breakout_records`: `6`
- `volatility_skip_hold_records`: `0`
- `volatility_skip_buy_sell_records`: `0`
- `records_with_volatility_skip_in_attribution`: `0`
- `records_with_atr_or_volatility_numeric_fields`: `650`
- `records_with_any_high_atr_pct_candidate_ge_config_threshold`: `650`
- `records_with_market_snapshot`: `650`
- `records_with_explicit_regime_field`: `0`

## Strategy ID Counts

- `volatility-skip`: `498`
- `trend-following`: `74`
- `unknown`: `72`
- `breakout`: `6`

## Action Counts

- `hold`: `412`
- `skip`: `86`
- `unknown`: `72`
- `short`: `43`
- `long`: `37`

## Monitoring Report Summaries

- `volatility-skip-monitoring-cadence-batch3r-manual-2026-07-03-0917-batch3u.json`: status=`watch`, records=`141`, hard_conflicts=`0`, volatile_breakout_selected=`0`, volatile_trend_following_selected=`2`, direct_block_rate=`0.0`
- `volatility-skip-monitoring-combined-batch3r-manual-2026-07-03-0917-batch3u.json`: status=`watch`, records=`296`, hard_conflicts=`0`, volatile_breakout_selected=`0`, volatile_trend_following_selected=`3`, direct_block_rate=`0.0`
- `volatility-skip-monitoring-cadence-batch3r-2026-07-02-batch3s.json`: status=`watch`, records=`141`, hard_conflicts=`0`, volatile_breakout_selected=`0`, volatile_trend_following_selected=`2`, direct_block_rate=`0.0`
- `volatility-skip-monitoring-combined-batch3r-2026-07-02-batch3s.json`: status=`watch`, records=`296`, hard_conflicts=`0`, volatile_breakout_selected=`0`, volatile_trend_following_selected=`3`, direct_block_rate=`0.0`
- `volatility-skip-monitoring-cadence-batch3q-retry-2026-07-02.json`: status=`watch`, records=`141`, hard_conflicts=`0`, volatile_breakout_selected=`0`, volatile_trend_following_selected=`2`, direct_block_rate=`0.0`
- `volatility-skip-monitoring-combined-batch3q-retry-2026-07-02.json`: status=`watch`, records=`296`, hard_conflicts=`0`, volatile_breakout_selected=`0`, volatile_trend_following_selected=`3`, direct_block_rate=`0.0`

## Interpretation

The zero direct-block watch flag does **not** mean volatility-skip never appears. It means the monitor did not observe volatility-skip directly blocking TraderAgent action records under its stricter definition. The replay artifacts show many selected volatility-skip HOLD/no-trade signals, while hard conflicts and volatile breakout selections remain zero.

This diagnostic should not be used to change config by itself. Candidate-level internals and confidence-floor failures are not fully exposed in current replay JSONL.

## Safety Confirmation

- No live trading.
- No order placement.
- No simulate-live execution.
- No StrategySignal-to-order mapping.
- No runtime/default config mutation.
- No scheduler/cron/systemd enablement.
- Raw replay logs remain local-only.

## Recommendation

Proceed to Batch 3V manual cadence run #3 after this diagnostic correction is committed. Keep scheduler disabled.
