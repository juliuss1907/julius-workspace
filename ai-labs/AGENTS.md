# AGENTS.md — AI Labs Domain

**Domain:** AI Labs
**Purpose:** System design, project development, automation workflows, and shared resources
**Version:** 1.0
**Last updated:** 2026-05-04

---

## 1. DOMAIN OVERVIEW

`ai-labs/` contains 5 subdomains:

| Subdomain | Purpose | Agent Permission |
|---|---|---|
| `projects/` | Active development projects | READ + WRITE (code, docs, tests) |
| `systems/` | System designs & architectures | READ + WRITE (design docs only) |
| `workflows/` | Reusable automation sequences | READ + WRITE (scripts, configs) |
| `pipelines/` | Data processing pipelines | READ + WRITE (ETL, transforms) |
| `resource/` | Shared library (skills, prompts, etc.) | READ-ONLY (see Section 6) |

---

## 2. GENERAL RULES

### Inheritance

This file inherits from `workspace/AGENTS.md` and adds domain-specific rules.

### Quality Standards

All work in `ai-labs/` must meet:
- **Functional:** Code runs without errors
- **Documented:** README.md + inline comments
- **Tested:** Critical paths have tests (when applicable)
- **Versioned:** Git commits with clear messages

### Forbidden Actions

Beyond global rules, in `ai-labs/` you must NOT:
- Deploy to production without Julius's approval
- Modify live infrastructure
- Delete project folders (escalate for archive)
- Install global packages without asking

---

## 3. PROJECTS RULES

### Code Generation Approach (Hybrid: Pair Programming)

**Agent scaffolds, Julius implements logic:**

1. **Agent provides:**
   - Project structure (folders, files)
   - Boilerplate code (imports, class skeletons, function signatures)
   - Configuration files (package.json, requirements.txt, .env.example)
   - Test scaffolds (test file structure, test cases outline)

2. **Julius implements:**
   - Core business logic
   - Complex algorithms
   - Domain-specific rules

3. **Agent assists:**
   - Code review (suggest improvements)
   - Debugging (help find issues)
   - Refactoring (optimize after logic works)

**Example workflow:**
```
Task: Build a simple REST API

Agent creates:
- api/
  ├── main.py              # Flask app scaffold
  ├── routes/
  │   └── users.py         # Route signatures only
  ├── models/
  │   └── user.py          # Model class skeleton
  ├── tests/
  │   └── test_users.py    # Test structure
  ├── requirements.txt
  └── README.md

Julius fills in:
- User model fields & validation logic
- Route handlers (GET, POST, PUT, DELETE)
- Business rules (authentication, authorization)

Agent reviews:
- Code quality, error handling, edge cases
```

### Documentation Requirements

Every project must have:

**README.md (required):**
```markdown
# [Project Name]

## What it does
[1-2 sentences]

## Setup
[Installation steps]

## Usage
[How to run]

## Architecture
[High-level overview or link to architecture.md]

## Status
[In development / Testing / Production]
```

**architecture.md (for complex projects):**
- System components
- Data flow
- Technology stack
- Design decisions

**CHANGELOG.md (optional):**
- Use when project has versions/releases

### Git Workflow (Hybrid)

**For main branch (strict):**
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
- Push proposal required (wait for Julius approval)
- No force push

**For experiment branches (relaxed):**
- Descriptive commits OK
- Auto-push OK (but notify Julius)
- Can force push (own branch only)

**Commit message format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

Example:
```
feat(api): add user authentication endpoint

Implement JWT-based auth with refresh tokens.
Uses bcrypt for password hashing.

Closes #12
```

### Dependencies

**Installing packages:**
- Agent can suggest packages
- Julius approves before install
- Always use lockfiles (requirements.txt, package-lock.json)
- Pin versions for production projects

**Version strategy:**
- Development: `^1.2.3` (caret) OK
- Production: `1.2.3` (exact) required

### Testing

**When tests are required:**
- API endpoints (all routes)
- Data transformations (ETL, parsing)
- Business logic (calculations, validations)

