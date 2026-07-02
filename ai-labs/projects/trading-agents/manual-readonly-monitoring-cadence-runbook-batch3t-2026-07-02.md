# Batch 3T - Option A Manual-On-Demand Read-Only Monitoring Cadence Runbook

## Executive Summary

- Selected option: **Option A - Manual-on-demand only**
- Status: **pass**
- Scheduler enabled: **false**
- Cron enabled: **false**
- systemd timer enabled: **false**
- Runtime/default config changed: **false**
- Live trading / order placement / simulate-live: **false**
- Recommendation: Adopt manual-on-demand cadence as the default operating mode for now.

## Why Option A Now

Batch 3S proved the cadence runner can execute end-to-end, but monitoring still has a watch item: volatility_skip_direct_block_rate == 0.0%. This is not a hard failure, but it is enough reason to keep monitoring human-triggered before handing it to cron/systemd.

## Latest Evidence

| Evidence | Value |
|---|---:|
| batch3s_status | pass |
| batch3s_raw_replay_records | 141 |
| batch3s_scheduler_enabled | False |
| batch3q_fresh_status | watch |
| batch3q_fresh_records | 141 |
| batch3q_fresh_hard_conflict_count | 0 |
| batch3q_fresh_volatile_breakout_selected_count | 0 |
| batch3q_combined_status | watch |
| batch3q_combined_records | 296 |
| batch3q_combined_hard_conflict_count | 0 |
| batch3q_combined_volatile_breakout_selected_count | 0 |
| known_watch_item | volatility_skip_direct_block_rate == 0.0% |

## Manual Cadence Policy

Default mode: manual-on-demand. Run after important strategy/config changes, or roughly weekly if Julius wants updated monitoring evidence. Hermes should only run the actual --run cadence after Julius explicitly asks in that session/batch.

## Standard Commands

Dry-run first:

    cd /home/julius/julius-workspace/ai-labs/projects/trading-agents
    python3 scripts/run_readonly_monitoring_cadence.py --date-tag manual-YYYY-MM-DD-HHMM --symbols BTCUSDT ETHUSDT SOLUSDT --days 14 --window 200 --step 4

Explicit run:

    python3 scripts/run_readonly_monitoring_cadence.py --run --date-tag manual-YYYY-MM-DD-HHMM --symbols BTCUSDT ETHUSDT SOLUSDT --days 14 --window 200 --step 4

## Output Policy

Raw replay log pattern:

    logs/replay_signals-batch3r-manual-YYYY-MM-DD-HHMM-core.jsonl

Policy: do not stage, commit, or push raw replay logs. Monitoring reports may be committed after review.

## Dry-Run Check Output

~~~text
Batch 3R manual read-only monitoring cadence
mode: DRY-RUN
date_tag: manual-dryrun-check
symbols: BTCUSDT ETHUSDT SOLUSDT
raw_replay_log: logs/replay_signals-batch3r-manual-dryrun-check-core.jsonl  # local-only, do not commit
committable_reports:
  - volatility-skip-monitoring-cadence-batch3r-manual-dryrun-check.md
  - volatility-skip-monitoring-cadence-batch3r-manual-dryrun-check.json
  - volatility-skip-monitoring-combined-batch3r-manual-dryrun-check.md
  - volatility-skip-monitoring-combined-batch3r-manual-dryrun-check.json
commands:
  [readiness] venv/bin/python scripts/check_replay_dependency_readiness.py --json
  [replay] venv/bin/python scripts/replay_signals.py --symbols BTCUSDT ETHUSDT SOLUSDT --days 14 --window 200 --step 4 --output logs/replay_signals-batch3r-manual-dryrun-check-core.jsonl
  [fresh_monitoring] venv/bin/python scripts/run_volatility_skip_monitoring.py --inputs logs/replay_signals-batch3r-manual-dryrun-check-core.jsonl --output volatility-skip-monitoring-cadence-batch3r-manual-dryrun-check.md --json-output volatility-skip-monitoring-cadence-batch3r-manual-dryrun-check.json
  [combined_monitoring] venv/bin/python scripts/run_volatility_skip_monitoring.py --inputs logs/replay_signals-batch3f-2026-06-28.jsonl logs/replay_signals-batch3g-2026-06-28.jsonl logs/replay_signals-batch3r-manual-dryrun-check-core.jsonl --output volatility-skip-monitoring-combined-batch3r-manual-dryrun-check.md --json-output volatility-skip-monitoring-combined-batch3r-manual-dryrun-check.json
scheduler_enabled: false
live_trading_authorized: false
order_placement_authorized: false
DRY-RUN only. Re-run with --run to execute. Raw replay logs must not be committed.

~~~

## Escalation Conditions

- dependency readiness fails
- fresh replay exits nonzero
- fresh replay records == 0
- fresh monitoring status == fail
- combined monitoring status == fail
- hard_conflict_count > 0
- volatile_breakout_selected_count > 0
- current_config.matches_variant_d == false
- runner asks for .env/secret inspection
- any step attempts live/simulate-live/order execution

## Future Scheduler Gate

Choosing Option A now does not block cron/systemd later. Reconsider scheduler only after 2-3 successful manual cadence runs, clean raw log handling, and explicit Julius approval.

Future exact approval phrase:

    Approve scheduled read-only monitoring cadence for trading-agents.

## Validation

| Command | Status | Notes |
|---|---|---|
| python3 scripts/run_readonly_monitoring_cadence.py --help | pass | rc=0 |
| python3 scripts/run_readonly_monitoring_cadence.py --date-tag manual-dryrun-check | pass | rc=0 |
| python3 scripts/test_readonly_monitoring_cadence.py | pass | rc=0 |
| python3 scripts/test_boundary_guardrails.py | pass | rc=0 |
| python3 scripts/test_volatility_skip_monitoring.py | pass | rc=0 |

## Boundary Confirmation

- No scheduler/cron/systemd automation was enabled.
- No runtime/default config changes were made.
- No live trading, order placement, or simulate-live execution was run.
- No StrategySignal-to-order mapping was introduced.
- .env contents were not read or printed.
- No raw replay logs were created by this report build.

## Decision Block

    Batch 3T Option A Decision:
    - Status: pass
    - Operating mode: manual-on-demand
    - Scheduler enabled: false
    - Runtime/default config changed: false
    - Raw replay logs committable: false
    - Next step: Run manual cadence only when Julius requests it; reconsider scheduler after 2-3 clean manual runs.
