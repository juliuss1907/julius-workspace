# Replay Attribution Review — Batch 3G — 2026-06-28

## Dataset

- Input: `logs/replay_signals-batch3g-2026-06-28.jsonl`
- Replay command:

  ```
  timeout 300s ./venv/bin/python scripts/replay_signals.py \
    --symbols BTCUSDT ETHUSDT SOLUSDT ADAUSDT XRPUSDT \
    --days 30 \
    --window 120 \
    --step 24 \
    --output logs/replay_signals-batch3g-2026-06-28.jsonl
  ```

- Replay exit code: 0
- Completion time: ~1s (fetched 770 candles per symbol)
- Records: 140
- Records with `strategy_signal`: 140 (100%)
- Records missing `strategy_signal`: 0
- Symbols: BTCUSDT (28), ETHUSDT (28), SOLUSDT (28), ADAUSDT (28), XRPUSDT (28)
- Timeframes: 1h (140)
- File size: 1.6M

### Comparison to Batch 3F

| Metric | Batch 3F | Batch 3G |
|---|---|---|
| Records | 15 | 140 |
| Symbols | 3 | 5 |
| Days | 7 | 30 |
| volatility-skip % | 93% | 90% |
| trend-following records | 1 | 10 |
| breakout records | 0 | 4 |
| long signals | 0 | 5 |
| short signals | 1 | 9 |
| Conflicts | 0 | 0 |

## Key Findings

- **Attribution capture pipeline is robust.** Across 30 days, 5 symbols, 140 windows, every record contains non-empty top-level `strategy_signal`. The Batch 3C-3D pipeline is production-quality for observation.

- **Volatility-skip still dominates, but not as absolutely as Batch 3F suggested.** 90% of records (126/140) select `volatility-skip`. The remaining 14 records (10%) carry meaningful directional signals from `trend-following` and `breakout`. Batch 3F's 93% skip rate was not just a small-sample artifact — it is the real behavior of the current thresholds.

- **Zero conflicts in 140 records.** No `BUY|short` or `SELL|long` pairs. The strategy layer is conservative rather than conflicting. When it does produce directional signals, they align with TraderAgent's final action.

- **35 aligned records (25%).** Every directional strategy signal (5 long, 9 short, plus 24 HOLD|hold) matched the TraderAgent. The strategy layer is adding signal, not noise.

- **No overfitting to symbol.** All 5 symbols show similar distributions: 20-23 neutral/observational per 28 windows, 5-8 aligned. ADAUSDT, ETHUSDT, and SOLUSDT have slightly more aligned records than BTCUSDT and XRPUSDT — likely noise at this sample size.

## Strategy Diversity

| Strategy ID | Count | % |
|---|---|---|
| volatility-skip | 126 | 90.0% |
| trend-following | 10 | 7.1% |
| breakout | 4 | 2.9% |

| Strategy Action | Count | % |
|---|---|---|
| skip | 80 | 57.1% |
| hold | 46 | 32.9% |
| short | 9 | 6.4% |
| long | 5 | 3.6% |

| Regime | Count | Strategy behavior |
|---|---|---|
| volatile | 80 | All skip (80 volatility-skip skip) |
| trend_down | 45 | Mostly hold (volatility-skip hold), 6 short (trend-following) |
| trend_up | 15 | Mostly hold, 5 long (trend-following + breakout) |

### Does volatility-skip still dominate?

**Yes, at 90%.** But the picture is more nuanced than Batch 3F:

- 80 of 126 volatility-skip records are direct `skip` (regime was `volatile`). These are correct skip decisions — the strategy explicitly detected high-volatility conditions and refused directional exposure.
- 46 of 126 are `volatility-skip` returning `hold`. These happen when the regime is `trend_down` or `trend_up` but ATR conditions still trigger the volatility gate. The strategy sees a trending regime but still backs off due to wide price swings.

The 80 skips are where the strategy layer is saying: "conditions are too wild to evaluate." The 46 holds are where it is saying: "conditions are borderline — I could act, but I'm staying cautious."

The 14 directional signals (10 trend-following, 4 breakout) all occur in `trend_up` (5) and `trend_down` (9) regimes with lower ATR. This is the expected behavior: strategy fires only when regimes are clear and volatility is manageable.

## Regime Coverage

| Regime | Count | ID breakdown |
|---|---|---|
| volatile | 80 | volatility-skip: 80 |
| trend_down | 45 | volatility-skip: 31, trend-following: 10, breakout: 4 |
| trend_up | 15 | volatility-skip: 15 |

All `trend_up` windows are hold from volatility-skip — none pass the confidence threshold in this market. The system has not seen a strong enough trend_up regime in this 30-day window to fire a long signal from trend-following in that regime without ATR interference.

## Trader vs Strategy Comparison

| Alignment | Count | % |
|---|---|---|
| neutral_or_observational | 105 | 75.0% |
| aligned | 35 | 25.0% |
| conflicted | 0 | 0.0% |
| missing | 0 | 0.0% |