**When tests are optional:**
- Proof-of-concept projects
- One-off scripts
- UI prototypes

**Test framework:**
- Python: pytest
- JavaScript: Jest
- Other: Julius decides

---

## 4. SYSTEMS RULES

### Purpose

`systems/` contains design documents, NOT implementations.

**What goes here:**
- Litepaper (high-level overview)
- Architecture diagrams (text-based or links to tools)
- Setup guides (how to implement)
- Decision logs (why we chose X over Y)

**What does NOT go here:**
- Code (goes to `projects/`)
- Task files (goes to `tasks/`)
- Temporary notes (goes to `tasks/inbox/`)

### Design Document Format

```markdown
# [System Name]

## Overview
[What problem does this solve?]

## Architecture
[Components, data flow, tech stack]

## Implementation Plan
[Phases, milestones, dependencies]

## Decisions
[Key design decisions with rationale]

## References
[Links to related docs, projects, external resources]
```

### System → Project Link

When implementing a system:
1. Create project folder: `projects/[system-name]-implementation/`
2. Reference system doc in project README:
   ```markdown
   Based on: [systems/[system-name]/litepaper.md](../../systems/[system-name]/litepaper.md)
   ```
3. Update system doc with project link:
   ```markdown
   Implementation: [projects/[system-name]-implementation/](../../projects/[system-name]-implementation/)
   ```

---

## 5. WORKFLOWS & PIPELINES RULES

### Workflows (Automation Sequences)

**What they are:**
- Bash scripts
- Task chains (cron jobs)
- CI/CD configs

**Safety rules:**
- No destructive commands without confirmation (rm -rf, chmod -R)
- Dry-run mode for testing
- Logging required (stdout + file)
- Error handling (exit codes, retries)

**Example workflow structure:**
```
workflows/backup-kb/
├── backup.sh           # Main script
├── config.yaml         # Configuration
├── README.md           # Usage guide
└── logs/               # Execution logs (gitignored)
```

### Pipelines (Data Processing)

**What they are:**
- ETL scripts
- Data transformations
- Batch processing

**Safety rules:**
- Input validation (check file exists, format correct)
- Output verification (check result before overwrite)
- Idempotent (can run multiple times safely)
- Rollback plan (backup before transform)

**Example pipeline structure:**
```
pipelines/kb-compile/
├── extract.py          # Read raw files
├── transform.py        # Process content
├── load.py             # Write to wiki
├── config.yaml
└── README.md
```

### External API Access

**Allowed:**
- Read-only APIs (fetch data)
- APIs with rate limits (respect limits)
- APIs with Julius's keys (from .env, never hardcode)

**Forbidden:**
- Write APIs without confirmation (POST, PUT, DELETE)
- Payment APIs
- APIs that modify production data

---

## 6. RESOURCE LIBRARY RULES

### Overview

`ai-labs/resource/` contains shared resources for entire workspace.

| Subfolder | Content | Agent Permission |
|---|---|---|
| `skills/` | Agent skill definitions | READ-ONLY |
| `prompts/` | Prompt templates | READ-ONLY |
| `personas/` | Agent personas | READ-ONLY |
| `mcps/` | MCP documentation | READ-ONLY |
| `plugins/` | Plugin documentation | READ-ONLY |
| `api-keys/` | Credentials | FORBIDDEN |

### Why Read-Only?

Resource library is **curated by Julius**. Changes affect entire workspace, so must be intentional.

### Proposing New Resources

If you identify a pattern that should become a skill/prompt/persona:

1. **Create proposal** in `tasks/inbox/resource-proposal-YYYY-MM-DD-HHmm.md`:
   ```markdown
   ---
   type: inbox
   inbox_type: resource-proposal
   resource_type: skill | prompt | persona
   created: YYYY-MM-DD-HHmm
   ---

   # Resource Proposal: [Name]

   ## Type
   [skill / prompt / persona]

   ## Problem
   [What pattern keeps repeating?]

   ## Proposed Solution
   [How would this resource solve it?]

   ## Usage Example
   [Show how it would be used]

   ## Files Needed
   [List files to create in resource/]
   ```

