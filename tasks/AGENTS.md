# AGENTS.md — Tasks Domain

> Inherits from: workspace/AGENTS.md
> Domain: Task queue management — how Hermes receives, processes, and completes tasks.

---

## 1. CONTEXT

The `tasks/` folder is Hermes's work queue. Julius assigns tasks here; Hermes picks them up, executes, and reports back. Tasks are **pointers** to work — not containers of content. Actual content lives in domain folders (`working/`, `learning/`, `ai-labs/`).

---

## 2. FOLDER STRUCTURE

```
tasks/
├── TASK_TEMPLATE.md      ← Template to clone when creating a new task
├── TASK_SKILL.md         ← Skill defining how Hermes manages task lifecycle
├── tasks.md              ← Index/dashboard of all active tasks
├── scheduled/            ← Tasks queued, not yet started
├── processing/           ← Tasks Hermes is currently working on
├── approved/             ← Tasks completed and approved by Julius
└── inbox/                ← Non-task items: escalations, kb-captures, notes
```

---

## 3. TASK FILE NAMING

Pattern: `<slug>-ddl-DD-MM-YYYY.md`

- Slug describes the task in 3-5 words
- `ddl-DD-MM-YYYY` = deadline date

**Examples:**
- `coin68-belo-review-ddl-15-05-2026.md`
- `x-thread-rag-explained-ddl-10-05-2026.md`
- `substack-essay-ai-agents-ddl-30-05-2026.md`

If no deadline, use `ddl-none`:
- `learning-python-oop-exercises-ddl-none.md`

---

## 4. TASK FRONTMATTER (REQUIRED)

Every task file MUST start with this YAML frontmatter:

```yaml
---
type: task
status: scheduled | processing | approved
priority: high | medium | low
target: <relative-path-to-output-file>
domain: coin68 | substack | x | clients | learning | ai-labs | other
skill: article-writer | thread-writer | substack-writer | researcher | seo-optimizer | none
deadline: YYYY-MM-DD | none
created: YYYY-MM-DD
---
```

### Field rules
- `target` — full relative path from workspace root, e.g., `working/Coin68/content/drafts/belo.md`
- `domain` — must match one of the listed values (lowercase)
- `skill` — reference to `ai-labs/resource/skills/<skill>/SKILL.md`. Use `none` if no specific skill needed.
- `deadline` — ISO date format `YYYY-MM-DD`, or literal string `none`

---

## 5. TASK LIFECYCLE

```
Julius creates → tasks/scheduled/<task>.md
                       ↓
Hermes picks up → moves to tasks/processing/<task>.md
                       ↓
                 Updates status: scheduled → processing
                       ↓
                 Reads target, domain AGENTS.md, skill SKILL.md
                       ↓
                 Executes work → writes to target path
                       ↓
                 Notifies Julius via channel: "Task X done, awaiting approval"
                       ↓
Julius approves → Hermes moves to tasks/approved/<task>.md
                       ↓
                 Updates status: processing → approved
                       ↓
                 (Hermes proposes git push — see workspace/AGENTS.md §8)
```

### Important
- **Hermes moves files between folders.** The `status` field in frontmatter MUST always match the parent folder.
- **Hermes never moves directly from scheduled to approved.** Always pass through `processing/`.
- **If Julius rejects a task** (e.g., output not satisfactory), Hermes moves the file back to `processing/` and addresses feedback. Do NOT create a `rejected/` folder.

---

## 6. MULTI-STEP TASKS

For tasks too large for one file (e.g., "write a 5-part series"):
1. Break into N task files, one per deliverable
2. Use a parent slug + suffix: `coin68-l2-series-01-arbitrum-ddl-DD-MM-YYYY.md`, `coin68-l2-series-02-zksync-ddl-DD-MM-YYYY.md`
3. Reference parent intent in each task's body: "Part 2 of 5 in the L2 series"

---

