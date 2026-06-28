# Replay Attribution Summary

## Overview
- Total records: 15
- Records with strategy_signal: 15
- Records missing strategy_signal: 0

## Strategy Decisions
| Strategy ID | Count |
|---|---:|
| volatility-skip | 14 |
| trend-following | 1 |

| Strategy Action | Count |
|---|---:|
| hold | 8 |
| skip | 6 |
| short | 1 |

| Strategy Family | Count |
|---|---:|
| volatility_skip | 14 |
| trend_following | 1 |

## Symbols and Timeframes
| Symbol | Count |
|---|---:|
| BTCUSDT | 5 |
| ETHUSDT | 5 |
| SOLUSDT | 5 |

| Timeframe | Count |
|---|---:|
| 1h | 15 |

## Market Regimes
| Regime | Count |
|---|---:|
| trend_down | 8 |
| volatile | 6 |
| trend_up | 1 |

## Trader vs Strategy Comparison
| Trader Action + Strategy Action | Count |
|---|---:|
| HOLD|hold | 5 |
| HOLD|skip | 5 |
| BUY|hold | 3 |
| SELL|short | 1 |
| SELL|skip | 1 |

| Alignment Label | Count |
|---|---:|
| neutral_or_observational | 9 |
| aligned | 6 |
| conflicted | 0 |
| missing | 0 |

## Volatility Skip Blocks
- Count: 6

## Examples for Review
### Conflicts
- None

### Volatility Skips
- BTCUSDT 1h Trader=HOLD Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure
- BTCUSDT 1h Trader=HOLD Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure
- BTCUSDT 1h Trader=HOLD Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure
- ETHUSDT 1h Trader=HOLD Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure
- ETHUSDT 1h Trader=SELL Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure
- SOLUSDT 1h Trader=HOLD Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure

### Missing Strategy Signal
- None

## Notes
- StrategySignal is observational-only.
- This report does not change TraderAgent actions, sizing, risk, or execution.
- No PnL/backtest metrics are included in Batch 3D.
