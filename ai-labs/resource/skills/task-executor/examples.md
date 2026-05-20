# Examples — Task Executor

Good vs bad task execution patterns.

---

## Example 1: Coin68 Article Task

### Good Execution

**Task file:** `tasks/scheduled/coin68-belo-ddl-15-05-2026.md`

**Frontmatter:**
```yaml
type: task
task_type: article
status: todo
priority: high
target: working/Coin68/contents/drafts/belo.md
domain: coin68
skill: coin68-writer
deadline: 2026-05-15
created: 2026-05-04
```

**Agent actions:**
1. Read task file
2. Read `working/Coin68/AGENTS.md`
3. Read `working/Coin68/context/coin68.md`
4. Present confirmation:
   ```
   [TASK CONFIRMATION]
   Task: Write Coin68 article about Belo
   Type: article
   Domain: coin68
   Deadline: 2026-05-15

   My understanding:
   - I will write a 1000-2000 word Vietnamese article about Belo project
   - I will follow Coin68 review format (là gì? structure)
   - Output will be saved to: working/Coin68/contents/drafts/belo.md

   Estimated time: 45 minutes

   Confirm to proceed?
   ```
5. Wait for "yes"
6. Move to processing/, update status
7. Load `coin68-writer/SKILL.md`
8. Execute: research → outline → draft → proofread
9. Write to `working/Coin68/contents/drafts/belo.md`
10. Move to approved/, notify Julius

**Result:** Complete article, correct location, ready for Julius review.

---

### Bad Execution

