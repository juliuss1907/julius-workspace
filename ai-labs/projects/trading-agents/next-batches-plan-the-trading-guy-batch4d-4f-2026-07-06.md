# Next Batches Plan — the-trading-guy Batch 4D–4F

Date: 2026-07-06

## Context

The standalone GitHub repo `the-trading-guy` has been split from `julius-workspace`, cleaned, and rewritten into a single clean commit.

Current remote:

```text
git@github.com:juliuss1907/the-trading-guy.git
```

Current clean single commit:

```text
89194f3009d7c0eabb91d505be4adea834d5d94d chore: initial standalone trading agents snapshot
```

Batch 4C status:

```text
Completed by Julius manual force-with-lease rewrite
Commit count: 1
Forbidden HEAD files: 0
Forbidden history paths: 0
```

## Global Safety Boundaries

These apply to all next batches:

- No live trading
- No order placement
- No simulate-live execution
- No StrategySignal-to-order mapping
- No runtime/default config changes unless Julius explicitly approves
- No raw replay logs committed
- No `.env` files read, printed, staged, or committed
- No unrelated/protected paths touched
- No auto-push without explicit approval
- No force-push by agent

---

# Batch 4D-A — Preserve Batch 4C Audit Evidence

## Goal

Preserve the Batch 4C rewrite evidence inside `julius-workspace` by committing the generated audit reports.

Current untracked files:

```text
ai-labs/projects/trading-agents/single-commit-rewrite-the-trading-guy-batch4c-2026-07-05.md
ai-labs/projects/trading-agents/single-commit-rewrite-the-trading-guy-batch4c-2026-07-05.json
```

## Scope

Only these two Batch 4C audit files should be staged and committed.

No source code, config, scripts, logs, outputs, raw replay logs, or `.env` files should be touched.

## Steps

1. Check workspace status.
2. Verify the two Batch 4C report files contain:
   - remote repo URL
   - final single commit hash
   - commit count = 1
   - forbidden files/history = 0
   - remote rewrite executed manually by Julius
   - agent did not execute force push
3. Stage only the two report files.
4. Commit locally with:

```text
docs(trading-agents): record clean repo rewrite audit
```

5. Do not push.
6. Provide a push proposal only if Julius asks or after all related report commits are grouped.

## Pass Criteria

```text
2 report files committed
No unrelated files staged
No raw logs committed
No .env committed
No remote push
```

---

# Batch 4D-B — Fresh Clone Integrity Audit for the-trading-guy

## Goal

Verify from a fresh clone that GitHub remote `the-trading-guy` is truly clean and single-commit.

This confirms the remote state independently of local temp repos.

## Scope

Read-only remote audit.

Clone into `/tmp`, for example:

```text
/tmp/batch4d-fresh-clone-the-trading-guy-YYYYMMDD-HHMMSS
```

No remote mutation. No push.

## Steps

1. Clone:

```bash
git clone git@github.com:juliuss1907/the-trading-guy.git /tmp/batch4d-fresh-clone-the-trading-guy-YYYYMMDD-HHMMSS/the-trading-guy
```

2. Verify remote URL:

```bash
git remote -v
```

3. Verify branch:

```bash
git branch --show-current
```

Expected:

```text
main
```

4. Verify HEAD:

```bash
git rev-parse HEAD
```

Expected:

```text
89194f3009d7c0eabb91d505be4adea834d5d94d
```

5. Verify commit count:

```bash
git rev-list --count HEAD
```

Expected:

```text
1
```

6. Verify file count:

```bash
find . -path './.git' -prune -o -type f -print | wc -l
```

Expected based on Batch 4C:

```text
341
```

7. Forbidden file scan for:

```text
.hermes/
.agent/
logs/
outputs/
venv/
.venv/
.pytest_cache/
__pycache__/
.env
.env.*
*.pyc
*.jsonl
```

Expected:

```text
0 forbidden files
```

8. Forbidden history path scan.

Expected:

```text
0 forbidden history paths
```

9. Conservative secret-marker scan, filenames only, for:

```text
PRIVATE_KEY
API_KEY
SECRET
TOKEN
PASSWORD
OPENAI_API_KEY
ANTHROPIC_API_KEY
BINANCE
BYBIT
```

This scan should not print matched values.

## Output

Write audit reports to:

```text
ai-labs/projects/trading-agents/fresh-clone-integrity-audit-the-trading-guy-batch4d-2026-07-06.md
ai-labs/projects/trading-agents/fresh-clone-integrity-audit-the-trading-guy-batch4d-2026-07-06.json
```

## Pass Criteria

```text
Remote HEAD == 89194f3009d7c0eabb91d505be4adea834d5d94d
Commit count == 1
Forbidden files == 0
Forbidden history paths == 0
File count == 341
No raw replay logs
No .env
No .hermes
```

---

# Batch 4D-C — Safe Read-Only Sanity Checks from Fresh Clone

## Goal

Verify that the standalone repo is usable from a fresh clone without executing trading, simulate-live, external order logic, or runtime state mutation.

## Scope

Run only safe checks inside the Batch 4D-B fresh clone.

No remote mutation. No config mutation. No dependency install without Julius approval.

## Candidate Checks

### Check 1 — Python syntax compile

Preferred safe check:

```bash
python -m compileall agents config dataflows policies scripts strategies trading utils
```

If needed, broaden to:

```bash
python -m compileall .
```

But avoid noisy generated/local directories if any appear.

