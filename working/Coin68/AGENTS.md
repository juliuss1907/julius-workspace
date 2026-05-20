# AGENTS.md — Coin68

> Inherits from: workspace/AGENTS.md
> Domain: Crypto/blockchain content writing for Coin68 (Vietnamese crypto media).

---

## 1. CONTEXT

Coin68 is a Vietnamese crypto news + research platform. Julius writes 3 broad types of content for Coin68:

| Type | Description | Length |
|---|---|---|
| **Tin tức** (News) | Quick-turnaround event coverage | 300-600 words |
| **Review dự án** (Project review) | "[Project] là gì?" encyclopedia-style article | 800-1500 words |
| **Phân tích chuyên sâu** (Deep dive) | Tokenomics, on-chain, ecosystem analysis | 1200-3000 words |

For all 3 types, output is in **Vietnamese**. General length target: **1000-2000 words** (deep-dives may exceed).

Brand context: `working/Coin68/context/coin68.md`
Julius's voice: `working/Coin68/context/julius.md`

---

## 2. ARTICLE CATEGORIES

Coin68 has many categories beyond a fixed set. The published index file maintains the canonical list:

**📌 Required step before writing**: Read `working/Coin68/contents/published/published.md` to identify the category that fits the current task.

### Rules
- ✅ READ the index to find an existing category match
- ❌ DO NOT add new categories to the index file (read-only access for Hermes)
- ❌ DO NOT auto-classify into a category that doesn't exist in the index
- ⚠️ If the project belongs to a NEW category not yet in the index → escalate to inbox and wait for Julius's approval

After identifying a matching category:
- Read 2-3 published articles in that category for voice/structure consistency
- Examples in `published/`: `solana.md`, `arbitrum.md`, `hyperliquid.md`, `zcash.md`, `perpdex.md`, `bluechip.md`, etc.

---

## 3. INPUT/OUTPUT

| Input | Output location |
|---|---|
| Source material (URL, PDF, project docs) | `working/Coin68/contents/drafts/<project-slug>.md` |
| Reference articles | Read from `working/Coin68/contents/published/` (read-only — Julius publishes) |
| Templates (charts, comparison tables) | Read from `working/Coin68/assets/templates/` |
| Category index | Read from `working/Coin68/contents/published/published.md` |

### Workflow rule
**Hermes writes ONLY to `drafts/`.** Julius edits drafts and manually moves to `published/` after final review. Hermes MUST NOT write to `published/` under any circumstances.

### Image handling
Image insertion is handled exclusively by Julius post-draft. Hermes does NOT touch images for Coin68 contents (see Section 7).

---

## 4. STYLE & FORMAT

Defer to the loaded skill (Section 5) for full format spec. Key cross-cutting rules apply regardless of skill:

- **Language**: Vietnamese (entire article body)
- **Length**: 1000-2000 words for standard articles; deep-dives may go up to 3000
- **Tone**: Analytical, neutral. No hype, no buy/sell recommendations
- **Bold**: First mention of project/org names, key numbers
- **Italic**: Technical terms on first use (with brief gloss)
- **Disclaimer**: All articles end with the standard Coin68 disclaimer

### Cross-language handling
Crypto-native English terms have priority over forced Vietnamese translation:
- ✅ `tokenomics`, `staking`, `liquidity pool`, `bridge`, `rollup`
- ❌ Forced VN translations like "kinh tế token", "cọc đặt", "hồ thanh khoản"

---

## 5. WORKFLOW

When Hermes receives a Coin68 task:

1. **Load TASK_SKILL** from `tasks/TASK_SKILL.md` (lifecycle methodology)
2. **Read category index** at `working/Coin68/contents/published/published.md` — identify matching category for the project
3. **Identify article type** from task description: news / review / deep-dive
4. **Load the corresponding skill** from `ai-labs/resource/skills/`:
   - News-style article → `article-writer/SKILL.md`
   - Review (encyclopedia "là gì?") → `article-writer/SKILL.md` (with review template flag)
   - Deep dive analysis → `researcher/SKILL.md` first, then `article-writer/SKILL.md`
5. **Read brand + voice context**: `context/coin68.md` + `context/julius.md`
6. **Read 2-3 reference articles** from the matched category in `published/` for voice/structure
7. **Execute the skill's workflow** (e.g., for review-style articles, the skill may enforce a multi-step process: source analysis → outline → draft, with checkpoints between steps)
8. **Write draft to** `working/Coin68/contents/drafts/<project-slug>.md`
9. **Append `kiểm chứng` block** at the end of the draft listing what's verified vs. needs verification
10. **Notify Julius** for approval

