# Batch 4A — Strategy-vs-TraderAgent Evaluation Proposal Plan

> **For Hermes / OpenCode:** This batch converts Batch 3G replay attribution evidence into a formal evaluation proposal. It is documentation-only and approval-gated: no execution mapping, no threshold tuning, no new replay generation, and no live trading.

**Goal:** Define the evaluation framework for comparing observational `StrategySignal` outputs against TraderAgent final actions, using Batch 3G as the baseline evidence, before any strategy influence, threshold tuning, or policy changes are considered.

**North Star:** Evidence-driven trading intelligence, not autonomous gambling.

```text
Observe → Attribute → Replay → Compare → Review → Evaluate → Then maybe execute
```

Batch 4A should answer: **What metrics, approval gates, and follow-up experiments are required before StrategySignal can influence reports, alerts, confidence, or execution policy?**

---

## Current Context

Repo:

```text
/home/julius/julius-workspace/ai-labs/projects/trading-agents
```

Completed replay attribution arc:

```text
97dcea3 feat(trading-agents): record strategy attribution in replay
9186e6a feat(trading-agents): add replay attribution analyzer
09ab91f docs(trading-agents): add replay attribution review
3e4c52c docs(trading-agents): add bounded replay attribution review
1ba2215 docs(trading-agents): expand replay attribution coverage
```

Batch 3G baseline artifacts:

```text
logs/replay_signals-batch3g-2026-06-28.jsonl
replay-attribution-summary-batch3g-2026-06-28.md
replay-attribution-summary-batch3g-2026-06-28.json
replay-attribution-review-batch3g-2026-06-28.md
```

Batch 3G baseline:

```text
total_records: 140
records_with_strategy_signal: 140
records_missing_strategy_signal: 0
strategy_ids: volatility-skip 126, trend-following 10, breakout 4
strategy_actions: skip 80, hold 46, short 9, long 5
market_regimes: volatile 80, trend_down 45, trend_up 15
trader_actions: SELL 41, HOLD 58, BUY 41
alignment: aligned 35, neutral_or_observational 105, conflicted 0, missing 0
```

Important divergence baseline:

```text
BUY|skip: 21
SELL|skip: 28
TraderAgent BUY/SELL while StrategySignal skip: 49/140 = 35%
```

---

## Hard Constraints

- Do **not** run live trading.
- Do **not** run new replay generation in Batch 4A.
- Do **not** change runtime code.
- Do **not** change strategy registry behavior.
- Do **not** change thresholds.
- Do **not** map strategy `long/short/hold/skip` into execution `BUY/SELL/HOLD`.
- Do **not** change `FinalAnalysis.action` or TraderAgent action semantics.
- Do **not** implement PnL/backtest/equity metrics in this batch.
- Do **not** implement `mean_reversion`.
- Do **not** add dependencies.
- Do **not** move code into `src/`.
- Do **not** touch `.agent/**` staged docs/renames.
- Do **not** touch unrelated untracked files: `ai-agent-trading-report.md`, `outputs/`, `researchs.md`.
- Use scoped staging/commit only. Never use `git add -A`.

---

## Design Decision

Batch 4A is a proposal/documentation batch.

It should produce one human-reviewable framework document:

```text
strategy-vs-traderagent-evaluation-proposal-2026-06-29.md
```

No JSON artifact is required for this batch unless Julius asks later. Machine-readable metrics can be implemented in Batch 4B.

---

## Deliverables

1. Plan file:

   ```text
   .hermes/plans/2026-06-29_084300-batch4a-strategy-vs-traderagent-evaluation-proposal.md
   ```

2. Proposal artifact:

   ```text
   strategy-vs-traderagent-evaluation-proposal-2026-06-29.md
   ```

3. Local commit only:

   ```text
   docs(trading-agents): add strategy evaluation proposal
   ```

---

## Proposal Content Requirements

The proposal must define:

1. Evaluation objective and non-goals.
2. Batch 3G baseline evidence.
3. Metric definitions:
   - attribution coverage
   - alignment rate
   - conflict rate
   - neutral/observational rate
   - directional strategy coverage
   - skip-during-TraderAgent-action rate
   - volatility-skip direct block rate
   - strategy-family diversity
4. Interpretation of Batch 3G metrics.
5. Approval gates for future strategy influence.
6. Proposal-only threshold/calibration experiments.
7. Follow-up recommendation.

---

## Evaluation Questions

Batch 4A should frame, not solve with runtime changes:

1. Is `volatility-skip` overblocking or correctly preventing bad trades?
2. Are `trend-following` and `breakout` too rare under current thresholds?
3. Are `BUY|skip` and `SELL|skip` warning signs or healthy caution?
4. What evidence is required before StrategySignal can affect report confidence?
5. What evidence is required before StrategySignal can affect alert labels?
6. What evidence is required before any execution influence is even proposed?

---

## Follow-up Decision Path

Recommended next batch after Batch 4A:

```text
Batch 4B — Evaluation Metrics Implementation
```

Purpose:

- Implement standardized metrics extraction from replay JSONL/summary artifacts.
- Produce repeatable evaluation reports against Batch 3G baseline.
- Keep observational-only boundaries intact.

Alternative later batch if metrics confirm skip dominance is the main blocker:

```text
Batch 3H — Volatility-Skip Calibration Review
```

Purpose:

- Run replay-only threshold variants.
- Compare skip rate, directional coverage, and conflicts against Batch 3G baseline.
- Do not change production/runtime thresholds.

---

## Validation

Because Batch 4A is documentation-only:

- Confirm only plan/proposal docs changed in this commit.
- Run `git diff --check` on the new docs.
- Confirm `.agent/**` staged work remains untouched and excluded from commit.
- Confirm protected untracked paths remain untouched.
- No replay, live trading, or dry-run smoke is required for this docs-only batch.
