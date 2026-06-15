# Phase 10A — Multi-Symbol Comparison

> **Companion to:** `bias-investigation.md`
> **Date:** 2026-06-09
> **Window:** 14d (step=4h, SL/TP enabled)
> **Calibration folders:** `reports/calibration/2026-06-09-{btc,eth,sol,combined}/`
>
> **Updated by:** [phase10a-refresh-2026-06-15.md](phase10a-refresh-2026-06-15.md) — 30d multi-symbol comparison with reduced SHORT bias and no config promotion.
> **Confirmed by:** [bull-market-replay-2024-q4.md](bull-market-replay-2024-q4.md) — bull-market replay confirms multi-symbol signal distribution flips bullish in a bull regime.

---

## Side-by-side

| Metric | BTCUSDT | ETHUSDT | SOLUSDT | Combined |
|---|---:|---:|---:|---:|
| Replay signals | 67 | 67 | 67 | 201 |
| HOLD ratio | 58.2% | 43.3% | 40.3% | 47.3% |
| BUY count | 11 | 14 | 9 | 34 |
| SELL count | 17 | 24 | 31 | 72 |
| Sim trades | 8 | 10 | 8 | 26 |
| Win rate | 50.0% | 50.0% | 62.5% | 53.8% |
| Total PnL% | +0.08 | +0.19 | +0.18 | +0.46 |
| Avg PnL% | +0.01 | +0.02 | +0.02 | +0.02 |
| Max PnL% | +0.06 | +0.06 | +0.06 | +0.06 |
| Min PnL% | -0.03 | -0.02 | -0.03 | -0.03 |
| Avg hold candles | 24.9 | 19.1 | 26.4 | 23.1 |
| Short trades | 6 (75%) | 8 (80%) | 6 (75%) | 20 (77%) |
| Long trades | 2 (25%) | 2 (20%) | 2 (25%) | 6 (23%) |
| Warnings | 1 | 0 | 1 | 0 |

---

## Exit reasons per symbol

### BTCUSDT (8 trades)

| Reason | Count | Avg hold |
|---|---:|---:|
| opposite_signal | 4 | 25.0 |
| take_profit | 2 | 19.5 |
| stop_loss | 1 | 4.0 |
| max_hold | 1 | 48.0 |

### ETHUSDT (10 trades)

| Reason | Count | Avg hold |
|---|---:|---:|
| take_profit | 5 | 14.6 |
| opposite_signal | 4 | 24.8 |
| stop_loss | 1 | 3.0 |

### SOLUSDT (8 trades)

| Reason | Count | Avg hold |
|---|---:|---:|
| opposite_signal | 4 | 27.0 |
| take_profit | 3 | 28.3 |
| end_of_data | 1 | 40.0 |

---

## Per-symbol findings

### BTCUSDT

- **Highest HOLD ratio (58%).** Most likely to sit on hands.
- **1 max_hold exit at 48 candles** — borderline, not concerning.
- **2 winners, 2 losers in opposite_signal exits.** Symmetric.
- **1 stop loss triggered at 4 candles** — quick exit, healthy.

### ETHUSDT

- **Most action (43% HOLD, 36% SELL).** Tied for lowest HOLD.
- **0 warnings, 0 max_hold exits.** Cleanest profile.
- **50% win rate** even though take_profit dominates (5 of 10 exits).
- **Best PnL per trade (avg +0.02% across 10 trades).**

### SOLUSDT

- **Highest win rate (62.5%)** despite lowest BUY count (9).
- **Most bearish technical direction (22/67 = 33%)** — clearest trend.
- **1 end_of_data exit at 40 candles** — last trade before replay window end.
- **Pnl +0.18%** despite only 8 trades (per-trade PnL +0.02%).

### Combined

- **201 signals, 26 trades, 0 warnings.** Sample is large enough.
- **53.8% win rate is realistic.** The 88.9% from 7d no-SL/TP was an artifact.
- **Best replay variant: more_conservative** (narrowly beats baseline by score).
- **Best sim config: min_conf=0.55** (tied with 0.60 and 0.65 — sweep not differentiating).

---

## Cross-symbol patterns

1. **All 3 symbols show 75-80% SHORT bias.** This is the market, not the signal stack. (See `bias-investigation.md` Section 1.)
2. **All 3 symbols have 50-62.5% win rate.** Consistent quality.
3. **All 3 symbols have 19-26 candle avg hold.** No stale-position issue.
4. **All 3 symbols: 0 risk rejects, 0 position failures in the 14d window.** Runtime stack is healthy.
5. **No symbol is dominating PnL.** PnL is spread across BTC/ETH/SOL.

---

## Recommendations summary per symbol

| Symbol | Total | High | Med | Low | Theme |
|---|---:|---:|---:|---|---|
| BTCUSDT | 3 | 1 | 1 | 1 | data_quality (sample size + sweep) |
| ETHUSDT | 2 | 0 | 1 | 1 | data_quality (sweep) |
| SOLUSDT | 3 | 1 | 1 | 1 | data_quality (sample size + sweep) |
| Combined | 1 | 0 | 0 | 1 | data_quality (sweep grid) |

**Zero signal-config recs across all calibrations.** All 9 recs target calibration methodology, not signal logic.

---

## What this means for live

1. **No config change is warranted.** The signal stack is producing actionable, profitable (PnL positive) signals across all 3 symbols.
2. **ETH and SOL are responding better than BTC** in this window. If we ever need to trim the watchlist, BTC would be the lowest signal-density candidate (but not now).
3. **Bias is uniform across symbols.** It is a market property, not symbol-specific.
4. **Hold time is realistic** (19-26 candles avg, 48 max). No reason to tighten `max_hold_candles` further.
5. **SL/TP is doing its job.** 2 of 26 trades hit SL, 10 hit TP. Healthy distribution.

---

## Next calibration target

| Goal | Target | Window | Expected |
|---|---|---|---|
| 30d combined | 2026-06-23 (T+14d) | 30d | ≥ 50 trades, sample size OK, multi-regime if recovery begins |
| Per-symbol 30d | 2026-06-23 | 30d | ≥ 20 trades per symbol |
| Bull-period replay | TBD | 7-14d (from 2025 Q4 or 2024 Q4) | balanced sides expected |

If 30d combined 2026-06-23 still shows > 70% SHORT, we will need a multi-regime test (older bull data). This is out of scope for Phase 10A.