---

## 6. SKILL DEFAULTS

| Task type | Skill chain |
|---|---|
| Standard article | `ai-labs/resource/skills/article-writer/SKILL.md` |
| Deep research before writing | `researcher` → `article-writer` |
| SEO optimization (on request) | `seo-optimizer` (load on demand) |

If a Coin68-specific skill is later created at `ai-labs/resource/skills/coin68-writer/`, it overrides `article-writer` for Coin68 tasks.

---

## 7. BOUNDARIES (overrides parent)

- **Output language**: Vietnamese (overrides parent default)
- **Image generation**: ❌ DO NOT generate project images. Image handling is Julius's responsibility post-draft.
- **Token/price recommendations**: ❌ NEVER write "should buy", "good entry", "x10 potential" or any financial advice
- **Project claims vs facts**: Always distinguish. Use phrases: "Theo [Project]...", "Phía dự án công bố...", "Dự án cho biết..."
- **Coin68 internal links**: Only include URLs to coin68.com after web-search verification. Otherwise placeholder: `[Cần Julius bổ sung link bài liên quan]`
- **Category index**: Read-only. Do not add new categories without Julius's approval.

---

## 8. EXAMPLES

### Good

**Example A — Standard review with existing category**
> Task: "Write review article about Belo project"
> Action:
> 1. Load `tasks/TASK_SKILL.md` for lifecycle handling
> 2. Read `working/Coin68/contents/published/published.md` → find Belo fits the `perpdex` category
> 3. Article type = review → load `ai-labs/resource/skills/article-writer/SKILL.md`
> 4. Read `context/coin68.md` + `context/julius.md`
> 5. Read 2-3 reference perpdex articles from `published/`
> 6. Execute skill workflow → write to `drafts/belo.md`
> 7. Append `🔍 Kiểm chứng thông tin (NỘI BỘ)` block
> 8. Notify Julius

**Example B — New category requires escalation**
> Task: "Write review about a new RWA-focused protocol called XYZ"
> Action:
> 1. Read `published.md` → no `rwa` category exists in the index
> 2. STOP. Write to `tasks/inbox/escalation-2026-05-04-1430.md`:
>    "Project XYZ doesn't fit any existing category in published.md. Suggested new category: `rwa` (Real-World Assets). Should I:
>    (a) Use closest existing category (e.g., `bluechip`)?
>    (b) Wait for you to add `rwa` to the index?
>    Awaiting your decision."
> 3. Wait for Julius's response.

**Example C — Deep dive with research phase**
> Task: "Deep dive analysis on Solana ecosystem 2026"
> Action:
> 1. Read `published.md` → category = `layer-1`
> 2. Article type = deep-dive → load `researcher/SKILL.md` first
> 3. Execute research phase: gather on-chain data, ecosystem metrics, team interviews
> 4. Load `article-writer/SKILL.md` for writing phase
> 5. Read 2-3 published deep-dives in `layer-1` (e.g., `solana.md`, `zcash.md`)
> 6. Write to `drafts/solana-deep-dive-2026.md`
> 7. Append verification block, notify Julius

### Bad

**Anti-example A — Writing to published/**
> Task done, Hermes moves draft to `working/Coin68/content/published/belo.md`
> Why bad: Only Julius moves to published. Hermes stops at drafts.

**Anti-example B — Skipping category check**
> Task starts → Hermes immediately writes article without reading `published.md`
> Why bad: Category determines reference articles to read for voice consistency. Cannot skip Step 2 of workflow.

**Anti-example C — Adding new category to index**
> Project doesn't fit existing category → Hermes adds new entry to `published.md` and proceeds writing
> Why bad: Index is read-only. New categories require Julius's explicit approval via inbox.

**Anti-example D — Generating project images**
> Hermes generates project logo with image_generate tool → embeds in draft
> Why bad: Image handling is Julius's responsibility. Hermes never touches images for Coin68.

**Anti-example E — Investment advice creep**
> Concluding paragraph: "Với roadmap mạnh và team chất lượng, đây là dự án đáng để theo dõi và đầu tư"
> Why bad: "Đáng để đầu tư" is investment advice. Replace with neutral summary or remove.

---

## 9. ESCALATE WHEN

- Source material is in a language other than Vietnamese or English (need translation strategy)
- **Project belongs to a new category not yet in `published.md` → propose to Julius and wait for approval**
- Number of reference articles in same category < 2 (insufficient voice anchor)
- Source material contains contradictory information that can't be resolved from public web
