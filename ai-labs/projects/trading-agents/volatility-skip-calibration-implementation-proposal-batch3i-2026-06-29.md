# Volatility-Skip Calibration Implementation Proposal

## Executive Summary

Batch 3H found two promising replay-only volatility-skip calibration candidates: **variant-b** and **variant-d**. This Batch 3I proposal recommends **variant-d** as the safer primary candidate for broader validation and keeps **variant-b** as an aggressive stress-test candidate only.

No production/runtime change is authorized by this proposal.

Key decision:

- Primary candidate: variant-d
- Secondary candidate: variant-b
- Production change authorized: false
- Requires approval before runtime change: true
- Next recommended batch: Batch 3J - Broader Replay Validation for Volatility-Skip Calibration

The main caution is that both promising variants reduce direct volatility-skip blocks from **57.1%** to **0.0%** in the current sample. That may indicate useful de-overblocking, but it may also mean the risk guard has been relaxed too aggressively. Broader replay validation is required before any production/default config change.

---

## Baseline Problem

Batch 4B measured the Batch 3G baseline:

| Metric | Baseline |
|---|---:|
| Total records | 140 |
| Attribution coverage | 100.0% |
| Alignment rate | 25.0% |
| Conflict rate | 0.0% |
| Neutral / observational rate | 75.0% |
| Directional strategy coverage | 10.0% |
| Skip during TraderAgent action | 35.0% |
| Volatility-skip direct block | 57.1% |

Baseline action highlights:

| Pair | Count |
|---|---:|
| <code>BUY|skip</code> | 21 |
| <code>SELL|skip</code> | 28 |
| <code>BUY|long</code> | 5 |
| <code>SELL|short</code> | 6 |
| <code>BUY|short</code> | 0 |
| <code>SELL|long</code> | 0 |

Interpretation:

- Attribution coverage is ready.
- Hard conflicts are absent.
- Directional strategy coverage is sparse.
- Volatility-skip dominates the strategy layer.
- TraderAgent often acts while StrategySignal skips.

---

## Batch 3H Evidence

Batch 3H compared replay-only calibration variants against the Batch 3G / Batch 4B baseline.

| Metric | Baseline | Variant B | Variant D |
|---|---:|---:|---:|
| Directional coverage | 10.0% | 12.9% | 10.7% |
| Skip during action | 35.0% | 0.0% | 0.0% |
| Volatility-skip block | 57.1% | 0.0% | 0.0% |
| Conflict rate | 0.0% | 0.0% | 0.0% |
| Alignment rate | 25.0% | 50.0% | 47.9% |

Batch 3H outcome:

- Variant B: promising, but aggressive.
- Variant D: promising, more conservative.
- Variant A and C: not promising because directional coverage did not improve.

---

## Candidate Review

### Variant B

Variant B is the moderate relaxation stress test.

| Metric | Value | Delta vs Baseline |
|---|---:|---:|
| Directional coverage | 12.9% | 2.9% |
| Skip during action | 0.0% | -35.0% |
| Volatility-skip block | 0.0% | -57.1% |
| Conflict rate | 0.0% | 0.0% |

Action highlights:

| Pair | Count |
|---|---:|
| <code>BUY|long</code> | 6 |
| <code>SELL|short</code> | 9 |
| <code>BUY|skip</code> | 0 |
| <code>SELL|skip</code> | 0 |
| <code>BUY|short</code> | 0 |
| <code>SELL|long</code> | 0 |

Pros:

- Best directional coverage improvement.
- No hard conflicts.
- Highest alignment rate among reviewed candidates.

Risks:

- Eliminates direct volatility-skip blocks entirely in this sample.
- Allows breakout in volatile replay context.
- May weaken the risk guard too aggressively for first production adoption.

Decision: **Keep as secondary stress-test candidate only.**

### Variant D

Variant D is the trend-following confidence floor review candidate.

| Metric | Value | Delta vs Baseline |
|---|---:|---:|
| Directional coverage | 10.7% | 0.7% |
| Skip during action | 0.0% | -35.0% |
| Volatility-skip block | 0.0% | -57.1% |
| Conflict rate | 0.0% | 0.0% |