2. **Wait for Julius approval**

3. **If approved:** Julius creates resource, you can then use it

### Using Existing Resources

**Skills:**
```
Load skill: ai-labs/resource/skills/coin68-writer/SKILL.md
```

**Prompts:**
```
Use prompt: ai-labs/resource/prompts/article-outline.md
```

**Personas:**
```
Adopt persona: ai-labs/resource/personas/technical-writer.md
```

---

## 7. QUALITY STANDARDS

### Code Quality

**Minimum standards:**
- [ ] Runs without errors
- [ ] Handles edge cases
- [ ] Has error messages (not silent failures)
- [ ] Follows language conventions (PEP 8 for Python, etc.)

**Good standards (aim for these):**
- [ ] Modular (functions < 50 lines)
- [ ] DRY (no copy-paste code)
- [ ] Readable (clear variable names, comments for "why" not "what")
- [ ] Tested (critical paths covered)

### Documentation Quality

**Minimum standards:**
- [ ] README.md exists
- [ ] Setup instructions work
- [ ] Usage examples provided

**Good standards:**
- [ ] Architecture explained
- [ ] Design decisions documented
- [ ] Troubleshooting section

### Testing Quality

**Minimum standards:**
- [ ] Happy path tested
- [ ] One edge case tested

**Good standards:**
- [ ] All edge cases covered
- [ ] Error conditions tested
- [ ] Integration tests (if applicable)

---

## 8. ESCALATION

Escalate to `tasks/inbox/escalation-*.md` when:

### Technical Decisions
- Architecture choice affects multiple projects
- Technology stack selection (framework, database, etc.)
- Breaking changes to existing projects

### Resource Constraints
- Need external service (API, database, hosting)
- Need paid tool or library
- Need more compute/storage than available

### Scope Creep
- Task grows beyond original scope
- New requirements conflict with existing design
- Timeline no longer realistic

### Blocked
- Dependency not available
- External API down
- Waiting for Julius's input on business logic

---

## 9. EXAMPLES

### Good Project Structure

```
projects/kb-api/
├── README.md                    # Clear setup & usage
├── requirements.txt             # Pinned versions
├── .env.example                 # Template (no secrets)
├── src/
│   ├── main.py                  # Entry point
│   ├── routes/
│   │   ├── concepts.py
│   │   └── sources.py
│   ├── models/
│   │   └── concept.py
│   └── utils/
│       └── markdown_parser.py
├── tests/
│   ├── test_routes.py
│   └── test_models.py
└── docs/
    └── architecture.md
```

### Good Commit Messages

```
feat(api): add concept search endpoint

Implement full-text search across wiki/concepts/ using
simple keyword matching. Returns ranked results.

Closes #23
```

```
fix(parser): handle markdown tables correctly

Previous parser broke on tables with pipes in content.
Now escapes pipes before parsing.

Fixes #45
```

### Good Escalation

```markdown
---
type: inbox
inbox_type: escalation
related_task: kb-api-search-feature
created: 2026-05-04-1600
---

# Escalation: Search Implementation Approach

## Task
kb-api-search-feature.md

## Issue
Need to decide between 3 search approaches:

**Option A: Simple keyword matching**
- Pros: Easy to implement, no dependencies
- Cons: Poor relevance, no fuzzy matching

**Option B: SQLite FTS5**
- Pros: Built-in, good performance, fuzzy search
- Cons: Requires SQLite setup, migration needed

**Option C: External service (Algolia/Meilisearch)**
- Pros: Best relevance, typo-tolerant, fast
- Cons: External dependency, cost, complexity

## Recommendation
Option B (SQLite FTS5) — good balance of quality and simplicity.

## Decision Needed
Which approach should I implement?
```

---

**Maintainer:** Julius
**Last updated:** 2026-05-04
