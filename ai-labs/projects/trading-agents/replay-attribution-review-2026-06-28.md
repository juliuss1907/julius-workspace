# Replay Attribution Review — 2026-06-28

## Dataset
- Input: `logs/replay_signals.jsonl`
- Generated summary: `replay-attribution-summary-2026-06-28.md`
- Generated JSON: `replay-attribution-summary-2026-06-28.json`
- Total records: 72
- Records with `strategy_signal`: 0
- Records missing `strategy_signal`: 72
- Symbols: BTCUSDT (24), ETHUSDT (24), SOLUSDT (24)
- Timeframes: 1h (72)

## Key Findings
- The available replay dataset is usable JSONL, but it is legacy data from before Batch 3C attribution capture.
- Every record is missing top-level `strategy_signal`, so Batch 3E cannot yet evaluate strategy-layer behavior against TraderAgent outputs.
- The analyzer is functioning correctly: it detected 72 records and classified all 72 as missing strategy attribution.
- No strategy ID, strategy action, strategy family, market regime, alignment matrix, or volatility-skip metrics can be meaningfully interpreted from this dataset.

## Strategy Behavior
- Top strategy IDs: unavailable because `strategy_signal` is missing in all records.
- Action distribution: unavailable because `strategy_signal.action` is missing in all records.
- Strategy family distribution: unavailable.
- Market regime distribution from strategy attribution: unavailable.

## Trader vs Strategy Comparison
- Aligned: 0
- Conflicted: 0
- Neutral/observational: 0
- Missing: 72
- Interpretation: this is a data availability issue, not evidence that strategies failed or disagreed with TraderAgent.
- Because there are no strategy actions, no comparison should be used for tuning or execution decisions.

## Volatility Skip Review
- Count: 0
- Interpretation: no conclusion. The current replay file does not contain strategy attribution, so it cannot show whether `volatility-skip` would have blocked trades.

## Data Quality Issues
- `logs/replay_signals.jsonl` exists and has 72 valid JSONL records.
- The records appear to predate Batch 3C, so they do not include the new top-level `strategy_signal` field.
- This makes the file suitable for testing analyzer missing-data behavior, but not suitable for Batch 3E strategy review.

## Recommendation
- Continue observational-only strategy attribution.
- Generate a new bounded replay dataset using post-Batch-3C code before attempting strategy-vs-TraderAgent conclusions.
- Recommended bounded replay command, pending Julius approval:

```bash
timeout 180s ./venv/bin/python scripts/replay_signals.py \
  --symbols BTCUSDT ETHUSDT SOLUSDT \
  --days 7 \
  --window 120 \
  --step 24 \
  --output logs/replay_signals-batch3e.jsonl
```

- Then rerun analyzer on the new file:

```bash
./venv/bin/python scripts/analyze_replay_attribution.py \
  --input logs/replay_signals-batch3e.jsonl \
  --output replay-attribution-summary-2026-06-28.md \
  --json-output replay-attribution-summary-2026-06-28.json \
  --max-examples 10
```

- If that replay succeeds and contains `strategy_signal`, the next review can answer alignment/conflict, volatility-skip, and strategy distribution questions.
- If a bounded replay is not approved yet, the next batch should be **Batch 3F — Bounded Replay Dataset Generation** with explicit runtime/network limits.

## Non-Actions
- No execution logic changed.
- No strategy action was mapped to a trading action.
- No PnL/backtest metrics included.
- No `mean_reversion` implementation.
- No live trading or full replay was run in this batch.
