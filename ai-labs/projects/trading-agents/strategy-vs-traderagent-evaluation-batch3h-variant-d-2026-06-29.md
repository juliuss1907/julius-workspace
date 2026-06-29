# Strategy vs TraderAgent Evaluation

## Dataset

- Total records: 140
- Records with strategy_signal: 140
- Records missing strategy_signal: 0
- Evaluation mode: offline / replay-only
- StrategySignal remains observational-only; this report does not authorize execution.

## Core Metrics

| Metric | Value |
|---|---:|
| Attribution coverage | 140/140 (100.0%) |
| Alignment rate | 67/140 (47.9%) |
| Conflict rate | 0/140 (0.0%) |
| Neutral / observational rate | 73/140 (52.1%) |
| Directional strategy coverage | 15/140 (10.7%) |
| Skip during TraderAgent action | 0/140 (0.0%) |
| Volatility-skip direct block | 0/140 (0.0%) |

## Strategy Distribution

| Strategy ID | Count |
|---|---:|
| volatility-skip | 125 |
| trend-following | 11 |
| breakout | 4 |

### Strategy Action

| Strategy Action | Count |
|---|---:|
| hold | 125 |
| short | 10 |
| long | 5 |

### Strategy Family

| Strategy Family | Count |
|---|---:|
| volatility_skip | 125 |
| trend_following | 11 |
| breakout | 4 |

### Strategy Family Share

| Strategy Family | Share |
|---|---:|
| volatility_skip | 89.3% |
| trend_following | 7.9% |
| breakout | 2.9% |

### Market Regime

| Market Regime | Count |
|---|---:|
| volatile | 79 |
| trend_down | 46 |
| trend_up | 15 |

## Action Matrix

| Trader Action + Strategy Action | Count |
|---|---:|
| HOLD|hold | 55 |
| BUY|hold | 36 |
| SELL|hold | 34 |
| SELL|short | 7 |
| BUY|long | 5 |
| HOLD|short | 3 |

## Gate Status

| Gate | Status | Message |
|---|---|---|
| attribution_ready | pass | All replay records include top-level strategy_signal. |
| conflict_review_ready | pass | No hard BUY|short or SELL|long conflicts detected. |
| directional_sample_insufficient | warn | Directional strategy sample is still sparse; collect more replay evidence before policy changes. |
| skip_calibration_needed | pass | Skip-during-action rate is below first-review warning threshold. |
| execution_not_authorized | blocked | Evaluation tooling does not authorize live trading, order routing, or strategy-to-execution mapping. |

## Interpretation

- This evaluator is repeatable offline tooling for replay attribution artifacts.
- Aligned pairs are BUY|long, SELL|short, and HOLD|hold.
- Conflicted pairs are BUY|short and SELL|long.
- Neutral/observational pairs are review signals, not execution instructions.
- StrategySignal remains observational-only and must not be mapped into orders.

## Next Recommendation

- Recommended next batch: Batch 3H — Volatility-Skip Calibration Review
- Reason: Use repeatable Batch 4B metrics to compare replay-only calibration variants against the Batch 3G baseline before any threshold tuning.
