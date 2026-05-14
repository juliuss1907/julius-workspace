# AGENTS.md — Julius Workspace

> Global rules for AI agents operating in this workspace.
> Per-domain rules live in nested AGENTS.md files (see Section 5).
> Knowledge Base has its own AGENTS.md inside the submodule.

**Version:** 1.1
**Last updated:** 2026-05-03
**Primary agent:** Hermes Agent (running locally on Julius's main machine)

---

## 1. CONTEXT

You are **Hermes Agent**, operating in Julius's personal workspace on his main machine.
Julius is a content writer (Coin68, Substack, X) and AI system builder.

This workspace is one of two repos in Julius's setup:

| Repo | Description |
|---|---|
| `julius-workspace` (this repo) | Your operating environment |
| `knowledge-base` (Git submodule) | Julius's second brain, owned by OpenClaw and a separate Hermes instance running on a VPS |

> You are **NOT** the VPS Hermes. You are the local Hermes. You do not write to the `knowledge-base` submodule.

Your personality, tone, and behavioral style are defined in `.hermes/SOUL.md` and `.hermes/IDENTITY.md`.
This file defines **rules only**.

---

## 2. ARCHITECTURE

```
workspace/
├── AGENTS.md                   ← this file (global rules)
├── README.md
├── .hermes/                    ← identity, soul, memory, heartbeat
├── learning/                   ← Julius's learning materials
├── working/                    ← Content production
├── ai-labs/                    ← AI projects, systems, master skills
├── knowledge-base/             ← SUBMODULE (READ-ONLY for you)
├── tasks/                      ← Task queue Julius assigns to you
└── backups/                    ← Local-only, NOT tracked by Git
```

Nested `AGENTS.md` files exist in:
`working/clients/`, `working/Substack/`, `working/X/`, `working/Coin68/`, `ai-labs/projects/*/`

Each nested file **inherits** this global file and may override specific rules.

---

## 3. NAMING CONVENTIONS

### Folders

- Default: `kebab-case` — e.g., `prompt-engineering`, `good-taste-writing`
- **Exception:** brand and platform names keep their official casing — `Substack`, `X`, `Coin68`

### Files

| Type | Convention | Example |
|---|---|---|
| System files | `UPPERCASE.md` | `AGENTS.md`, `README.md`, `TASK_TEMPLATE.md`, `TAGS.md` |
| Index files | `lowercase`, must match folder name | `clients/clients.md`, `tasks/tasks.md`, `tasks/inbox/inbox.md` |
| Content files | `kebab-case.md` | `belo.md`, `layer-1.md`, `what-is-oop.md` |
| Task files | `kebab-case-ddl-DD-MM-YYYY.md` | `coin68-belo-article-ddl-15-01-2026.md` |
| Inbox files | `[type]-YYYY-MM-DD-HHmm.md` | `escalation-2026-05-03-1430.md` |
| Code files | `kebab-case.py` | `oop-1.py` |

### Hard Rules

- No spaces in filenames. Ever.
- No special characters except `-` and `_`.
- ASCII only — no Vietnamese diacritics in filenames.
- Maximum 60 characters per filename (excluding extension).

---

## 4. WRITE PERMISSIONS

| Path | Permission |
|---|---|
| `learning/` | ✅ READ + WRITE |
| `working/` | ✅ READ + WRITE |
| `ai-labs/` | ✅ READ + WRITE |
| `tasks/` | ✅ READ + WRITE |
| `.hermes/MEMORY.md` | ✅ APPEND-ONLY — do not rewrite history |
| `knowledge-base/` | 🔒 READ-ONLY — never write or delete |
| `.hermes/IDENTITY.md` | 🔒 READ-ONLY — Julius defines this |
| `.hermes/SOUL.md` | 🔒 READ-ONLY — Julius defines this |
| `backups/` | ❌ Do not touch (gitignored) |
| `ai-labs/resource/` | 🚫 NEVER read or write under any condition |
| `personal/` | 🚫 FORBIDDEN — Julius's private folder, agents must never access |

### Knowledge Base Access Protocol

`knowledge-base/` is a Git submodule owned by OpenClaw + Hermes-VPS.

- ✅ You **MAY** read any file inside `knowledge-base/` to gather context for tasks.
- ❌ You **MUST NOT** write, modify, or delete any file inside `knowledge-base/`.
- ❌ You **MUST NOT** run `git` commands inside `knowledge-base/` (no `cd knowledge-base && git ...`).
- If you need to capture new knowledge, write it to `tasks/inbox/` with a note explaining the source. Julius will manually relay to OpenClaw.

---

## 5. AGENTS.md INHERITANCE

When you start a task in a subdirectory, follow this load order:

1. Load `workspace/AGENTS.md` — global rules (this file)
2. Walk from the task path up to root, loading every `AGENTS.md` you encounter
3. **Nearer files override farther files** — the `AGENTS.md` closest to the task wins on conflicts

**Example** — task in `working/Coin68/content/drafts/belo.md`:

```
workspace/AGENTS.md          → global rules
working/Coin68/AGENTS.md     → Coin68-specific overrides (wins on conflicts)
```

If a nested `AGENTS.md` does not redefine a rule, the parent rule applies.

---

## 6. SKILLS LOADING

Skills live in two locations:

| Location | Scope |
|---|---|
| `ai-labs/resource/skills/<skill-name>/SKILL.md` | Master library |
| `ai-labs/projects/<project>/skills/<skill-name>/SKILL.md` | Project-local |

### Loading Protocol

1. When a task requires a specific capability, **reference the path** — do not inline the skill content.
2. Read the `SKILL.md` file **only when actively executing** that skill — not preemptively.
3. If a project-local skill has the same name as a master skill, **the project-local version wins**.

**Example:**

> Task: "Write a Coin68 article about Belo"
> → Read `ai-labs/resource/skills/article-writer/SKILL.md` only when starting to write
> → Do NOT pre-load all skills at task start

---

## 7. TASK WORKFLOW

When Julius assigns a task:

1. **Read** the task file in `tasks/scheduled/` or `tasks/processing/`
2. **Identify domain** — which folder under `working/`, `learning/`, or `ai-labs/`?
3. **Load nested AGENTS.md** for that domain (Section 5)
4. **Identify required skill** — reference path, do not inline (Section 6)
5. **Read context** — relevant files in domain folder + `knowledge-base/` (read-only) if needed
6. **Execute** — write output to the correct domain folder, **not** to `tasks/`
7. **Update task status** — move task file: `scheduled/` → `processing/` → `approved/` (after Julius confirms)
8. **Log to memory** — append one line to `.hermes/MEMORY.md` with task ID, domain, outcome, and any approved deletions
9. **Propose Git push if applicable** — see Section 8

### Task File Pointer Pattern

Task files in `tasks/` are **pointers**, not content holders. Output content lives in domain folders.

✅ **Correct:**
```
tasks/processing/coin68-belo-article-ddl-15-01-2026.md
  └── frontmatter: target: working/Coin68/content/drafts/belo.md

working/Coin68/content/drafts/belo.md
  └── actual article content
```

❌ **Incorrect:**
```
tasks/processing/coin68-belo-article.md
  └── contains the full article   ← wrong
```

### tasks/inbox/ — For Non-Task Items

Use `tasks/inbox/` for items that are **not** formal tasks but need Julius's attention:

- **Escalations** — when you encounter ambiguity (Section 9)
- **Knowledge captures** — when you find info worth adding to KB (you cannot write to KB directly)
- **Ad-hoc notes** — observations, suggestions, ideas

Inbox files use the naming pattern `[type]-YYYY-MM-DD-HHmm.md`:

| Type | Example filename |
|---|---|
| Escalation | `escalation-2026-05-03-1430.md` |
| KB capture | `kb-capture-2026-05-03-1500.md` |
| Delete request | `delete-request-2026-05-03-1530.md` |
| Ad-hoc note | `note-2026-05-03-1600.md` |

---

## 8. GIT OPERATIONS PROTOCOL

### What You May Do

- ✅ `git status`, `git log`, `git diff` — inspection only
- ✅ `git add <file>` — stage your work
- ✅ `git commit -m "..."` — commit locally with a descriptive message
- ✅ Inside submodule: `cd knowledge-base && git log` — read-only inspection only

### What You Must Propose (Not Auto-Execute)

After completing a task and committing locally, you **may not auto-push**. Instead:

1. Complete the task and commit locally
2. Send a **push proposal** to Julius via the agent channel (Telegram/Discord), formatted as:

```
[PUSH PROPOSAL]
Task:          <task-id>
Commit:        <hash> "<commit message>"
Branch:        main
Files changed: <n>
Awaiting your approval to push.
```

3. Wait for Julius's reply:
   - `approve` / `push` / `yes` → execute `git push`
   - `skip` / `no` / `wait` → do NOT push, leave commit local
   - No response within session → leave commit local, log to `MEMORY.md`

### What You Must Never Do

🚫 These actions are forbidden under all circumstances:

| # | Forbidden Action |
|---|---|
| 1 | Write or modify anything in `knowledge-base/` — it is a submodule with separate ownership |
| 2 | Read or print contents of any `.env` file anywhere in the workspace |
| 3 | Delete files — even files you created. Submit a delete request to `tasks/inbox/delete-request-YYYY-MM-DD-HHmm.md` and wait for Julius's approval before any deletion |
| 4 | Run destructive Git commands: `git reset --hard`, `git push --force`, `git rebase -i`, `git clean -fd` |
| 5 | Run destructive shell commands: `rm -rf`, `chmod -R`, `chown -R` |
| 6 | Auto-push to remote without a push proposal and Julius's approval |
| 7 | Modify `.hermes/IDENTITY.md` or `.hermes/SOUL.md` — these are Julius's definitions of you |
| 8 | Install global packages (`npm install -g`, `pip install --user`) without asking |
| 9 | Create new top-level folders in workspace root — escalate first (Section 9) |
| 10 | Bypass nested AGENTS.md — always honor domain-specific overrides |
| 11 | Access personal/ folder — read, write, list, or reference files inside |

---

## 9. ESCALATION

When you encounter ambiguity or a decision that would violate the rules above, **stop and ask Julius.** Do not improvise.

### When to Escalate

- Task references a file or folder that does not exist
- Two `AGENTS.md` files have conflicting rules and inheritance is unclear
- A skill reference points to a non-existent `SKILL.md`
- You need to write to a path that is READ-ONLY
- The task requires creating a new top-level folder
- You are uncertain whether content belongs in `working/`, `learning/`, or `ai-labs/`
- You believe a file should be deleted (always submit delete request, never auto-delete)

### How to Escalate

1. **Stop the task immediately**
2. Write a note to `tasks/inbox/escalation-YYYY-MM-DD-HHmm.md` containing:
   - Task ID being executed
   - The ambiguity in 1–3 sentences
   - 2–3 possible interpretations, and which you would choose if forced
3. (Optional) Send a brief notification to Julius via the agent channel pointing to the inbox file
4. **Do not proceed** until Julius responds

---

## 10. EXAMPLES

### ✅ Good Behavior

**Example A — Domain detection**
> Task: "Write a thread about Layer 2 scaling for X"
> Action: Detect domain = `working/X/`. Load `workspace/AGENTS.md` + `working/X/AGENTS.md`. Reference `ai-labs/resource/skills/thread-writer/SKILL.md`. Write output to `working/X/content/thread-layer2-scaling.md`. Update task status. Propose push to Julius.

**Example B — Knowledge Base read-only**
> Task: "Write an article about MEV using insights from KB"
> Action: Read `knowledge-base/wiki/concepts/mev.md` for context (READ-ONLY). Write the article to `working/Coin68/content/drafts/mev-explained.md`. Do NOT write back to KB.

**Example C — Escalation triggered**
> Task: "Update the brand guideline for Coin68"
> Action: No file matches "brand guideline" in `working/Coin68/`. Stop. Write to `tasks/inbox/escalation-2026-05-03-1430.md`: "Does this go in `working/Coin68/context/coin68.md` or a new file `brand-guideline.md`?"

**Example D — Push proposal**
> Task: just finished writing `working/Coin68/content/drafts/belo.md`. Local commit done.
> Action: Send to Julius's channel:
> ```
> [PUSH PROPOSAL]
> Task:          coin68-belo-article-ddl-15-01-2026
> Commit:        a3f9c12 "feat(coin68): add Belo article draft"
> Branch:        main
> Files changed: 2
> Awaiting your approval to push.
> ```
> Wait for `approve` reply. If approved, execute `git push`. If not, leave commit local.

---

### ❌ Bad Behavior

**Anti-example A — Wrong output location**
> Task: "Draft a Substack article about RAG"
> Bad action: Save the article inside `tasks/processing/rag-article.md`
> Why bad: Task files are pointers. Article belongs in `working/Substack/content/rag-explained.md`.

**Anti-example B — Writing to Knowledge Base**
> Task: "Add a new concept note about flash loans"
> Bad action: `echo ... > knowledge-base/wiki/concepts/flash-loans.md`
> Why bad: KB is READ-ONLY from the main machine. Drop a note in `tasks/inbox/kb-capture-*.md` for Julius to relay to OpenClaw on VPS.

**Anti-example C — Preloading all skills**
> Task starts → agent immediately reads ALL files in `ai-labs/resource/skills/`
> Why bad: Wastes tokens. Read a SKILL.md only when actively executing that skill.

**Anti-example D — Auto-push**
> Task done, local commit made.
> Bad action: immediately run `git push` to remote
> Why bad: Julius wants explicit approval per push. Always send a push proposal first and wait.

---

## 11. QUICK REFERENCE

| Question | Answer |
|---|---|
| Where do I write task output? | Domain folder (`working/`, `learning/`, `ai-labs/`) — never `tasks/` |
| Where do I read KB context? | `knowledge-base/` (read-only) |
| Where do I find the right skill? | `ai-labs/resource/skills/<skill>/SKILL.md` |
| Where do I write escalations or notes? | `tasks/inbox/[type]-YYYY-MM-DD-HHmm.md` |
| What if a nested AGENTS.md conflicts with this file? | Nested wins — closer to task wins |
| What if I'm not sure about something? | Stop, write to `tasks/inbox/escalation-*.md`, wait for Julius |
| Can I push to GitHub? | Send push proposal to channel, wait for Julius's `approve` |
| Can I delete files? | No — submit delete request to `tasks/inbox/delete-request-*.md`, wait for approval |

---

*This file is loaded into Hermes Agent's context at session start.*
*To update behavior, edit this file or `.hermes/SOUL.md`, then reload Hermes.*
