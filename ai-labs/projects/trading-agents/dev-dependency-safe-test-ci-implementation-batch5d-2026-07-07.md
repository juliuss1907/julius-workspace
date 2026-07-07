# Batch 5D — Dev Dependency / Safe Test CI Implementation

Date: 2026-07-07

## Goal

Add a minimal dev dependency strategy and extend CI to run one safe pytest subset.

## Source Repo

- Path: `/home/julius/julius-workspace/ai-labs/projects/the-trading-guy`
- Remote: `git@github.com:juliuss1907/the-trading-guy.git`
- Base HEAD before commit: `60eec5639f6fcb9c49eef70947908fb1803b449c`
- Base log before commit: `60eec56 ci: add repository safety checks`

## Local Source Commit

- Commit: `b83fb38292a24f260f7372ab557326b2ba50093d`
- Log: `b83fb38 ci: add safe pytest subset`
- Push executed: **no**

Files changed:

```text
.github/workflows/safety-checks.yml
requirements-dev.txt
```

## Changes Made

- Added `requirements-dev.txt` with minimal dev/test dependencies:
  - `pytest`
  - `pytest-asyncio`
- Updated `.github/workflows/safety-checks.yml` to install dev dependencies and run:

```bash
python -m pytest -q -p no:cacheprovider scripts/test_candidate_level_attribution.py
```

## Local Validation

Existing safety checks after change:

```text
forbidden_files_check=ok
required_docs_check=ok
python_files_checked=181
syntax_check=ok
```

Local pytest availability:

```text
available=false
exit=1
/usr/bin/python: No module named pytest
```

Safe pytest subset local run:

```text
status=skipped_pytest_unavailable
exit=skipped
pytest unavailable locally; dependency install intentionally not executed in Batch 5D
```

Note: dependency install was intentionally not executed locally in Batch 5D.

## Safety Boundaries

- Live trading: not executed
- Order placement: not executed
- Simulate-live: not executed
- StrategySignal-to-order mapping: not added
- Runtime/default config changes: not changed
- Dependency install: not executed locally
- External API calls: not executed
- Secrets printed: none
- `.env` files read/printed/committed: none
- Raw replay logs committed: none
- Scheduler/cron/systemd enabled: no
- Push: no

## Status

`completed_local_ci_commit_ready_for_push_proposal`

## Push Proposal Required

The source repo commit is local. Push requires Julius approval.
