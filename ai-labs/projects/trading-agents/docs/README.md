# Trading Agents — Documentation Index

> **Project:** Crypto trading agents system with one shared analysis core and two main consumers: demo auto-trade + manual discretionary reports.
> **Last updated:** 2026-06-15

---

## Start here

Nếu anh hoặc contributor mới quay lại repo sau vài ngày, đọc theo thứ tự này để tránh quay lại execution-first design:

1. [14-rescue-architecture.md](14-rescue-architecture.md) — north-star architecture reset
2. [15-orchestration-implementation-plan.md](15-orchestration-implementation-plan.md) — roadmap đã dùng cho shared-core / policy / readonly cleanup milestones
3. [01-architecture.md](01-architecture.md) — product/system architecture gốc 5 layers
4. [runtime-runbook.md](runtime-runbook.md) — chỉ khi làm việc với runtime demo path

## Architecture + refactor docs

| Doc | Purpose | Read when |
|---|---|---|
| [14-rescue-architecture.md](14-rescue-architecture.md) | North-star reset: shared brain, separate demo/manual output tracks. | First architecture pass. |
| [15-orchestration-implementation-plan.md](15-orchestration-implementation-plan.md) | Concrete carve-out plan that produced the current orchestration split. | Before editing `orchestration/`, `policies/`, or top-level entrypoints. |
| [01-architecture.md](01-architecture.md) | 5-layer system vision, modes, systems-thinking framing. | After understanding the rescue docs. |
| [13-implementation-roadmap.md](13-implementation-roadmap.md) | Historical roadmap and phased buildout. | When mapping older milestones. |

## Operational docs (runtime/demo path)

| Doc | Purpose | Read when |
|---|---|---|
| [runtime-runbook.md](runtime-runbook.md) | Day-to-day operations: start/stop/restart, health checks, common incidents. | First thing every runtime session. |
| [daily-ops-checklist.md](daily-ops-checklist.md) | Pre-flight + end-of-session checks. | Once per runtime session. |
| [alerting-policy.md](alerting-policy.md) | When to stop, investigate, observe. Severity levels P0/P1/P2. | When something looks off. |
| [config-promotion-checklist.md](config-promotion-checklist.md) | Gate before applying any config change. | Before editing `default_params.yaml`. |
| [service-setup.md](service-setup.md) | `nohup` vs `tmux` vs `systemd` comparison. systemd templates. | When ready to leave `nohup` behind. |

## Reference docs

| Doc | Purpose |
|---|---|
| [01-architecture.md](01-architecture.md) | System architecture and data flow. Historical product vision; pair with docs 14/15 for current repo boundaries. |
| [02-data-sources.md](02-data-sources.md) | Data sources, rate limits, fallback behavior. |
| [03-execution-layer.md](03-execution-layer.md) | `OrderManager`, `base_trader`, paper vs testnet. |
| [04-error-handling.md](04-error-handling.md) | Error taxonomy and recovery patterns. |
| [05-state-management.md](05-state-management.md) | JSONL signal log + SQLite database. |
| [06-data-storage.md](06-data-storage.md) | Storage layout, retention, cleanup. |
| [07-backtesting.md](07-backtesting.md) | Replay + simulation + sweep. |
| [08-confidence-scoring.md](08-confidence-scoring.md) | Analyst weights, thresholds, debate adjustment. |
| [09-position-sizing.md](09-position-sizing.md) | Risk manager + pyramiding + drawdown. |
| [10-monitoring.md](10-monitoring.md) | Health, supervisor, signal analytics. |
| [11-parameter-tuning.md](11-parameter-tuning.md) | Calibration workflow. |
| [12-fine-tuning.md](12-fine-tuning.md) | Future: model fine-tuning (not active). |
| [13-implementation-roadmap.md](13-implementation-roadmap.md) | Phase progress and roadmap. |
| [14-rescue-architecture.md](14-rescue-architecture.md) | Accepted north-star reset: 5-layer system with separate demo auto-trade and manual report tracks. |
| [15-orchestration-implementation-plan.md](15-orchestration-implementation-plan.md) | Concrete implementation plan for extracting shared orchestration and reconnecting demo/runtime + manual report consumers. |

## Specialized guides

| Doc | Purpose |
|---|---|
| [BACKTESTING.md](BACKTESTING.md) | Replay, sweep, simulation, dashboard usage. |
| [LITE_FULL_MODE.md](LITE_FULL_MODE.md) | Lite mode vs full mode runtime. |
| [PAPER_TRADING.md](PAPER_TRADING.md) | Paper trading mode details. |
| [TELEGRAM_BOT.md](TELEGRAM_BOT.md) | Telegram bot integration. |
| [SESSION_HANDOFF_2026-06-06.md](SESSION_HANDOFF_2026-06-06.md) | Historical session notes. |

