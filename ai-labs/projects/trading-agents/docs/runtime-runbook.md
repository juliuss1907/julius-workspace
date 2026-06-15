# Runtime Operations Runbook

> **Audience:** Operators (Julius) on the main machine.
> **Scope:** Day-to-day operation of `scripts/run_paper_trading.py`, supervisor, scheduler, and supporting CLIs.
> **Last updated:** 2026-06-09

---

## 1. Mental model

The trading runtime is a single Python process that runs cycle-by-cycle. Around it sit three safety layers:

| Layer | Purpose | Disabled by default? |
|---|---|---|
| **Process lock** | Prevent two runtimes from running at once (Telegram 409). | No — always on when `runtime.prevent_duplicate_instances: true` |
| **Scheduler guard** | Skip scheduled launch if a runtime is already live. | No — always on |
| **Auto-restart supervisor** | Detect stale/dead runtimes and (optionally) restart. | **Yes** — `runtime.supervisor.enabled: false` |

These layers are independent. Removing one does not enable the next.

---

## 2. Paths and files (defaults)

All paths are relative to project root unless absolute.

| File | Purpose |
|---|---|
| `logs/run_paper_trading.lock` | PID lock file. Created on start, removed on clean stop. |
| `logs/runtime_health.json` | Last health snapshot (status, cycle_count, last_cycle_at, etc.). |
| `logs/runtime_control.log` | Runtime control start/stop log. |
| `logs/runtime_supervisor.log` | Supervisor classification / restart log. |
| `logs/runtime_supervisor_state.json` | Supervisor restart budget (events older than 24h are pruned). |
| `logs/paper_trading.log` | Runtime main log (rotated by log_rotation policy). |
| `logs/system.log` | System-level log (rotated). |
| `logs/errors.log` | Error log (rotated). |
| `logs/lite_mode.log` | Lite mode log (rotated). |
| `logs/signals.jsonl` | Append-only signal log (one record per cycle). |

---

## 3. Quick reference CLI

```bash
# Use project venv
./venv/bin/python ...

# Health snapshot (read-only, safe)
./venv/bin/python scripts/check_runtime_health.py
./venv/bin/python scripts/check_runtime_health.py --json

# Runtime control
./venv/bin/python scripts/runtime_control.py status
./venv/bin/python scripts/runtime_control.py start
./venv/bin/python scripts/runtime_control.py stop
./venv/bin/python scripts/runtime_control.py restart
./venv/bin/python scripts/runtime_control.py status --json

# Supervisor
./venv/bin/python scripts/runtime_supervisor.py --once --dry-run
./venv/bin/python scripts/runtime_supervisor.py --once --dry-run --mode auto_restart --json
./venv/bin/python scripts/runtime_supervisor.py --loop                # foreground
./venv/bin/python scripts/runtime_supervisor.py --help

# Scheduler (cron-friendly, but already guards live lock)
./venv/bin/python scripts/trading_scheduler.py
```

---

## 4. Standard operational flows

### 4.1 Start a single cycle (dry-run smoke test)

Use this for safe smoke tests. It exercises the analysis + demo-policy decision path without operational side effects.

```bash
cd /home/julius/julius-workspace/ai-labs/projects/trading-agents
./venv/bin/python scripts/run_paper_trading.py --single-cycle --dry-run
```

Expected dry-run behavior:
- Process exits with code 0.
- Skips process lock acquire/release.
- Skips runtime health writes (`logs/runtime_health.json` is not updated).
- Skips Telegram bot startup.
- Skips notifier/Telegram message sends.
- Skips position monitoring.
- Skips reconciliation.
- Skips portfolio snapshot save.
- Skips position mutations (no open/close/reduce/reverse/execute).
- Logs `DRY-RUN` decision summaries per symbol.
- No leftover `logs/run_paper_trading.lock`.

