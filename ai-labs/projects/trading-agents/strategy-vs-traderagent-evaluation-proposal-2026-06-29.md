# Strategy-vs-TraderAgent Evaluation Proposal — Batch 4A

**Date:** 2026-06-29  
**Status:** Proposal / evaluation framework  
**Baseline:** Batch 3G replay attribution coverage expansion  
**North Star:** Evidence-driven trading intelligence, not autonomous gambling.

```text
Observe → Attribute → Replay → Compare → Review → Evaluate → Then maybe execute
```

---

## 1. Purpose

Batch 4A defines how the project should evaluate observational `StrategySignal` outputs against TraderAgent final actions before any threshold tuning, report influence, alert influence, or execution policy change is considered.

The strategy layer now produces auditable attribution during replay. Batch 3G proved that capture is robust across a bounded dataset. The next step is not to tune the strategy layer immediately. The next step is to define what evidence would make a strategy signal useful, safe, and worthy of greater influence.

---

## 2. Non-Goals

Batch 4A does **not** authorize or implement:

- Live trading.
- Order placement.
- Strategy-to-execution mapping.
- Changes to `FinalAnalysis.action` or TraderAgent action semantics.
- Runtime threshold tuning.
- Production config changes.
- PnL/backtest/equity metrics.
- `mean_reversion` implementation.
- Any strategy signal influence on execution authority.

This proposal is documentation-only. It defines evaluation standards and follow-up work.

---

## 3. Baseline Evidence: Batch 3G

Batch 3G generated a broader bounded replay dataset after strategy attribution was added to replay artifacts.

### Dataset

```text
Input: logs/replay_signals-batch3g-2026-06-28.jsonl
Symbols: BTCUSDT, ETHUSDT, SOLUSDT, ADAUSDT, XRPUSDT
Window: 30 days
Replay windows: 140
Timeframe: 1h
Records with top-level strategy_signal: 140/140
Records missing strategy_signal: 0/140
```

### Strategy distribution

| Strategy ID | Count | Share |
|---|---:|---:|
| volatility-skip | 126 | 90.0% |
| trend-following | 10 | 7.1% |
| breakout | 4 | 2.9% |

| Strategy action | Count | Share |
|---|---:|---:|
| skip | 80 | 57.1% |
| hold | 46 | 32.9% |
| short | 9 | 6.4% |
| long | 5 | 3.6% |

| Market regime | Count | Share |
|---|---:|---:|
| volatile | 80 | 57.1% |
| trend_down | 45 | 32.1% |
| trend_up | 15 | 10.7% |

### Trader-vs-strategy comparison

| Alignment class | Count | Share |
|---|---:|---:|
| aligned | 35 | 25.0% |
| neutral_or_observational | 105 | 75.0% |
| conflicted | 0 | 0.0% |
| missing | 0 | 0.0% |

Important action matrix:

| Pair | Count | Interpretation |
|---|---:|---|
| BUY\|long | 5 | aligned bullish |
| SELL\|short | 6 | aligned bearish |
| HOLD\|hold | 24 | aligned no-trade |
| BUY\|skip | 21 | TraderAgent directional, strategy refuses volatile conditions |
| SELL\|skip | 28 | TraderAgent directional, strategy refuses volatile conditions |
| BUY\|hold | 15 | TraderAgent bullish, strategy cautious |
| SELL\|hold | 7 | TraderAgent bearish, strategy cautious |
| HOLD\|skip | 31 | both effectively stay out |
| HOLD\|short | 3 | strategy directional, TraderAgent does not follow |

Core baseline observation:

```text
TraderAgent BUY/SELL while StrategySignal skip: 49/140 = 35.0%
```

---

## 4. Metric Definitions

These metrics should become the standard evaluation vocabulary for replay attribution reviews.

### 4.1 Attribution coverage

Measures whether replay artifacts contain usable top-level `strategy_signal`.

```text
records_with_strategy_signal / total_records
```

Batch 3G baseline:

```text
140 / 140 = 100%
```

Interpretation:

- 100% means attribution capture is reliable enough for evaluation.
- Anything below 100% should be treated as a data quality issue before behavior conclusions are drawn.

### 4.2 Alignment rate

Measures direct agreement between TraderAgent final action and StrategySignal action.

Aligned pairs:

