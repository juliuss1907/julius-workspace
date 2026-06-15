# Phase 10A Refresh — Longer Calibration + Bias Investigation

- **Date:** 2026-06-15
- **Window:** 30d (≈ 2026-05-16 to 2026-06-15)
- **Symbols:** BTCUSDT, ETHUSDT, SOLUSDT (combined + per-symbol)
- **Method:** `run_calibration_workflow.py --days 30 --window 120 --step 4 --use-sl-tp`
- **Calibration artifacts:**
  - `reports/calibration/2026-06-15-combined-30d/`
  - `reports/calibration/2026-06-15-btc-30d/`
  - `reports/calibration/2026-06-15-eth-30d/`
  - `reports/calibration/2026-06-15-sol-30d/`

---

## TL;DR

1. **SHORT bias is still present but materially reduced.** Combined 30d shows 60% SHORT trades (down from 77% in the 14d window). The 30d window includes a partial recovery/bounce, but all three symbols still end the period net negative.
2. **Bias is explained by market regime, not by signal logic.** BTC -14.6%, ETH -19.5%, SOL -16.3% over 30d, with drawdowns of -23.8%, -27.7%, and -29.2% respectively. Technical direction distribution matches price action.
3. **No draft→final flips occurred.** ResearchDebate modulates confidence only; it does not introduce directional bias.
4. **No config promotion is recommended.** The only recommendations are low-priority `data_quality` items (sweep grid not differentiating). BTC has a high-priority negative-expectancy warning, but it is per-symbol (22 trades) and explicitly counsels against live config changes.
5. **Thesis quality remains a calibration limitation.** Replay uses only the TechnicalAnalyst, so research theses are minimal (e.g., "Volatile market; RSI neutral"). This is a report-quality issue, not a trading-config issue.

---

## 1. Calibration setup

### Commands run

```bash
# Combined 30d calibration
./venv/bin/python scripts/run_calibration_workflow.py \
  --symbols BTCUSDT ETHUSDT SOLUSDT \
  --days 30 --window 120 --step 4 \
  --output-date 2026-06-15-combined-30d \
  --use-sl-tp

# Per-symbol 30d calibrations
./venv/bin/python scripts/run_calibration_workflow.py \
  --symbols BTCUSDT --days 30 --window 120 --step 4 \
  --output-date 2026-06-15-btc-30d --use-sl-tp

./venv/bin/python scripts/run_calibration_workflow.py \
  --symbols ETHUSDT --days 30 --window 120 --step 4 \
  --output-date 2026-06-15-eth-30d --use-sl-tp

./venv/bin/python scripts/run_calibration_workflow.py \
  --symbols SOLUSDT --days 30 --window 120 --step 4 \
  --output-date 2026-06-15-sol-30d --use-sl-tp
```

### Artifacts generated

| Artifact | Combined | BTC | ETH | SOL |
|---|---|---|---|---|
| `workflow-summary.md` | ✅ | ✅ | ✅ | ✅ |
| `backtest-dashboard.json` | ✅ | ✅ | ✅ | ✅ |
| `backtest-dashboard.md` | ✅ | ✅ | ✅ | ✅ |
| `parameter-recommendations.json` | ✅ | ✅ | ✅ | ✅ |
| `parameter-recommendations.md` | ✅ | ✅ | ✅ | ✅ |
| `simulation_summary.json` | ✅ | ✅ | ✅ | ✅ |
| `simulated_trades.jsonl` | ✅ | ✅ | ✅ | ✅ |
| `replay_signals.jsonl` | ✅ | ✅ | ✅ | ✅ |
| `replay_sweep_report.json/md` | ✅ | ✅ | ✅ | ✅ |
| `parameter_sweep_report.json/md` | ✅ | ✅ | ✅ | ✅ |

### Fallbacks

No fallbacks were needed. The full 30d combined run completed in under 30 seconds, and per-symbol runs completed in under 10 seconds each. No commands failed.

---

## 2. Market context

| Symbol | First close | Last close | Change | Drawdown from high | Bounce from low | Regime assessment |
|---|---|---:|---:|---:|---:|---|
| BTCUSDT | 77,029.40 | 65,812.01 | **-14.56%** | -23.81% | +10.80% | Bearish with late bounce; volatile |
| ETHUSDT | 2,137.52 | 1,719.82 | **-19.54%** | -27.70% | +11.08% | Deeper bearish trend; partial recovery |
| SOLUSDT | 85.26 | 71.36 | **-16.30%** | -29.20% | +15.60% | Sharpest drawdown, strongest bounce |

