# Batch 5A Plan — Source-of-Truth Working Clone Setup

Date: 2026-07-07

## Goal

Set up a stable local working clone for the new source-of-truth repository:

~~~text
git@github.com:juliuss1907/the-trading-guy.git
~~~

This follows Batch 4F, where Julius selected **Option B**:

~~~text
the-trading-guy = source of truth
julius-workspace/ai-labs/projects/trading-agents = historical/audit/reference copy
~~~

## Current Remote State

Remote `main` at plan time:

~~~text
a8bf806e0a8e733b9937e737d49abe4408a0ab21
~~~

Expected recent repo state:

~~~text
89194f3 chore: initial standalone trading agents snapshot
a8bf806 docs: polish standalone repo onboarding
~~~

So expected commit count is currently:

~~~text
2
~~~

## Recommended Target Path

Recommended stable local working clone path:

~~~text
/home/julius/julius-workspace/ai-labs/projects/the-trading-guy
~~~

Reasoning:

- It is inside `ai-labs/projects/`, where project work is allowed.
- It is separate from the old audit/reference copy at `ai-labs/projects/trading-agents`.
- It makes the new source-of-truth repo easy to locate.
- It avoids using temporary `/tmp` clones for ongoing work.

## Approval Needed Before Build

Before Batch 5A creates the clone, Julius should approve the target path because this creates a new project folder under `ai-labs/projects/`.

Recommended approval phrase:

~~~text
Approve Batch 5A working clone target: /home/julius/julius-workspace/ai-labs/projects/the-trading-guy
~~~

If Julius prefers another path, update the target before build.

## Scope

Batch 5A should:

- Verify the target path does not already exist.
- Clone `the-trading-guy` into the approved target path.
- Verify remote URL.
- Verify branch is `main`.
- Verify HEAD equals current GitHub `main`.
- Verify commit count is expected.
- Verify onboarding docs exist.
- Run repo hygiene scan for forbidden files.
- Write setup audit report in the old workspace audit/reference folder.
- Commit only the setup audit report in `julius-workspace`, if report is created and Julius wants evidence preserved.

Batch 5A should **not**:

- Modify project code.
- Install dependencies.
- Run live trading.
- Run simulate-live.
- Place orders.
- Run external API scripts.
- Change runtime/default config.
- Push any repo.
- Delete anything.

## Proposed Build Steps

### Step 1 — Preflight

From workspace root:

~~~bash
cd /home/julius/julius-workspace
~~~

Check target path:

~~~bash
test ! -e /home/julius/julius-workspace/ai-labs/projects/the-trading-guy
~~~

If the path exists, stop and audit it instead of overwriting.

### Step 2 — Clone source-of-truth repo

~~~bash
git clone git@github.com:juliuss1907/the-trading-guy.git /home/julius/julius-workspace/ai-labs/projects/the-trading-guy
~~~

### Step 3 — Verify clone identity

Inside the new clone:

~~~bash
cd /home/julius/julius-workspace/ai-labs/projects/the-trading-guy
git remote -v
git branch --show-current
git rev-parse HEAD
git rev-list --count HEAD
git log --oneline -5
~~~

Expected:

~~~text
remote = git@github.com:juliuss1907/the-trading-guy.git
branch = main
HEAD = a8bf806e0a8e733b9937e737d49abe4408a0ab21
commit count = 2, unless new approved commits were added after this plan
~~~

### Step 4 — Verify onboarding docs

Required files:

~~~text
README.md
docs/SAFETY.md
docs/MONITORING.md
~~~

Required safety content:

~~~text
No live trading
No order placement
No simulate-live
No StrategySignal-to-order bridge
manual-only monitoring
volatility_skip_direct_block_rate caveat
~~~

### Step 5 — Forbidden file scan

Scan for forbidden/local/generated paths:

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

Expected:

~~~text
0 forbidden files
~~~

### Step 6 — Secret marker filename-only scan

Conservative scan, filenames only / no matched values printed, for markers like:

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

This is awareness only and may catch placeholders such as `os.getenv("BINANCE_API_KEY")`.

### Step 7 — Write setup audit report

Write audit output to the old workspace audit/reference folder:

~~~text
ai-labs/projects/trading-agents/source-of-truth-working-clone-setup-batch5a-2026-07-07.md
ai-labs/projects/trading-agents/source-of-truth-working-clone-setup-batch5a-2026-07-07.json
~~~

### Step 8 — Optional local commit in julius-workspace

If the audit report is created, commit only those report files with:

~~~text
docs(trading-agents): record source-of-truth clone setup
~~~

No push unless Julius approves.

## Pass Criteria

~~~text
Working clone exists at approved target path
Remote URL is correct
Branch is main
HEAD equals GitHub main at setup time
Commit count is expected
README.md exists
docs/SAFETY.md exists
docs/MONITORING.md exists
Forbidden files = 0
No dependency install
No code changes
No live trading
No order placement
No simulate-live
No runtime/default config changes
No push
~~~

## Failure / Stop Conditions

Stop and ask Julius if:

- Target path already exists.
- Remote HEAD differs unexpectedly.
- Forbidden files are found.
- Onboarding docs are missing.
- Git clone fails.
- Any command would require credentials or external API execution beyond Git clone/fetch.

## Safety Boundaries

- Live trading: not executed.
- Order placement: not executed.
- Simulate-live: not executed.
- StrategySignal-to-order mapping: not added.
- Runtime/default config changes: not changed.
- Dependency install: not executed.
- Raw replay logs committed: none.
- `.env` files read/printed/committed: none.
- Scheduler/cron/systemd enabled: no.
- Push: no.
- Delete: no.

## Recommended Next Command

After Julius approves the target path:

~~~text
Approve Batch 5A working clone target: /home/julius/julius-workspace/ai-labs/projects/the-trading-guy
~~~

Then:

~~~text
Build Batch 5A — Source-of-Truth Working Clone Setup
~~~
