# Batch 3W — Candidate-Level Attribution Instrumentation

Status: pass
Mode: read-only instrumentation only; no config changes

## Summary

Batch 3W adds candidate-level attribution to the StrategyRegistry output so future replay and monitoring reports can explain why each strategy candidate was selected, rejected, skipped, or overridden.

## Files Changed

- ai-labs/projects/trading-agents/scripts/run_volatility_skip_monitoring.py
- ai-labs/projects/trading-agents/strategies/registry.py
- ai-labs/projects/trading-agents/strategies/volatility_skip.py

## Instrumentation Fields Added

- attribution.candidate_schema_version
- attribution.selection_reason
- attribution.selected_candidate_index
- attribution.prefer_action_over_hold_applied
- attribution.min_action_confidence
- attribution.evaluated[].family
- attribution.evaluated[].selected
- attribution.evaluated[].eligible
- attribution.evaluated[].selection_reason
- attribution.evaluated[].rejection_reason
- attribution.evaluated[].thresholds
- attribution.evaluated[].observed

## Sample Attribution Interpretation

- Selected strategy: trend-following
- Selected action: long
- Selection reason: action_confidence_above_floor
- Prefer action over hold applied: True
- Evaluated candidates: 2

## Backward Compatibility

- Legacy evaluated candidate keys remain present: strategy_id, action, confidence.
- Monitoring candidate-level counts default to zero for older replay logs.
- No runtime/default config files were changed.

## Validation

- candidate_level_attribution_tests: PASS 4 candidate-level attribution tests
- strategy_registry_tests: passed
- strategy_attribution_tests: passed
- boundary_guardrails: All 39 boundary guardrails pass
- volatility_skip_monitoring_tests: PASS 7 volatility-skip monitoring tests

## Safety Confirmation

- No live trading.
- No order placement.
- No simulate-live execution.
- No StrategySignal-to-order mapping.
- No TraderAgent / FinalAnalysis semantic changes.
- No runtime/default config changes.
- No cron/systemd/scheduler enablement.
- No raw replay logs committed.

## Next Recommended Batch

Batch 3X — Fresh Replay With Candidate-Level Attribution should run fresh replay using the new fields and verify the zero-block explanation with direct candidate-level evidence.
