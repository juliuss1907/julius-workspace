---
name: feynman
description: "Delegate research to Feynman CLI — multi-agent AI research agent for deep research, literature review, paper audit, and experiment replication."
version: 1.0.0
author: Markus / Hermes
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Research-Agent, Feynman, Deep-Research, Paper-Review, Autonomous]
    related_skills: [deep-research, codex, opencode]
---

# Feynman CLI

Delegate research tasks to [Feynman](https://github.com/juliuss1907/feynman) — an open-source AI research agent with multi-agent reasoning, academic paper search, code auditing, and experiment replication.

## When to Use

- User asks for deep research on a topic
- Need literature review with citations
- Want to audit a paper against its codebase
- Need a structured research brief with provenance
- Multi-agent research workflows (researcher → reviewer → writer → verifier)

## Prerequisites

- Feynman installed: `curl -fsSL https://feynman.is/install | bash`
- Auth configured: `feynman setup` (select provider, login OAuth or set API key)
- Web search configured: `feynman search set auto` or `feynman search set perplexity <key>`
- Verify: `feynman doctor` should show `authenticated providers: 1+` and `default model valid: yes`

## Key Commands

| Command | Purpose |
|---------|---------|
| `feynman` | Launch interactive REPL |
| `feynman chat "/deepresearch <topic>"` | One-shot deep research |
| `feynman chat "/lit <topic>"` | Literature review |
| `feynman chat "/audit <paper>"` | Paper vs codebase audit |
| `feynman doctor` | Diagnose config/auth/runtime |
| `feynman setup` | Guided setup wizard |
| `feynman search set <backend> [key]` | Configure web search |

## Output Locations

**Reality:** Feynman writes ALL outputs to `/tmp/outputs/`, regardless of the `workdir` parameter. The workdir only sets the shell's starting directory — Feynman's internal file operations use `/tmp` as root.

```
/tmp/outputs/
├── .plans/<slug>.md        # Research plan (generated first)
├── .drafts/<slug>-draft.md # Initial draft
├── .drafts/<slug>-cited.md # Draft with citations
├── <slug>.md               # Final report
└── <slug>.provenance.md    # Source provenance sidecar
```

**After Feynman completes**, copy results to the workspace:
```bash
cp -r /tmp/outputs/* ~/julius-workspace/working/research/feynman/outputs/
```

**During interactive workflow**: Read the plan directly from `/tmp/outputs/.plans/<slug>.md` while Feynman waits for confirmation.

## One-Shot Research

**Warning:** `echo "yes" | feynman chat` (piped stdin, no PTY) has been observed to produce zero output — this approach is unreliable. Use one of the interactive or pexpect methods below instead.

### Method A: Interactive (with Julius review) — see "Interactive Confirmation Workflow" below
### Method B: Pexpect auto-confirm (unattended)

For unattended runs where plan review is skipped, use the pexpect runner (see `references/pexpect-runner.py`):

```bash
terminal(
  command="/usr/bin/python3 ~/julius-workspace/.hermes/skills/autonomous-ai-agents/feynman/references/pexpect-runner.py '<topic>'",
  background=true,
  notify_on_complete=true,
  timeout=900
)
```

## Interactive Confirmation Workflow (Julius's Preference)

**Default workflow:** Julius wants to review every Feynman research plan before it executes. Do NOT auto-confirm.

### Step-by-step

⚠️ **CRITICAL: Julius MUST review every plan before confirming. Auto-confirmation is forbidden unless explicitly instructed.**

1. **Launch Feynman with PTY** so we can interact with it mid-session:
```bash
terminal(
  command="feynman chat '/deepresearch <topic>'",
  workdir="~/julius-workspace/working/research/feynman/",
  background=true,
  pty=true,
  timeout=900
)
```

2. **Poll until plan appears.** Watch the log for "Proceed with this deep research plan? Reply 'yes' to continue". When you see it, Feynman has stopped and is waiting.

3. **Find and read the plan.** Feynman writes plans to `/tmp/outputs/.plans/<slug>.md` (NOT the workdir — see Pitfalls). Find it:
```bash
terminal(command="find /tmp -name '*.md' -path '*/.plans/*' -type f 2>/dev/null")
```
Or check the log for the slug, then:
```bash
read_file("/tmp/outputs/.plans/<slug>.md")
```

4. **Summarize for Julius.** Send a concise summary: scale, key questions, research tracks, pipeline steps. Ask "Anh confirm nhé?".

**⚠️ Do NOT proceed to step 5 until Julius explicitly says "yes" or "confirm".**

5. **Wait for Julius's response.** 
   - If **yes/ok/confirm** → send "yes" via `process(action="submit", data="yes", session_id="<id>")`
   - ⚠️ **If Feynman doesn't react** (submit ignored — known issue, happened 2/2 times in session 2026-05-22): kill the PTY process and restart using the pexpect runner instead:
     ```bash
     terminal(
       command="/usr/bin/python3 ~/julius-workspace/.hermes/skills/autonomous-ai-agents/feynman/references/pexpect-runner.py '<topic>'",
       background=true,
       notify_on_complete=true,
       timeout=900
     )
     ```
   - If **no/changes requested** → send "no" or kill the process, update plan per his feedback
   - If he doesn't respond → do NOT proceed. The process will wait.

6. **After confirmation**, Feynman spawns subagents. Monitor with `process(action="poll")` periodically. Research takes 5-15 minutes.

### When to auto-confirm (skip Julius review)

Only when Julius explicitly says "cứ chạy đi", "auto confirm", "không cần review plan", or when running via a cron job. **Even in cron, ensure the execution environment has a PTY** (see `references/interactive-only.md` for why this is critical).

**⚠️ Do NOT use** `bash -c "echo 'yes' | feynman chat ..."` — this approach has been tested and confirmed broken with Feynman v0.2.58 (produces zero output). Always use a PTY wrapper or the pexpect runner for auto-confirmation.

## Background Research — Auto-Confirm (Unattended / Cron)

**For unattended runs** where Julius approved skipping plan review, use the pexpect runner script. It spawns Feynman with a real PTY, waits for plan generation, auto-confirms, and exits when research completes.

```bash
terminal(
  command="/usr/bin/python3 ~/julius-workspace/.hermes/skills/autonomous-ai-agents/feynman/references/pexpect-runner.py '<topic>'",
  background=true,
  notify_on_complete=true,
  timeout=900
)
```

The script logs progress ("Spawning...", "Waiting for plan...", "Confirmed!", "RESEARCH COMPLETE") to stdout so you can monitor via `process(action="poll")`.

**Do NOT use** `bash -c "echo 'yes' | feynman chat ..."` — this approach produces zero output because Feynman requires a PTY. The pipe-only method has been tested and confirmed broken (session 2026-05-22).

## Slash Commands (Workflows)

| Command | Description |
|---------|-------------|
| `/deepresearch <topic>` | Multi-agent investigation with parallel researchers, synthesis, verification |
| `/lit <topic>` | Literature review with consensus, disagreements, open questions |
| `/review <artifact>` | Simulated peer review with severity and revision plan |
| `/audit <item>` | Paper vs. codebase mismatch audit |
| `/replicate <paper>` | Replicate experiments on local or cloud GPUs |
| `/compare <topic>` | Source comparison matrix |
| `/draft <topic>` | Paper-style draft from research findings |

## Four Built-in Agents

- **Researcher** – Gathers evidence across papers, web, repos, and docs
- **Reviewer** – Simulated peer review with severity-graded feedback
- **Writer** – Converts research notes into structured drafts
- **Verifier** – Validates inline citations, URLs, and removes dead links

## Pitfalls

- **Output goes to /tmp, NOT the workdir**: Even when `workdir` is set, Feynman writes outputs (`.plans/`, `.drafts/`, final `.md`, `.provenance.md`) to `/tmp/outputs/`. Always check `/tmp/outputs/` for results. The workdir setting only affects the shell's cwd during startup — Feynman's internal file writes use `/tmp` as root. After Feynman completes, copy outputs to the workspace: `cp -r /tmp/outputs/* ~/julius-workspace/working/research/feynman/outputs/`.
- **Plan discovery**: Plans are at `/tmp/outputs/.plans/<slug>.md`. If you don't know the slug, run `find /tmp -name '*.md' -path '*/.plans/*' -type f 2>/dev/null` to find the latest plan.
- **Web search missing**: After `feynman setup`, still need `feynman search set auto` for web access during research.
- **AlphaXiv auth optional**: Paper search works without AlphaXiv login, but authenticated access gives more features.
- **Long runtime**: Deep research can take 5-15 minutes. Always use `background=true` with adequate timeout (≥600s).
- **PTY + process submit is unreliable**: In testing (session 2026-05-22), `process(action="submit", data="yes")` was sent to Feynman's PTY but Feynman never reacted — this failed 2/2 times. The pexpect runner (`references/pexpect-runner.py`) is the reliable alternative: it holds a real PTY and sends input directly.
- **Piped stdin (no PTY) produces no output**: `echo "yes" | feynman chat ...` yields zero output — Feynman requires a PTY. Tested and confirmed broken 2026-05-22.
- **Interactive `feynman` REPL** (no `chat` subcommand) needs `pty=true` — this is only for the full TUI session, not for one-shot commands.

## Verification

Smoke test after setup:
```bash
feynman doctor 2>&1 | grep -E "auth|model.*valid|search route"
# Should show: authenticated providers: 1+, default model valid: yes
```

Quick research test:
```bash
terminal(
  command="feynman chat 'Reply exactly: FEYNMAN_OK'",
  workdir="/tmp"
)
# Should output: FEYNMAN_OK
```

## Integration with Hermes

Feynman outputs feed into other workflows:
- Research brief → Coin68 article draft (use `coin68-writer` skill)
- Literature review → X thread content (use `x-post-writer` skill)
- Paper audit → verification block in Coin68 article

## References

- **Plan discovery recipe**: `references/plan-discovery.md` — how to find plans in `/tmp`, summarize for Julius, and handle confirmation.
- **Pexpect runner**: `references/pexpect-runner.py` — reliable Python script for spawning Feynman with a real PTY, auto-confirming, and waiting for completion. Use this when `process submit` to PTY fails or for unattended runs.
- **OOM debug for cron**: `references/oom-debug.md` — diagnosing SIGKILL (exit -9) when Feynman runs via cron; memory limits, systemd cgroup, and wrapper fixes.
- Repo: https://github.com/juliuss1907/feynman (Julius's fork)
- Upstream: https://github.com/companion-inc/feynman
- Install: https://feynman.is/install
