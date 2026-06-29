# Volatility-Skip Calibration Review

## Baseline

- Total records: 140
- Source: Batch 3G replay + Batch 4B evaluator
- Scope: offline replay-only; production/runtime thresholds were not changed.

| Metric | Baseline |
|---|---:|
| attribution_coverage_rate | 100.0% |
| alignment_rate | 25.0% |
| conflict_rate | 0.0% |
| neutral_or_observational_rate | 75.0% |
| directional_strategy_coverage_rate | 10.0% |
| skip_during_trader_action_rate | 35.0% |
| volatility_skip_direct_block_rate | 57.1% |

## Variant Comparison

| Variant | Directional | Δ Directional | Skip During Action | Δ Skip During Action | Vol-Skip Block | Δ Vol-Skip Block | Conflict |
|---|---:|---:|---:|---:|---:|---:|---:|
| variant-a | 10.0% | 0.0% | 0.0% | -35.0% | 0.0% | -57.1% | 0.0% |
| variant-b | 12.9% | 2.9% | 0.0% | -35.0% | 0.0% | -57.1% | 0.0% |
| variant-c | 10.0% | 0.0% | 0.0% | -35.0% | 0.0% | -57.1% | 0.0% |
| variant-d | 10.7% | 0.7% | 0.0% | -35.0% | 0.0% | -57.1% | 0.0% |

## Acceptance Review

| Variant | Promising | BUY|skip | SELL|skip | BUY|long | SELL|short | BUY|short | SELL|long |
|---|---|---:|---:|---:|---:|---:|---:|
| variant-a | no | 0 | 0 | 5 | 6 | 0 | 0 |
| variant-b | yes | 0 | 0 | 6 | 9 | 0 | 0 |
| variant-c | no | 0 | 0 | 5 | 6 | 0 | 0 |
| variant-d | yes | 0 | 0 | 5 | 7 | 0 | 0 |

## Variant Notes

### variant-a

- Description: Mild volatility relaxation: only hard-skip volatile regimes at higher regime confidence; keep conservative ATR guard.
- Gate status: {'attribution_ready': 'pass', 'conflict_review_ready': 'pass', 'directional_sample_insufficient': 'warn', 'skip_calibration_needed': 'pass', 'execution_not_authorized': 'blocked'}

### variant-b

- Description: Moderate relaxation stress test: materially higher volatile confidence and ATR floors, with breakout allowed in volatile replay only.
- Gate status: {'attribution_ready': 'pass', 'conflict_review_ready': 'pass', 'directional_sample_insufficient': 'warn', 'skip_calibration_needed': 'pass', 'execution_not_authorized': 'blocked'}

### variant-c

- Description: Trend-down short exception: allow only volatile downtrends through trend-following after volatility guard relaxation.
- Gate status: {'attribution_ready': 'pass', 'conflict_review_ready': 'pass', 'directional_sample_insufficient': 'warn', 'skip_calibration_needed': 'pass', 'execution_not_authorized': 'blocked'}

### variant-d

- Description: Trend-following confidence floor review: lower replay-only trend/action floors without changing production defaults.
- Gate status: {'attribution_ready': 'pass', 'conflict_review_ready': 'pass', 'directional_sample_insufficient': 'warn', 'skip_calibration_needed': 'pass', 'execution_not_authorized': 'blocked'}

## Recommendation

- Outcome: Outcome A — Calibration looks promising
- Next step: Batch 3I — Replay-Only Calibration Implementation Proposal
- Reason: Promising variants: variant-b, variant-d.
- Boundary: production/runtime thresholds were not changed; no live trading or execution mapping was introduced.
