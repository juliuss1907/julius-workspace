# Batch 3I — Volatility-Skip Calibration Implementation Proposal Plan

> **For Hermes / OpenCode:** This batch is a proposal/review batch. It must not change live trading behavior, runtime defaults, execution semantics, order routing, or production thresholds. It turns Batch 3H evidence into an approval-gated implementation proposal.

**Goal:** Convert Batch 3H replay-only calibration evidence into a clear implementation proposal for future volatility-skip calibration, including candidate selection, risks, approval gates, rollback plan, and additional replay requirements.

**North Star:** Evidence-driven trading intelligence, not autonomous gambling.

```text
Observe → Attribute → Replay → Compare → Review → Propose → Approve → Then maybe implement
```

Batch 3I should answer: **Which volatility-skip calibration candidate, if any, deserves a future approval-gated implementation batch, and what safeguards must exist before runtime behavior changes?**

---

## Current Context

Repo:

```text
/home/julius/julius-workspace/ai-labs/projects/trading-agents
```

Relevant completed batches:

```text
cc9267e docs(trading-agents): add strategy evaluation proposal
c220ea5 feat(trading-agents): add strategy evaluation metrics
8e3a12a feat(trading-agents): add volatility skip calibration review
```

Key Batch 4B artifacts:

```text
strategy-vs-traderagent-evaluation-batch4b-2026-06-29.md
strategy-vs-traderagent-evaluation-batch4b-2026-06-29.json
scripts/evaluate_strategy_vs_trader.py
scripts/test_strategy_vs_trader_evaluator.py
```

Key Batch 3H artifacts:

```text
volatility-skip-calibration-review-batch3h-2026-06-29.md
volatility-skip-calibration-review-batch3h-2026-06-29.json
strategy-vs-traderagent-evaluation-batch3h-variant-a-2026-06-29.md/json
strategy-vs-traderagent-evaluation-batch3h-variant-b-2026-06-29.md/json
strategy-vs-traderagent-evaluation-batch3h-variant-c-2026-06-29.md/json
strategy-vs-traderagent-evaluation-batch3h-variant-d-2026-06-29.md/json
scripts/run_volatility_skip_calibration.py
scripts/test_volatility_skip_calibration.py
```

Batch 3H recommendation:

```text
Outcome A — Calibration looks promising
Promising variants: variant-b, variant-d
Next step: Batch 3I — Replay-Only Calibration Implementation Proposal
```

---

## Baseline Evidence

Batch 3G / Batch 4B baseline:

| Metric | Baseline |
|---|---:|
| total_records | 140 |
| attribution_coverage_rate | 100.0% |
| alignment_rate | 25.0% |
| conflict_rate | 0.0% |
| neutral_or_observational_rate | 75.0% |
| directional_strategy_coverage_rate | 10.0% |
| skip_during_trader_action_rate | 35.0% |
| volatility_skip_direct_block_rate | 57.1% |

Baseline action matrix highlights:

| Pair | Count |
|---|---:|
| BUY|skip | 21 |
| SELL|skip | 28 |
| BUY|long | 5 |
| SELL|short | 6 |
| BUY|short | 0 |
| SELL|long | 0 |

Baseline interpretation:

- Attribution is complete.
- Hard conflicts are absent.
- Directional strategy coverage is sparse.
- Volatility-skip dominates the strategy layer.
- TraderAgent often acts while StrategySignal skips.

---

## Batch 3H Evidence Summary

### Variant A — Mild volatility threshold relaxation

| Metric | Value | Delta vs Baseline |
|---|---:|---:|
| directional_strategy_coverage_rate | 10.0% | +0.0 pp |
| skip_during_trader_action_rate | 0.0% | -35.0 pp |
| volatility_skip_direct_block_rate | 0.0% | -57.1 pp |
| conflict_rate | 0.0% | +0.0 pp |

Status: **Not promising** because directional coverage did not improve.

### Variant B — Moderate relaxation stress test

| Metric | Value | Delta vs Baseline |
|---|---:|---:|
| directional_strategy_coverage_rate | 12.86% | +2.86 pp |
| skip_during_trader_action_rate | 0.0% | -35.0 pp |
| volatility_skip_direct_block_rate | 0.0% | -57.1 pp |
| conflict_rate | 0.0% | +0.0 pp |

Action highlights:

| Pair | Count |
|---|---:|
| BUY|long | 6 |
| SELL|short | 9 |
| BUY|skip | 0 |
| SELL|skip | 0 |
| BUY|short | 0 |
| SELL|long | 0 |

Status: **Promising, but aggressive.**

Why promising:

