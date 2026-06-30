# Batch 3M-A — Read-only Runtime Config Seam Audit + Dry-run Patch Proposal

## Executive Summary

This batch audits the runtime/config seam for a possible future Batch 3M implementation. It does not change runtime/default config and does not apply variant-d.

| Field | Value |
|---|---|
| Mode | read_only_runtime_config_seam_audit_and_dry_run_patch_proposal |
| Recommended candidate | variant-d |
| Stress-test candidate | variant-b only |
| Production change authorized | false |
| Implementation authorized | false |
| Runtime/default config change performed | false |
| Dry-run patch applied | false |
| Explicit approval still required | true |

## Evidence Recap
- batch3l_recommended_candidate: variant-d
- batch3l_variant_e_required: False
- batch3k_baseline_blocks_reviewed: 86
- batch3k_outcome: Variant D zero-block behavior is mostly explained by the replay-only volatile confidence floor.
- batch3j_windows: 2
- batch3j_outcome: Variant D remains the safer primary candidate for another review step.

## Strategy Code Support Audit

| Check | Result |
|---|---|
| volatility_skip_configurable_high_atr_pct | true |
| volatility_skip_configurable_confidence_floor | true |
| trend_following_allow_volatile_up | true |
| trend_following_allow_volatile_down | true |
| trend_following_min_regime_confidence | true |
| breakout_allow_volatile_config_exists | true |
| registry_selection_min_action_confidence | true |
| attribution_accepts_strategy_config | true |
| replay_signals_strategy_config_reference | true |
| run_paper_trading_strategy_config_reference | false |

Interpretation: strategy policy classes appear to support the main variant-d knobs, so a future implementation should prefer config-only changes if the runtime config seam is confirmed.

## YAML Config Surface Audit

### config/default_params.yaml
| Key | Present |
|---|---|
| volatility_skip | true |
| volatile_confidence_floor | false |
| high_atr_pct | true |
| trend_following | true |
| allow_volatile_trend_up | false |
| allow_volatile_trend_down | false |
| min_regime_confidence | false |
| selection | true |
| min_action_confidence | true |
| breakout | true |
| allow_volatile | false |
| strategy_config | false |
| strategies | true |

### config/thresholds.yaml
| Key | Present |
|---|---|
| volatility_skip | false |
| volatile_confidence_floor | false |
| high_atr_pct | false |
| trend_following | false |
| allow_volatile_trend_up | false |
| allow_volatile_trend_down | false |
| min_regime_confidence | false |
| selection | false |
| min_action_confidence | false |
| breakout | false |
| allow_volatile | false |
| strategy_config | false |
| strategies | false |

Interpretation: the exact authoritative YAML source and runtime pass-through still need confirmation before any mutation. This is the main reason no config was changed in 3M-A.

## Dry-run Patch Proposal — Not Applied

The following values are proposed only for a future explicitly approved implementation. They were not applied.

~~~yaml
volatility_skip:
  volatile_confidence_floor: 0.75
  high_atr_pct: 0.10
trend_following:
  allow_volatile_trend_up: true
  allow_volatile_trend_down: true
  min_regime_confidence: 0.50
selection:
  min_action_confidence: 0.50
breakout:
  allow_volatile: false
~~~

## Candidate Change Surface

| Path | Status | Risk |
|---|---|---|
| config/default_params.yaml or config/thresholds.yaml | needs exact authoritative source confirmation | Wrong YAML source may create dead config or unintended runtime behavior |
| strategies/volatility_skip.py | appears to support high_atr_pct and volatile_confidence_floor | Code change not preferred unless config support is incomplete |
| strategies/trend_following.py | appears to support volatile allowances and min_regime_confidence | Volatile trend-following must remain explicit and reversible |
| strategies/breakout.py | allow_volatile exists but must remain false | Accidentally applying variant-b behavior |
| strategies/registry.py | appears to support selection.min_action_confidence | Selection floor may alter all strategies if scoped incorrectly |

## Readiness Decision

| Check | Value |
|---|---|
| safe_to_implement_now | False |
| requires_explicit_batch3m_approval_phrase | True |
| strategy_knobs_supported_in_code | True |
| yaml_strategy_surface_detected | True |
| approval_phrase | Approve Batch 3M runtime/default implementation for variant-d volatility-skip calibration. |

## Stop Conditions
- No explicit approval phrase for Batch 3M runtime/default implementation.
- Authoritative runtime config source is not yet proven.
- Any implementation would require touching execution/order/trading/live paths.
- Volatile breakout would need to be enabled by default.
- Rollback path cannot be made simple and testable.

## Recommendation
- Outcome: Do not implement runtime/default changes yet. The next safe step is explicit approval plus final config seam confirmation before applying variant-d.
- Next batch: Batch 3M-B or Batch 3M implementation, only after explicit approval phrase and final config seam confirmation

## Decision Block

~~~text
Batch 3M-A Decision:
- Production change authorized: false
- Implementation authorized: false
- Runtime/default config change performed: false
- Dry-run patch applied: false
- Recommended candidate remains: variant-d
- Do not apply variant-b to production/default config
- Main blocker: explicit approval phrase and final authoritative config seam confirmation
- Required approval phrase: Approve Batch 3M runtime/default implementation for variant-d volatility-skip calibration.
~~~
