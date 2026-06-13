# Phase 10A — Promotion Decisions

> **Companion to:** `bias-investigation.md`, `multi-symbol-comparison.md`
> **Date:** 2026-06-09

Per `docs/config-promotion-checklist.md`, every recommendation was evaluated against the 6 hard gates and 4 soft gates. Decisions are explicit and final.

---

## Combined 14d (1 recommendation)

### R001 (low, data_quality) — "Sweep not differentiating"

- **Verdict:** DEFER
- **Reason:** Methodological improvement only, not a signal config change. Widening the sweep grid would help future calibrations but does not affect live trading.
- **Action required:** None for live config. Note for Phase 11+ sweep grid improvement.
- **Promote to live?** NO

---

## BTCUSDT 14d (3 recommendations)

### R001 (high, data_quality) — "Sample size too small"

- **Verdict:** REJECT
- **Reason:** HG-2 fails (only 8 simulated trades). Per-symbol 14d is below the 30-trade threshold.
- **Action required:** None. Re-evaluate after 30d calibration.
- **Promote to live?** NO

### R003 (medium, data_quality) — "Best sweep config unreliable"

- **Verdict:** REJECT
- **Reason:** Sample size too small to trust sweep ranking.
- **Action required:** None.
- **Promote to live?** NO

### R002 (low, data_quality) — "Sweep not differentiating"

- **Verdict:** DEFER
- **Reason:** Same as combined R001.
- **Promote to live?** NO

---

## ETHUSDT 14d (2 recommendations)

### R002 (medium, data_quality) — "Best sweep config unreliable"

- **Verdict:** REJECT
- **Reason:** Sample size too small (10 trades, < 30).
- **Action required:** None.
- **Promote to live?** NO

### R001 (low, data_quality) — "Sweep not differentiating"

- **Verdict:** DEFER
- **Reason:** Methodological only.
- **Promote to live?** NO

---

## SOLUSDT 14d (3 recommendations)

### R001 (high, data_quality) — "Sample size too small"

- **Verdict:** REJECT
- **Reason:** HG-2 fails (only 8 simulated trades).
- **Action required:** None.
- **Promote to live?** NO

### R003 (medium, data_quality) — "Best sweep config unreliable"

- **Verdict:** REJECT
- **Reason:** Sample size too small (4 best-config trades).
- **Action required:** None.
- **Promote to live?** NO

### R002 (low, data_quality) — "Sweep not differentiating"

- **Verdict:** DEFER
- **Reason:** Methodological only.
- **Promote to live?** NO

---

## Summary

| Decision | Count | Items |
|---|---:|---|
| PROMOTE | 0 | — |
| DEFER (methodological) | 4 | Combined R001, BTC R002, ETH R001, SOL R002 |
| REJECT (sample too small) | 5 | BTC R001+R003, ETH R002, SOL R001+R003 |
| **Total evaluated** | **9** | |

**Net effect on live config: ZERO changes.** `config/default_params.yaml` remains at the calibrated Phase 6B baseline.

---

## What changes would be safe to consider next time

If a future calibration produces a rec that passes all hard gates, the safest candidates are:

| Config path | Risk | Reversibility |
|---|---|---|
| `analyst_weights.full.technical` (currently 0.75) | Low — already heavy | Trivial |
| `analyst_weights.direction_thresholds.hold_confidence_cap` (currently 0.55) | Low | Trivial |
| `position_manager.execution_mode` | Medium — affects live behavior | Trivial |
| `runtime.supervisor.mode` (currently monitor_only) | Medium — affects auto-restart | Trivial |
| `risk_manager.pyramiding` (currently conservative) | Medium-High | Trivial |

**Never promote without 30+ trades and a non-degraded replay variant baseline.**

---

## Action items

1. ✅ No config edits.
2. ✅ No deployment action.
3. 📅 Schedule next calibration for **2026-06-23** with `--days 30`.
4. 📝 Note sweep-grid improvement as future work (Phase 11+).
5. 🔄 Re-run multi-symbol comparison after next calibration.
