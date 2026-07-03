# Batch 3V-alt — Volatility-Skip Zero-Block Diagnostic

**Status:** `watch`
**Mode:** read-only diagnostic, no runtime/default config changes

## Final Correction Note

This diagnostic normalizes StrategySignal ids/families with hyphen/underscore equivalence, e.g. `volatility-skip` -> `volatility_skip`.

## Short Answer

- Across inspected replay files, `498` records selected volatility-skip as the StrategySignal family/strategy, and `412` of those are HOLD/no-trade style signals.
- Volatility-skip was evaluated in `578` records and evaluated-but-not-selected in `80` records.
- The monitoring metric `volatility_skip_direct_block_rate` is narrower than selected-volatility-skip frequency: it tracks direct blocks during TraderAgent action contexts. Therefore it can remain 0.0 even when volatility-skip is selected often as HOLD/no-trade.
- ATR attribution is visible in `412` records, but only `0` meet high_atr_pct >= 0.1; most volatility-skip HOLDs appear below the high direct-block threshold.
- Hard conflicts and volatile breakout selections remain zero in inspected monitoring reports, so this is a watch/interpretation issue rather than a hard safety failure.
- Some records show trend-following/breakout selected after volatility-skip evaluation; prefer_action_over_hold may contribute when action confidence is available, but candidate-level causality remains only partially observable.

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
- `selected_volatility_skip_records`: `498`
- `selected_trend_following_records`: `74`
- `selected_breakout_records`: `6`
- `volatility_skip_hold_records`: `412`
- `volatility_skip_long_short_records`: `0`
- `records_where_volatility_skip_was_evaluated`: `578`
- `records_where_volatility_skip_was_evaluated_but_not_selected`: `80`
- `records_with_volatile_regime_attribution`: `365`
- `records_with_atr_pct_attribution`: `412`
- `records_with_atr_pct_ge_high_atr_threshold`: `0`
- `records_with_atr_or_volatility_numeric_fields`: `650`

## Canonical Strategy ID Counts

- `volatility_skip`: `498`
- `trend_following`: `74`
- `unknown`: `72`
- `breakout`: `6`

## Action Counts

- `hold`: `412`
- `skip`: `86`
- `unknown`: `72`
- `short`: `43`
- `long`: `37`

## Attribution Regime Counts

- `volatile`: `365`
- `trend_down`: `133`
- `trend_up`: `80`
- `unknown`: `72`

## Monitoring Report Summaries

- `volatility-skip-monitoring-cadence-batch3r-manual-2026-07-03-0917-batch3u.json`: status=`watch`, records=`141`, hard_conflicts=`0`, volatile_breakout_selected=`0`, volatile_trend_following_selected=`2`, direct_block_rate=`0.0`
- `volatility-skip-monitoring-combined-batch3r-manual-2026-07-03-0917-batch3u.json`: status=`watch`, records=`296`, hard_conflicts=`0`, volatile_breakout_selected=`0`, volatile_trend_following_selected=`3`, direct_block_rate=`0.0`
- `volatility-skip-monitoring-cadence-batch3r-2026-07-02-batch3s.json`: status=`watch`, records=`141`, hard_conflicts=`0`, volatile_breakout_selected=`0`, volatile_trend_following_selected=`2`, direct_block_rate=`0.0`
- `volatility-skip-monitoring-combined-batch3r-2026-07-02-batch3s.json`: status=`watch`, records=`296`, hard_conflicts=`0`, volatile_breakout_selected=`0`, volatile_trend_following_selected=`3`, direct_block_rate=`0.0`
- `volatility-skip-monitoring-cadence-batch3q-retry-2026-07-02.json`: status=`watch`, records=`141`, hard_conflicts=`0`, volatile_breakout_selected=`0`, volatile_trend_following_selected=`2`, direct_block_rate=`0.0`
- `volatility-skip-monitoring-combined-batch3q-retry-2026-07-02.json`: status=`watch`, records=`296`, hard_conflicts=`0`, volatile_breakout_selected=`0`, volatile_trend_following_selected=`3`, direct_block_rate=`0.0`

## Interpretation

The zero direct-block watch flag does **not** mean volatility-skip never appears. It means the monitoring direct-block metric did not observe volatility-skip directly blocking TraderAgent action records under its stricter definition. The replay artifacts show many selected volatility-skip HOLD/no-trade signals, while hard conflicts and volatile breakout selections remain zero.

This diagnostic should not be used to change config by itself. Candidate-level confidence-floor failures are only partially exposed in current replay JSONL.

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