All three symbols were in a net bearish 30d window. However, the window includes a meaningful bounce from the lows (BTC +10.8%, ETH +11.1%, SOL +15.6%). This is why the combined SHORT bias dropped from 77% (14d) to 60% (30d): the later part of the 30d window was less one-directionally bearish.

The market context is sufficient to explain why SELL signals outnumber BUY signals. The signal stack is tracking the market, not fighting it.

---

## 3. Signal distribution

### Final action distribution

| Symbol | Signals | HOLD | BUY | SELL | SELL:BUY ratio |
|---|---|---:|---:|---:|---:|
| BTCUSDT | 163 | 74 (45.4%) | 40 (24.5%) | 49 (30.1%) | 1.23 |
| ETHUSDT | 163 | 60 (36.8%) | 41 (25.2%) | 62 (38.0%) | 1.51 |
| SOLUSDT | 163 | 63 (38.7%) | 39 (23.9%) | 61 (37.4%) | 1.56 |
| **Combined** | **489** | **197 (40.3%)** | **120 (24.5%)** | **172 (35.2%)** | **1.43** |

### Technical analyst direction distribution (raw, pre-trader)

| Symbol | bullish | neutral | bearish | bullish:bearish |
|---|---|---:|---:|---:|---:|
| BTCUSDT | 19 | 121 | 23 | 1:1.21 |
| ETHUSDT | 17 | 109 | 37 | 1:2.18 |
| SOLUSDT | 23 | 101 | 39 | 1:1.70 |

ETH has the most bearish raw technical skew (37 bearish vs 17 bullish), matching its steeper net decline. BTC is the most neutral-heavy, consistent with its lower volatility and smaller net decline.

### Draft vs final

For all symbols, draft direction equals final direction in 100% of signals:

| Symbol | Draft → Final | Count |
|---|---|---:|
| BTCUSDT | neutral → neutral | 74 |
| BTCUSDT | bearish → bearish | 49 |
| BTCUSDT | bullish → bullish | 40 |
| ETHUSDT | neutral → neutral | 60 |
| ETHUSDT | bearish → bearish | 62 |
| ETHUSDT | bullish → bullish | 41 |
| SOLUSDT | neutral → neutral | 63 |
| SOLUSDT | bearish → bearish | 61 |
| SOLUSDT | bullish → bullish | 39 |

**ResearchDebate did not flip any signal.** Confidence adjustments are small (typically 0.0 in balanced consensus). Side bias is not introduced by debate.

---

## 4. Confidence and thesis quality

### Average confidence by final action

| Symbol | HOLD | BUY | SELL |
|---|---:|---:|---:|
| BTCUSDT | 0.550 | 0.859 | 0.854 |
| ETHUSDT | 0.550 | 0.869 | 0.862 |
| SOLUSDT | 0.550 | 0.878 | 0.861 |

HOLD confidence is pinned at exactly 0.55 across all symbols. This is the `hold_confidence_cap` behavior: neutral-weighted scores are capped at the hold threshold. BUY/SELL confidence is high (~0.85–0.88), indicating the trader is decisive when it moves away from neutral.

### Observations

- **HOLD cap is working as designed.** The flat 0.55 across all HOLD signals is expected from the confidence-cap logic.
- **BUY/SELL confidence is high but not obviously inflated.** The spread between directional and HOLD confidence is wide (~0.30), which is useful for filtering.
- **Thesis quality is weak because replay only uses TechnicalAnalyst.** Example thesis: "Volatile market; RSI neutral (50.4)". Research debate cases are also minimal ("bear case not supported; main support: no decisive bearish evidence"). This is a calibration/reporting limitation, not a signal-config bug. The live runtime uses news, sentiment, fundamentals, and derivatives analysts, which would produce richer theses.

---

## 5. Trade simulation quality

### Per-symbol and combined summary

| Metric | BTCUSDT | ETHUSDT | SOLUSDT | Combined |
|---|---:|---:|---:|---:|
| Simulated trades | 22 | 24 | 19 | 65 |
| Wins / Losses / BE | 8 / 14 / 0 | 8 / 15 / 1 | 11 / 8 / 0 | 27 / 37 / 1 |
| Win rate | 36.4% | 33.3% | 57.9% | 41.5% |
| Total PnL% | -0.01% | +0.10% | +0.19% | +0.28% |
| Avg PnL% | -0.0003% | +0.004% | +0.010% | +0.004% |
| Avg hold candles | 22.9 | 20.1 | 27.7 | 23.3 |
| Max hold candles | ~48 | ~58 | ~40 | ~58 |
| Avg MAE% | -0.79% | -0.79% | -0.91% | -0.83% |
| Avg MFE% | +1.62% | +1.90% | +2.66% | +2.03% |

