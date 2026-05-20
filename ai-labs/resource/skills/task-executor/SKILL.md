# SKILL — Task Executor

**Agent:** Hermes (local)
**Purpose:** Execute tasks from task queue following workspace lifecycle
**Version:** 2.0
**Last updated:** 2026-05-04

---

## Role

Execute tasks Julius assigns from the task queue. Follow lifecycle, confirm before acting, deliver complete results.

Task Executor is the **meta-skill** that orchestrates other skills. It handles:
- Task discovery and intake
- Skill routing (which skill to load for which task)
- Lifecycle management (scheduled → processing → approved)
- Quality assurance before delivery
- Communication with Julius

---

## When to Use

Load this skill when:
- Starting a work session (scan for new tasks)
- Julius assigns a task via channel
- Periodic check (every 2 hours during work hours)

Do NOT load for:
- Ad-hoc questions (answer directly)
- Clarifications (respond in-context)
- Emergencies (escalate immediately)

---

## Task Lifecycle

```
tasks/scheduled/     <- Julius creates task here
       |
[Discover & Confirm]
       |
tasks/processing/    <- Move here after confirmation
       |
[Execute with domain skill]
       |
tasks/approved/      <- Move here after completion
       |
[Julius reviews]     <- Final destination varies by task type
```

---

## Workflow

See [workflow.md](workflow.md) for detailed step-by-step process.

**Quick summary:**
1. **Discover** — Scan `tasks/scheduled/` for assigned tasks
2. **Confirm** — Present understanding, wait for approval
3. **Execute** — Load domain skill, follow checklist
4. **Deliver** — Move to approved/, notify Julius

---

## Task Type Routing

| Task Type | Load Skill | Output Location |
|---|---|---|
| Coin68 article | `coin68-writer` | `working/Coin68/contents/drafts/` |
| X thread | `thread-writer` | `working/X/contents/draft/` |
| X article | `x-article-writer` | `working/X/contents/draft/` |
| Substack essay | `substack-writer` | `working/Substack/contents/draft/` |
| Research | `researcher` (future) | `tasks/processing/<task-file>` Section 4 |
| Code | (no skill yet) | Inline in task file or target path |

---

## Quality Standards

Before moving task to `approved/`, verify:

**Completeness:**
- [ ] All checklist items done
- [ ] No placeholders or TODOs
- [ ] Output in correct location

**Quality:**
- [ ] Proofread (no typos)
- [ ] Formatted (proper markdown)
- [ ] Links work (internal references valid)
- [ ] Follows domain AGENTS.md rules

**Metadata:**
- [ ] Frontmatter updated (`status: done`)
- [ ] Section 5: Notes filled (if applicable)
- [ ] File moved to `approved/`

---

## Escalation

Escalate to `tasks/inbox/escalation-YYYY-MM-DD-HHmm.md` when:

- Task violates workspace rules (e.g., asks to access `personal/`)
- Task requires destructive action (delete files, modify production)
- Task requires external access you don't have (API keys, credentials)
- Task is ambiguous after reading context
- Task deadline impossible to meet
- Task is ethically questionable

**Escalation template:** See [templates.md](templates.md)

---

## References

- [workflow.md](workflow.md) — Detailed execution steps
- [examples.md](examples.md) — Good vs bad task execution
- [templates.md](templates.md) — Task confirmation, escalation, delivery templates
- [checklist.md](checklist.md) — Pre-flight and post-flight checks

---

**Maintainer:** Julius
**Last updated:** 2026-05-04
