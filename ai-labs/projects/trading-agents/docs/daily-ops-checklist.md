# Daily Operations Checklist

> **Cadence:** Run once per active session (or once per day if running 24/7).
> **Audience:** Operator (Julius).
> **Last updated:** 2026-06-09

---

## Pre-flight (start of session)

- [ ] Project path correct: `/home/julius/julius-workspace/ai-labs/projects/trading-agents`
- [ ] Virtualenv present: `ls venv/bin/python`
- [ ] No leftover lock: `ls logs/run_paper_trading.lock` should not exist
- [ ] No leftover process: `ps aux | grep -v grep | grep run_paper_trading.py`
- [ ] Disk space available: `df -h .` (logs grow ~1–2 MB/day)
- [ ] Telegram notifier reachable (manual test if needed)

## Runtime status

- [ ] `runtime_control status` shows expected state
- [ ] `check_runtime_health.py` shows `status: running` (or `stopped` if expected)
- [ ] `runtime_supervisor.py --once --dry-run --json` shows `classification` matching expectation
- [ ] `recent_restarts < max_restarts_per_hour` in supervisor state

## Signal & position health

- [ ] `tail -n 50 logs/paper_trading.log` — no repeated tracebacks
- [ ] `tail -n 5 logs/signals.jsonl` — last 5 records parse cleanly
- [ ] `python -c "import json; [print(json.loads(l)['final_signal']['action'], json.loads(l).get('execution_status')) for l in open('logs/signals.jsonl').readlines()[-10:]]"`
- [ ] Open positions reasonable: `python scripts/analyze_positions.py` (look for unexpected count)
- [ ] No `position_reversed_close_failed` or `position_reversed_open_failed` in recent signals

## Risk & position manager

- [ ] Risk rejection count: `grep -c '"status": "risk_rejected"' logs/signals.jsonl` (compare to baseline)
- [ ] Pyramiding rejections: `grep -c 'pyramiding disabled' logs/paper_trading.log` (should be 0 unless intended)
- [ ] Drawdown triggers: `grep -c 'drawdown_blocked' logs/paper_trading.log` (should be 0 unless market stress)
- [ ] Position actions distribution: `python scripts/analyze_position_events.py` (or `analyze_positions.py`)

## Calibration freshness

- [ ] Latest calibration run date: `ls -t reports/calibration/ | head -1`
- [ ] Recommendations: `ls reports/parameter-recommendations.md` (refresh weekly)
- [ ] No new high-priority recommendations waiting for review (read `parameter-recommendations.md`)

## Log & disk

- [ ] `du -sh logs/` (expect < 100 MB with rotation working)
- [ ] `ls logs/*.log.* | wc -l` (rotated files count, capped at `keep_files: 5`)
- [ ] `ls -la logs/runtime_supervisor_state.json` (state file present, sane size)

## Dynamic watchlist (if enabled)

- [ ] `cat watchlist/dynamic-watchlist.json | head -5` (if `enabled: true`)
- [ ] `status: approved` required for runtime use
- [ ] `enabled_for_runtime: true` required for runtime use
- [ ] **Currently disabled** — only re-check if `dynamic_watchlist.enabled: true` is set

## Supervisor (if enabled)

- [ ] **Currently disabled** — `runtime.supervisor.enabled: false`
- [ ] If re-enabling: confirm `mode: monitor_only` first (not `auto_restart`)
- [ ] `python scripts/runtime_supervisor.py --once --dry-run --json` should be clean

## End of session

- [ ] Decide: keep runtime running or `runtime_control stop`?
- [ ] If stopping: confirm lock released (`ls logs/run_paper_trading.lock` → not found)
- [ ] Note any anomalies in `journal/` if present
- [ ] Commit local changes if any (use push proposal flow, not auto-push)

---

## Red flags (stop and investigate)

- `recent_restarts >= 3` in supervisor state
- `position_reversed_*_failed` in last 5 signals
- `health.json` older than 1 hour while status is `running`
- `paper_trading.log` last line older than 5 minutes while running
- Multiple `Telegram 409` errors
- Calibration report with `100%` side bias and small sample size
- PnL drawdown > 5% in 24h (open positions)

If any red flag fires: `runtime_control stop` → read logs → escalate if root cause unclear.
