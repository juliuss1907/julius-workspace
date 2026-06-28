# Replay Attribution Review — Batch 3F — 2026-06-28

## Dataset

- Input: `logs/replay_signals-batch3f-2026-06-28.jsonl`
- Replay command:

  ```
  timeout 180s ./venv/bin/python scripts/replay_signals.py \
    --symbols BTCUSDT ETHUSDT SOLUSDT \
    --days 7 \
    --window 120 \
    --step 24 \
    --output logs/replay_signals-batch3f-2026-06-28.jsonl
  ```

- Replay exit code: 0
- Records: 15
- Records with `strategy_signal`: 15 (100%)
- Records missing `strategy_signal`: 0
- Symbols: BTCUSDT (5), ETHUSDT (5), SOLUSDT (5)
- Timeframes: 1h (15)
- File size: 174K

## Key Findings

- **Post-Batch-3C attribution capture works.** Every one of the 15 bounded replay records includes a top-level non-empty `strategy_signal`. The Batch 3C wiring () is verified end-to-end.

- **Volatility-skip dominates overwhelmingly.** 14 of 15 records selected `volatility-skip`, and only 1 selected `trend-following`. This means the registry spends nearly all its time in the safety guard before any directional strategy even runs.

- **Zero conflicts.** No record shows a `BUY+short` or `SELL+long` mismatch. The system is currently biased conservative, so there is nothing to conflict with.

- **One notable `SELL+skip` case** (ETHUSDT, 2026-06-26): TraderAgent issued SELL while volatility-skip blocked strategy evaluation. This is exactly the kind of case Batch 3D should catch — it shows the strategy layer saying "too risky to decide" while the TraderAgent layer went ahead. Whether the TraderAgent was right or wrong is unknowable without PnL tracking (out of scope for now), but the divergence is documented.

- **Three `BUY+hold` cases** (SOLUSDT): Strategy held while TraderAgent bought. These are `neutral_or_observational` — the strategy layer saw conditions below its confidence threshold and deferred.

- **`HOLD+skip` cases** (5 records): Both layers effectively agreed to stay out, but via different mechanisms. TraderAgent said HOLD, strategy said skip (volatile regime). Low friction, no real disagreement.

## Strategy Behavior

| Metric | Distribution |
|---|---|
| Top strategy IDs | `volatility-skip` (14), `trend-following` (1) |
| Strategy actions | `hold` (8), `skip` (6), `short` (1) |
| Strategy families | `volatility_skip` (14), `trend_following` (1) |
| Market regimes | `trend_down` (8), `volatile` (6), `trend_up` (1) |

Interpretation:

- The `volatility-skip` gating strategy is very sensitive with current default thresholds. In the 7-day bounded window, it triggered on 14/15 windows.
- The one `trend-following` short signal came under `trend_down` regime — consistent with the strategy's design (short in downtrends).
- The `hold` actions (8 records) come from the registry's fallback when the selected strategy returns hold rather than skip, which happens when volatility-skip evaluates the regime as not-quite-volatile-enough but the registry still picks skip as the top strategy.

## Trader vs Strategy Comparison

| Alignment | Count | % |
|---|---|---|
| Aligned | 6 | 40% |
| Neutral/observational | 9 | 60% |
| Conflicted | 0 | 0% |
| Missing | 0 | 0% |

| Trader + Strategy | Count | Notes |
|---|---|---|
| HOLD + hold | 5 | Both layers agree: stay out |
| HOLD + skip | 5 | Strategy side-steps, TraderAgent holds — no friction |
| BUY + hold | 3 | SOLUSDT: strategy held, TraderAgent bought |
| SELL + short | 1 | ETHUSDT: both aligned bearish |
| SELL + skip | 1 | ETHUSDT: strategy skipped volatile, TraderAgent sold |

## Volatility Skip Review

- **Count:** 6 direct skip actions, plus 8 hold-from-skip-fallback.
- **Interpretation:** The volatility-skip guardrail is the dominant signal in this 7-day window. It correctly detected volatile/trending-down conditions and refused directional exposure.
- **SELL+skip case (ETHUSDT):** Strategy said the regime was too volatile for a directional call; TraderAgent went SELL anyway. This is worth watching — if volatility-skip tends to block during profitable SELLs in a downtrend, the gate may be too conservative. Conversely, if the TraderAgent SELL turned out poorly, the skip was right. Either way: needs PnL tracking (deferred to later batch) to evaluate.
- **Recommendation:** Consider lowering the volatility threshold slightly or adding a `trend_down` exception that still allows short signals during volatile downtrends. But do not tune without broader replay coverage first.

## Data Quality Notes

- **Network/API:** No issues. Binance responded within timeout.
- **Sample size:** 15 records across 3 symbols × 5 daily windows is small. The findings are directional, not statistically robust.
- **Missing legacy comparison:** The old `logs/replay_signals.jsonl` (72 records, legacy) has no `strategy_signal` and cannot be used for direct before/after comparison.
- **Partial replay caveat:** None — all 15 records wrote cleanly.

## Recommendation

### Continue observational

The attribution capture pipeline works correctly. Batch 3F proved that:

1. Post-Batch-3C replay writes `strategy_signal` into every record.
2. The Batch 3D analyzer produces clean, readable summaries.
3. The alignment matrix can detect and classify TraderAgent-vs-StrategySignal relationships.

### Before Batch 4A (evaluation proposal), consider Batch 3G

The 15-record sample is too small and too skip-dominated to draw strong conclusions for an evaluation proposal. Recommend:

- **Expand replay coverage** to 30 days across 5 symbols (add ADAUSDT, XRPUSDT) with the same window/step.
- **Slice by regime** in the analyzer so the review can answer: "Does strategy behave differently in trending vs ranging vs volatile conditions?"
- **Tune volatility-skip thresholds** only after broader coverage confirms skip dominance persists across multiple market conditions.

Tuning boundaries without broader data risks solving for the last 7 days instead of the general case.

### Batch 4A should wait until:

- At least 50+ attribution records with meaningful strategy ID diversity (not just `volatility-skip`).
- Clear alignment and conflict patterns emerge that can justify an evaluation proposal.

## Non-Actions

- No execution logic changed.
- No strategy action was mapped to trading action.
- No live trading was run — this was bounded historical replay only.
- No PnL/backtest metrics included.
- No `mean_reversion` implementation.
- `.agent/**` and unrelated untracked outputs remain untouched.