```text
BUY + long
SELL + short
HOLD + hold
```

Batch 3G baseline:

```text
35 / 140 = 25.0%
```

Interpretation:

- Alignment does not prove profitability.
- It shows that when the strategy layer speaks directionally, it is not contradicting TraderAgent.
- Low alignment can be acceptable if neutral/observational cases are intentional caution.

### 4.3 Conflict rate

Measures hard directional disagreement.

Conflicted pairs:

```text
BUY + short
SELL + long
```

Batch 3G baseline:

```text
0 / 140 = 0.0%
```

Interpretation:

- A low conflict rate is necessary before StrategySignal can influence reports.
- Any non-zero conflict rate should be reviewed by symbol, regime, and strategy family.
- Conflict does not automatically mean StrategySignal is wrong, but it requires review.

### 4.4 Neutral / observational rate

Measures cases that are neither aligned nor conflicted.

Examples:

```text
BUY + skip
SELL + skip
BUY + hold
SELL + hold
HOLD + skip
HOLD + short
```

Batch 3G baseline:

```text
105 / 140 = 75.0%
```

Interpretation:

- High neutral rate means the strategy layer is conservative or observational.
- This is acceptable for the current architecture, but it limits immediate decision influence.
- Neutral cases should be decomposed into caution, abstention, and unresolved disagreement buckets.

### 4.5 Directional strategy coverage

Measures how often StrategySignal produces an actionable directional view.

```text
(strategy_action == long or short) / total_records
```

Batch 3G baseline:

```text
(5 long + 9 short) / 140 = 10.0%
```

Interpretation:

- Current directional coverage is low.
- Low directional coverage makes strategy influence sparse but potentially high precision.
- Before any influence policy is added, directional records need more sample size across market regimes.

### 4.6 Skip-during-TraderAgent-action rate

Measures how often TraderAgent takes a directional action while StrategySignal says `skip`.

```text
(BUY|skip + SELL|skip) / total_records
```

Batch 3G baseline:

```text
(21 + 28) / 140 = 35.0%
```

Interpretation:

- This is the key unresolved divergence.
- It may indicate useful caution during volatile markets.
- It may also indicate overblocking if TraderAgent directional calls would have performed well.
- Without PnL/backtest, this metric should trigger review, not tuning.

### 4.7 Volatility-skip direct block rate

Measures how often `volatility-skip` directly selects `skip`.

```text
volatility_skip_blocks / total_records
```

Batch 3G baseline:

```text
80 / 140 = 57.1%
```

Interpretation:

- The current strategy registry is dominated by volatility gating.
- Direct skip blocks are concentrated in `volatile` regimes.
- This may be correct risk avoidance, but it needs calibration evidence before policy changes.

### 4.8 Strategy-family diversity

Measures whether the registry is producing diverse strategy families or collapsing to a single gate.

Batch 3G baseline:

```text
volatility_skip: 126 / 140 = 90.0%
trend_following: 10 / 140 = 7.1%
breakout: 4 / 140 = 2.9%
```

Interpretation:

- Current diversity is low.
- This is acceptable for a conservative first strategy layer.
- It is not enough for broad strategy evaluation across market styles.

---

## 5. Interpretation of Batch 3G

### What is strong

1. **Attribution capture is robust.** Every replay record contains top-level `strategy_signal`.
2. **No hard conflicts were found.** StrategySignal never opposed TraderAgent directionally in 140 records.
3. **Directional signals align when they occur.** `BUY|long` and `SELL|short` appear, while `BUY|short` and `SELL|long` do not.
4. **The system remains observational.** StrategySignal attribution is recorded without changing downstream action semantics.

### What is unresolved

1. **Volatility-skip dominates.** 90% of records select `volatility-skip`.
2. **Directional coverage is low.** Only 10% of records produce `long` or `short`.
3. **TraderAgent often acts while strategy skips.** 35% of all windows are `BUY|skip` or `SELL|skip`.
4. **No PnL evidence exists.** We cannot yet know whether skip decisions avoid bad trades or miss good ones.

### Core question

The central question is not whether StrategySignal should execute trades. It should not.

The central question is:

> When StrategySignal disagrees observationally with TraderAgent, should it affect confidence, review priority, or alert labeling?

---

## 6. Approval Gates for Future Strategy Influence

