# Batch 5D Plan — Dev Dependency / Safe Test CI Proposal

Date: 2026-07-07

## Goal

Design the next safe CI extension for the source-of-truth repo:

~~~text
git@github.com:juliuss1907/the-trading-guy.git
~~~

Batch 5D should decide how to make pytest available and whether to add a **safe pytest subset** to CI, starting with:

~~~text
scripts/test_candidate_level_attribution.py
~~~

This is a proposal/design batch first. It should not install dependencies or modify the source repo unless Julius explicitly approves implementation.

## Current Source-of-Truth State

- Working clone: \
- Working clone exists: \
- Working clone branch: \
- Working clone HEAD: \
- Working clone commit count: \
- Working clone status lines: \
- Remote `main`: \

Recent completed batches:

- Batch 5A: stable source-of-truth clone created.
- Batch 5B: hygiene/docs/syntax CI added and pushed.
- Batch 5C: dependency/test readiness audited.

## Batch 5C Findings To Build On

Batch 5C found:

~~~text
requirements.txt exists
requirements-dev.txt missing
pytest is declared in requirements.txt
pytest-asyncio is declared in requirements.txt
local environment does not currently have pytest available
67 test files discovered
scripts/test_candidate_level_attribution.py classified safe
candidate attribution test was skipped because pytest unavailable
~~~

## Core Decision

Batch 5D should answer:

> How should the project provide dev/test dependencies for CI without over-installing runtime/API-heavy dependencies?

And:

> Should the safe candidate-level attribution test be added to CI after pytest availability is solved?

## Options

### Option A — Use existing requirements.txt in CI

Install:

~~~bash
pip install -r requirements.txt
~~~

Then run:

~~~bash
python -m pytest -q -p no:cacheprovider scripts/test_candidate_level_attribution.py
~~~

#### Pros

- No new dependency file.
- Uses current dependency declaration.
- Likely includes pytest already.

#### Cons

- Installs broad runtime/API-related dependencies.
- Slower CI.
- Pulls in exchange/API/LLM/Telegram libraries not needed for the safe unit test.
- Increases CI surface area unnecessarily.

### Option B — Add minimal requirements-dev.txt

Add a minimal dev dependency file, e.g.:

~~~text
pytest
pytest-asyncio
~~~

Then CI installs:

~~~bash
pip install -r requirements-dev.txt
~~~

#### Pros

- Clear dev/test dependency boundary.
- Lightweight CI.
- Avoids installing exchange/API-heavy runtime dependencies.
- Easier to expand later.

#### Cons

- Adds a new dependency declaration file.
- Dependency additions require Julius approval.
- Version pinning decision needed.

### Option C — Install pytest directly in GitHub Actions

CI step:

~~~bash
pip install pytest pytest-asyncio
~~~

#### Pros

- Simple initial implementation.
- No new dependency file.

#### Cons

- Dependencies are hidden in workflow instead of a repo dependency file.
- Harder to reuse locally.
- Less clean long-term.

## Recommendation

Recommend **Option B**:

~~~text
Add minimal requirements-dev.txt for safe tests / CI-only dev dependencies.
~~~

Initial content should be minimal and only include:

~~~text
pytest
pytest-asyncio
~~~

Version strategy can be either:

1. Development-friendly loose pins:

~~~text
pytest
pytest-asyncio
~~~

2. More reproducible exact pins after checking available/current versions:

~~~text
pytest==<approved-version>
pytest-asyncio==<approved-version>
~~~

For this project stage, the safer process is:

- Plan first.
- Ask Julius for dependency-file approval.
- Add minimal dev requirements only after approval.
- Run only the known safe test first.

## Proposed Batch 5D Implementation Scope After Approval

If Julius approves implementation, Batch 5D-build should modify source repo:

~~~text
/home/julius/julius-workspace/ai-labs/projects/the-trading-guy
~~~

Proposed files to change:

~~~text
requirements-dev.txt
.github/workflows/safety-checks.yml
~~~

Optional new helper script only if needed:

~~~text
scripts/ci_safe_tests_check.py
~~~

But simplest implementation:

1. Add `requirements-dev.txt`.
2. Update GitHub Actions workflow:

~~~yaml
      - name: Install dev test dependencies
        run: pip install -r requirements-dev.txt

      - name: Run safe pytest subset
        run: python -m pytest -q -p no:cacheprovider scripts/test_candidate_level_attribution.py
~~~

## Safe Test Subset v1

Initial safe test subset should include only:

~~~text
scripts/test_candidate_level_attribution.py
~~~

Do not add the full test suite yet.

Reason:

- Batch 5C discovered 67 test files.
- Many tests may involve network/API/trading/state markers.
- Full suite requires a separate classification/refactor strategy.

## Local Validation Plan If Implemented

Before committing implementation:

1. Verify source repo clean and aligned with remote main.
2. Add `requirements-dev.txt` and workflow update.
3. Do **not** install dependencies locally unless Julius separately approves local install.
4. If pytest is still unavailable locally, document local pytest run as skipped.
5. Existing CI scripts should still pass:

~~~bash
python scripts/ci_forbidden_files_check.py
python scripts/ci_required_docs_check.py
python scripts/ci_syntax_check.py
~~~

6. If local pytest is available, run:

~~~bash
python -m pytest -q -p no:cacheprovider scripts/test_candidate_level_attribution.py
~~~

7. Commit source repo locally:

~~~text
ci: add safe pytest subset
~~~

8. Request push approval.

## Explicit Non-Goals

Batch 5D must not:

- Install dependencies without approval.
- Add broad/full pytest suite to CI.
- Run live trading.
- Place orders.
- Run simulate-live.
- Run external API scripts.
- Run exchange account calls.
- Run Telegram bot runtime.
- Run state mutation scripts.
- Change runtime/default config.
- Enable scheduler/cron/systemd.
- Read/print/commit `.env`.
- Commit raw replay logs.
- Push without approval.

## Safety Boundaries

- Live trading: not executed.
- Order placement: not executed.
- Simulate-live: not executed.
- StrategySignal-to-order mapping: not added.
- Runtime/default config changes: not changed.
- Dependency install: not executed unless separately approved.
- External API calls: not executed.
- Secrets printed: none.
- `.env` files read/printed/committed: none.
- Raw replay logs committed: none.
- Scheduler/cron/systemd enabled: no.
- Push: no without approval.

## Pass Criteria For This Planning Batch

~~~text
Plan documented
Options compared
Recommended dev dependency strategy selected
Safe test subset v1 identified
No source repo code changes
No dependency install
No test execution
No push
~~~

## Recommended Approval Phrase For Implementation

If Julius agrees with Option B:

~~~text
Approve Batch 5D implementation — add minimal requirements-dev and safe candidate attribution test to CI
~~~

Then the implementation batch can proceed.
