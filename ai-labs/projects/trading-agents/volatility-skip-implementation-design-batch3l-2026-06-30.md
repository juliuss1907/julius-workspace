# Batch 3L — Approval-Gated Volatility-Skip Calibration Implementation Design

## Executive Summary

Batch 3L converts the replay-only evidence from Batches 3H/3I/3J/3K into an implementation design for a possible future runtime/default calibration batch.

This batch is design-only. It does not authorize or perform production/default/runtime changes.

| Field | Value |
|---|---|
| Mode | design_only_approval_gated |
| Recommended candidate | variant-d |
| Secondary/stress-test candidate | variant-b |
| Variant E required before implementation | false |
| Production change authorized | false |
| Implementation authorized | false |
| Runtime/default config change performed | false |
| Future approval required | true |

## Scope Boundary
- No live trading.
- No order placement.
- No simulate-live execution.
- No StrategySignal-to-order mapping.
- No TraderAgent / FinalAnalysis semantic change.
- No production/default config mutation.
- No runtime behavior change.

## Evidence Chain

### Batch 3H — Candidate Discovery
Batch 3H found two promising replay-only volatility-skip calibration candidates: variant-b and variant-d.

### Batch 3I — Implementation Proposal
Batch 3I recommended variant-d as the safer primary candidate and kept variant-b as an aggressive stress-test candidate only.

### Batch 3J — Broader Replay Validation
- Windows: 2
- Records: 155

| Candidate | Directional coverage mean | Skip-during-action mean | Volatility-skip direct block mean |
|---|---:|---:|---:|
| baseline | 8.3% | 20.8% | 48.6% |
| variant-d | 8.7% | 0.0% | 0.0% |
| variant-b | 9.8% | 0.0% | 0.0% |

Batch 3J kept variant-d as the primary candidate but flagged the 0.0% direct-block behavior for targeted review.

### Batch 3K — Zero-Block Explanation
- Baseline direct volatility-skip blocks reviewed: 86
- Variant D remaining direct blocks: 0
- Variant D hard conflicts: 0
- Variant B remaining direct blocks: 0
- Variant B hard conflicts: 0

#### Variant D dominant reason categories
| Reason | Count |
|---|---:|
| atr_below_candidate_threshold | 86 |
| lower_action_confidence_floor | 85 |
| trend_following_allowed_volatile | 1 |
| volatile_confidence_below_floor | 86 |

#### Variant B dominant reason categories
| Reason | Count |
|---|---:|
| atr_below_candidate_threshold | 86 |
| breakout_allowed_volatile | 4 |
| volatile_confidence_below_floor | 86 |

## Candidate D Proposed Parameters
These are the replay-only variant-d parameters to use as the design baseline for a future approval-gated implementation. They are not production defaults yet.

~~~yaml
volatility_skip:
  volatile_confidence_floor: 0.75
  high_atr_pct: 0.1
trend_following:
  allow_volatile_trend_up: true
  allow_volatile_trend_down: true
  min_regime_confidence: 0.5
selection:
  min_action_confidence: 0.5
~~~

## Candidate B Stress-Test Parameters
variant-b remains a stress-test candidate because it is more aggressive and permits volatile breakout behavior.

~~~yaml
volatility_skip:
  volatile_confidence_floor: 0.95
  high_atr_pct: 0.12
trend_following:
  allow_volatile_trend_up: true
  allow_volatile_trend_down: true
breakout:
  allow_volatile: true
selection:
  min_action_confidence: 0.55
~~~

## Future Approved Change Surface
| Path | Future action if approved | Batch 3L action |
|---|---|---|
| config/default_params.yaml or config/thresholds.yaml | Expose/adopt variant-d volatility-skip and strategy-selection parameters as runtime/default config values. | read/document only; no mutation |
| strategies/volatility_skip.py | Confirm configured volatile_confidence_floor and high_atr_pct are wired safely; defaults must remain reversible. | document existing support; no mutation |
| strategies/trend_following.py | Confirm volatile trend-following allowances and min_regime_confidence can be configured without changing semantics unexpectedly. | document candidate-d allowances; no mutation |
| strategies/registry.py | Confirm selection.min_action_confidence mapping and strategy order remain explicit and reversible. | document future change surface; no mutation |
| scripts/test_boundary_guardrails.py and strategy tests | Add/extend tests proving no execution leak, reversible defaults, and no StrategySignal-to-order mapping. | document required test suite; no runtime mutation |

## Approval Gate
No runtime/default implementation should happen without this explicit approval phrase:

> Approve Batch 3M runtime/default implementation for variant-d volatility-skip calibration.

## Rollback Plan for a Future Implementation Batch
- Restore prior volatility_skip HIGH_ATR_PCT/default high_atr_pct behavior.
- Restore volatile_confidence_floor behavior to prior default-equivalent behavior.
- Disable volatile trend-following allowances unless explicitly approved.
- Restore selection.min_action_confidence to prior default behavior.
- Keep volatile breakout disabled for production unless separately approved.
- Rerun Batch 4B evaluator, Batch 3J broader validation, and Batch 3K zero-block review after rollback.
- Confirm default volatile regime still skips and high ATR still skips via existing strategy tests.

## Monitoring Plan After Any Future Approved Change
- volatility_skip_direct_block_rate
- skip_during_trader_action_rate
- directional_strategy_coverage_rate
- hard_conflict_count: BUY|short and SELL|long
- selected_strategy_family_distribution
- volatile trend-following selected cases
- volatile breakout selected cases
- fallback_or_missing_state_count
- gate_status changes from Batch 4B evaluator

## Required Tests for Future Implementation Batch
- Default legacy behavior can still be restored.
- Default volatile regime still skips when calibration is not enabled.
- Default high ATR still skips when calibration is not enabled.
- Volatile breakout remains disabled for production unless explicitly approved.
- StrategySignal remains observational-only and is not mapped into orders.
- No runtime/execution/order imports leak into strategy/evaluation tooling.
- Config changes are isolated, explicit, and reversible.
- Batch 4B/3J/3K replay metrics can be regenerated after implementation.

## Variant E Decision
Variant E is not required before implementation based on current evidence, because Batch 3K gives a coherent explanation for variant-d zero-block behavior and found no hard conflicts.

However, Variant E remains a possible conservative compromise if Julius wants an additional replay-only review before runtime/default implementation.

Potential Variant E concept if requested later:

~~~yaml
volatility_skip:
  volatile_confidence_floor: 0.80
  high_atr_pct: 0.10
trend_following:
  allow_volatile_trend_up: true
  allow_volatile_trend_down: false
  min_regime_confidence: 0.55
selection:
  min_action_confidence: 0.55
breakout:
  allow_volatile: false
~~~

## Recommendation
- Outcome: Prepare Batch 3M only if Julius explicitly approves runtime/default implementation for variant-d.
- Reason: Batch 3K explains variant-d zero-block behavior without hard conflicts, but Batch 3L performs no runtime/default changes.
- Next batch: Batch 3M approval-gated runtime/default implementation for variant-d, only after explicit approval

## Decision Block

~~~text
Batch 3L Decision:
- Production change authorized: false
- Runtime/default config change performed: false
- Recommended implementation candidate: variant-d
- Stress-test candidate: variant-b
- Variant E required before implementation: false
- Future approval required: true
- Approval phrase: Approve Batch 3M runtime/default implementation for variant-d volatility-skip calibration.
- Next batch: Batch 3M — approval-gated runtime/default implementation, only if Julius explicitly approves
~~~
