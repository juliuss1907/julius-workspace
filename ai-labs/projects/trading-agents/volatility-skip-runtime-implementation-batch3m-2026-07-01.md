# Batch 3M — Runtime/Default Implementation for Variant-D Volatility-Skip Calibration

## Executive Summary

Batch 3M applied the approved variant-d volatility-skip calibration to the runtime/default strategy_layer config. This was a config-only implementation plus tests/reporting.

| Field | Value |
|---|---|
| Approval phrase received | yes |
| Implementation candidate | variant-d |
| Variant-b applied | false |
| Production/default config changed | true |
| Live trading authorized | false |
| Order placement authorized | false |
| StrategySignal-to-order mapping introduced | false |
| Authoritative config source | config/default_params.yaml |

## Config Changes

| Key | Old value | New value | Expected |
|---|---|---|---|
| regime_strategy_order.volatile | ['volatility_skip'] | ['volatility_skip', 'trend_following', 'breakout'] | ['volatility_skip', 'trend_following', 'breakout'] |
| volatility_skip.volatile_confidence_floor | absent | 0.75 | 0.75 |
| volatility_skip.high_atr_pct | absent | 0.1 | 0.1 |
| trend_following.allow_volatile_trend_up | absent | True | True |
| trend_following.allow_volatile_trend_down | absent | True | True |
| trend_following.min_regime_confidence | absent | 0.5 | 0.5 |
| selection.min_action_confidence | 0.55 | 0.5 | 0.5 |
| breakout.allow_volatile | absent | False | False |

## Safety Boundaries
- Variant-b was not applied.
- breakout.allow_volatile remains false.
- StrategySignal remains observational-only.
- No live trading, order placement, or StrategySignal-to-order mapping was introduced.

## Tests Run
- python3 scripts/test_strategy_registry.py
- python3 scripts/test_strategy_playbooks.py
- python3 scripts/test_volatility_skip_calibration.py
- python3 scripts/test_volatility_skip_broader_validation.py
- python3 scripts/test_volatility_skip_zero_blocks.py
- python3 scripts/test_strategy_vs_trader_evaluator.py
- python3 scripts/test_boundary_guardrails.py

## Post-Implementation Replay Report Summary

- Batch 3J recommendation: Variant D remains the safer primary candidate for another review step.
- Batch 3K recommendation: Variant D zero-block behavior is mostly explained by the replay-only volatile confidence floor.

## Rollback Plan
- Revert the Batch 3M commit, or restore strategy_layer volatile order to [volatility_skip].
- Remove strategy_layer.volatility_skip, strategy_layer.trend_following, and strategy_layer.breakout overrides if reverting manually.
- Restore strategy_layer.selection.min_action_confidence to 0.55.
- Rerun strategy registry/playbook tests and boundary guardrails.
- Rerun Batch 3J and Batch 3K replay validation reports.

## Recommendation
- Outcome: Variant-d runtime/default strategy_layer config implemented with approval; keep monitoring replay metrics before any further runtime expansion.
- Next batch: Batch 3N — post-implementation monitoring/rollback drill or broader replay collection before any live/paper execution changes.

## Decision Block

~~~text
Batch 3M Decision:
- Approval phrase received: true
- Runtime/default config change performed: true
- Candidate implemented: variant-d
- Variant-b applied: false
- breakout.allow_volatile: false
- Live trading authorized: false
- Order placement authorized: false
- StrategySignal-to-order mapping introduced: false
- Values match expected: true
- Next batch: Batch 3N — post-implementation monitoring/rollback drill or broader replay collection before any live/paper execution changes.
~~~
