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
| Alignment rate | 70/140 (50.0%) |
| Conflict rate | 0/140 (0.0%) |
| Neutral / observational rate | 70/140 (50.0%) |
| Directional strategy coverage | 18/140 (12.9%) |
| Skip during TraderAgent action | 0/140 (0.0%) |
| Volatility-skip direct block | 0/140 (0.0%) |

## Strategy Distribution

| Strategy ID | Count |
|---|---:|
| volatility-skip | 122 |
| trend-following | 10 |
| breakout | 8 |

### Strategy Action

| Strategy Action | Count |
|---|---:|
| hold | 122 |
| short | 12 |
| long | 6 |

### Strategy Family

| Strategy Family | Count |
|---|---:|
| volatility_skip | 122 |
| trend_following | 10 |
| breakout | 8 |

### Strategy Family Share

| Strategy Family | Share |
|---|---:|
| volatility_skip | 87.1% |
| trend_following | 7.1% |
| breakout | 5.7% |

### Market Regime

| Market Regime | Count |
|---|---:|
| volatile | 80 |
| trend_down | 45 |
| trend_up | 15 |

## Action Matrix

| Trader Action + Strategy Action | Count |
|---|---:|
| HOLD|hold | 55 |
| BUY|hold | 35 |
| SELL|hold | 32 |
| SELL|short | 9 |
| BUY|long | 6 |
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
