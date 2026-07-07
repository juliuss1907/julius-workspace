# Batch 5D — Dev Dependency / Safe Test CI Implementation

Date: 2026-07-07

## Goal

Add a minimal dev dependency strategy and extend CI to run one safe pytest subset.

## Source Repo

- Path: `/home/julius/julius-workspace/ai-labs/projects/the-trading-guy`
- Commit: `b83fb38292a24f260f7372ab557326b2ba50093d`
- Commit log: `b83fb38 ci: add safe pytest subset`

## Push

Julius approved:

```text
Push the-trading-guy Batch 5D
```

Push executed: **yes**

- Remote `main` after push: `b83fb38292a24f260f7372ab557326b2ba50093d`
- `origin/main` after fetch: `b83fb38292a24f260f7372ab557326b2ba50093d`
- Remote log after push: `b83fb38 ci: add safe pytest subset`
- Remote commit count after push: `4`

## Files Changed

```text
requirements-dev.txt
.github/workflows/safety-checks.yml
```

## Changes Made

- Added `requirements-dev.txt` with minimal dev/test dependencies:
  - `pytest`
  - `pytest-asyncio`
- Updated `.github/workflows/safety-checks.yml` to install dev dependencies and run:

```bash
python -m pytest -q -p no:cacheprovider scripts/test_candidate_level_attribution.py
```

## Post-Push Local Validation

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
pytest unavailable locally; dependency install intentionally not executed during push verification
```

Note: dependency install was intentionally not executed locally. GitHub Actions will install `requirements-dev.txt` in CI.

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
- Push: executed only after Julius approval

## Status

`pushed_and_verified`