**Same task, but agent:**
1. Skips confirmation → starts writing immediately
2. Writes in English instead of Vietnamese (didn't read domain AGENTS.md)
3. Writes output in task file instead of target path
4. Leaves placeholders: `[TODO: add tokenomics section]`
5. Doesn't move to approved/, just stops

**Why bad:**
- No confirmation → Julius can't catch misunderstanding early
- Wrong language → violates Coin68 AGENTS.md
- Wrong location → Julius has to move file manually
- Incomplete → not ready for review
- No notification → Julius doesn't know it's done

---

## Example 2: X Thread Task

### Good Execution

**Task file:** `tasks/scheduled/x-thread-rag-ddl-10-05-2026.md`

**Frontmatter:**
```yaml
type: task
task_type: tweet
status: todo
priority: medium
target: working/X/contents/draft/thread-rag-explained.md
domain: x
skill: thread-writer
deadline: 2026-05-10
created: 2026-05-04
```

**Agent actions:**
1. Read task + context
2. Confirm understanding (thread = 8-12 tweets, hook + body + CTA)
3. Move to processing/
4. Load `thread-writer/SKILL.md`
5. Write thread with numbered tweets
6. Check character limits (each tweet < 280 chars)
7. Save to target path
8. Move to approved/, notify

**Output in `working/X/contents/draft/thread-rag-explained.md`:**
```markdown
---
type: thread
tweets: 10
status: draft
---

# Thread: RAG Explained

1/ RAG (Retrieval-Augmented Generation) is how AI systems remember things without retraining.

Think of it like giving an AI a library card instead of memorizing every book.

Here's how it actually works

2/ Traditional LLMs are frozen in time. GPT-4 knows nothing after its training cutoff.

RAG fixes this by letting the model search external knowledge in real-time.

[... 8 more tweets ...]

10/ Want to build your own RAG system?

Start with:
- Vector DB (Pinecone/Weaviate)
- Embedding model (OpenAI/Cohere)
- Chunking strategy

I'll share a starter template next week. Follow for updates.
```

**Result:** Complete thread, proper format, character limits checked.

---

### Bad Execution

**Same task, but agent:**
1. Writes thread as one long paragraph (not numbered tweets)
2. Tweet 3 is 340 characters (over limit)
3. No CTA at the end
4. Saves to `working/X/contents/published/` instead of `draft/`

**Why bad:**
- Wrong format → can't copy-paste to X
- Over character limit → won't post
- No CTA → misses engagement opportunity
- Wrong folder → violates workflow (draft → review → published)

---

## Example 3: Research Task

### Good Execution

**Task file:** `tasks/scheduled/research-kb-tools-ddl-none.md`

**Frontmatter:**
```yaml
type: task
task_type: research
status: todo
priority: low
target: none
domain: ai-labs
skill: none
deadline: none
created: 2026-05-04
```

**Agent actions:**
1. Read task: "Compare Obsidian vs Notion vs Roam for KB"
2. Confirm scope: workspace + KB + web search
3. Move to processing/
4. Search workspace for existing notes
5. Search KB for relevant concepts
6. Web search for recent comparisons
7. Synthesize findings
8. Write report in task file Section 4
9. Cite all sources
10. Move to approved/, notify

**Output in Section 4:**
```markdown
## 4. Research Findings

### Comparison: Obsidian vs Notion vs Roam

**Obsidian:**
- Pros: Local-first, plain markdown, graph view, plugin ecosystem
- Cons: No built-in sync, steeper learning curve
- Best for: Developers, privacy-focused users
- Source: [1][2]

**Notion:**
- Pros: Databases, collaboration, templates, all-in-one
- Cons: Proprietary format, slower with large vaults
- Best for: Teams, project management
- Source: [3]

**Roam:**
- Pros: Bidirectional links, daily notes, block references
- Cons: Expensive, web-only, smaller ecosystem
- Best for: Researchers, networked thought
- Source: [4]

### Recommendation for Julius

Based on current setup (plain markdown, Git, AI agents):
**Obsidian** is the best fit because:
1. Already using markdown in workspace
2. Local files = agents can read/write directly
3. Graph view helps visualize connections
4. Plugin ecosystem supports AI integration

### Sources
[1] workspace/ai-labs/systems/llm-knowledge-base/litepaper.md
[2] knowledge-base/wiki/concepts/obsidian-setup.md
[3] https://notion.so/product
[4] https://roamresearch.com
```

**Result:** Complete research, clear recommendation, all sources cited.

---

### Bad Execution

**Same task, but agent:**
1. Only searches web, ignores workspace/KB
2. Copies marketing copy from each tool's website
3. No synthesis or comparison
4. No recommendation
5. No source citations

**Why bad:**
- Didn't use available context (workspace/KB)
- Not original analysis (just copied text)
- Doesn't answer "which one for Julius?"
- Can't verify claims (no sources)

---

## Example 4: Escalation (Good)

**Task file:** `tasks/scheduled/delete-old-drafts-ddl-none.md`

**Task description:** "Delete all draft files older than 6 months in working/Coin68/contents/drafts/"

**Agent actions:**
1. Read task
2. Recognize: this is destructive action
3. Do NOT execute
4. Create escalation:

**File:** `tasks/inbox/escalation-2026-05-04-1430.md`
```markdown
---
type: inbox
inbox_type: escalation
related_task: delete-old-drafts-ddl-none
created: 2026-05-04-1430
---

# Escalation: Destructive Action Request

## Task
delete-old-drafts-ddl-none.md

## Issue
Task asks me to delete files older than 6 months in working/Coin68/contents/drafts/.

This is a destructive action. Per workspace/AGENTS.md Section 8 Rule #3, I cannot delete files without approval.

## Files that would be affected
(After scanning the directory)
- belo-old.md (created 2025-10-12, 7 months old)
- saturn-draft.md (created 2025-09-20, 8 months old)
- fun-review.md (created 2025-08-15, 9 months old)

Total: 3 files

## Proposed action
Option A: Submit delete-request for each file individually
Option B: You manually review and delete
Option C: Move to archive folder instead of deleting

Which approach do you prefer?
```

5. Wait for Julius's decision
6. Do NOT proceed until confirmed

**Result:** Destructive action prevented, Julius makes informed decision.

---

**Last updated:** 2026-05-04
