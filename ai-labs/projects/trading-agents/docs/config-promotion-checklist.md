# Config Promotion Checklist

> **Scope:** Mandatory steps before applying ANY change to `config/default_params.yaml` that affects live trading behavior.
> **Audience:** Operator (Julius) when reviewing `parameter-recommendations.md` or proposing manual tweaks.
> **Last updated:** 2026-06-09

---

## Why this exists

Phase 7A produces parameter recommendations. Phase 8B produces dynamic watchlist proposals. Both default to **`manual_review_required`** and never auto-apply. This checklist enforces the review gate.

A change is "promotable" only if **all** hard gates pass and the soft gates are explicitly acknowledged.

---

## Hard gates (must pass — fail = do not promote)

### HG-1: Source is documented

- [ ] Change originates from one of:
  - `reports/parameter-recommendations.md` (with `priority: high` or `medium`)
  - Manual hypothesis with written justification
  - Quoted `apply_status: manual_review_required` evidence
- [ ] If from recommendation: the `config_path`, `current_value`, `suggested_value` fields are read and understood.

### HG-2: Sample size adequate

For weight/threshold changes:
- [ ] Source calibration used `--days >= 7` and produced `>= 30` simulated trades
- [ ] If `sample_size < 30`: do NOT promote. Run longer calibration first.

For risk/position changes:
- [ ] At least 50 live signal records in `logs/signals.jsonl` since last config change
- [ ] Position actions distributed across multiple symbols

### HG-3: Side bias acceptable

- [ ] In current calibration, no side (`LONG`/`SHORT`) accounts for `> 90%` of trades
- [ ] If side bias present: bias has a known cause (e.g., bear market screening filter) and is documented

### HG-4: Drawdown within risk budget

- [ ] Recommendation's max drawdown estimate `< 2x` current `risk_manager.drawdown.max_account_drawdown_pct`
- [ ] If recommendation would tighten drawdown: confirm runtime has been operating with looser limits without breaches

### HG-5: No conflicting recommendations

- [ ] No other `priority: high` recommendation targets the same `config_path` (would mean evidence is contradictory)
- [ ] If conflict exists: do not promote either; re-run calibration with longer window

### HG-6: No recent runtime instability

- [ ] `recent_restarts < max_restarts_per_hour` in supervisor state
- [ ] `runtime_health.json` shows `status: stopped` or `running` with no errors in last 100 log lines
- [ ] No `position_reversed_*_failed` in last 50 signal records

---

## Soft gates (acknowledge before promoting)

### SG-1: Reversibility

- [ ] Change can be reverted by editing one line in `default_params.yaml` and `runtime_control restart`
- [ ] No migration or DB schema change required

### SG-2: Config diff readable

Run `git diff config/default_params.yaml` and confirm:
- [ ] Diff is `< 10` lines changed
- [ ] No unrelated formatting or whitespace changes
- [ ] Comments near changed values still accurate

### SG-3: Impact scope

Document which subsystems are affected:
- [ ] `analyst_weights.*` → all signals
- [ ] `risk_manager.*` → entry gate
- [ ] `position_manager.*` → existing positions
- [ ] `simulation.*` → calibration only (does not affect live)
- [ ] `dynamic_watchlist.*` → watchlist source
- [ ] `runtime.*` → operational behavior

### SG-4: Monitoring plan

- [ ] Operator will re-run `daily-ops-checklist.md` within 24h of change
- [ ] Operator will compare next 20 signals to baseline distribution
- [ ] Rollback trigger defined: "if X happens, revert"

---

## Promotion procedure

Once all hard gates pass and soft gates are acknowledged:

1. **Stop runtime**
   ```bash
   ./venv/bin/python scripts/runtime_control.py stop
   ```

2. **Apply change** to `config/default_params.yaml`

3. **Verify config loads** (does not raise):
   ```bash
   ./venv/bin/python -c "import yaml; print(yaml.safe_load(open('config/default_params.yaml'))['analyst_weights'])"
   ```

4. **Smoke test single cycle (dry-run first)**:
   ```bash
   # Safe smoke: validates config load + analysis/policy path without operational side effects
   ./venv/bin/python scripts/run_paper_trading.py --single-cycle --dry-run
   ```

   Only run a plain operational single cycle after manual approval if needed:
   ```bash
   ./venv/bin/python scripts/run_paper_trading.py --single-cycle
   ./venv/bin/python scripts/check_runtime_health.py
   ```

   > A plain `--single-cycle` run is operational: it may start Telegram, send notifications, write runtime health/state, save portfolio snapshots, run reconciliation, and mutate paper positions depending on config.

5. **Commit locally** (do NOT push):
   ```bash
   git add config/default_params.yaml
   git commit -m "config: <one-line description>"
   ```

6. **Send push proposal** to operator channel (Telegram/Discord) with diff summary.

7. **Start runtime** only after push approval (or stay on local commit if user prefers):
   ```bash
   ./venv/bin/python scripts/runtime_control.py start
   ```

8. **Log the change** in `journal/` (if maintained) with date, reason, evidence pointer.

---

## Forbidden promotion patterns

| Pattern | Why forbidden |
|---|---|
| Apply `priority: high` recommendation with `sample_size < 30` | Insufficient evidence |
| Apply during `recent_restarts >= 3` flapping | Compounds instability |
| Apply weight change without re-running calibration | Speculative |
| Apply dynamic watchlist with `status != approved` | Bypasses manual gate |
| Edit `default_params.yaml` while runtime running | Race condition with cycle reads |
| Auto-push config commit | Operator must approve each push |
| Auto-promote from recommendation | Phase 7A explicitly outputs `manual_review_required` |

---

## Rollback procedure

If post-promotion signals look wrong:

1. `runtime_control stop`
2. `git diff HEAD~1 config/default_params.yaml` → identify the change
3. Revert with `git revert HEAD` (or manual edit)
4. `runtime_control restart`
5. Verify signals return to expected distribution
6. If revert doesn't fix: stop, escalate, do not re-apply

Do not roll forward and back repeatedly. Each cycle is data — let it accumulate.

---

## When to skip this checklist

**Never.** This checklist applies to **all** config changes affecting trading behavior, including:

- Manual tweaks ("just bump this by 0.05")
- "Quick" threshold changes
- Watchlist edits
- Risk manager adjustments

If a change is so small it doesn't need this checklist, it's so small it doesn't matter — and you should not be making it under pressure.
