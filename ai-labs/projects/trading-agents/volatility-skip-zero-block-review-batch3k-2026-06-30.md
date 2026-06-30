# Batch 3K — Zero Volatility-Skip Block Review

## Executive Summary

- Mode: offline_replay_only
- Windows evaluated: 2
- Baseline direct volatility-skip blocks reviewed: 86
- Variants: variant-d, variant-b
- Production change authorized: false
- Implementation authorized: false
- Runtime/default config change performed: false
- Recommendation: Variant D zero-block behavior is mostly explained by the replay-only volatile confidence floor.

## Scope Boundary

No live trading, order placement, StrategySignal-to-order mapping, production config/default changes, or runtime semantic changes.

## Replay Windows

| Window | Source | Total records | Baseline direct blocks |
|---|---|---:|---:|
| replay_signals-batch3f-2026-06-28 | logs/replay_signals-batch3f-2026-06-28.jsonl | 15 | 6 |
| replay_signals-batch3g-2026-06-28 | logs/replay_signals-batch3g-2026-06-28.jsonl | 140 | 80 |

## Baseline Block Subset Distribution

| Window | Count |
|---|---:|
| replay_signals-batch3g-2026-06-28 | 80 |
| replay_signals-batch3f-2026-06-28 | 6 |

| Symbol | Count |
|---|---:|
| BTCUSDT | 21 |
| ETHUSDT | 18 |
| XRPUSDT | 17 |
| ADAUSDT | 16 |
| SOLUSDT | 14 |

| Trader Action | Count |
|---|---:|
| HOLD | 36 |
| SELL | 29 |
| BUY | 21 |

| Market Regime | Count |
|---|---:|
| volatile | 86 |

| Confidence Bucket | Count |
|---|---:|
| <0.50 | 0 |
| 0.50-0.75 | 86 |
| 0.75-0.95 | 0 |
| >=0.95 | 0 |
| unknown | 0 |

| ATR/Close Bucket | Count |
|---|---:|
| <8% | 86 |
| 8-10% | 0 |
| 10-12% | 0 |
| >=12% | 0 |
| unknown | 0 |

## Numeric State Summary

| Metric | Count | Min | Mean | Max |
|---|---:|---:|---:|---:|
| Market confidence | 86 | 0.5140427566785924 | 0.6004341504204822 | 0.6928509770373988 |
| ATR/close | 86 | 0.003722103202760044 | 0.009317054734339985 | 0.022421511272193065 |

## Candidate Behavior on Baseline-Blocked Subset

| Candidate | Direct blocks | Direct block rate | Hard conflicts | Hard conflict rate | Selected strategies | Selected actions |
|---|---:|---:|---:|---:|---|---|
| variant-d | 0 | 0.0% | 0 | 0.0% | volatility-skip:85, trend-following:1 | hold:85, short:1 |
| variant-b | 0 | 0.0% | 0 | 0.0% | volatility-skip:82, breakout:4 | hold:82, short:3, long:1 |

## Candidate Reason Categories

### variant-d

| Reason | Count |
|---|---:|
| atr_below_candidate_threshold | 86 |
| volatile_confidence_below_floor | 86 |
| lower_action_confidence_floor | 85 |
| trend_following_allowed_volatile | 1 |

### variant-b

| Reason | Count |
|---|---:|
| atr_below_candidate_threshold | 86 |
| volatile_confidence_below_floor | 86 |
| breakout_allowed_volatile | 4 |

## Interpretation

- A zero direct-block rate is acceptable only if explained by safe replay-only filters rather than unrestricted volatile entries.
- Variant D is safer than Variant B because it does not allow volatile breakout behavior.
- Variant B remains useful as a stress-test, not as a default production candidate.
- This review remains observational and does not authorize runtime/default calibration changes.

## Recommendation

- Outcome: Variant D zero-block behavior is mostly explained by the replay-only volatile confidence floor.
- Primary candidate: variant-d
- Secondary candidate: variant-b
- Zero-block explanation: {'variant-d_top_reasons': [('atr_below_candidate_threshold', 86), ('volatile_confidence_below_floor', 86), ('lower_action_confidence_floor', 85)], 'variant-b_top_reasons': [('atr_below_candidate_threshold', 86), ('volatile_confidence_below_floor', 86), ('breakout_allowed_volatile', 4)]}
- Confidence: medium
- Next step: Batch 3L — approval-gated implementation design or Variant E review, depending on Julius preference

## Decision Block

~~~text
Batch 3K Decision:
- Production change authorized: false
- Runtime/default config change: not performed
- Primary candidate: variant-d
- Secondary candidate: variant-b
- Zero-block explanation: {'variant-d_top_reasons': [('atr_below_candidate_threshold', 86), ('volatile_confidence_below_floor', 86), ('lower_action_confidence_floor', 85)], 'variant-b_top_reasons': [('atr_below_candidate_threshold', 86), ('volatile_confidence_below_floor', 86), ('breakout_allowed_volatile', 4)]}
- Confidence: medium
- Next batch: Batch 3L — approval-gated implementation design or Variant E review, depending on Julius preference
~~~
