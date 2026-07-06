# Batch 4E Plan — Standalone Repo Onboarding Polish for the-trading-guy

Date: 2026-07-06

## Context

`the-trading-guy` is now a standalone GitHub repository with clean single-commit history.

Remote:

```text
git@github.com:juliuss1907/the-trading-guy.git
```

Current standalone commit:

```text
89194f3009d7c0eabb91d505be4adea834d5d94d chore: initial standalone trading agents snapshot
```

Batch 4D verified:

```text
Fresh clone integrity: passed
Commit count: 1
Forbidden HEAD files: 0
Forbidden history paths: 0
Safe sanity checks: passed
Staging/index cleanup in workspace: completed
```

## Goal

Polish the standalone repo onboarding so a reader can understand:

1. What the project does.
2. How to set it up safely.
3. What commands are safe to run.
4. What safety boundaries are mandatory.
5. Why monitoring remains manual-only.

## Non-Goals

Batch 4E must not:

- Add live trading behavior.
- Add order placement.
- Add simulate-live execution.
- Add StrategySignal-to-order mapping.
- Change runtime/default config.
- Add secrets or `.env` files.
- Add raw logs or replay JSONL files.
- Enable cron/systemd/scheduler automation.

## Working Location

Recommended working location:

```text
Fresh clone or dedicated local clone of git@github.com:juliuss1907/the-trading-guy.git
```

Do not make Batch 4E docs changes in `julius-workspace/ai-labs/projects/trading-agents` unless Julius explicitly decides workspace remains source of truth.

## Target Files

Minimum target files in standalone repo:

```text
README.md
docs/SAFETY.md
docs/MONITORING.md
```

Optional only if useful:

```text
docs/SETUP.md
docs/REPO_HISTORY.md
```

## README Target Structure

```markdown
# The Trading Guy

## Status
Read-only / research / monitoring tooling. No live trading by default.

## What it does
StrategySignal / TraderAgent evaluation and monitoring framework.

## Safety Boundaries
- No live trading
- No order placement
- No simulate-live unless explicitly approved
- No StrategySignal-to-order bridge
- No runtime/default config changes without approval

## Setup
Python version, virtualenv, dependency install notes.

## Configuration
Do not commit `.env`. Use environment variables. No secrets in repo.

## Safe Usage
Examples of safe commands only.

## Monitoring Cadence
Manual-only cadence; no cron/systemd enabled.

## Project Structure
agents/, strategies/, scripts/, docs/, config/.

## Current Known Decisions
Variant-D config, manual-only scheduler, volatility-skip direct block metric explanation, candidate-level attribution enabled.

## License / Ownership
Private or TBD.
```

## `docs/SAFETY.md` Requirements

Must include:

- No live trading.
- No order placement.
- No simulate-live by default.
- No StrategySignal-to-order mapping.
- No default runtime config changes without approval.
- No `.env` files in repo.
- No raw replay logs in repo.
- Manual approval gates for dangerous operations.

## `docs/MONITORING.md` Requirements

Must include:

- Manual-only read-only cadence.
- No cron/systemd scheduler enabled.
- What the monitoring reports are for.
- Volatility-skip direct block rate caveat.
- Candidate-level attribution summary.
- Dependency readiness caveat.

## Proposed Execution Steps

1. Create/refresh a dedicated clone of `the-trading-guy` in `/tmp` or another approved working directory.
2. Verify it is on commit `89194f3009d7c0eabb91d505be4adea834d5d94d` or newer if Julius has made updates.
3. Inspect current README/docs.
4. Draft minimal onboarding changes.
5. Run safe docs-only validation:
   - `git diff -- README.md docs/SAFETY.md docs/MONITORING.md`
   - no runtime script execution required.
6. Commit locally in `the-trading-guy`:

```text
docs: polish standalone repo onboarding
```

7. Do not push until Julius approves a push proposal.

## Pass Criteria

```text
README clearly explains project
Safety boundaries visible near top
Setup instructions do not require secrets
No `.env.example` added unless explicitly approved and sanitized
No live trading instructions
Manual-only cadence documented
Docs commit created locally in standalone repo
No push without approval
```

## Safety Boundaries

- Live trading: not executed
- Order placement: not executed
- Simulate-live: not executed
- StrategySignal-to-order mapping: not added
- Runtime/default config changes: not changed
- Raw replay logs committed: none
- `.env` files read/printed/committed: none
- Scheduler/cron/systemd enablement: none
- Push: approval required

## Recommended Next Command

```text
Build Batch 4E — Standalone Repo Onboarding Polish
```
