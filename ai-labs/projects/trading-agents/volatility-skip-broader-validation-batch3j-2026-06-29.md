# Batch 3J — Broader Replay Validation for Volatility-Skip Calibration

## Executive Summary

- Mode: offline_replay_only
- Windows evaluated: 2
- Candidates: baseline, variant-d, variant-b
- Production change authorized: false
- Implementation authorized: false
- Requires approval before runtime change: true
- Recommendation: Variant D remains the safer primary candidate for another review step.

## Scope Boundary

No live trading, order placement, StrategySignal-to-order mapping, production config/default changes, or runtime semantic changes.

## Replay Windows

| Window | Source | Records | Symbols | Regimes |
|---|---|---:|---|---|
| replay_signals-batch3f-2026-06-28 | logs/replay_signals-batch3f-2026-06-28.jsonl | 15 | BTCUSDT, ETHUSDT, SOLUSDT | trend_down:8, trend_up:1, volatile:6 |
| replay_signals-batch3g-2026-06-28 | logs/replay_signals-batch3g-2026-06-28.jsonl | 140 | ADAUSDT, BTCUSDT, ETHUSDT, SOLUSDT, XRPUSDT | trend_down:45, trend_up:15, volatile:80 |

## Aggregate Core Metrics

| Candidate | Metric | Mean | Min | Max | Range |
|---|---|---:|---:|---:|---:|
| baseline | attribution_coverage_rate | 100.0% | 100.0% | 100.0% | 0.0% |
| baseline | alignment_rate | 32.5% | 25.0% | 40.0% | 15.0% |
| baseline | conflict_rate | 0.0% | 0.0% | 0.0% | 0.0% |
| baseline | neutral_or_observational_rate | 67.5% | 60.0% | 75.0% | 15.0% |
| baseline | directional_strategy_coverage_rate | 8.3% | 6.7% | 10.0% | 3.3% |
| baseline | skip_during_trader_action_rate | 20.8% | 6.7% | 35.0% | 28.3% |
| baseline | volatility_skip_direct_block_rate | 48.6% | 40.0% | 57.1% | 17.1% |
| variant-d | attribution_coverage_rate | 100.0% | 100.0% | 100.0% | 0.0% |
| variant-d | alignment_rate | 60.6% | 47.9% | 73.3% | 25.5% |
| variant-d | conflict_rate | 0.0% | 0.0% | 0.0% | 0.0% |
| variant-d | neutral_or_observational_rate | 39.4% | 26.7% | 52.1% | 25.5% |
| variant-d | directional_strategy_coverage_rate | 8.7% | 6.7% | 10.7% | 4.0% |
| variant-d | skip_during_trader_action_rate | 0.0% | 0.0% | 0.0% | 0.0% |
| variant-d | volatility_skip_direct_block_rate | 0.0% | 0.0% | 0.0% | 0.0% |
| variant-b | attribution_coverage_rate | 100.0% | 100.0% | 100.0% | 0.0% |
| variant-b | alignment_rate | 61.7% | 50.0% | 73.3% | 23.3% |
| variant-b | conflict_rate | 0.0% | 0.0% | 0.0% | 0.0% |
| variant-b | neutral_or_observational_rate | 38.3% | 26.7% | 50.0% | 23.3% |
| variant-b | directional_strategy_coverage_rate | 9.8% | 6.7% | 12.9% | 6.2% |
| variant-b | skip_during_trader_action_rate | 0.0% | 0.0% | 0.0% | 0.0% |
| variant-b | volatility_skip_direct_block_rate | 0.0% | 0.0% | 0.0% | 0.0% |

## Per-Window Candidate Comparison

| Window | Candidate | Records | Align | Conflict | Directional | Skip During Action | Vol-Skip Block | BUY/skip | SELL/skip | BUY/long | SELL/short |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| replay_signals-batch3f-2026-06-28 | baseline | 15 | 40.0% | 0.0% | 6.7% | 6.7% | 40.0% | 0 | 1 | 0 | 1 |
| replay_signals-batch3f-2026-06-28 | variant-d | 15 | 73.3% | 0.0% | 6.7% | 0.0% | 0.0% | 0 | 0 | 0 | 1 |
| replay_signals-batch3f-2026-06-28 | variant-b | 15 | 73.3% | 0.0% | 6.7% | 0.0% | 0.0% | 0 | 0 | 0 | 1 |
| replay_signals-batch3g-2026-06-28 | baseline | 140 | 25.0% | 0.0% | 10.0% | 35.0% | 57.1% | 21 | 28 | 5 | 6 |
| replay_signals-batch3g-2026-06-28 | variant-d | 140 | 47.9% | 0.0% | 10.7% | 0.0% | 0.0% | 0 | 0 | 5 | 7 |
| replay_signals-batch3g-2026-06-28 | variant-b | 140 | 50.0% | 0.0% | 12.9% | 0.0% | 0.0% | 0 | 0 | 6 | 9 |

## Regression / Watch Flags

| Severity | Window | Candidate | Metric | Message |
|---|---|---|---|---|
| watch | replay_signals-batch3f-2026-06-28 | variant-d | volatility_skip_direct_block_rate | Volatility-skip direct block rate dropped to 0.0%; confirm de-overblocking rather than over-relaxation. |
| watch | replay_signals-batch3f-2026-06-28 | variant-b | volatility_skip_direct_block_rate | Volatility-skip direct block rate dropped to 0.0%; confirm de-overblocking rather than over-relaxation. |
| watch | replay_signals-batch3g-2026-06-28 | variant-d | volatility_skip_direct_block_rate | Volatility-skip direct block rate dropped to 0.0%; confirm de-overblocking rather than over-relaxation. |
| watch | replay_signals-batch3g-2026-06-28 | variant-b | volatility_skip_direct_block_rate | Volatility-skip direct block rate dropped to 0.0%; confirm de-overblocking rather than over-relaxation. |

## Variant Interpretation

- Variant D is treated as the safer primary candidate because it changes fewer assumptions than Variant B.
- Variant B remains an aggressive stress-test candidate because it allows volatile breakout replay behavior.
- A 0.0% volatility-skip direct block rate is not automatically good; it requires follow-up review for over-relaxation.
- These metrics remain observational and do not authorize production/default threshold changes.

## Recommendation

- Outcome: Variant D remains the safer primary candidate for another review step.
- Primary candidate: variant-d
- Secondary candidate: variant-b
- Confidence: medium
- Reason: Validated 2 replay-only variants across 2 windows / 155 records. Variant D directional mean delta=0.0036; Variant D skip-during-action mean delta=-0.2083.
- Next step: Batch 3K — targeted review of zero volatility-skip block behavior before runtime/default changes

## Decision Block

~~~text
Batch 3J Decision:
- Production change authorized: false
- Runtime/default config change: not performed
- Primary candidate: variant-d
- Secondary candidate: variant-b
- Confidence: medium
- Reason: Validated 2 replay-only variants across 2 windows / 155 records. Variant D directional mean delta=0.0036; Variant D skip-during-action mean delta=-0.2083.
- Next batch: Batch 3K — targeted review of zero volatility-skip block behavior before runtime/default changes
~~~
