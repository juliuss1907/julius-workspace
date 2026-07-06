# Batch 4F — Source-of-Truth Workflow Decision for the-trading-guy

Date: 2026-07-06

## Decision

**Option B is selected:** `the-trading-guy` becomes the source of truth for the trading agents project.

From this point forward:

~~~text
git@github.com:juliuss1907/the-trading-guy.git
~~~

is the active project repository for code and standalone project documentation.

## Context

The project was originally developed inside:

~~~text
/home/julius/julius-workspace/ai-labs/projects/trading-agents
~~~

It has now been split into a standalone GitHub repository:

~~~text
git@github.com:juliuss1907/the-trading-guy.git
~~~

Current remote `main` at decision time:

~~~text
a8bf806e0a8e733b9937e737d49abe4408a0ab21
~~~

Recent completed milestones:

- Batch 4C: clean single-commit remote rewrite completed.
- Batch 4D-B: fresh clone integrity audit passed.
- Batch 4D-C: safe read-only sanity checks passed.
- Batch 4D-D: workspace staging/index cleanup completed.
- Batch 4E: standalone onboarding docs polished and pushed.

## Source-of-Truth Rule

### Active development

Future code and standalone docs changes should happen in a dedicated clone of:

~~~text
git@github.com:juliuss1907/the-trading-guy.git
~~~

This includes changes to:

- `README.md`
- `docs/`
- `agents/`
- `strategies/`
- `scripts/`
- `trading/`
- `config/`, if explicitly approved
- all future project-level implementation files

### Workspace copy

The workspace copy remains as a historical/audit/reference copy:

~~~text
/home/julius/julius-workspace/ai-labs/projects/trading-agents
~~~

It may still store Hermes operation records, audit reports, decision notes, and migration evidence, but it should no longer be treated as the active development source for the standalone project.

## Workflow Going Forward

Recommended workflow:

1. Use a fresh or dedicated clone of `the-trading-guy` for active development.
2. Make project code/docs commits in the standalone repo.
3. Push from standalone repo only after Julius approves.
4. Keep workspace reports as audit evidence when needed.
5. Do not use subtree/filter flows again unless explicitly requested.
6. Do not copy workspace-local artifacts into the standalone repo.

## Safety Boundaries Preserved

The source-of-truth decision does not change the existing safety boundaries:

- No live trading.
- No order placement.
- No simulate-live execution unless explicitly approved.
- No StrategySignal-to-order mapping.
- No runtime/default config changes unless explicitly approved.
- No scheduler/cron/systemd enablement unless explicitly approved.
- No raw replay logs committed.
- No `.env` files committed, read, or printed.
- No secrets committed.
- No push without Julius approval.
- No force push by agent.

## Workspace Cleanup Policy

No workspace deletion is performed in Batch 4F.

The old workspace project copy is retained for now as a reference/audit copy. If Julius later wants to archive or delete it, that should be handled in a separate explicit cleanup batch or delete/archive request.

Potential future cleanup batch:

~~~text
Batch 4G — Archive/Delete Request for old workspace trading-agents copy
~~~

## Impact

This decision reduces future drift and avoids repeated subtree/filter work.

Expected benefits:

- Cleaner project workflow.
- Standalone repo becomes the real project repo.
- Lower risk of workspace artifacts leaking into the project.
- Easier future CI/release/docs management.

## Execution Status

- Decision documented: yes
- Deletion executed: no
- Repo rewrite executed: no
- Push executed: no
- Knowledge-base changes: none
- Live trading/order/simulate-live: not executed

## Final Decision Statement

`the-trading-guy` is now the source of truth for the trading agents project.

`julius-workspace/ai-labs/projects/trading-agents` is retained as a historical/audit/reference copy until Julius explicitly decides otherwise.
