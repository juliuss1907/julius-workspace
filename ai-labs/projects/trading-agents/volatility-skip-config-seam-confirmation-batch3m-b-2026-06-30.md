# Batch 3M-B — Authoritative Config Seam Confirmation

## Executive Summary

Batch 3M-B traces whether YAML strategy config is truly connected to runtime strategy selection. It is read-only and performs no runtime/default config mutation.

| Field | Value |
|---|---|
| Mode | read_only_authoritative_config_seam_confirmation |
| Production change authorized | false |
| Implementation authorized | false |
| Runtime/default config change performed | false |
| Authoritative config source | candidate_detected_but_not_proven |
| Runtime path confirmed | false |
| Replay path confirmed | true |
| Config-only implementation feasible | partial |
| Dead config risk | medium |

## Config Source Matrix

| File | Exists | Strategy surface detected | Reference count | Authoritative status |
|---|---|---|---:|---|
| config/default_params.yaml | true | true | 97 | candidate_source_needs_confirmation |
| config/thresholds.yaml | true | false | 22 | candidate_source_needs_confirmation |

## Runtime / Replay Path Trace

Static inspection confirms the strategy layer supports the required knobs and that replay tooling references strategy_config/build_strategy_signal. Runtime authoritative YAML pass-through is still not fully proven by static inspection alone.

### First strategy-flow references by file

| Path | Line | Text |
|---|---:|---|
| scripts/test_boundary_guardrails.py | 473 | code = _leak_code("from strategies.registry import StrategyRegistry", forbidden=_STRATEGY_EXEC_SUBSTR) |
| scripts/test_strategy_registry.py | 10 | from strategies.registry import StrategyRegistry |
| scripts/run_volatility_skip_calibration.py | 31 | from strategies.attribution import build_strategy_signal  # noqa: E402 |
| scripts/test_strategy_attribution.py | 9 | from strategies.attribution import build_strategy_signal, fallback_strategy_signal |
| scripts/run_volatility_skip_broader_validation.py | 132 | candidate_records = rebuild_replay_records(records, VARIANTS[candidate]["strategy_config"], source=f"batch3j:{candidate}") |
| scripts/test_volatility_skip_calibration.py | 16 | from strategies.registry import StrategyRegistry  # noqa: E402 |
| scripts/replay_signals.py | 25 | from strategies.attribution import build_strategy_signal |
| scripts/analyze_volatility_skip_zero_blocks.py | 118 | return VARIANTS[candidate]["strategy_config"] |
| scripts/test_analysis_runner.py | 484 | def test_strategy_registry_receives_nested_strategy_config(): |
| strategies/attribution.py | 11 | from strategies.registry import StrategyRegistry |
| strategies/registry.py | 26 | class StrategyRegistry: |
| strategies/__init__.py | 20 | from strategies.registry import StrategyRegistry |
| orchestration/analysis_runner.py | 27 | from strategies.attribution import build_strategy_signal |
| volatility-skip-runtime-readiness-batch3m-a-2026-06-30.json | 110 | "text": "from strategies.attribution import build_strategy_signal  # noqa: E402" |
| volatility-skip-runtime-readiness-batch3m-a-2026-06-30.md | 37 | / attribution_accepts_strategy_config / true / |
| docs/07-backtesting.md | 489 | strategy_config = load_yaml("config/active_strategy.yaml") |
| .hermes/plans/2026-06-26_110228-batch3-strategy-signal-integration-seam.md | 7 | **Architecture:** `TechnicalAnalyst` already produces `technical_state` and `market_state`; `StrategyRegistry` already selects one pure `StrategySignal`. Batch 3 adds a thin seam in `orchestration/analysis_runner.py`: extract the states from the technical anal |
| .hermes/plans/2026-06-26_144206-batch3b-strategy-attribution-surface.md | 7 | **Architecture:** Batch 3A already added the core orchestration seam: `TechnicalAnalyst` state → `StrategyRegistry` → serialized `StrategySignal` → `FinalAnalysis.metadata["strategy_signal"]`. Batch 3B should keep that as the single source of truth and only ex |
| .hermes/plans/opencode-strategy-layer-foundation-prompt.md | 218 | - `from strategies.registry import StrategyRegistry` must not leak execution modules. |
| .hermes/plans/2026-06-26_150825-batch3c-replay-strategy-attribution.md | 35 | _build_strategy_signal(technical_analysis: dict, strategy_config: Optional[Dict] = None) -> Dict |
| .hermes/plans/2026-06-16_opencode-strategy-layer-batch2-prompt.md | 149 | 2. Implement `StrategyRegistry`. |
| .hermes/plans/2026-06-29_095700-batch3h-volatility-skip-calibration-review.md | 334 | - Add a small calibration wrapper that passes explicit `strategy_config` to attribution, or |
| .hermes/plans/2026-06-16_120000-strategy-layer-foundation.md | 835 | code = _leak_code("from strategies.registry import StrategyRegistry") |

## Key Mapping Matrix

| Proposed key | Expected receiver | Code support confirmed | Runtime YAML source confirmed |
|---|---|---|---|
| volatility_skip.volatile_confidence_floor | VolatilitySkipStrategy | true | false |
| volatility_skip.high_atr_pct | VolatilitySkipStrategy | true | false |
| trend_following.allow_volatile_trend_up | TrendFollowingStrategy | true | false |
| trend_following.allow_volatile_trend_down | TrendFollowingStrategy | true | false |
| trend_following.min_regime_confidence | TrendFollowingStrategy | true | false |
| selection.min_action_confidence | StrategyRegistry | true | false |
| breakout.allow_volatile | BreakoutStrategy | true | false |

## Dead Config Risk Assessment

- YAML strategy-looking keys may be present but not necessarily consumed by runtime.
- Static scan found code support for knobs, but authoritative loader/pass-through still needs side-effect-free confirmation.

## Outcome

- Outcome B — strategy knobs are code-supported, but authoritative runtime YAML seam remains partially confirmed only.
- Next batch: Batch 3M-C or approved Batch 3M implementation should first confirm runtime loader behavior with a side-effect-free probe before mutating config.

## Boundary Confirmation

- No config/default file was edited.
- No strategy runtime code was edited.
- No variant-d patch was applied.
- No variant-b behavior was applied.
- Volatile breakout was not enabled.

## Decision Block

~~~text
Batch 3M-B Decision:
- Production change authorized: false
- Runtime/default config change performed: false
- Authoritative config source: candidate_detected_but_not_proven
- Runtime strategy config path confirmed: false
- Config-only implementation feasible: partial
- Dead config risk: medium
- Next batch: Batch 3M-C or approved Batch 3M implementation should first confirm runtime loader behavior with a side-effect-free probe before mutating config.
~~~
