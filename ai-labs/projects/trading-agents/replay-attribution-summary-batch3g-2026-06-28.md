# Replay Attribution Summary

## Overview
- Total records: 140
- Records with strategy_signal: 140
- Records missing strategy_signal: 0

## Strategy Decisions
| Strategy ID | Count |
|---|---:|
| volatility-skip | 126 |
| trend-following | 10 |
| breakout | 4 |

| Strategy Action | Count |
|---|---:|
| skip | 80 |
| hold | 46 |
| short | 9 |
| long | 5 |

| Strategy Family | Count |
|---|---:|
| volatility_skip | 126 |
| trend_following | 10 |
| breakout | 4 |

## Symbols and Timeframes
| Symbol | Count |
|---|---:|
| ADAUSDT | 28 |
| BTCUSDT | 28 |
| ETHUSDT | 28 |
| SOLUSDT | 28 |
| XRPUSDT | 28 |

| Timeframe | Count |
|---|---:|
| 1h | 140 |

## Market Regimes
| Regime | Count |
|---|---:|
| volatile | 80 |
| trend_down | 45 |
| trend_up | 15 |

## Trader vs Strategy Comparison
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

| Alignment Label | Count |
|---|---:|
| neutral_or_observational | 105 |
| aligned | 35 |
| conflicted | 0 |
| missing | 0 |

## Volatility Skip Blocks
- Count: 80

## Examples for Review
### Conflicts
- None

### Volatility Skips
- BTCUSDT 1h Trader=SELL Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure
- BTCUSDT 1h Trader=BUY Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure
- BTCUSDT 1h Trader=HOLD Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure
- BTCUSDT 1h Trader=SELL Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure
- BTCUSDT 1h Trader=BUY Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure
- BTCUSDT 1h Trader=BUY Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure
- BTCUSDT 1h Trader=BUY Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure
- BTCUSDT 1h Trader=BUY Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure
- BTCUSDT 1h Trader=BUY Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure
- BTCUSDT 1h Trader=HOLD Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure
- BTCUSDT 1h Trader=SELL Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure
- BTCUSDT 1h Trader=BUY Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure
- BTCUSDT 1h Trader=BUY Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure
- BTCUSDT 1h Trader=BUY Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure
- BTCUSDT 1h Trader=HOLD Strategy=volatility-skip:skip Confidence=0.6 Reason=Volatile regime — avoid new directional exposure

### Missing Strategy Signal
- None

## Notes
- StrategySignal is observational-only.
- This report does not change TraderAgent actions, sizing, risk, or execution.
- No PnL/backtest metrics are included in Batch 3D.
