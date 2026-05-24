# Plan Discovery & Confirmation Recipe

> How to find and present Feynman plans when using the interactive workflow.

## Problem

Feynman writes plans to `/tmp/outputs/.plans/<slug>.md`, which differs from the `workdir` set at launch. When Feynman stops and shows "Proceed with this deep research plan?", the agent needs to:
1. Find the plan file
2. Read and summarize it for Julius
3. Wait for confirmation before proceeding

## Two Approaches

### Approach A: Interactive PTY (Julius reviews plan)

Use when Julius wants to approve the plan before Feynman spawns subagents.

1. Launch Feynman with `pty=true, background=true`
2. Poll until "Proceed" prompt appears in log
3. Find and read plan from `/tmp/outputs/.plans/<slug>.md`
4. Summarize for Julius
5. Wait for confirmation, then `process(action="submit", data="yes")`

**⚠️ Warning:** `process submit` to PTY is unreliable (ignored 2/2 times in session 2026-05-22). If Feynman doesn't react after submit, kill the process and use Approach B instead.

### Approach B: Pexpect runner (auto-confirm, reliable)

Use when Julius already approved the plan (or for unattended/cron runs).

```bash
terminal(
  command="/usr/bin/python3 ~/julius-workspace/.hermes/skills/autonomous-ai-agents/feynman/references/pexpect-runner.py '<topic>'",
  background=true,
  notify_on_complete=true,
  timeout=900
)
```

The pexpect script holds a real PTY and `sendline("yes")` works reliably. It auto-confirms after plan generation. See `references/pexpect-runner.py` for the full script.

### When to use which

| Scenario | Approach |
|----------|----------|
| Julius wants to review plan first | A (try submit, fall back to B if submit fails) |
| Julius says "cứ chạy đi, không cần review" | B |
| Cron job / unattended | B |
| First time testing a new topic | A (let Julius see the plan structure) |

## Discovery Commands

### Find the latest plan (when slug is unknown)
```bash
find /tmp -name '*.md' -path '*/.plans/*' -type f 2>/dev/null
```
Example output: `/tmp/outputs/.plans/ai-agent-trading.md`

### Find plans by topic keyword
```bash
find /tmp -name '*.md' -path '*/.plans/*' -type f -newer /tmp -mmin -10 2>/dev/null
```
This finds plans modified in the last 10 minutes.

### Read the plan
```bash
read_file("/tmp/outputs/.plans/<slug>.md")
```

## Plan Structure

Feynman plans follow this structure:
```markdown
# Plan: <Topic>
**Slug:** <slug>
**Date:** YYYY-MM-DD
**Scale:** <direct|multi-faceted survey — N researcher subagents>

## Key Questions
1. ...
2. ...

## Evidence Needed
| Evidence Type | Sources |
|---|---|

## Scale Decision
...

## Task Ledger
| Step | Task | Owner | Status |
|---|---|---|---|

## Verification Log
| Check | Status |
|---|---|

## Decision Log
| Decision | Rationale |
|---|---|
```

## Summary Template for Julius

When presenting the plan, use this concise format (Vietnamese):

```
## 📋 Feynman Plan: <Topic>
**Scale:** N researcher subagents

### 🔑 Key Questions
| # | Question |
|---|----------|
| 1 | ... |
| 2 | ... |

### 🔬 Research Tracks
| Track | Researcher | Focus |
|-------|-----------|-------|
| R1 | ... | ... |

### 📦 Output: N files (plan → draft → cited → final + provenance)
### ⛓️ Pipeline: R1–RN (parallel) → Synthesize → Verifier → Reviewer → Fix → Final

Anh confirm nhé?
```

## Confirmation

- **Julius says yes/ok/confirm**: `process(action="submit", data="yes", session_id="<id>")` — but note this is unreliable (see warning above). Fall back to pexpect runner if Feynman doesn't react.
- **Julius says no/changes**: `process(action="submit", data="no", session_id="<id>")` or `process(action="kill", session_id="<id>")`
- **No response**: Do nothing. The process waits. Do not auto-confirm.

## What Went Wrong (Session 2026-05-22)

1. **PTY + submit ignored (×2):** Both attempts to send "yes" via `process submit` to a PTY-mode Feynman were silently ignored. Feynman sat at the confirmation prompt for 52 minutes. Root cause: Hermes's process stdin doesn't reliably reach PTY-spawned TUI apps. **Fix:** Use pexpect runner (`references/pexpect-runner.py`) which holds a real PTY and calls `sendline()` directly.
2. **File not found:** Tried reading from `~/julius-workspace/working/research/feynman/outputs/.plans/` — file wasn't there. Found it at `/tmp/outputs/.plans/` via `find`.
3. **Log navigation:** PTY output makes logs hard to parse (escape sequences, spinner animations). Prefer reading the plan file from disk over scraping the log.
4. **Piped stdin broken:** `echo "yes" | feynman chat ...` produced zero output — Feynman requires a PTY to function.
5. **pexpect string matching fragile:** `child.expect("Proceed with this deep research plan")` with exact string matching timed out even though the prompt was visible. The pexpect runner now uses `[r"Proceed with this deep research plan", pexpect.TIMEOUT]` list pattern so it never hangs indefinitely.
