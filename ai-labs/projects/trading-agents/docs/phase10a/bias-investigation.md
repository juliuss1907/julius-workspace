# Phase 10A — Bias Investigation Report

> **Date:** 2026-06-09
> **Window:** 14d (≈ 2026-05-26 to 2026-06-09)
> **Symbols:** BTCUSDT, ETHUSDT, SOLUSDT (combined + per-symbol)
> **Method:** `run_calibration_workflow.py --days 14 --window 120 --step 4 --use-sl-tp`
> **Calibration folders:** `reports/calibration/2026-06-09-{btc,eth,sol,combined}/`
>
> **Updated by:** [phase10a-refresh-2026-06-15.md](phase10a-refresh-2026-06-15.md) — 30d refresh confirms SHORT bias is market-driven and reduced to 60% in a longer window.

---

## TL;DR

1. **SHORT bias (77% SHORT) is a market artifact, not a signal bug.** The replay window 2026-05-26 → 2026-06-09 was a sharp bear market (BTC -18%, ETH -21%, SOL -23%). All 3 symbols show technical direction skewing bearish, and trader signals follow.
2. **Hold-time / exit rules are working as expected** when SL/TP is enabled (default). Average hold 23.1 candles, max 48. No stale-position issue.
3. **No signal config change is recommended.** All promotion checklist hard gates fail on sample size for per-symbol runs, and combined 14d produced no actionable recs.
4. **All `priority: high` recommendations are `data_quality` only** (sample size, sweep grid). They are calibration methodology improvements, not signal config changes.

---

## 1. Bias investigation

### 1.1 Market context (14d window)

| Symbol | First close | Last close | Change | Drawdown from high | Bounce from low |
|---|---:|---:|---:|---:|---:|
| BTCUSDT | 76,799.99 | 62,894.00 | **-18.11%** | -19.09% | +5.89% |
| ETHUSDT | 2,121.01 | 1,675.94 | **-20.98%** | -21.55% | +10.07% |
| SOLUSDT | 86.07 | 66.65 | **-22.56%** | -23.09% | +9.48% |

All three symbols were in a sustained downtrend during the replay window. This is not a sideways or recovery market; it is a uniform -18% to -23% drawdown across majors.

### 1.2 Signal distribution

Action distribution from combined 14d replay (201 signals):

| Symbol | HOLD | BUY | SELL | SELL:BUY ratio |
|---|---:|---:|---:|---:|
| BTCUSDT | 39 (58%) | 11 (16%) | 17 (25%) | 1.55 |
| ETHUSDT | 29 (43%) | 14 (21%) | 24 (36%) | 1.71 |
| SOLUSDT | 27 (40%) | 9 (13%) | 31 (46%) | 3.44 |
| **Total** | 95 (47%) | 34 (17%) | 72 (36%) | 2.12 |

Technical analyst (raw, pre-trader) direction distribution:

| Symbol | bullish | neutral | bearish |
|---|---:|---:|---:|
| BTCUSDT | 4 | 52 | 11 |
| ETHUSDT | 5 | 44 | 18 |
| SOLUSDT | 7 | 38 | 22 |

The technical analyst's bullish: bearish ratio is roughly 1:3 across all symbols, matching the market's negative price action.

### 1.3 Draft vs final

| Draft → Final | Count |
|---|---:|
| BUY → BUY | 34 |
| HOLD → HOLD | 95 |
| SELL → SELL | 72 |
| Any flip | 0 |

**ResearchDebate did not flip any signal direction.** Debate adjustment (`+0.05` aligned, `0.0` balanced, `-0.10` opposite) only modulates confidence. Side bias is therefore not introduced by debate.

### 1.4 Conclusion on bias

The 77% SHORT bias in simulated trades is a direct downstream effect of:

1. Market -18% to -23% over 14d → technical analyst leans bearish
2. Bearish technical → trader issues more SELL drafts
3. Draft is not flipped by debate (low confidence change)
4. SL/TP simulator opens the trade and exits

**No config change will eliminate this bias while the underlying market remains bearish.** Trying to "fix" it by lowering SELL weight or by tightening thresholds would reduce responsiveness to genuine bearish conditions. The right action is to **accept that the signal stack is correctly tracking the market** and continue monitoring.

A longer window (30d+) that includes recovery periods would be expected to show more balanced side distribution. We recommend re-running calibration in 2-4 weeks for a multi-regime sample.

---