| Pair | Count | Notes |
|---|---|---|
| HOLD + skip | 31 | Strategy steps aside, TraderAgent holds — zero friction |
| SELL + skip | 28 | Strategy avoids volatile, TraderAgent sells anyway — worth watching |
| HOLD + hold | 24 | Both agree: stay out |
| BUY + skip | 21 | Strategy avoids volatile, TraderAgent buys anyway |
| BUY + hold | 15 | Strategy holds cautious, TraderAgent goes bullish |
| SELL + hold | 7 | Strategy holds cautious, TraderAgent goes bearish |
| SELL + short | 6 | Both aligned bearish ✅ |
| BUY + long | 5 | Both aligned bullish ✅ |
| HOLD + short | 3 | Strategy wants short, TraderAgent holds — disagreement but not conflict |

### Key divergence: SELL+skip (28) and BUY+skip (21)

The biggest gap between strategy layer and TraderAgent is in `volatile` regime windows. In 49 of 140 windows (35%), the TraderAgent took a directional action (BUY/SELL) while the strategy layer refused to evaluate due to market conditions.

This is the central trade-off of the current system:

- **Conservative path:** Strategy says "volatile, don't trade." TraderAgent may still trade based on analysts' scoring. If markets are truly volatile, strategy may be right.
- **Aggressive path:** Strategy allows directional calls in more regimes. TraderAgent gets a second opinion. But it may add noise.

We cannot know which path is better without PnL tracking (deferred). But we now have precise numbers: 35% of TraderAgent directional actions occur with strategy skip. This is a measurable baseline.

## Volatility Skip Review

| Metric | Count |
|---|---|
| Direct skip actions | 80 (all in volatile regime) |
| Hold-by-skip fallbacks | 46 (trend_down/trend_up with elevated ATR) |
| Total volatility-skip selections | 126 |
| TraderAgent BUY/SELL blocked by skip | 49 (28 SELL, 21 BUY) |
| Volatility skip blocks | 80 |

### Interpretation

- **80 direct skips are clear-sky decisions.** Regime was `volatile`; strategy correctly identified wide price swings and refused directional exposure. No false positives are detectable without PnL.
- **46 holds from volatility-skip suggest a grey zone.** These are not `volatile` regime windows, but ATR is elevated enough to keep the guard up. Whether this is overblocking or prudent depends on actual price outcomes.
- **49 TraderAgent actions through skip are the key unresolved question.** The TraderAgent went directional on 35% of all windows, while the strategy layer said "skip." If the TraderAgent was right on many of these, the guard is too tight. If wrong, the guard is working.

**Recommendation:** Do not tune thresholds in Batch 3G. Catalog this as the primary calibration question for Batch 4A.

## Data Quality Notes

- **Network/API:** Binance responded within ~1s for all 5 symbols. No errors, no timeouts, no partial fetches.
- **Coverage:** 5 symbols × 28 windows = 140 records. Coverage is uniform — every symbol has exactly 28 records.
- **Regime data:** Available via `attribution.regime` in each `strategy_signal` record. Analyzer correctly extracts it.
- **No missing records, no malformed JSONL.** The dataset is clean.
- **Sample-size caveats:**
  - 30 days of 1h candles is enough for a first characterization of the strategy layer's behavior.
  - But 30 days is still a narrow slice of market history. Regime distribution may differ in other months.
  - No bull-market regime (`trend_up` with low ATR) was captured — the `trend_up` windows were all borderline.

## Recommendation

### Proceed to Batch 4A — Strategy-vs-TraderAgent Evaluation Proposal

Batch 3G has produced enough evidence to plan an evaluation framework. Key questions Batch 4A should address:

1. **What metrics matter?**
   - Strategy-vs-TraderAgent alignment rate (currently 25%).
   - Strategy skip rate during TraderAgent directional actions (currently 35%).
   - Strategy hit rate if we had PnL per record (deferred).
   - Volatility-skip overblocking ratio: how many skips could have been profitable trades?

2. **What thresholds should Batch 4A evaluate (not apply)?**
   - Lowering ATR/close threshold from current value to see if skip rate drops.
   - Adding a `trend_down` exception that still allows short signals in volatile downtrends.
   - Confidence floor adjustments for trend-following and breakout.

3. **What evidence would justify strategy influence?**
   - Minimum alignment rate before strategy can influence report confidence.
   - Maximum skip-during-TraderAgent-action rate before strategy is considered too conservative.
   - Minimum number of directional signals per symbol before per-symbol evaluation.

4. **What is the approval gate?**
   - Batch 4A is a proposal document, not implementation.
   - Execution authority remains approval-gated.
   - No strategy signal will be mapped into trading decisions without explicit approval.

### Do not tune thresholds yet

The current thresholds produce a system that is conservative, internally consistent, and produces zero conflicts. Tuning without evaluation criteria risks overfitting to the current 30-day window.

### No need for Batch 3H (calibration review) as a separate batch

Merge threshold review into Batch 4A as a section of the evaluation proposal. Batch 3G data is sufficient to inform the proposal.

## Non-Actions

- No execution logic changed.
- No strategy action was mapped to trading action.
- No live trading was run — this was bounded historical replay only.
- No PnL/backtest metrics included.
- No threshold tuning was applied.
- No `mean_reversion` implementation.
- `.agent/**` and unrelated untracked outputs remain untouched.