Action highlights:

| Pair | Count |
|---|---:|
| <code>BUY|long</code> | 5 |
| <code>SELL|short</code> | 7 |
| <code>BUY|skip</code> | 0 |
| <code>SELL|skip</code> | 0 |
| <code>BUY|short</code> | 0 |
| <code>SELL|long</code> | 0 |

Pros:

- Improves directional coverage without hard conflicts.
- Changes fewer assumptions than Variant B.
- Does not rely on allowing volatile breakout as the main improvement path.

Risks:

- Improvement is modest.
- Also eliminates direct volatility-skip blocks in this dataset.
- Needs broader replay evidence before any runtime/default config adoption.

Decision: **Use as primary candidate for broader replay validation.**

---

## Risk Assessment

1. **Full suppression of volatility-skip direct blocks may be too aggressive.** Both promising variants reduce volatility-skip direct block rate from 57.1% to 0.0%.
2. **Single replay window may overfit a specific market period.** Batch 3H used the Batch 3G replay window only.
3. **Variant B may weaken risk posture.** It allows breakout in volatile replay context and should remain a stress-test candidate.
4. **Variant D improvement is modest.** A +0.7 percentage-point directional coverage improvement may not justify runtime change by itself.
5. **No PnL evidence exists by design.** This proposal evaluates attribution quality, not profitability.
6. **StrategySignal remains observational-only.** No output from StrategySignal should be used to route orders or change TraderAgent action semantics.

---

## Proposed Candidate

Recommended candidate hierarchy:

1. Primary candidate: Variant D
2. Secondary candidate: Variant B as aggressive stress test
3. Potential new candidate: Variant E middle-ground guard

Variant E should be considered if broader replay confirms that Variant D and B eliminate too much volatility-skip utility. The Variant E hypothesis:

> Reduce overblocking while preserving non-zero volatility-skip direct block behavior across genuinely volatile windows.

---

## Approval Gates

Before any future runtime/default config change, require:

1. Broader multi-period replay dataset.
2. Batch 4B evaluator metrics on every additional replay window.
3. Conflict rate remains 0.0%, or every conflict is explicitly reviewed.
4. Directional coverage improves without eliminating all risk guard utility across windows.
5. Julius explicitly approves runtime/default config change.
6. Rollback plan is documented and tested.
7. No live execution mapping from StrategySignal to orders is introduced.

---

## Rollback Plan

Any future implementation must be rollbackable by:

1. Reverting strategy config to current defaults.
2. Disabling any calibration config block.
3. Re-running the Batch 4B evaluator against post-rollback replay artifacts.
4. Confirming baseline-like volatility guard behavior returns.
5. Preserving StrategySignal as observational-only unless separately approved.

Rollback triggers:

- Conflict rate rises materially.
- Volatility guard stops producing useful skip coverage across volatile windows.
- Runtime behavior diverges from approved observational-only scope.

---

## Additional Replay Required

Recommended validation before implementation:

| Requirement | Recommendation |
|---|---|
| Minimum windows | 3 |
| Preferred windows | 5 |
| Regimes | trend_up, trend_down, volatile, ranging |
| Candidates | baseline, variant-d, variant-b, possible variant-e |
| Metrics | Batch 4B evaluator metrics |

The next batch should validate whether Variant D remains safer across more windows and whether Variant B is too aggressive outside the Batch 3G sample.

---

## Recommendation

Do **not** authorize production calibration yet.

Use **Variant D** as the primary candidate for broader replay validation. Use **Variant B** as an aggressive upper-bound stress test only. Consider designing **Variant E** as a middle-ground guard if broader replay shows Variant D/B suppress volatility-skip direct blocks too completely.

Recommended next batch:

- Batch 3J - Broader Replay Validation for Volatility-Skip Calibration

---

## Scope Boundary

This Batch 3I proposal does not authorize trading changes.

No StrategySignal output may be used for orders, live execution, runtime action mapping, production threshold changes, or default config changes in this batch.
