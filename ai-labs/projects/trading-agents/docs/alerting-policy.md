# Alerting Policy

> **Scope:** Define **when** something is wrong and **what** to do about it.
> **Last updated:** 2026-06-09

This is a policy document. No automated alerting is wired up in Phase 9B — these rules are designed for **manual** or **future** alerting.

---

## Severity levels

| Level | Meaning | Operator action |
|---|---|---|
| **P0 — Stop** | Runtime is unsafe or producing losses. | `runtime_control stop` immediately. |
| **P1 — Investigate** | Anomaly that may be benign. | Read logs, decide within 1 hour. |
| **P2 — Observe** | Trending concern, not urgent. | Note in journal, check next session. |

---

## P0 — Stop conditions

### P0.1 Stale lock + live PID mismatch

- **Trigger:** Lock file present, holder PID dead, OR live PID has no lock.
- **Detection:** `check_runtime_health.py` shows `lock_pid_alive: false` but `status: running` for >5 min.
- **Action:** `runtime_control stop` (force if needed), investigate why runtime didn't release lock.

### P0.2 Budget-blocked restart loop

- **Trigger:** Supervisor `recent_restarts >= max_restarts_per_hour` (default 2) for 3+ consecutive checks.
- **Detection:** `runtime_supervisor --once --dry-run --json` shows `blocked_by_budget: true` repeatedly.
- **Action:** Stop supervisor. Inspect `logs/runtime_supervisor.log` for crash reason. Fix root cause before re-enabling.

### P0.3 Health malformed or stale

- **Trigger:** `runtime_health.json` missing OR `status: running` with `last_cycle_at` older than 30 minutes.
- **Detection:** `check_runtime_health.py` exits non-zero OR `runtime_supervisor` classification `stale_running`.
- **Action:** `runtime_control stop`, `tail` last 100 log lines, restart after diagnosis.

### P0.4 Reverse flow failure

- **Trigger:** Signal log contains `position_reversed_close_failed` or `position_reversed_open_failed`.
- **Detection:** `grep 'position_reversed_.*_failed' logs/signals.jsonl` returns lines.
- **Action:** `runtime_control stop`. Reverse mode is guarded but failures indicate state corruption. Manual reconciliation needed.

### P0.5 Telegram 409 / duplicate runtime

- **Trigger:** Two `run_paper_trading.py` processes detected, OR Telegram 409 in logs.
- **Detection:** `ps aux | grep run_paper_trading | wc -l >= 2` OR `grep -i '409' logs/errors.log`.
- **Action:** `runtime_control stop`, kill all but the most recent process, ensure lock not leaked.

---

## P1 — Investigate conditions

### P1.1 Sudden spike in risk rejections

- **Trigger:** > 50% of last 20 signals ended in `risk_rejected`.
- **Detection:**
  ```bash
  tail -n 20 logs/signals.jsonl | python -c "
  import json, sys
  recs = [json.loads(l) for l in sys.stdin]
  rej = sum(1 for r in recs if r.get('risk_decision', {}).get('decision') == 'reject')
  print(f'rejected: {rej}/{len(recs)}')
  "
  ```
- **Action:** Read rejected reasons. If a single check (pyramiding, exposure, drawdown) dominates, consider whether thresholds are still appropriate. **Do not auto-tune.**

### P1.2 Hold ratio drift

- **Trigger:** HOLD ratio > 80% over last 50 signals.
- **Detection:** `python scripts/analyze_signal_logs.py` (HOLD vs actionable distribution).
- **Action:** Check analyst outputs — are thresholds too tight? Is market genuinely quiet? Calibrate weekly, do not react intra-day.

### P1.3 Calibration findings with sample size < 30

- **Trigger:** `parameter-recommendations.md` shows high-priority recommendation based on `< 30` trades.
- **Detection:** Read evidence block in recommendation.
- **Action:** Schedule longer calibration (`--days 14` or more) before considering config change.

### P1.4 Position reduce cluster

- **Trigger:** 3+ `reduce_position` actions in last 20 signals without re-entry.
- **Detection:** `python scripts/analyze_position_events.py --window 20`.
- **Action:** Inspect market state and `max_drawdown_pct` setting. May indicate drawdown triggers are too aggressive.

### P1.5 Repeated log errors

- **Trigger:** Same error message > 10 times in `errors.log` within 1 hour.
- **Detection:** `grep -c 'MESSAGE' logs/errors.log`.
- **Action:** Read full error context. Likely a data source issue. May need backoff or source replacement.

---

## P2 — Observe conditions

### P2.1 Side bias in calibration

- **Trigger:** 100% of simulated trades are LONG or SHORT.
- **Why it's P2:** Calibration artifact, not necessarily live signal bias.
- **Action:** Note in journal. Investigate during next calibration run with longer window.

### P2.2 Avg hold time outliers

- **Trigger:** Average hold > 200 candles (>33 hours) for trades that exited normally.
- **Action:** May want to tighten `simulation.max_hold_candles` (recommendation only, manual review).

### P2.3 Supervisor state file growth

- **Trigger:** `runtime_supervisor_state.json` > 50 KB.
- **Action:** Normal — events auto-prune after 24h. If it stays large, check for bug in `prune_old_events`.

### P2.4 Watchlist churn

- **Trigger:** Dynamic watchlist changed > 30% of selected symbols vs. previous run.
- **Action:** Investigate if screening thresholds are too loose.

---

## Anti-patterns (do NOT alert on these)

- **Single HOLD signal** — expected behavior, not an alert.
- **One risk rejection** — risk manager doing its job.
- **A stale signal log line older than 1 hour during a quiet market** — runtime may be waiting for next cycle window.
- **Calibration warning about sample size** — already documented as a known limitation, not an alert.

---

## Notification paths (current)

| Channel | Wired? | Used for |
|---|---|---|
| `logs/paper_trading.log` | Yes | All events |
| `logs/errors.log` | Yes | Error-level events only |
| Telegram (via `trade_notifier.py`) | Yes | Trades, position events, risk rejections |
| Email | **No** | Not implemented |
| Slack / Discord | **No** | Not implemented |
| PagerDuty / Pager | **No** | Not implemented |

If you need email/Slack alerting, escalate as Phase 9B follow-up — do not add ad-hoc.

---

## Future work (out of scope for 9B)

- Wire supervisor `mode: auto_restart` events to a notification channel.
- Auto-tile `parameter-recommendations.md` to a daily summary message.
- Heartbeat ping (every N cycles) so operator can confirm runtime is alive even when not trading.
- Disk-usage alert when `logs/` exceeds 200 MB.

Do not implement any of these without explicit Julius approval.