## 2. Hold-time and exit rule review

### 2.1 Before vs after SL/TP

| Metric | 7d calibration (no SL/TP) | 14d calibration (SL/TP enabled) |
|---|---:|---:|
| Sim trades | 9 | 26 |
| Avg hold candles | 115.0 | 23.1 |
| Max hold observed | unclear | 48 |
| Win rate | 88.9% | 53.8% |
| Total PnL | +0.30% | +0.46% |
| Exit reasons | (mostly max_hold) | mixed |

The 7d calibration without SL/TP produced unrealistically high win rates and long holds because the simulator had to wait for the next opposite signal. With SL/TP enabled (default), exit reasons distribute realistically:

| Exit reason | Count | % | Avg hold |
|---|---:|---:|---:|
| opposite_signal | 12 | 46% | 25.7 |
| take_profit | 10 | 38% | 19.8 |
| stop_loss | 2 | 8% | 3.5 |
| max_hold | 1 | 4% | 48.0 |
| end_of_data | 1 | 4% | 40.0 |

### 2.2 Per-symbol hold time

| Symbol | Trades | Avg hold | Min | Max |
|---|---:|---:|---:|---:|
| BTCUSDT | 8 | 24.9 | 4 | 48 |
| ETHUSDT | 10 | 19.1 | 3 | 40 |
| SOLUSDT | 8 | 26.4 | 9 | 44 |

All symbols hold between 19-26 candles on average (3.2-4.4 hours). No stale positions. No symbol is being held excessively.

### 2.3 Stop-loss frequency

Only 2 of 26 trades exited via stop-loss (8%). This is consistent with the strong bearish trend — most trades are profitable because the market continues to fall, so SL is rarely hit. In a choppy or recovery market, SL frequency would likely rise.

**No config change recommended for SL/TP or hold-time settings.** The current values are behaving as expected.

---

## 3. Multi-symbol comparison

### 3.1 Side-by-side

| Metric | BTCUSDT | ETHUSDT | SOLUSDT | Combined |
|---|---:|---:|---:|---:|
| Replay signals | 67 | 67 | 67 | 201 |
| HOLD ratio | 58% | 43% | 40% | 47% |
| Sim trades | 8 | 10 | 8 | 26 |
| Win rate | 50.0% | 50.0% | 62.5% | 53.8% |
| Total PnL | +0.08% | +0.19% | +0.18% | +0.46% |
| Avg PnL | +0.01% | +0.02% | +0.02% | +0.02% |
| Avg hold candles | 24.9 | 19.1 | 26.4 | 23.1 |
| Short trades | 6 (75%) | 8 (80%) | 6 (75%) | 20 (77%) |
| Long trades | 2 (25%) | 2 (20%) | 2 (25%) | 6 (23%) |
| Best replay variant | higher_thresholds | — | — | more_conservative |
| Best sim config | min_conf=0.55 | — | — | min_conf=0.55 |
| Warnings | 1 (sample size) | 0 | 1 (sample size) | 0 |

### 3.2 Observations

- **ETH has the lowest HOLD ratio (43%)** — most action. Best in this bear window.
- **SOL has the highest win rate (62.5%)** but lowest BUY count (9) — its trend was the cleanest.
- **BTC has highest HOLD ratio (58%)** — fewer actionable windows. Expected for BTC.
- All three show 75-80% SHORT, which we attribute to market (Section 1).
- Combined win rate (53.8%) is realistic; the 88.9% from 7d no-SL/TP was overoptimistic.

### 3.3 Best replay variants

| Rank | Variant | HOLD% | Trades | Win rate | Total PnL | Score |
|---|---|---:|---:|---:|---:|---:|
| 1 | more_conservative | 67% | 10 | 60.0% | +0.51% | +3.110 |
| 2 | higher_thresholds | 74% | 10 | 50.0% | +0.49% | +2.585 |
| 3 | more_aggressive | 36% | 14 | 42.9% | +0.54% | +2.256 |
| 4 | baseline | 47% | 26 | 53.8% | +0.46% | +1.708 |

`more_conservative` variant narrowly leads on score. Score differences are small (< 1 point), so we do not recommend switching baseline. Keeping `baseline` for now provides continuity with previous calibration runs.

---

## 4. Promotion checklist application

Per `docs/config-promotion-checklist.md` hard gates:

