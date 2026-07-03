# Batch 3X — Fresh Replay With Candidate-Level Attribution

Status: watch
Mode: read-only replay and monitoring; no config changes; no scheduler

## Summary

Batch 3X ran fresh replay after Batch 3W candidate-level attribution instrumentation. The raw replay log remains local-only. Summary reports only are committable.

## Status Reasons

- candidate-level attribution is present on every fresh replay record
- volatility_skip_direct_block_rate remains 0.0, but candidate-level counts now explain the condition
- hard_conflict_count and volatile_breakout_selected_count remain 0 with variant-D config intact
- scheduler remains disabled; Batch 3X does not authorize cron/systemd/scheduler

## Candidate Schema Coverage

- evaluated_candidate_count: 403
- records: 141
- records_with_candidate_schema_version: 141
- records_with_evaluated_candidates: 141
- records_with_strategy_signal: 141
- volatility_skip_action_override_count: 23
- volatility_skip_confidence_floor_failed_count: 94
- volatility_skip_evaluated_count: 141
- volatility_skip_evaluated_not_selected_count: 23
- volatility_skip_selected_hold_count: 118
- volatility_skip_threshold_failed_count: 141

## Fresh Monitoring

- path: volatility-skip-monitoring-candidate-batch3x-2026-07-03.json
- status: watch
- total_records: 141
- hard_conflict_count: 0
- volatile_breakout_selected_count: 0
- volatile_trend_following_selected_count: 2
- fallback_or_missing_state_count: 0
- volatility_skip_evaluated_count: 0
- volatility_skip_selected_hold_count: 0
- volatility_skip_evaluated_not_selected_count: 0
- volatility_skip_action_override_count: 0
- volatility_skip_threshold_failed_count: 0
- volatility_skip_confidence_floor_failed_count: 0
- alignment_rate: 0.41134751773049644
- attribution_coverage_rate: 1.0
- conflict_rate: 0.0
- directional_strategy_coverage_rate: 0.16312056737588654
- skip_during_trader_action_rate: 0.0
- volatility_skip_direct_block_rate: 0.0
- current_config_matches_variant_d: True

## Combined Monitoring

- path: volatility-skip-monitoring-combined-candidate-batch3x-2026-07-03.json
- status: watch
- total_records: 296
- hard_conflict_count: 0
- volatile_breakout_selected_count: 0
- volatile_trend_following_selected_count: 3
- fallback_or_missing_state_count: 0
- volatility_skip_evaluated_count: 0
- volatility_skip_selected_hold_count: 0
- volatility_skip_evaluated_not_selected_count: 0
- volatility_skip_action_override_count: 0
- volatility_skip_threshold_failed_count: 0
- volatility_skip_confidence_floor_failed_count: 0
- alignment_rate: 0.4594594594594595
- attribution_coverage_rate: 1.0
- conflict_rate: 0.0
- directional_strategy_coverage_rate: 0.13175675675675674
- skip_during_trader_action_rate: 0.0
- volatility_skip_direct_block_rate: 0.0
- current_config_matches_variant_d: True

## Interpretation

The direct-block rate can remain 0.0 while volatility-skip candidate activity is visible. Batch 3X uses candidate-level fields to separate volatility-skip evaluated, selected HOLD, evaluated-not-selected, action override, threshold-failed, and confidence-floor-failed counts.

## Safety Confirmation

- No live trading.
- No order placement.
- No simulate-live execution.
- No StrategySignal-to-order mapping.
- No runtime/default config change.
- No cron/systemd/scheduler enablement.
- Raw replay log is local-only and must not be committed.

Raw replay log: logs/replay_signals-batch3x-candidate-2026-07-03-1038-core.jsonl

## Recommendation

Keep manual-only mode for now. Consider Batch 3Y documentation consolidation or scheduler proposal refresh without enabling scheduler.