### Exit reason distribution

| Symbol | opposite_signal | take_profit | stop_loss | max_hold | end_of_data |
|---|---:|---:|---:|---:|---:|
| BTCUSDT | 16 | 2 | 1 | 2 | 1 |
| ETHUSDT | 17 | 4 | 2 | 0 | 1 |
| SOLUSDT | 13 | 4 | 0 | 1 | 1 |
| **Combined** | **46** | **10** | **3** | **3** | **3** |

### Observations

- **SL/TP behavior is healthy.** Only 3 of 65 trades (4.6%) hit stop-loss. Take-profit accounts for 10 exits (15.4%). Most exits are opposite-signal (70.8%), which is expected in a mean-reverting/choppy environment.
- **Avg hold is 20–28 candles (≈ 20–28 hours).** No stale-position issue. Max hold reaches 48–58 candles only occasionally.
- **SOL remains the cleanest trend follower** with the highest win rate (57.9%) and positive PnL.
- **BTC underperforms in this window** with slight negative PnL and the lowest win rate. This is consistent with BTC being the most neutral/least directional symbol in the raw technical distribution.
- **Combined PnL is positive but small (+0.28%).** Win rate (41.5%) is below the 50% naive expectation, but positive expectancy comes from asymmetric SL/TP (3% SL vs 6% TP) and trend-following shorts in a net bearish window.

---

## 6. Bias diagnosis

### Is there still SHORT bias?

Yes, but reduced:

| Window | SHORT trades | LONG trades | SHORT% |
|---|---:|---:|---:|
| 14d (2026-06-09) | 20 | 6 | 77% |
| 30d (2026-06-15) | 39 | 26 | 60% |

### Is it explained by market regime?

Yes. The 30d window is net bearish for all three symbols (BTC -14.6%, ETH -19.5%, SOL -16.3%). The technical analyst produces more bearish than bullish raw signals, and the trader follows that skew. The reduction from 77% to 60% SHORT aligns with the partial recovery/bounce included in the longer window.

### Is it uniform across symbols?

Fairly uniform in direction, but not in performance:

| Symbol | SHORT% | SHORT PnL | LONG PnL |
|---|---:|---:|---:|
| BTCUSDT | 59% | +0.033% | -0.039% |
| ETHUSDT | 62.5% | +0.112% | -0.015% |
| SOLUSDT | 58% | +0.175% | +0.018% |

All symbols are SHORT-skewed, but SOL and ETH shorts are profitable while BTC shorts only marginally offset long losses. BTC's weakness is symbol-specific within this window.

### Where is bias introduced?

| Layer | Effect |
|---|---|
| Technical analyst | Primary source — raw direction skew matches market |
| Trader synthesis | Follows technical; no independent flip |
| ResearchDebate | No flips; only small confidence adjustments |
| Risk manager | Not in replay path; simulation uses fixed SL/TP |
| Simulation | SL/TP and fees are symmetric; does not create bias |

### Is there any evidence of a code/config bug?

No. The signal distribution, confidence behavior, and trade outcomes are internally consistent. The only anomaly is the uniformly flat HOLD confidence (0.550), but this is expected from the `hold_confidence_cap` logic.

---

## 7. Promotion checklist

Per `docs/config-promotion-checklist.md` hard gates:

| Gate | Combined 30d | BTC 30d | ETH 30d | SOL 30d |
|---|---|---|---|---|
| HG-1: Source documented | ✅ | ✅ | ✅ | ✅ |
| HG-2: Sample size ≥ 30 | ✅ (65) | ❌ (22) | ❌ (24) | ❌ (19) |
| HG-3: Side bias acceptable | ⚠️ 60% SHORT (explained) | ⚠️ 59% | ⚠️ 62.5% | ⚠️ 58% |
| HG-4: Drawdown budget | ✅ | ✅ | ✅ | ✅ |
| HG-5: No conflicting recs | ✅ | ✅ | ✅ | ✅ |
| HG-6: No runtime instability | ✅ | ✅ | ✅ | ✅ |

