# Julius Workspace

Personal AI-powered workspace for content creation, learning, and system building.

**Version:** 1.0  
**Last updated:** 2026-05-04

---

## Overview

This workspace is designed for AI-assisted work across three domains:
- **Content creation** — Coin68 articles, X threads, Substack essays
- **Learning** — Python, prompt engineering, AI systems
- **System building** — AI projects, workflows, pipelines

The workspace follows a structured approach where AI agents operate under clear rules defined in `AGENTS.md` files at each level.

---

## Architecture

### Folder Structure

```
julius-workspace/
├── AGENTS.md              # Global rules for all agents
├── README.md              # This file
├── personal/              # Private folder (agents forbidden)
├── learning/              # Learning materials & practice
├── working/               # Content production
│   ├── Coin68/           # Crypto content (Vietnamese)
│   ├── X/                # Twitter content (English)
│   ├── Substack/         # Newsletter (English)
│   └── clients/          # Client work
├── ai-labs/               # AI projects & systems
│   ├── projects/         # Active projects
│   ├── systems/          # System designs
│   ├── workflows/        # Reusable workflows
│   ├── pipelines/        # Data pipelines
│   └── resource/         # Shared resources
│       ├── skills/       # Agent skill definitions
│       ├── prompts/      # Prompt library
│       ├── personas/     # Agent personas
│       └── api-keys/     # API credentials (gitignored)
├── tasks/                 # Task queue for agents
│   ├── scheduled/        # Queued tasks
│   ├── processing/       # Active tasks
│   ├── approved/         # Completed tasks
│   └── inbox/            # Escalations & notes
├── knowledge-base/        # Separate repo (see below)
└── backups/               # Local backups (gitignored)
```

### Naming Conventions

| Type | Convention | Example |
|---|---|---|
| Folders | `kebab-case` | `prompt-engineering`, `good-taste-writing` |
| System files | `UPPERCASE.md` | `AGENTS.md`, `README.md` |
| Index files | Match folder name | `tasks/tasks.md`, `clients/clients.md` |
| Content files | `kebab-case.md` | `belo.md`, `layer-1.md` |
| Task files | `kebab-case-ddl-DD-MM-YYYY.md` | `coin68-belo-ddl-15-05-2026.md` |
| Code files | `snake_case.py` | `oop_basic.py` |

**Hard rules:**
- No spaces in filenames
- No special characters except `-` and `_`
- ASCII only (no Vietnamese diacritics in filenames)
- Max 60 characters per filename

---

## Getting Started

### Prerequisites

- Git
- Python 3.9+ (for learning/ and ai-labs/)
- Node.js 18+ (optional, for some projects)
- Obsidian (optional, for visual navigation)

### Clone

```bash
# Clone workspace
git clone git@github.com:juliuss1907/julius-workspace.git
cd julius-workspace

# Clone knowledge-base separately (managed independently)
git clone git@github.com:juliuss1907/knowledge-base.git
```

### Setup

```bash
# Create personal/ folder (gitignored, for private notes)
mkdir -p personal/{notes,mindsets,researchs}

# Verify structure
ls -la
# → Should see: AGENTS.md, learning/, working/, ai-labs/, tasks/, knowledge-base/, personal/
```

---

## Daily Workflow

### Working on Content

```bash
# Coin68 article
cd working/Coin68/contents/drafts
# Create/edit article
# When done, move to published/ manually

# X thread
cd working/X/contents/draft
# Create thread file
# When done, move to published/threads/

# Substack essay
cd working/Substack/contents/draft
# Create essay
# When done, move to published/
```

### Working on Learning

```bash
cd learning/python/oop
# Edit knowledge/ or practice/ files
# Commit when reaching a milestone
```

### Working with Tasks

```bash
# Create new task
cd tasks/scheduled
cp ../TASK_TEMPLATE.md my-task-ddl-10-05-2026.md
# Fill in frontmatter and description

# Agent picks up task → moves to processing/
# After completion → Julius reviews → moves to approved/
```

### Committing Changes

```bash
# Workspace changes
cd ~/julius-workspace
git add .
git commit -m "feat: add new Coin68 article"
git push

# Knowledge-base changes (separate repo)
cd ~/julius-workspace/knowledge-base
git add .
git commit -m "feat: add new concept"
git push origin master
```

---

## Agent Rules

Agents operating in this workspace follow rules defined in `AGENTS.md` files:

### Global Rules (`workspace/AGENTS.md`)
- Agents can read/write: `learning/`, `working/`, `ai-labs/`, `tasks/`
- Agents can read-only: `knowledge-base/`
- Agents forbidden: `personal/`, `backups/`, `.env` files

### Domain-Specific Rules
- `tasks/AGENTS.md` — Task lifecycle management
- `working/Coin68/AGENTS.md` — Vietnamese crypto content rules
- `working/X/AGENTS.md` — English Twitter content rules
- `working/Substack/AGENTS.md` — Newsletter rules

**Inheritance:** Nested AGENTS.md files inherit from parent and may override specific rules.

### Key Constraints

Agents must never:
- Access `personal/` folder
- Read `.env` files
- Delete files without approval (submit delete-request to `tasks/inbox/`)
- Auto-push to Git (must propose push and wait for approval)
- Modify `.hermes/IDENTITY.md` or `.hermes/SOUL.md`

---

## Knowledge Base

The `knowledge-base/` folder is a **separate Git repository** managed independently from the workspace.

### Structure

```
knowledge-base/
├── raw/           # Ingested content (articles, papers, videos)
├── wiki/          # Compiled knowledge (concepts, sources)
├── context/       # User profile & context
├── .openclaw/     # OpenClaw agent (VPS)
└── .hermes/       # Hermes agent (VPS)
```

### Workflow

**Workspace agents (local):**
- Can **read** knowledge-base for context
- Cannot write to knowledge-base

**Knowledge-base agents (VPS):**
- OpenClaw: ingest → compile → index
- Hermes: validate quality, format, hygiene

**Committing:**
```bash
# KB changes are committed separately
cd knowledge-base
git add .
git commit -m "..."
git push origin master

# Workspace commits do NOT include KB changes
cd ..
git status
# → knowledge-base/ does not appear (gitignored)
```

---

## Troubleshooting

### "Agent tried to access personal/"

**Cause:** Agent violated forbidden access rule.

**Fix:** Agent should escalate to `tasks/inbox/escalation-*.md` instead.

### "Git shows knowledge-base as modified"

**Cause:** KB is not properly gitignored.

**Fix:**
```bash
# Verify .gitignore
cat .gitignore | grep knowledge-base
# → Should see: knowledge-base/

# If missing, add it
echo "knowledge-base/" >> .gitignore
git add .gitignore
git commit -m "chore: gitignore knowledge-base"
```

### "Task file in wrong folder"

**Cause:** Task lifecycle not followed.

**Fix:** Tasks must flow: `scheduled/` → `processing/` → `approved/`. Never skip steps.

### ".obsidian/ folders appearing in git status"

**Cause:** Obsidian vault settings not gitignored.

**Fix:** Already in `.gitignore`. Run `git status` — should not appear.

---

## Contributing

This is a personal workspace. If you're a collaborator:

1. Read `AGENTS.md` before making changes
2. Follow naming conventions strictly
3. Never commit to `personal/` or `knowledge-base/`
4. Create tasks in `tasks/scheduled/` for agent work
5. Use `tasks/inbox/` for escalations

---

## License

Private workspace — not for public distribution.

---

**Maintainer:** Julius  
**Contact:** [Your contact method]  
**Last updated:** 2026-05-04
