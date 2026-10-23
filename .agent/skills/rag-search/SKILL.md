# SKILL — RAG Search

**Agent:** Markus  
**Purpose:** Search workspace and knowledge-base to answer questions  
**Version:** 2.0

---

## Role

Search Julius's workspace and knowledge-base to find information, connect ideas, and answer questions. Adapt search scope based on context.

---

## Workflow

### 1. Understand the question

Determine:
- What is being asked? (fact, concept, how-to, comparison)
- What domain? (AI, crypto, tech, code)
- What scope? (KB, workspace, or both)

### 2. Choose strategy

See [references/search-strategies.md](references/search-strategies.md) for detailed patterns by question type.

Quick reference:
- Concept questions → `knowledge-base/wiki/concepts/`
- How-to questions → `knowledge-base/wiki/concepts/` + `learning/`
- Code questions → `learning/`, `ai-labs/projects/`
- Task status → `tasks/scheduled/`, `tasks/processing/`

### 3. Execute search

**Structured searches** (tags, topics):
1. Check `wiki/tag/[tag].md` or `wiki/topic/[topic].md` first
2. Follow links to concepts/sources
3. Read top 3-5 matches

**Keyword searches**:
1. Use grep/ripgrep across target scope
2. Rank by relevance (filename > content)
3. Read top 3-5 matches

### 4. Synthesize answer

See [references/output-formats.md](references/output-formats.md) for templates.

- 1 source → answer + cite
- Multiple sources → synthesize + cite all
- Not found → say so + suggest next steps
- Partial → answer what's known + flag gaps

---

## Forbidden

- Never search `personal/` (workspace rule)
- Never read `.env` files (security rule)

---

**Last updated:** 2026-05-04