Any future influence should be staged and explicit.

### Gate 1 — Report annotation only

Possible future influence:

- Add StrategySignal summary to reports.
- Label cases like `BUY|skip` as caution.
- Label aligned directional cases as confluence.

Minimum evidence before approval:

- 100% attribution coverage on current replay datasets.
- Clear metric report generated by a repeatable evaluator.
- Conflicts reviewed and explained if non-zero.
- Julius explicitly approves report annotation behavior.

### Gate 2 — Confidence modifier proposal

Possible future influence:

- Increase confidence when TraderAgent and StrategySignal align.
- Decrease confidence or add caution when TraderAgent acts while StrategySignal skips.

Minimum evidence before approval:

- Repeatable evaluation metrics across multiple replay windows.
- Directional strategy sample size large enough for review.
- Skip-during-action behavior understood by regime.
- No runtime execution changes.
- Julius explicitly approves confidence modifier design.

### Gate 3 — Alert policy proposal

Possible future influence:

- Change alert labels, severity, or review priority based on strategy confluence/divergence.

Minimum evidence before approval:

- Report annotation has been reviewed.
- False-positive/false-negative categories are documented.
- Alert policy is documented separately.
- Julius explicitly approves alert behavior.

### Gate 4 — Execution influence proposal

Possible future influence:

- StrategySignal contributes to execution gating or order policy.

Minimum evidence before approval:

- This is out of scope for Batch 4A.
- Requires separate planning, backtest/PnL design, risk approval, and Julius approval.
- No current artifact authorizes execution influence.

---

## 7. Proposal-Only Calibration Experiments

These experiments are candidates for future replay-only batches. They should not change production/runtime thresholds until evaluated.

### Experiment A — Lower volatility threshold variant

Question:

> Does reducing the ATR/close volatility gate increase directional coverage without creating conflicts?

Compare against Batch 3G:

- `volatility-skip` selection rate.
- direct skip rate.
- directional coverage.
- conflict rate.
- `BUY|skip` and `SELL|skip` counts.

### Experiment B — Trend-down exception for shorts

Question:

> Should strong downtrends allow short signals even when volatility is elevated?

Compare against Batch 3G:

- `SELL|short` increase.
- `SELL|skip` decrease.
- conflict rate.
- regime-specific behavior in `trend_down`.

### Experiment C — Trend-following confidence floor variant

Question:

> Are trend-following signals too rare because confidence thresholds are too strict?

Compare against Batch 3G:

- trend-following selection count.
- `long` and `short` count.
- alignment rate.
- neutral/observational rate.

### Experiment D — Breakout sensitivity variant

Question:

> Is breakout underrepresented because the breakout trigger is too conservative?

Compare against Batch 3G:

- breakout selection count.
- `long` and `short` count.
- conflict rate.
- symbol-specific breakout behavior.

---

## 8. Recommended Next Batch

Recommended next step:

```text
Batch 4B — Evaluation Metrics Implementation
```

Purpose:

- Implement a repeatable metrics extractor for replay attribution datasets.
- Produce a standardized evaluation report from JSONL/summary artifacts.
- Codify the metrics defined in this proposal.
- Keep strategy attribution observational-only.

Why Batch 4B before calibration:

- Calibration without standardized metrics risks threshold guessing.
- Batch 3G already exposes the key question: volatility-skip dominance.
- Batch 4B makes future calibration comparisons objective and repeatable.

Alternative follow-up after Batch 4B:

```text
Batch 3H — Volatility-Skip Calibration Review
```

Purpose:

- Run replay-only variants after metrics are standardized.
- Compare each variant against Batch 3G baseline.
- Decide whether threshold tuning deserves a separate approval request.

---

## 9. Decision Summary

Batch 3G proved that replay attribution is ready for evaluation.

Batch 4A establishes the evaluation framework:

- StrategySignal is valuable as evidence.
- StrategySignal is not execution authority.
- Current behavior is conservative, not conflicting.
- `volatility-skip` dominance is the main calibration question.
- Metrics must be standardized before threshold experiments.

Recommended path:

```text
Batch 4A proposal → Batch 4B metrics implementation → Batch 3H replay-only calibration review → possible confidence/report policy proposal
```

No strategy-to-execution path should be considered until much later and only with explicit approval.
