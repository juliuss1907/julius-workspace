# Batch 5C Plan — Dependency & Test Readiness Audit

Date: 2026-07-07

## Goal

Audit dependency and test readiness for the source-of-truth repo:

```text
git@github.com:juliuss1907/the-trading-guy.git
```

Batch 5C answers:

1. What dependency files exist?
2. What tests exist?
3. Which tests are safe unit/import tests?
4. Which tests require network, credentials, exchange APIs, state mutation, or trading behavior?
5. Whether pytest/dev dependencies are available.
6. What should be added to CI later, and what should remain excluded.

This is an **audit-first** batch. It should not install dependencies or modify project code.

## Current Source-of-Truth State

- Working clone: `/home/julius/julius-workspace/ai-labs/projects/the-trading-guy`
- Working clone exists: `True`
- Working clone branch: `main`
- Working clone HEAD: `60eec5639f6fcb9c49eef70947908fb1803b449c`
- Working clone commit count: `3`
- Working clone status lines: `0`
- Remote `main`: `60eec5639f6fcb9c49eef70947908fb1803b449c`

Batch 5B already added repository safety CI checks:

```text
.github/workflows/safety-checks.yml
scripts/ci_forbidden_files_check.py
scripts/ci_required_docs_check.py
scripts/ci_syntax_check.py
```

Batch 5C should decide what, if anything, is safe to add next.

## Scope

Allowed in Batch 5C:

- Inspect dependency files.
- Inspect test files.
- Classify tests by safety category.
- Run already-approved local CI safety scripts.
- Check whether pytest is available.
- Run only tests classified as safe and dependency-ready.
- Write audit report in the old workspace audit/reference folder.
- Commit only the audit report in `julius-workspace` if generated.

Not allowed in Batch 5C:

- No dependency install.
- No live trading.
- No order placement.
- No simulate-live execution.
- No external API calls.
- No exchange account calls.
- No Telegram bot runtime.
- No state mutation scripts.
- No runtime/default config changes.
- No scheduler/cron/systemd enablement.
- No `.env` read/print/commit.
- No raw replay logs staged or committed.
- No push without approval.

## Files and Areas to Inspect

### Dependency files

Inspect whether these exist:

```text
requirements.txt
requirements-dev.txt
pyproject.toml
setup.py
setup.cfg
Pipfile
poetry.lock
```

Record:

- dependency file presence
- whether pytest is listed
- whether dev/test dependencies are separated
- whether dependency pins are loose or exact
- whether any dependency appears to imply external services

### Test files

Find test candidates with:

```bash
find . -name 'test_*.py' -o -name '*_test.py'
```

Classify each as:

```text
safe_unit
safe_import_or_attribution
requires_pytest_only
requires_optional_dependency
requires_network
requires_exchange_api
requires_credentials
mutates_state
trading_or_order_related
unknown_requires_review
```

### Scripts that must not be run by default

Do not run scripts that appear related to:

```text
paper trading
live trading
order placement
position sync
reconciliation
Telegram bot runtime
external exchange/API data fetch
simulate-live flows
scheduler/cadence execution
```

Examples likely requiring caution:

```text
scripts/run_paper_trading.py
scripts/replay_signals.py
scripts/run_readonly_monitoring_cadence.py
scripts/reconcile_positions.py
scripts/reconcile_futures_positions.py
scripts/sync_futures_positions_to_db.py
telegram_bot/bot.py
```

## Proposed Audit Steps

### Step 1 — Preflight source repo

From source-of-truth clone:

```bash
cd /home/julius/julius-workspace/ai-labs/projects/the-trading-guy
git status --short --untracked-files=all
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

Expected:

```text
working tree clean
HEAD == remote main
```

If the working tree is dirty or local HEAD differs from remote main, stop and ask Julius.

### Step 2 — Run existing safety CI scripts

These were added in Batch 5B and are safe by design:

```bash
python scripts/ci_forbidden_files_check.py
python scripts/ci_required_docs_check.py
python scripts/ci_syntax_check.py
```

Expected:

```text
forbidden_files_check=ok
required_docs_check=ok
syntax_check=ok
```

### Step 3 — Inspect dependency metadata

Read filenames and dependency declarations only. Do not install.

Record:

```text
which dependency files exist
whether pytest is included
whether requirements-dev.txt exists
whether dependency files mention exchange/API libraries
```

### Step 4 — Discover and classify tests

Find test files and inspect imports/function names enough to classify risk.

Do not execute unknown tests.

### Step 5 — Check pytest availability

Safe command:

```bash
python -m pytest --version
```

If unavailable:

```text
record missing pytest; do not install
```

### Step 6 — Run only explicitly safe tests, if available

Candidate safe test from prior work:

```text
scripts/test_candidate_level_attribution.py
```

Only run it if inspection confirms:

- no network
- no exchange API
- no credentials
- no state mutation
- no order placement
- pytest is available

Command if safe:

```bash
python -m pytest scripts/test_candidate_level_attribution.py
```

If pytest is missing or classification is not fully safe, skip and document why.

### Step 7 — Dependency readiness checker decision

Inspect:

```text
scripts/check_replay_dependency_readiness.py
```

Only run if it is confirmed to be read-only and not network/API dependent.

Otherwise, classify it as `deferred_requires_dedicated_review`.

### Step 8 — Write Batch 5C audit report

Write:

```text
ai-labs/projects/trading-agents/dependency-test-readiness-audit-batch5c-2026-07-07.md
ai-labs/projects/trading-agents/dependency-test-readiness-audit-batch5c-2026-07-07.json
```

Recommended report sections:

- source repo state
- dependency files discovered
- pytest availability
- tests discovered
- test safety classification
- safe tests run / skipped
- dependency checker decision
- CI recommendation
- next actions

### Step 9 — Optional local workspace commit

If report is created and validated, commit only those report files in `julius-workspace`:

```text
docs(trading-agents): add dependency test readiness audit
```

No push unless Julius approves.

## Expected Outcomes

### Outcome A — Safe test subset ready

If `scripts/test_candidate_level_attribution.py` or similar tests are safe and runnable:

- document as CI candidate
- propose Batch 5D to add safe pytest subset to CI

### Outcome B — Missing pytest/dev deps

If pytest is unavailable:

- document missing pytest
- propose `requirements-dev.txt` or dev dependency strategy
- do not install automatically

### Outcome C — Tests require API/credentials/state

If tests are unsafe/mixed:

- classify unsafe tests
- exclude from CI
- propose refactor or marking strategy later

## Pass Criteria

```text
Source repo preflight passed
Existing Batch 5B CI scripts pass
Dependency files inspected
Tests discovered and classified
No dependency install
No external API calls
No live trading/order/simulate-live
No state mutation scripts run
Safe tests run only if confirmed safe and dependencies available
Audit report created
Next recommendations clear
No push without approval
```

## Safety Boundaries

- Live trading: not executed.
- Order placement: not executed.
- Simulate-live: not executed.
- StrategySignal-to-order mapping: not added.
- Runtime/default config changes: not changed.
- Dependency install: not executed.
- External API calls: not executed.
- Secrets printed: none.
- `.env` files read/printed/committed: none.
- Raw replay logs committed: none.
- Scheduler/cron/systemd enabled: no.
- Push: no.

## Recommended Next Command

```text
Build Batch 5C — Dependency & Test Readiness Audit
```
