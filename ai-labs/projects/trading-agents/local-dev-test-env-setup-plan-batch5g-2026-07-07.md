# Batch 5G — Local Dev Test Environment Setup Plan

## Option

`Option A — Minimal local venv`

## Goal

Create a repo-local Python virtual environment for the source-of-truth repo:

```text
/home/julius/julius-workspace/ai-labs/projects/the-trading-guy
```

The purpose is to run the safe local pytest subset before future pushes:

```bash
.venv/bin/python -m pytest -q -p no:cacheprovider scripts/test_candidate_level_attribution.py
```

This is a dev/test environment only. It is not runtime trading infrastructure.

## Current Preflight Snapshot

Source repo status:

```text
## main...origin/main
```

Source repo HEAD:

```text
b83fb38292a24f260f7372ab557326b2ba50093d
```

Source repo `origin/main`:

```text
b83fb38292a24f260f7372ab557326b2ba50093d
```

Source repo remote main:

```text
b83fb38292a24f260f7372ab557326b2ba50093d
```

Python version:

```text
Python 3.14.3
```

`requirements-dev.txt`:

```text
pytest
pytest-asyncio
```

Relevant `.gitignore` entries found:

```text
8:__pycache__/
14:venv/
16:.venv
40:logs/*.jsonl
86:.pytest_cache/
```

## Allowed Scope

Batch 5G may:

1. Create local-only `.venv/` inside `the-trading-guy`.
2. Install dev dependencies from `requirements-dev.txt` into `.venv` only.
3. Run the already-approved safe pytest subset only:

```bash
.venv/bin/python -m pytest -q -p no:cacheprovider scripts/test_candidate_level_attribution.py
```

4. Write setup audit evidence to `ai-labs/projects/trading-agents/`.
5. Commit that workspace audit evidence locally.

## Not Allowed

Batch 5G must not:

- Run live trading.
- Place orders.
- Run simulate-live.
- Add or touch StrategySignal-to-order bridge logic.
- Mutate runtime/default config.
- Read, print, or commit `.env` files.
- Install packages globally.
- Use `sudo`.
- Use `pip install --user`.
- Upgrade pip unless separately approved.
- Run the full test suite.
- Run replay or monitoring jobs.
- Stage or commit raw replay logs.
- Enable scheduler/cron/systemd.
- Push without explicit approval.

## Planned Commands

```bash
cd /home/julius/julius-workspace/ai-labs/projects/the-trading-guy

git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git ls-remote origin refs/heads/main
python --version
python -m venv --help
cat requirements-dev.txt

python -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q -p no:cacheprovider scripts/test_candidate_level_attribution.py

git status --short --branch
git ls-files .venv .pytest_cache
git ls-files '*.pyc' '*.jsonl'
```

Explicitly not planned:

```bash
.venv/bin/python -m pip install --upgrade pip
python -m pytest
```

## Stop Conditions

Stop and ask Julius if:

1. Source repo is not clean before setup.
2. Source repo HEAD, `origin/main`, and remote main are not aligned.
3. `requirements-dev.txt` is missing or unexpectedly broad.
4. `.venv/` is not ignored or would become tracked.
5. `python -m venv` is unavailable.
6. `pip install` requires sudo/global permissions.
7. Safe test requires `.env`, network, exchange access, or runtime mutation.
8. Test creates raw replay logs or tracked generated files.
9. Post-test git status shows source/config changes beyond ignored local cache/venv artifacts.

## Expected Output Files After Build

If build is approved and completed, write:

```text
ai-labs/projects/trading-agents/local-dev-test-env-setup-batch5g-2026-07-07.md
ai-labs/projects/trading-agents/local-dev-test-env-setup-batch5g-2026-07-07.json
```

Then commit locally with:

```text
docs(trading-agents): record local dev test env setup
```

## Push Policy

No push will be performed without explicit approval.