- Best directional coverage improvement.
- No hard conflicts.
- Higher alignment rate.

Why risky:

- Eliminates direct volatility-skip blocks entirely in the sample.
- Allows breakout in volatile replay context.
- May weaken the risk guard too aggressively for a first production candidate.

### Variant C — Trend-down short exception proposal test

| Metric | Value | Delta vs Baseline |
|---|---:|---:|
| directional_strategy_coverage_rate | 10.0% | +0.0 pp |
| skip_during_trader_action_rate | 0.0% | -35.0 pp |
| volatility_skip_direct_block_rate | 0.0% | -57.1 pp |
| conflict_rate | 0.0% | +0.0 pp |

Status: **Not promising** because directional coverage did not improve.

### Variant D — Trend-following confidence floor review

| Metric | Value | Delta vs Baseline |
|---|---:|---:|
| directional_strategy_coverage_rate | 10.71% | +0.71 pp |
| skip_during_trader_action_rate | 0.0% | -35.0 pp |
| volatility_skip_direct_block_rate | 0.0% | -57.1 pp |
| conflict_rate | 0.0% | +0.0 pp |

Action highlights:

| Pair | Count |
|---|---:|
| BUY|long | 5 |
| SELL|short | 7 |
| BUY|skip | 0 |
| SELL|skip | 0 |
| BUY|short | 0 |
| SELL|long | 0 |

Status: **Promising, more conservative than Variant B.**

Why promising:

- Improves directional coverage without conflicts.
- Changes fewer strategy assumptions than Variant B.
- Does not allow volatile breakout by default.

Why still risky:

- Also eliminates direct volatility-skip blocks entirely in this dataset.
- Improvement is modest.
- Needs broader replay validation before runtime adoption.

---

## Hard Constraints

Batch 3I must not:

- Run live trading.
- Place, submit, simulate-live, or execute orders.
- Map strategy `long/short/hold/skip` into execution `BUY/SELL/HOLD`.
- Change `FinalAnalysis.action` or TraderAgent action semantics.
- Change default runtime config behavior.
- Change production thresholds.
- Add PnL/backtest/equity metrics.
- Implement `mean_reversion`.
- Add dependencies.
- Move code into `src/`.
- Touch `.agent/**` staged docs/renames.
- Touch unrelated untracked files: `ai-agent-trading-report.md`, `outputs/`, `researchs.md`.
- Use `git add -A`.

Batch 3I may:

- Read existing Batch 4B and Batch 3H artifacts.
- Write proposal Markdown and JSON.
- Recommend a candidate for future approval.
- Define approval gates and rollback plan.
- Recommend additional replay validation.

---

## Design Decision

Batch 3I should be **docs/proposal only**.

Do not add new code unless a tiny generator is clearly worth it. Preferred deliverables are flat Markdown + JSON proposal artifacts. The current Batch 3H tooling is sufficient.

Rationale:

- Batch 3H already added replay-only knobs and comparison tooling.
- Batch 3I is a decision gate, not another calibration experiment.
- The suspicious drop of volatility-skip direct blocks to 0.0% needs human review before implementation.

---

## Proposed Recommendation Direction

Recommended stance:

```text
Primary candidate: Variant D
Secondary candidate: Variant B for stress testing only
Production runtime change authorized: false
Require broader replay validation before any runtime/default config change
```

Reasoning:

- Variant B has stronger metrics but is more aggressive.
- Variant B allows volatile breakout, which may compromise the risk guard.
- Variant D is less aggressive and closer to a cautious first candidate.
- Both promising variants reduce direct volatility-skip blocks to 0.0%, which is a red flag requiring broader validation.

Recommended decision:

```text
Do not implement production threshold changes yet.
Use Variant D as the leading candidate for a future replay-only validation batch.
Use Variant B only as an upper-bound stress case.
```

---

## Deliverables

Create:

```text
volatility-skip-calibration-implementation-proposal-batch3i-2026-06-29.md
volatility-skip-calibration-implementation-proposal-batch3i-2026-06-29.json
```

### Markdown proposal required sections

```text
# Volatility-Skip Calibration Implementation Proposal
## Executive Summary
## Baseline Problem
## Batch 3H Evidence
## Candidate Review
### Variant B
### Variant D
## Risk Assessment
## Proposed Candidate
## Approval Gates
## Rollback Plan
## Additional Replay Required
## Recommendation
## Scope Boundary
```

### JSON proposal shape

