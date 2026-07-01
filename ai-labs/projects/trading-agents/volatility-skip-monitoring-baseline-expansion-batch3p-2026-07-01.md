# Batch 3P — Broader Replay Monitoring Baseline Expansion

## Executive Summary

- Mode: broader_replay_monitoring_baseline_expansion
- Status: **watch**
- Included replay windows: **3**
- Total records: **227**
- Runtime/default config changed in Batch 3P: **false**
- Current config matches approved variant-d: **true**
- Hard conflicts: **0**
- Volatile breakout selected count: **0**
- Recommendation: Keep variant-d default config, maintain watch status, and collect broader fresh replay windows before further runtime expansion.

Batch 3P reused the Batch 3O monitoring runner with explicit expanded non-variant replay inputs. The runner output is wrapped here as the Batch 3P baseline-expansion report.

## Replay Inventory

### Included Inputs

- `logs/replay_signals-batch3f-2026-06-28.jsonl`
- `logs/replay_signals-batch3g-2026-06-28.jsonl`
- `logs/replay_signals.jsonl`

### Excluded Variant Artifacts

- `logs/replay_signals-batch3h-variant-a-2026-06-29.jsonl` — generated Batch 3H variant artifact; excluded to avoid variant bias / double counting.
- `logs/replay_signals-batch3h-variant-b-2026-06-29.jsonl` — generated Batch 3H variant artifact; excluded to avoid variant bias / double counting.
- `logs/replay_signals-batch3h-variant-c-2026-06-29.jsonl` — generated Batch 3H variant artifact; excluded to avoid variant bias / double counting.
- `logs/replay_signals-batch3h-variant-d-2026-06-29.jsonl` — generated Batch 3H variant artifact; excluded to avoid variant bias / double counting.

### Other Local Logs Not Selected

- `logs/replay_smoke.jsonl` — smoke artifact, not approved baseline replay window.
- `logs/signals.jsonl` — generic signal log, not approved replay window for this batch.
- `logs/simulated_trades.jsonl` — trade artifact, not replay signal baseline input.

## Current Config Verification

| Key | Expected | Actual | Matches |
|---|---|---|---|
| `breakout.allow_volatile` | `False` | `False` | true |
| `regime_strategy_order.volatile` | `['volatility_skip', 'trend_following', 'breakout']` | `['volatility_skip', 'trend_following', 'breakout']` | true |
| `selection.min_action_confidence` | `0.5` | `0.5` | true |
| `trend_following.allow_volatile_trend_down` | `True` | `True` | true |
| `trend_following.allow_volatile_trend_up` | `True` | `True` | true |
| `trend_following.min_regime_confidence` | `0.5` | `0.5` | true |
| `volatility_skip.high_atr_pct` | `0.1` | `0.1` | true |
| `volatility_skip.volatile_confidence_floor` | `0.75` | `0.75` | true |

## Batch 3O vs Batch 3P Comparison

| Metric | Batch 3O | Batch 3P | Delta |
|---|---:|---:|---:|
| total records | 155 | 227 | +72 |
| hard conflicts | 0 | 0 | +0 |
| volatile breakout selected | 0 | 0 | +0 |
| volatile trend-following selected | 1 | 1 | +0 |
| fallback/missing-state records | 0 | 72 | +72 |
| attribution coverage | 100.0% | 100.0% | +0.0% |
| directional strategy coverage | 10.3% | 7.0% | -3.3% |
| skip during TraderAgent action | 0.0% | 10.6% | +10.6% |
| volatility-skip direct block rate | 0.0% | 0.0% | +0.0% |

## Batch 3P Per-Window Summary

| Window | Records | Hard conflicts | Volatile trend-following | Volatile breakout | Vol-skip block rate | Directional rate | Fallback/missing-state |
|---|---:|---:|---:|---:|---:|---:|---:|
| replay_signals-batch3f-2026-06-28 | 15 | 0 | 0 | 0 | 0.0% | 6.7% | 0 |
| replay_signals-batch3g-2026-06-28 | 140 | 0 | 1 | 0 | 0.0% | 10.7% | 0 |
| replay_signals | 72 | 0 | 0 | 0 | 0.0% | 0.0% | 72 |

## Alerts

| Level | Metric | Message |
|---|---|---|
| watch | volatility_skip_direct_block_rate | Volatility-skip direct block rate is 0.0%; continue watching for over-relaxation. |
| watch | fallback_or_missing_state_count | Fallback or missing-state records were observed. |

## Interpretation

- Expanding from 155 to 227 records did **not** introduce hard conflicts.
- Volatile breakout selected count remains **0**, so the approved `breakout.allow_volatile: false` boundary is still respected.
- Volatile trend-following selected count remains low at **1**.
- The volatility-skip direct block rate remains **0.0%**, so the same watch condition remains active.
- The added `logs/replay_signals.jsonl` window contributes **72 fallback/missing-state records**, so it broadens sample size but is lower quality for strategy attribution than the Batch 3F/3G replay windows.

## Boundary Confirmation

- No runtime/default config changes were made by Batch 3P.
- No live trading, order placement, simulate-live execution, or StrategySignal-to-order mapping was introduced.
- TraderAgent / FinalAnalysis semantics were not changed.
- No PnL, backtest, or equity metrics were added.
- No dependencies were added.
- Raw replay logs were not modified and should not be staged/committed.

## Recommendation

- Outcome: Keep variant-d default config, maintain watch status, and collect broader fresh replay windows before further runtime expansion.
- Next batch: Batch 3Q — collect fresh non-variant replay windows across more symbols/regimes, or add a scheduled read-only monitoring cadence after Julius approval.

## Decision Block

```text
Batch 3P Decision:
- Runtime/default config change performed in Batch 3P: false
- Current config matches variant-d: true
- Expanded baseline records: 227
- Hard conflict count: 0
- Volatile breakout selected count: 0
- Volatility-skip direct block rate: 0.0%
- Monitoring status: watch
- Recommendation: Keep variant-d default config, maintain watch status, and collect broader fresh replay windows before further runtime expansion.
```
