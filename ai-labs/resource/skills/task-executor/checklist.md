# Checklist — Task Executor

Pre-flight and post-flight checks for task execution.

---

## Pre-Flight Checklist

Run before starting any task.

### Discovery Phase
- [ ] Task file exists in `tasks/scheduled/`
- [ ] Frontmatter is complete (type, status, priority, deadline, domain, skill)
- [ ] Task description is clear (Section 1: Yêu cầu)
- [ ] Context files referenced exist (Section 2: Context)
- [ ] Checklist is actionable (Section 3: Checklist)

### Context Loading
- [ ] Read domain AGENTS.md (e.g., `working/Coin68/AGENTS.md`)
- [ ] Read context files listed in task
- [ ] Check knowledge-base for relevant concepts (read-only)
- [ ] Identify which skill to load (from frontmatter `skill:` field)

### Safety Check
- [ ] Task does NOT ask to access `personal/`
- [ ] Task does NOT ask to delete files without approval
- [ ] Task does NOT ask to modify `.hermes/IDENTITY.md` or `SOUL.md`
- [ ] Task does NOT require external credentials I don't have
- [ ] Task deadline is achievable

If any safety check fails → escalate immediately, do NOT proceed.

---

## Confirmation Checklist

Before moving task to `processing/`.

- [ ] Presented understanding to Julius using confirmation template
- [ ] Waited for explicit "yes" or "confirm"
- [ ] Clarified any ambiguities
- [ ] Estimated time is realistic

---

## Execution Checklist

During task execution.

### Setup
- [ ] Moved task file to `tasks/processing/`
- [ ] Updated frontmatter: `status: in_progress`, `started: YYYY-MM-DD-HHmm`
- [ ] Loaded correct skill from `ai-labs/resource/skills/<skill>/SKILL.md`

### Work
- [ ] Following checklist in task file Section 3
- [ ] Updating checklist as items complete
- [ ] Writing output to correct location (target path or Section 4)
- [ ] Following domain AGENTS.md rules

### Quality
- [ ] Output is complete (no placeholders, no TODOs)
- [ ] Proofread (no typos, grammar correct)
- [ ] Formatted properly (markdown, code blocks, headers)
- [ ] Internal links work (if any)
- [ ] Citations included (if research task)

---

## Post-Flight Checklist

Before moving task to `approved/`.

### Verification
- [ ] All checklist items in Section 3 are checked
- [ ] Output matches task requirements
- [ ] Output follows domain AGENTS.md rules
- [ ] No violations of workspace/AGENTS.md global rules
- [ ] Self-review passed (read output as if you're Julius)

### Metadata
- [ ] Updated frontmatter: `status: done`, `completed: YYYY-MM-DD-HHmm`
- [ ] Filled Section 5: Notes with completion details
- [ ] Logged to `.hermes/MEMORY.md`

### Delivery
- [ ] Moved task file to `tasks/approved/`
- [ ] Sent completion notification to Julius
- [ ] Proposed Git push if applicable (new files created)
- [ ] Cleaned up temporary files

---

## Escalation Checklist

When creating an escalation.

- [ ] Created file in `tasks/inbox/escalation-YYYY-MM-DD-HHmm.md`
- [ ] Frontmatter includes `related_task:` field
- [ ] Issue described clearly in 1-3 sentences
- [ ] Context provided (what was tried, what failed)
- [ ] 2-3 proposed solutions listed
- [ ] Ended with clear question for Julius
- [ ] Did NOT proceed with risky action while waiting

---

## Error Recovery Checklist

When task fails mid-execution.

- [ ] Stopped execution immediately
- [ ] Did NOT move to `approved/`
- [ ] Updated Section 5 with error details
- [ ] Moved back to `scheduled/` or kept in `processing/`
- [ ] Created escalation explaining failure
- [ ] Proposed alternative approach or asked for guidance

---

## Daily Maintenance Checklist

Run at start of each work session.

- [ ] Scan `tasks/scheduled/` for new tasks
- [ ] Check `tasks/processing/` for stalled tasks (>24h without update)
- [ ] Review `.hermes/MEMORY.md` last 5 entries (pattern check)
- [ ] Verify no orphaned files in `tasks/inbox/` (>7 days old)

---

**Last updated:** 2026-05-04