```json
{
  "batch": "3I",
  "proposal_type": "replay_only_calibration_implementation_proposal",
  "production_change_authorized": false,
  "requires_approval_before_runtime_change": true,
  "recommended_candidate": "variant-d",
  "secondary_candidate": "variant-b",
  "baseline": {},
  "candidate_evidence": {},
  "risk_assessment": [],
  "approval_gates": [],
  "rollback_plan": {},
  "additional_replay_required": {},
  "recommendation": {}
}
```

---

## Required Proposal Content

### 1. Executive summary

Must say clearly:

- Batch 3H found promising replay-only candidates.
- Variant D is recommended as the safer primary candidate.
- Variant B remains a stress-test / secondary candidate.
- No runtime behavior change is authorized.
- Broader replay validation is required before implementation.

### 2. Baseline problem

Must include:

- `volatility_skip_direct_block_rate = 57.1%`
- `skip_during_trader_action_rate = 35.0%`
- `directional_strategy_coverage_rate = 10.0%`
- `conflict_rate = 0.0%`

### 3. Candidate evidence

Must compare Variant B and Variant D:

| Metric | Baseline | Variant B | Variant D |
|---|---:|---:|---:|
| directional coverage | 10.0% | 12.86% | 10.71% |
| skip during action | 35.0% | 0.0% | 0.0% |
| volatility-skip block | 57.1% | 0.0% | 0.0% |
| conflict rate | 0.0% | 0.0% | 0.0% |

### 4. Risk assessment

Must include at least:

- Full suppression of volatility-skip direct blocks may be too aggressive.
- Single replay window may overfit a specific market period.
- Variant B allows volatile breakout and may weaken risk posture.
- Variant D has modest improvement and may not justify production change yet.
- No PnL evidence exists by design.
- StrategySignal remains observational-only.

### 5. Approval gates

Before any future runtime/default config change, require:

1. Broader multi-period replay dataset.
2. Same evaluator metrics on all windows.
3. Conflict rate remains 0.0% or every conflict is reviewed.
4. Directional coverage improves without eliminating all risk guard utility.
5. Julius explicitly approves runtime/default config change.
6. Rollback plan is documented and tested.
7. No live execution mapping is introduced.

### 6. Rollback plan

Future implementation must be rollbackable by:

- Reverting strategy config to current defaults.
- Disabling calibration config block.
- Re-running Batch 4B evaluator against new replay artifacts.
- Confirming baseline-like risk guard behavior returns.

### 7. Additional replay required

Recommend:

```text
At least 3–5 additional replay windows
Same symbols or broader symbol set
Different market regimes: trend_up, trend_down, volatile, ranging
Compare baseline, variant-d, variant-b, and possibly a new intermediate variant-e
```

### 8. Recommendation

Expected recommendation:

```text
Do not authorize production calibration yet.
Use Variant D as the primary candidate for broader replay validation.
Use Variant B as an aggressive upper-bound stress test only.
Consider designing Variant E as a middle-ground guard that reduces overblocking without taking volatility-skip direct blocks to 0.0%.
```

---

## Acceptance Criteria

Batch 3I is complete if:

- Proposal Markdown exists and contains all required sections.
- Proposal JSON exists and is machine-readable.
- JSON explicitly sets `production_change_authorized: false`.
- JSON explicitly sets `requires_approval_before_runtime_change: true`.
- Recommendation clearly names primary and secondary candidates.
- Risks and approval gates are explicit.
- Rollback plan is explicit.
- Additional replay requirement is explicit.
- No runtime behavior is changed.
- No production config defaults are changed.
- Protected/unrelated paths remain untouched.
- Validation commands pass.
- Scoped commit only.

---

## Validation Commands

Run targeted tests:

```bash
./venv/bin/python scripts/test_volatility_skip_calibration.py
./venv/bin/python scripts/test_strategy_vs_trader_evaluator.py
./venv/bin/python scripts/test_boundary_guardrails.py
```

Validate JSON artifact:

```bash
python -m json.tool volatility-skip-calibration-implementation-proposal-batch3i-2026-06-29.json >/tmp/batch3i-proposal.json
```

Optional extra tests:

```bash
./venv/bin/python scripts/test_strategy_registry.py
./venv/bin/python scripts/test_strategy_playbooks.py
```

Whitespace check:

```bash
git diff --check -- \
  volatility-skip-calibration-implementation-proposal-batch3i-2026-06-29.md \
  volatility-skip-calibration-implementation-proposal-batch3i-2026-06-29.json
```

---

## Commit

Commit locally only, with scoped files:

```text
docs(trading-agents): add volatility skip calibration proposal
```

Do not push unless Julius explicitly approves.

---

## Scope Boundary

Batch 3I is a proposal batch. It does not authorize trading changes.

No StrategySignal output may be used for orders, live execution, runtime action mapping, or production threshold changes in this batch.