### Per-recommendation decision

#### Combined 30d

- **R001 (low, data_quality)** — "Top 6 parameter sweep configs are within 5% of each other on score (+2.114). Sweep is not differentiating."
  - **Verdict:** DEFER
  - **Reason:** Methodological improvement only, not a signal config change.
  - **Promote to live?** NO

#### BTCUSDT 30d

- **R001 (high, thresholds)** — "Total PnL -0.01% across 22 simulated trades. Negative expectancy at current config."
  - **Verdict:** REJECT
  - **Reason:** HG-2 fails (22 trades < 30). The recommendation text itself says "Do not change live config on a single negative run." BTC also recovers in the combined run.
  - **Promote to live?** NO

- **R002 (low, data_quality)** — "Sweep not differentiating."
  - **Verdict:** DEFER
  - **Reason:** Methodological only.
  - **Promote to live?** NO

#### ETHUSDT 30d

- **R001 (low, data_quality)** — "Sweep not differentiating."
  - **Verdict:** DEFER
  - **Reason:** Methodological only.
  - **Promote to live?** NO

#### SOLUSDT 30d

- **R001 (low, data_quality)** — "Sweep not differentiating."
  - **Verdict:** DEFER
  - **Reason:** Methodological only.
  - **Promote to live?** NO

### Summary

| Decision | Count | Items |
|---|---:|---|
| PROMOTE | 0 | — |
| DEFER (methodological) | 4 | Combined R001, BTC R002, ETH R001, SOL R001 |
| REJECT (sample too small / negative single-symbol) | 1 | BTC R001 |
| **Total evaluated** | **5** | |

**Net effect on live config: ZERO changes.** `config/default_params.yaml` remains at the current baseline.

---

## 8. Decision

**NO CHANGE.**

Current baseline config remains in place. The 30d calibration confirms the previous 14d conclusion: the SHORT bias is a market-regime artifact, not a signal bug. The longer window reduces bias from 77% to 60% as the replay includes a partial recovery, but the overall window is still net bearish.

No recommendation passes all hard gates for promotion. The only high-priority item (BTC negative expectancy) explicitly counsels against live config changes and fails the sample-size gate.

---

## 9. Next steps

1. **Continue live ops with current config.** Accumulate more `signals.jsonl` data.
2. **Re-run calibration in 2–4 weeks** with a 30d+ window to capture a potential bull/recovery regime.
3. **Widen the sweep grid** as a methodology improvement (out of scope for live config):
   - Include `fee_pct`, `slippage_pct`, `stop_loss_pct`, or `take_profit_pct` in parameter sweep.
   - Current `min_confidence_values` grid `[0.55, 0.6, 0.65, 0.7, 0.75, 0.8]` produces identical scores because the replay only uses TechnicalAnalyst and confidence is either capped at 0.55 (HOLD) or high (~0.85) for directional signals.
4. **Consider a multi-regime replay** once enough bullish historical data is available (e.g., 2025 Q4 or 2024 Q4). This is the fastest way to verify that the signal stack can produce balanced BUY/SELL ratios in a bull market.
5. **Improve replay report tooling** to optionally include richer theses when running with full analyst stack, or clearly label replay as "technical-only" so thesis quality is not misinterpreted.
6. **Revisit BTC-specific behavior** if live BTC signals continue to underperform ETH/SOL over the next 50 cycles.

---

## 10. Commands run (copy-paste)

```bash
# Combined 30d
./venv/bin/python scripts/run_calibration_workflow.py \
  --symbols BTCUSDT ETHUSDT SOLUSDT \
  --days 30 --window 120 --step 4 \
  --output-date 2026-06-15-combined-30d \
  --use-sl-tp

# Per-symbol 30d
./venv/bin/python scripts/run_calibration_workflow.py \
  --symbols BTCUSDT --days 30 --window 120 --step 4 \
  --output-date 2026-06-15-btc-30d --use-sl-tp

./venv/bin/python scripts/run_calibration_workflow.py \
  --symbols ETHUSDT --days 30 --window 120 --step 4 \
  --output-date 2026-06-15-eth-30d --use-sl-tp

./venv/bin/python scripts/run_calibration_workflow.py \
  --symbols SOLUSDT --days 30 --window 120 --step 4 \
  --output-date 2026-06-15-sol-30d --use-sl-tp
```

---

**Phase 10A Refresh complete. No signal config changes. Bias remains market-driven. Hold current baseline.**
