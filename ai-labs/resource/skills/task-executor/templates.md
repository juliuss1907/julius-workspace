# Templates — Task Executor

Reusable templates for task execution.

---

## Task Confirmation Template

Use when presenting understanding before execution.

```
[TASK CONFIRMATION]
Task: <task-title>
Type: <task_type from frontmatter>
Domain: <domain from frontmatter>
Deadline: <deadline from frontmatter>
Priority: <priority from frontmatter>

My understanding:
- I will <action 1 in plain language>
- I will <action 2>
- I will <action 3>
- Output will be saved to: <target path or "inline in task file">

Estimated time: <X minutes/hours>

Confirm to proceed? (yes/no/clarify)
```

**Example:**
```
[TASK CONFIRMATION]
Task: Write Coin68 article about Belo
Type: article
Domain: coin68
Deadline: 2026-05-15
Priority: high

My understanding:
- I will write a 1000-2000 word Vietnamese article about Belo project
- I will follow Coin68 review format (là gì? structure)
- I will read context from working/Coin68/context/ and knowledge-base/
- Output will be saved to: working/Coin68/contents/drafts/belo.md

Estimated time: 45 minutes

Confirm to proceed?
```

---

## Task Completion Notification Template

Use when task is done and moved to approved/.

```
[TASK COMPLETE]
Task: <task-title>
Output: <path or "inline in task file Section 4">
Time taken: <actual time>
Ready for review.
```

**Example:**
```
[TASK COMPLETE]
Task: Write Coin68 article about Belo
Output: working/Coin68/contents/drafts/belo.md
Time taken: 52 minutes
Ready for review.
```

---

## Escalation Template

Use when encountering issues that require Julius's decision.

```markdown
---
type: inbox
inbox_type: escalation
related_task: <task-file-name>
created: YYYY-MM-DD-HHmm
---

# Escalation: <Brief Issue Title>

## Task
<task-file-name>

## Issue
<1-3 sentences describing the problem>

## Context
<Relevant details: what you tried, what failed, what's blocking>

## Proposed Solutions
Option A: <solution 1>
Option B: <solution 2>
Option C: <solution 3>

Which approach do you prefer?
```

**Example:**
```markdown
---
type: inbox
inbox_type: escalation
related_task: coin68-belo-ddl-15-05-2026
created: 2026-05-04-1520
---

# Escalation: Missing Context File

## Task
coin68-belo-ddl-15-05-2026.md

## Issue
Task references working/Coin68/context/belo-research.md but this file does not exist.

## Context
I checked:
- working/Coin68/context/ (only coin68.md and context.md exist)
- knowledge-base/wiki/concepts/ (no belo-related concepts)
- knowledge-base/raw/ (no belo sources)

## Proposed Solutions
Option A: Proceed without this context file (research from web only)
Option B: Wait for you to provide the file
Option C: Use general crypto project research approach

Which approach do you prefer?
```

---

## Push Proposal Template

Use when task created new files and you want to commit.

```
[PUSH PROPOSAL]
Task: <task-id>
Commit message: "<proposed message>"
Files changed: <n>
New files:
- <file 1>
- <file 2>

Awaiting your approval to commit and push.
```

**Example:**
```
[PUSH PROPOSAL]
Task: coin68-belo-ddl-15-05-2026
Commit message: "feat(coin68): add Belo article draft"
Files changed: 1
New files:
- working/Coin68/contents/drafts/belo.md

Awaiting your approval to commit and push.
```

---

## Task File Section 5 Template

Use when filling Section 5: Notes after task completion.

```markdown
## 5. Notes / Feedback

**Completed:** YYYY-MM-DD HH:MM
**Output location:** <path or "inline Section 4">
**Time:** Estimated <X> min vs Actual <Y> min
**Notes:** <Any deviations, additions, or observations>
```

**Example:**
```markdown
## 5. Notes / Feedback

**Completed:** 2026-05-04 14:30
**Output location:** working/Coin68/contents/drafts/belo.md
**Time:** Estimated 45 min vs Actual 52 min
**Notes:** Added extra section on tokenomics per context file suggestion. Used 3 sources from KB (perpdex concepts) + 2 web sources (Belo docs, Belo Twitter).
```

---

**Last updated:** 2026-05-04