> **Warning:** A plain `--single-cycle` run (without `--dry-run`) is an operational run. It may start the Telegram bot, send notifications, write runtime health/state, save portfolio snapshots, run reconciliation, and mutate paper positions depending on config. Only run it deliberately as an operational step, not as a smoke test.

To verify a production single-cycle run afterwards, you can check:
```bash
./venv/bin/python scripts/check_runtime_health.py
```

### 4.2 Start runtime continuously

```bash
# Via runtime_control (recommended)
./venv/bin/python scripts/runtime_control.py start

# Check
./venv/bin/python scripts/runtime_control.py status
./venv/bin/python scripts/check_runtime_health.py

# View logs
tail -f logs/paper_trading.log
```

`runtime_control start` will:
1. Check `logs/run_paper_trading.lock`. If a live PID holds it, refuse to start.
2. Start the runtime in the background (nohup-style).
3. Wait briefly, then report status.

### 4.3 Stop runtime

```bash
# Graceful
./venv/bin/python scripts/runtime_control.py stop

# Force (last resort — kills lock holder PID only)
./venv/bin/python scripts/runtime_control.py stop --force
```

`runtime_control stop` will:
1. Read PID from lock file.
2. Send SIGTERM and wait up to 30s for graceful exit.
3. On timeout, fall back to SIGKILL **only if `--force` is passed**.
4. Remove stale lock.

### 4.4 Restart runtime

```bash
./venv/bin/python scripts/runtime_control.py restart
./venv/bin/python scripts/runtime_control.py status
```

Equivalent to `stop` then `start` with a short health gap.

### 4.5 Check supervisor health

```bash
./venv/bin/python scripts/runtime_supervisor.py --once --dry-run --json
```

Output fields:
- `decision.classification`: `fresh_running | stale_running | stale_lock | running_no_lock | stopped | never_started | malformed`
- `decision.would_restart`: bool
- `decision.blocked_by_budget`: bool (only true when `mode: auto_restart` and recent restarts ≥ `max_restarts_per_hour`)
- `decision.recent_restarts`: int (events within last 1h)
- `state`: live state snapshot

### 4.6 Run calibration

```bash
./venv/bin/python scripts/run_calibration_workflow.py --symbol BTCUSDT --days 7
ls reports/calibration/$(date +%Y-%m-%d)/
```

Outputs dated bundle: replay, replay-sweep, simulation, sweep, dashboard, recommendations, summary.

---

## 5. Common incidents and responses

### 5.1 "Telegram 409 Conflict" on startup

**Cause:** Two runtimes trying to use the same Telegram bot token.

**Fix:**
```bash
./venv/bin/python scripts/runtime_control.py status
ps -p <PID>           # is it alive?
./venv/bin/python scripts/runtime_control.py stop
# If still alive:
kill <PID>
sleep 2
rm -f logs/run_paper_trading.lock   # only if lock is stale
./venv/bin/python scripts/runtime_control.py start
```

### 5.2 Stale lock (process dead, lock present)

```bash
./venv/bin/python scripts/check_runtime_health.py
# If lock holder PID is dead:
rm -f logs/run_paper_trading.lock
./venv/bin/python scripts/runtime_control.py start
```

`runtime_control start` also auto-cleans stale locks. If it doesn't, the lock holder PID is unexpectedly still alive — investigate via `ps -p <PID>`.

### 5.3 Runtime looks stuck

1. `ps -p <PID>` — is the process alive and what state?
2. `tail -n 100 logs/paper_trading.log` — last activity?
3. `cat logs/runtime_health.json` — is `last_cycle_at` recent?
4. If truly stuck: `kill <PID>` (SIGTERM). Wait 30s. If still alive: `kill -9 <PID>`.

Avoid `kill -9` as the first action — runtime needs to release lock and flush health.

### 5.4 Health file shows malformed

**Cause:** Runtime crashed mid-write, or external process tampered with file.

