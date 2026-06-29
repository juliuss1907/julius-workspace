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
| Alignment rate | 35/140 (25.0%) |
| Conflict rate | 0/140 (0.0%) |
| Neutral / observational rate | 105/140 (75.0%) |
| Directional strategy coverage | 14/140 (10.0%) |
| Skip during TraderAgent action | 49/140 (35.0%) |
| Volatility-skip direct block | 80/140 (57.1%) |

## Strategy Distribution

| Strategy ID | Count |
|---|---:|
| volatility-skip | 126 |
| trend-following | 10 |
| breakout | 4 |

### Strategy Action

| Strategy Action | Count |
|---|---:|
| skip | 80 |
| hold | 46 |
| short | 9 |
| long | 5 |

### Strategy Family

| Strategy Family | Count |
|---|---:|
| volatility_skip | 126 |
| trend_following | 10 |
| breakout | 4 |

### Strategy Family Share

| Strategy Family | Share |
|---|---:|
| volatility_skip | 90.0% |
| trend_following | 7.1% |
| breakout | 2.9% |

### Market Regime

| Market Regime | Count |
|---|---:|
| volatile | 80 |
| trend_down | 45 |
| trend_up | 15 |

## Action Matrix

| Trader Action + Strategy Action | Count |
|---|---:|
| HOLD|skip | 31 |
| SELL|skip | 28 |
| HOLD|hold | 24 |
| BUY|skip | 21 |
| BUY|hold | 15 |
| SELL|hold | 7 |
| SELL|short | 6 |
| BUY|long | 5 |
| HOLD|short | 3 |

## Gate Status

| Gate | Status | Message |
|---|---|---|
| attribution_ready | pass | All replay records include top-level strategy_signal. |
| conflict_review_ready | pass | No hard BUY|short or SELL|long conflicts detected. |
| directional_sample_insufficient | warn | Directional strategy sample is still sparse; collect more replay evidence before policy changes. |
| skip_calibration_needed | warn | TraderAgent often acts while StrategySignal skips; calibration review is needed before tuning. |
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