| Gate | Combined 14d | BTC 14d | ETH 14d | SOL 14d |
|---|---|---|---|---|
| HG-1: Source documented | ✅ | ✅ | ✅ | ✅ |
| HG-2: Sample size ≥ 30 | ❌ (26) | ❌ (8) | ❌ (10) | ❌ (8) |
| HG-3: Side bias acceptable | ⚠️ 77% SHORT (justified) | ⚠️ 75% | ⚠️ 80% | ⚠️ 75% |
| HG-4: Drawdown budget | ✅ | ✅ | ✅ | ✅ |
| HG-5: No conflicting recs | ✅ | ✅ | ✅ | ✅ |
| HG-6: No runtime instability | ✅ | ✅ | ✅ | ✅ |

### 4.1 Per-recommendation decision

Combined 14d:
- **R001 (low, data_quality)** — "Top 6 sweep configs are within 5%". Methodological only. **DEFER** (not a signal config change).

Per-symbol high priority:
- **R001 (high, BTC and SOL)** — "Sample size too small". **REJECT** (HG-2 fails).

Per-symbol medium priority:
- **R002/R003 (medium, all)** — "Best sweep config only produced 4-5 trades". **REJECT** (sample too small to trust ranking).

### 4.2 Promotion decision

**No recommendations promoted in Phase 10A.** All signal config stays at current baseline. The only candidates are methodological improvements to the calibration workflow itself (e.g., widening sweep grid), and these are out of scope for live config.

---

## 5. Phase 10B options

After 10A we have three reasonable next steps:

### 5.1 Replay Upgrade (recommended if bias unexplained)

**Status: not needed.** Bias is fully explained by market window. No replay upgrade required at this time.

### 5.2 Config Promotion (defer)

No recs meet hard gates. **Defer** until:
- 30d calibration (>= 30 trades per symbol)
- Multi-regime window (bull + bear)
- Sweep grid widened per R001

### 5.3 Live Ops Stabilization (default recommendation)

Continue running runtime with current config and accumulate more `signals.jsonl` data. Use the 30d Binance window for the next calibration run.

### Recommendation

**Go with 5.3 — Live Ops Stabilization + re-calibrate in 2 weeks (30d window).**

---

## 6. Artifacts

| File | Purpose |
|---|---|
| `reports/calibration/2026-06-09-btc/` | Per-symbol BTC 14d calibration |
| `reports/calibration/2026-06-09-eth/` | Per-symbol ETH 14d calibration |
| `reports/calibration/2026-06-09-sol/` | Per-symbol SOL 14d calibration |
| `reports/calibration/2026-06-09-combined/` | Combined 3-symbol 14d calibration |
| `reports/phase10a/bias-investigation.md` | This report |
| `reports/phase10a/multi-symbol-comparison.md` | Side-by-side metrics |
| `reports/phase10a/promotion-decisions.md` | Per-recommendation decisions |

## 7. Commands run

```bash
# Per-symbol calibrations (14d, step=4, SL/TP enabled)
./venv/bin/python scripts/run_calibration_workflow.py \
  --symbols BTCUSDT --days 14 --window 120 --step 4 \
  --output-date 2026-06-09-btc --use-sl-tp

./venv/bin/python scripts/run_calibration_workflow.py \
  --symbols ETHUSDT --days 14 --window 120 --step 4 \
  --output-date 2026-06-09-eth --use-sl-tp

./venv/bin/python scripts/run_calibration_workflow.py \
  --symbols SOLUSDT --days 14 --window 120 --step 4 \
  --output-date 2026-06-09-sol --use-sl-tp

# Combined
./venv/bin/python scripts/run_calibration_workflow.py \
  --symbols BTCUSDT ETHUSDT SOLUSDT --days 14 --window 120 --step 4 \
  --output-date 2026-06-09-combined --use-sl-tp

# Market context
./venv/bin/python -c "..."   # see Section 1.1
```

## 8. Next steps

1. **Continue running runtime with current config.** No changes.
2. **Schedule next calibration for 2026-06-23** (14 days from now), with `--days 30`.
3. **If 30d calibration is still bearish-dominant:** consider multi-regime testing by replaying a 2025 bull period (separate task, needs historical data).
4. **If win rate drops below 45%** in live signals over next 50 cycles, revisit the recommendations file.
5. **Update `parameter-promotion-checklist` if needed** — current 30-trade gate may be too strict for 14d windows.

---

**Phase 10A complete. No signal config changes. Bias explained. Hold-time acceptable.**