---

## Quick start

```bash
cd /home/julius/julius-workspace/ai-labs/projects/trading-agents

# 1. Understand the architecture split first
sed -n '1,120p' docs/14-rescue-architecture.md

# 2. Lightweight manual-path check
./venv/bin/python scripts/generate_manual_trade_report.py --help

# 3. Lightweight readonly-analysis CLI check
./venv/bin/python scripts/analyze_symbol_readonly.py --help

# 4. Verify runtime health
./venv/bin/python scripts/check_runtime_health.py

# 5. Single-cycle dry-run smoke test (demo path)
#    Safe: no Telegram startup, no position mutations, no production state writes.
./venv/bin/python scripts/run_paper_trading.py --single-cycle --dry-run

# 6. Start runtime operationally (after dry-run smoke passes and operator approves)
./venv/bin/python scripts/runtime_control.py start

# 7. Status
./venv/bin/python scripts/runtime_control.py status

# 8. Stop
./venv/bin/python scripts/runtime_control.py stop
```

> **Safety note:** Use `--single-cycle --dry-run` for smoke tests. A plain `--single-cycle` run is an operational run: it may start the Telegram bot, send notifications, write runtime health/state, save portfolio snapshots, run reconciliation, and mutate paper positions depending on config.

For full operational procedures, see [runtime-runbook.md](runtime-runbook.md).

## Shared-core entrypoints

These are the files that define the current architecture seam:

- `orchestration/contracts.py` — normalized contracts including `FinalAnalysis`
- `orchestration/analysis_runner.py` — shared analysis orchestration
- `policies/demo_execution.py` — demo-path decision adapter
- `policies/manual_report.py` — manual-path report adapter
- `policies/reverse_planner.py` — stdlib-only guarded-reverse planner
- `scripts/run_paper_trading.py` — demo runtime consumer
- `scripts/generate_manual_trade_report.py` — manual report consumer
- `scripts/analyze_symbol_readonly.py` — thin read-only orchestration client; demo-policy inspection only with `--include-demo-decision`

If a change is reusable across both output paths, it probably belongs in `orchestration/` or `policies/`, not inside the runtime script.

## Phase status

- **Shared-core / policy / readonly cleanup:** DONE through readonly analyzer cleanup
  - `orchestration/` produces normalized `FinalAnalysis`
  - demo runtime consumes `policies.demo_execution`
  - manual reports consume `policies.manual_report`
  - readonly CLI is thin by default and only loads demo/runtime managers behind `--include-demo-decision`
  - boundary guardrails cover lazy imports, pure policy modules, and lightweight CLI help paths
- **Docs alignment:** DONE
  - README + docs index are aligned with actual import paths
  - rescue/implementation docs now distinguish historical plan language from current committed modules
  - runtime smoke docs now require `--single-cycle --dry-run` and warn against plain `--single-cycle`
- **Repo hygiene:** DONE
  - source/docs are tracked; generated/runtime/private artifacts are ignored
  - stale untracked inventory artifact `trading-agents-repo-inventory.md` was removed after review
- **9A — Production Hardening:** DONE
  - 9A.1 Process Lock + Healthcheck
  - 9A.2 Scheduler Guard + Log Rotation + Health CLI
  - 9A.3 Runtime Control CLI
  - 9A.4 Auto-Restart Supervisor
- **9B — Operational Runbook + Service Setup:** DONE
  - 5 ops docs (runbook, checklist, alerting, config-promotion, service-setup)
  - systemd templates in `ops/systemd/`
  - This index

Parallel next topics:

- **Repo inventory / tracking plan:** categorize remaining untracked source, docs, generated artifacts, and private/runtime paths
- **Runtime integration smoke:** DONE — safe dry-run/single-cycle smoke for demo runtime is implemented and validated (`--single-cycle --dry-run`)
- **10A — Longer Calibration + Bias Investigation:** DONE — 30d combined + per-symbol calibration completed on 2026-06-15; see [phase10a/phase10a-refresh-2026-06-15.md](phase10a/phase10a-refresh-2026-06-15.md)
- **10A.2 — Multi-Regime Bull-Market Replay:** DONE — 91d 2024 Q4 bull-market replay completed on 2026-06-15; confirms signal stack is market-tracking, not intrinsically bear-biased; see [phase10a/bull-market-replay-2024-q4.md](phase10a/bull-market-replay-2024-q4.md)