**Fix:**
```bash
cat logs/runtime_health.json   # inspect
# If JSON is broken:
rm -f logs/runtime_health.json
./venv/bin/python scripts/runtime_control.py restart
```

### 5.5 Supervisor says `blocked_by_budget: true`

**Cause:** More than `max_restarts_per_hour` (default 2) restarts in last 60 minutes.

**Fix:**
1. Stop supervisor.
2. Inspect `logs/runtime_supervisor.log` for repeated crash reasons.
3. Fix root cause.
4. Optional: `rm -f logs/runtime_supervisor_state.json` to reset budget.
5. Restart supervisor.

**Do not** reset budget reflexively — it hides flapping.

### 5.6 Stale running classification

**Cause:** `last_cycle_at` older than `stale_after_seconds` (default 15 min) but runtime still claims running.

**Likely root cause:**
- Exchange rate limit stall.
- Data fetch hang.
- Long-running LLM call.

**Fix:**
1. `tail -n 50 logs/paper_trading.log` — where is the last log line?
2. If truly stuck, restart.
3. If still classified stale after restart, raise `stale_after_seconds` in config (intentional, conservative bump).

### 5.7 Calibration ran but recommendations look weird

Always read `reports/parameter-recommendations.md` and verify:
- Sample size (`>30` trades preferred)
- Side bias (`100% SHORT` is a red flag)
- Win rate with confidence interval
- Total PnL vs. baseline

Never apply `apply_status: manual_review_required` items without reading the evidence block. See `config-promotion-checklist.md`.

---

## 6. Log rotation policy

Configured under `runtime.log_rotation`:
- `max_bytes: 10485760` (10 MB)
- `keep_files: 5`
- Files: `paper_trading.log`, `system.log`, `errors.log`, `lite_mode.log`

Rotation runs at scheduler tick (every cycle) via `utils/log_rotation.rotate_logs()`.

`signals.jsonl` and `runtime_health.json` are **not** rotated automatically — they are append-only. Use `scripts/analyze_signal_logs.py` to compact if needed.

---

## 7. Process lockdown policy

| Action | Who | When |
|---|---|---|
| Start runtime | `runtime_control.py start` | After confirming no live lock |
| Stop runtime | `runtime_control.py stop` | Before any config change |
| Stop + restart | `runtime_control.py restart` | After calibration acceptance |
| Force-kill | `kill -9` | **Last resort**, only via `runtime_control.py stop --force` or manual |
| Auto-restart | Supervisor `mode: auto_restart` | **Disabled by default** |

**Rule of thumb:** if a runtime is misbehaving, **stop → investigate → fix → start**. Do not leave a flapping runtime running.

---

## 8. Quick troubleshooting matrix

| Symptom | First command | Likely cause |
|---|---|---|
| `Telegram 409 Conflict` | `runtime_control status` | Duplicate runtime |
| `lock file present, no process` | `cat logs/run_paper_trading.lock` + `ps -p <PID>` | Stale lock |
| `health.json missing` | `runtime_control status` | Runtime never started or crashed pre-write |
| `health.json status: running, no cycles` | `tail -f logs/paper_trading.log` | Stuck in pre-cycle init |
| `stale_running` for >30 min | `tail -n 50 logs/paper_trading.log` | Data hang or LLM stall |
| `recent_restarts >= 3/hr` | `runtime_supervisor --once --dry-run` | Flapping runtime |
| Recommendations show 100% SHORT bias | `reports/parameter-recommendations.md` | Watchlist or signal imbalance |

---

## 9. When in doubt

1. **Stop** the runtime (`runtime_control stop`).
2. **Read** the relevant log file (do not guess).
3. **Check** `logs/runtime_health.json` and `logs/runtime_control.log`.
4. **Escalate** via `tasks/inbox/escalation-YYYY-MM-DD-HHmm.md` if root cause is unclear.

Do not improvise. Do not delete log files. Always `runtime_control stop` before destructive operations.