## 7. TEMPLATE vs SKILL — phân biệt

Two UPPERCASE files in `tasks/` serve different roles:

### TASK_TEMPLATE.md
- **Type**: Template (boilerplate)
- **Purpose**: Starter file with required frontmatter + checklist sections
- **When to use**: Julius (or Hermes on Julius's behalf) clones this file when creating a new task
- **Action**: Copy to `tasks/scheduled/<slug>-ddl-DD-MM-YYYY.md`, fill in frontmatter, write task description

### TASK_SKILL.md
- **Type**: Skill (methodology)
- **Purpose**: Defines HOW Hermes manages the task lifecycle — validation rules, when to move files, when to notify, how to handle status mismatches
- **When to use**: Hermes loads this skill at the start of any task-related action (pickup, move, complete, reject-handling)
- **Not cloned**: this file is read-only methodology, not a template

### Loading order for a new task
1. Julius creates task → clones `TASK_TEMPLATE.md` → fills frontmatter → places in `scheduled/`
2. Hermes picks up task → loads `TASK_SKILL.md` to know how to handle lifecycle
3. Hermes loads domain AGENTS.md (e.g., `working/Coin68/AGENTS.md`)
4. Hermes loads referenced skill from `ai-labs/resource/skills/` (per `skill:` frontmatter field)
5. Hermes executes

---

## 8. TASKS/INBOX/ — Non-task items

Use `tasks/inbox/` for items that need Julius's attention but aren't formal tasks. Naming: `<type>-YYYY-MM-DD-HHmm.md`

| Type | When to use |
|---|---|
| `escalation-*` | Hermes hits ambiguity and needs Julius's decision (see workspace/AGENTS.md §9) |
| `kb-capture-*` | Hermes finds info worth adding to KB (cannot write to KB directly) |
| `delete-request-*` | Hermes wants to delete or archive a file — needs Julius's approval before any deletion |
| `note-*` | Ad-hoc observation, suggestion, idea |

Inbox files do NOT have the task frontmatter schema. Use a simpler frontmatter:
```yaml
---
type: inbox
inbox_type: escalation | kb-capture | delete-request | note
related_task: <task-id-if-applicable>
created: YYYY-MM-DD
---
```

---

## 9. EXAMPLES

### Good
**Task assignment:**
> Julius creates `tasks/scheduled/coin68-belo-review-ddl-15-05-2026.md` with frontmatter `domain: coin68, skill: none, target: working/Coin68/content/drafts/belo.md`

**Hermes pickup:**
> Hermes loads `TASK_SKILL.md` → moves task to `tasks/processing/`, updates status, loads `working/Coin68/AGENTS.md`, reads context files, writes to `working/Coin68/content/drafts/belo.md`, notifies Julius.

### Bad
**Anti-example A — Wrong content location:**
> Hermes writes the article body inside the task file at `tasks/processing/coin68-belo-review-ddl-15-05-2026.md`
> Why bad: Task file is a pointer. Article goes to `target` path.

**Anti-example B — Skipping processing:**
> Task moves directly from `scheduled/` to `approved/`
> Why bad: Status must reflect actual lifecycle. Pass through `processing/`.

**Anti-example C — Status mismatch:**
> File is in `tasks/processing/` but frontmatter says `status: scheduled`
> Why bad: Frontmatter and folder must match.

**Anti-example D — Cloning TASK_SKILL.md as a task:**
> Hermes copies `TASK_SKILL.md` to `scheduled/` thinking it's a template
> Why bad: TASK_SKILL.md is methodology, not a clonable template. Use TASK_TEMPLATE.md instead.

---

## 10. ESCALATE WHEN

- Task `target` path doesn't exist and creating it would require new top-level folder
- Task `domain` value doesn't match any listed domain
- Task `skill` references a SKILL.md that doesn't exist
- Conflicting tasks have the same `target` path
- Julius hasn't responded to "awaiting approval" notification for >24h
