# Search Strategies by Question Type

## Concept Questions

**Pattern:** "What is [concept]?"

**Primary scope:** `knowledge-base/wiki/concepts/`  
**Secondary scope:** `wiki/sources/`

**Steps:**
1. Check `wiki/tag/` for relevant tag
2. Read concept file if exists
3. Follow "Liên quan" links for connected concepts
4. Check sources for deeper context

---

## How-To Questions

**Pattern:** "How do I [task]?"

**Primary scope:** `knowledge-base/wiki/concepts/`  
**Secondary scope:** `learning/`, `ai-labs/workflows/`

**Steps:**
1. Search concepts for procedural knowledge
2. Check learning/ for practice examples
3. Check workflows/ for established patterns

---

## Source Questions

**Pattern:** "Where did I read about [topic]?"

**Primary scope:** `knowledge-base/wiki/sources/`  
**Secondary scope:** `raw/`

**Steps:**
1. Search sources/ by topic or author
2. Check raw/ if not yet compiled
3. Use grep for keyword match

---

## Code Questions

**Pattern:** "Show me code for [feature]"

**Primary scope:** `learning/`, `ai-labs/projects/`  
**Secondary scope:** `working/`

**Steps:**
1. Search by language folder first
2. Use grep for function/class names
3. Read full file for context

---

## Task Status Questions

**Pattern:** "What tasks are pending?"

**Primary scope:** `tasks/scheduled/`, `tasks/processing/`

**Steps:**
1. List files in scheduled/
2. Read frontmatter for status
3. Summarize by deadline

---

## Content Questions

**Pattern:** "What did I write about [topic]?"

**Primary scope:** `working/`  
**Secondary scope:** `knowledge-base/wiki/concepts/`

**Steps:**
1. Search working/ by domain (Coin68, X, Substack)
2. Check published/ folders
3. Cross-reference with KB concepts
