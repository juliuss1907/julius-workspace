# Batch 5B Plan — CI / Safety Workflow Proposal for the-trading-guy

Date: 2026-07-07

## Goal

Design a lightweight CI / safety workflow for the source-of-truth repo:

~~~text
git@github.com:juliuss1907/the-trading-guy.git
~~~

The goal is to preserve repo hygiene after the migration by making every push/PR check for obvious safety violations before project work continues.

## Current Source-of-Truth State

- Working clone: \
- Working clone status: \
- Working clone branch: \
- Working clone HEAD: \
- Working clone commit count: \
- Working clone status lines: \
- Remote `main`: \

Batch 5A established this clone as the stable local working copy for future source-of-truth work.

## Important Scope Decision

Batch 5B should begin as a **proposal/design batch**, not an immediate CI implementation batch.

Reason:

- CI affects future development workflow.
- We should agree which checks are blocking vs warning-only.
- Some tests may require dependencies or external APIs and should not be added blindly.
- No GitHub Actions workflow should be added until Julius approves the proposed CI shape.

## Non-Goals

Batch 5B must not:

- Enable live trading.
- Place orders.
- Run simulate-live flows.
- Add StrategySignal-to-order mapping.
- Change runtime/default config.
- Install dependencies without approval.
- Add secrets or `.env` files.
- Add raw replay logs or `.jsonl` files.
- Enable scheduler/cron/systemd automation.
- Push without approval.

## Proposed CI Checks

### Check 1 — Forbidden files / repo hygiene

Fail CI if any forbidden/local/generated path exists:

~~~text
.env
.env.*
logs/
outputs/
.agent/
.hermes/
venv/
.venv/
.pytest_cache/
__pycache__/
*.pyc
*.jsonl
~~~

Rationale:

- Prevent credentials from leaking.
- Prevent raw replay logs from being committed.
- Prevent local workspace artifacts from entering source-of-truth repo.

### Check 2 — Required docs presence

Fail CI if these are missing:

~~~text
README.md
docs/SAFETY.md
docs/MONITORING.md
~~~

Required phrase checks should include:

~~~text
No live trading
No order placement
No simulate-live
No StrategySignal-to-order bridge
manual-only
volatility_skip_direct_block_rate
~~~

### Check 3 — Python syntax check without bytecode

Prefer an AST parser script over `compileall` to avoid writing `__pycache__` or `.pyc` files.

Proposed source directories:

~~~text
agents
config
dataflows
orchestration
policies
scripts
strategies
telegram_bot
trading
utils
watchlist
~~~

### Check 4 — Secret-marker awareness scan

Conservative scan for marker names only:

~~~text
PRIVATE_KEY
API_KEY
SECRET
TOKEN
PASSWORD
OPENAI_API_KEY
ANTHROPIC_API_KEY
BINANCE
BYBIT
~~~

Recommended initial behavior:

~~~text
warning-only, filenames only, do not print matched values
~~~

Rationale:

- Code legitimately references environment variable names like `BINANCE_API_KEY`.
- A blocking secret-marker check may create false positives.

### Check 5 — Safe test subset proposal

Do not add full pytest suite to CI until Batch 5C classifies tests.

Initial CI should either:

1. skip pytest, or
2. run only explicitly safe unit tests after Batch 5C confirms them.

Candidate safe test to inspect in Batch 5C:

~~~text
scripts/test_candidate_level_attribution.py
~~~

## Proposed Future Implementation Files

Only after Julius approves Batch 5B build/implementation:

~~~text
.github/workflows/safety-checks.yml
scripts/ci_forbidden_files_check.py
scripts/ci_syntax_check.py
scripts/ci_required_docs_check.py
~~~

Optional later:

~~~text
scripts/ci_secret_marker_scan.py
~~~

## Proposed GitHub Actions Shape

Potential workflow:

~~~yaml
name: Safety Checks

on:
  pull_request:
  push:
    branches: [main]

jobs:
  safety:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: python scripts/ci_forbidden_files_check.py
      - run: python scripts/ci_required_docs_check.py
      - run: python scripts/ci_syntax_check.py
~~~

## Recommended Batch 5B Execution Plan

### Phase 5B-Plan

This current plan:

- Document desired CI checks.
- Decide blocking vs warning-only checks.
- Do not modify source-of-truth repo yet.
- Do not push.

### Phase 5B-Build, after approval

If Julius approves CI implementation:

1. Work in source-of-truth clone:

~~~text
/home/julius/julius-workspace/ai-labs/projects/the-trading-guy
~~~

2. Add minimal CI scripts and workflow.
3. Run the CI scripts locally.
4. Commit locally in `the-trading-guy`:

~~~text
ci: add repository safety checks
~~~

5. Request push approval before pushing.

## Relationship to Batch 5C

Batch 5C should audit dependencies and tests before enabling pytest in CI.

Recommended sequence:

~~~text
Batch 5B — approve/implement hygiene + docs + syntax CI
Batch 5C — classify dependencies/tests
Batch 5D — optionally add safe test subset to CI
~~~

## Pass Criteria for Batch 5B Plan

~~~text
CI proposal documented
Blocking vs warning checks proposed
No source-of-truth repo code changes yet
No workflow file added yet
No dependency install
No live trading
No order placement
No simulate-live
No push
~~~

## Safety Boundaries

- Live trading: not executed.
- Order placement: not executed.
- Simulate-live: not executed.
- StrategySignal-to-order mapping: not added.
- Runtime/default config changes: not changed.
- Dependency install: not executed.
- External API calls: not executed.
- Secrets printed: none.
- Scheduler/cron/systemd enabled: no.
- Push: no.

## Recommended Next Command

After reviewing this plan, Julius can approve implementation with:

~~~text
Build Batch 5B — CI Safety Workflow Proposal
~~~

If Julius wants implementation immediately after the proposal, use:

~~~text
Approve Batch 5B implementation — add hygiene/docs/syntax CI only
~~~