### Check 2 — Import-light strategy probe

Only after inspecting import safety:

```bash
python - <<'PY'
import strategies.registry
import strategies.volatility_skip
import strategies.trend_following
import strategies.breakout
print('ok')
PY
```

Do not run if inspection suggests network/API side effects.

### Check 3 — Candidate-level attribution tests

If dependencies are available and tests are network-free:

```bash
pytest scripts/test_candidate_level_attribution.py
```

If `pytest` or dependencies are missing, do not install automatically. Report missing dependency.

### Check 4 — Dependency readiness dry audit

If confirmed safe by inspection:

```bash
python scripts/check_replay_dependency_readiness.py
```

Do not run if it touches external APIs or live data.

## Explicitly Forbidden

Do not run:

```text
run_paper_trading.py
run_readonly_monitoring_cadence.py if it may call live data
replay_signals.py if it may call external APIs
telegram_bot/bot.py
trading execution scripts
anything with order placement
anything simulate-live
anything that mutates state
```

## Output

Write reports to:

```text
ai-labs/projects/trading-agents/fresh-clone-sanity-checks-the-trading-guy-batch4d-2026-07-06.md
ai-labs/projects/trading-agents/fresh-clone-sanity-checks-the-trading-guy-batch4d-2026-07-06.json
```

## Pass Criteria

Minimum:

```text
Fresh clone exists
Commit count == 1
Safe checks executed or explicitly skipped with reason
No live trading
No simulate-live
No order placement
No state mutation
```

Ideal:

```text
compileall passes
candidate-level attribution tests pass
safe dependency readiness check passes or reports expected missing optional deps
```

---

# Batch 4E — Standalone Repo Onboarding Polish

## Goal

Make `the-trading-guy` understandable and usable as a standalone repository.

The repo should clearly explain what it is, how to set it up safely, and what safety boundaries apply.

## Scope

Likely files in standalone repo:

```text
README.md
docs/SAFETY.md
docs/MONITORING.md
```

Optional:

```text
docs/SETUP.md
docs/REPO_HISTORY.md
```

Do not overbuild documentation. Start with README + safety/monitoring docs.

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

## Docs Targets

### `docs/SAFETY.md`

Should document:

- no live trading
- no order placement
- no simulate-live
- no default runtime config changes
- no `.env` commits
- no raw logs
- manual approval gates

### `docs/MONITORING.md`

Should document:

- manual-only cadence
- what reports exist
- what metrics mean
- volatility-skip direct block rate caveat
- candidate-level attribution summary

## Pass Criteria

```text
README clearly explains project
Safety boundaries visible near top
Setup instructions do not require secrets
No .env.example added unless intentionally sanitized and approved
No live trading instructions
Manual-only cadence documented
```

## Output

A docs commit in `the-trading-guy`, for example:

```text
docs: polish standalone repo onboarding
```

Push requires separate Julius approval.

---

# Batch 4F — Decide Source-of-Truth Workflow

## Goal

Decide where active development should happen now that `the-trading-guy` exists as a standalone repo.

Current duplicated locations:

```text
/home/julius/julius-workspace/ai-labs/projects/trading-agents
git@github.com:juliuss1907/the-trading-guy.git
```

## Option A — Workspace remains source of truth

```text
julius-workspace/ai-labs/projects/trading-agents = dev source
the-trading-guy = release mirror
```

### Pros

- Minimal workflow change
- Existing audit/report context stays in workspace

### Cons

- Easy for workspace and standalone repo to drift
- Future sync requires subtree/filter process again
- Workspace artifacts may leak if not carefully filtered

## Option B — `the-trading-guy` becomes source of truth

```text
the-trading-guy = active project repo
julius-workspace = orchestration/audit workspace
```

### Pros

- Cleanest long-term
- Standalone repo becomes the real project repo
- Easier CI, releases, GitHub workflow, collaboration
- Avoids repeated subtree/filter operations

### Cons

- Requires workflow transition
- Existing workspace copy becomes reference/archive
- Cleanup requires explicit delete/archive approval due workspace rules

## Recommendation

Choose Option B after Batch 4D confirms fresh clone integrity and sanity checks.

Recommended state:

```text
the-trading-guy = source of truth
julius-workspace/ai-labs/projects/trading-agents = archived/reference copy until cleanup is approved
```

## Steps

1. Write source-of-truth decision note:

```text
ai-labs/projects/trading-agents/source-of-truth-decision-the-trading-guy-batch4f-2026-07-06.md
```

2. If Option B is chosen, document:
   - future code changes happen in standalone repo
   - workspace keeps audit/report notes
   - no more subtree split flow unless explicitly needed

3. If cleanup is desired:
   - create delete/archive request in `tasks/inbox/`
   - wait for Julius approval
   - do not delete automatically

## Pass Criteria

```text
Source-of-truth decision documented
Future workflow is clear
No deletion executed
No remote rewrite
No push without approval
```

---

# Recommended Execution Order

```text
1. Batch 4D-A — Commit Batch 4C audit reports in julius-workspace
2. Batch 4D-B — Fresh clone integrity audit for the-trading-guy
3. Batch 4D-C — Safe read-only sanity checks from fresh clone
4. Batch 4E — Standalone repo onboarding polish
5. Batch 4F — Decide source-of-truth workflow
```

## Recommended Next Command

```text
Build Batch 4D-A — Commit Batch 4C audit reports
```
