# Workflow — Task Executor

Step-by-step process for executing tasks.

---

## Phase 1: Discovery

### Step 1.1: Scan scheduled tasks

```bash
cd ~/julius-workspace/tasks/scheduled
ls -la
```

Look for:
- Files with `assigned_to: hermes` in frontmatter
- Files with `status: todo` and no assignee (can volunteer)

### Step 1.2: Read task file

Read in order:
1. **Frontmatter** — type, status, priority, deadline, domain, skill
2. **Section 1: Yêu cầu** — What Julius wants
3. **Section 2: Context** — Links to relevant files
4. **Section 3: Checklist** — Steps to complete

### Step 1.3: Load context

If task references context files:
- Read files in `working/<domain>/context/`
- Read files in `knowledge-base/wiki/concepts/` (read-only)
- Use RAG search if needed

---

## Phase 2: Confirmation

### Step 2.1: Present understanding

Format:
```
[TASK CONFIRMATION]
Task: <title>
Type: <task_type>
Domain: <domain>
Deadline: <deadline>
Priority: <priority>

My understanding:
- I will <action 1>
- I will <action 2>
- Output will be saved to: <path>

Estimated time: <X minutes/hours>

Confirm to proceed? (yes/no/clarify)
```

### Step 2.2: Wait for confirmation

- If **yes** → proceed to Phase 3
- If **no** → ask for clarification
- If **clarify** → answer questions, re-confirm

Do NOT proceed without explicit confirmation.

---

## Phase 3: Execution

### Step 3.1: Move task to processing

```bash
cd ~/julius-workspace/tasks
mv scheduled/<task-file>.md processing/<task-file>.md
```

### Step 3.2: Update frontmatter

Change:
```yaml
status: todo
```

To:
```yaml
status: in_progress
started: YYYY-MM-DD-HHmm
```

### Step 3.3: Load domain skill

Based on `skill:` field in frontmatter:
- `coin68-writer` → Load `ai-labs/resource/skills/coin68-writer/SKILL.md`
- `thread-writer` → Load `ai-labs/resource/skills/thread-writer/SKILL.md`
- `x-article-writer` → Load `ai-labs/resource/skills/x-article-writer/SKILL.md`
- `substack-writer` → Load `ai-labs/resource/skills/substack-writer/SKILL.md`

### Step 3.4: Execute checklist

Follow checklist in Section 3 of task file.

Update checklist as you complete each item:
```markdown
- [x] Read context
- [x] Research additional sources
- [ ] Write outline  <- currently working on this
```

### Step 3.5: Write output

**If task has `target:` path in frontmatter:**
- Write output to that path
- Reference output location in task file Section 4

**If no `target:` path:**
- Write output directly in task file Section 4: Draft

### Step 3.6: Self-review

Before marking done, check:
- [ ] All checklist items completed
- [ ] Output is complete (no placeholders)
- [ ] Proofread (no typos)
- [ ] Links work
- [ ] Follows domain AGENTS.md rules

---

## Phase 4: Delivery

### Step 4.1: Update task file

1. Update frontmatter:
```yaml
status: done
completed: YYYY-MM-DD-HHmm
```

2. Fill Section 5: Notes:
```markdown
## 5. Notes / Feedback

Completed on: 2026-05-04 14:30
Output location: working/Coin68/contents/drafts/belo.md
Estimated vs actual time: 45 min vs 52 min
Notes: Added extra section on tokenomics per context file suggestion.
```

### Step 4.2: Move to approved

```bash
cd ~/julius-workspace/tasks
mv processing/<task-file>.md approved/<task-file>.md
```

### Step 4.3: Notify Julius

```
[TASK COMPLETE]
Task: <title>
Output: <path or "inline in task file">
Time taken: <X minutes>
Ready for review.
```

### Step 4.4: Propose Git push (if applicable)

If task created new files in `working/` or `learning/`:

```
[PUSH PROPOSAL]
Task: <task-id>
Files changed: <n>
New files: <list>
Awaiting your approval to commit and push.
```

Wait for Julius's approval before pushing.

---

## Phase 5: Post-Delivery

### Step 5.1: Log to memory

Append one line to `.hermes/MEMORY.md`:

```
2026-05-04 14:30 | task:<task-id> | <domain> | <task-type> | done | <time-taken>
```

### Step 5.2: Clean up

- Remove any temporary files created during execution
- Close any open context windows

### Step 5.3: Return to discovery

Scan `tasks/scheduled/` for next task.

---

## Error Handling

### If task fails mid-execution

1. Do NOT move to approved/
2. Update task file Section 5 with error details
3. Move back to scheduled/ or keep in processing/
4. Escalate to `tasks/inbox/escalation-*.md`

### If context files missing

1. List missing files in escalation
2. Ask Julius to provide or confirm they're not needed

### If deadline impossible

1. Escalate immediately
2. Propose revised timeline or reduced scope

---

**Last updated:** 2026-05-04
