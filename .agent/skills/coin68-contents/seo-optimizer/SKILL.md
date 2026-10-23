# SKILL — Coin68 SEO Optimizer

**Agent:** Hermes (local)
**Purpose:** Generate pre-writing SEO/GEO brief for Coin68 articles
**Version:** 1.1
**Last updated:** 2026-05-26

---

## Role

Generate an SEO brief **before** content-writer starts drafting. The brief provides keywords, optimized title, meta description, competitor analysis, and content angle — everything content-writer needs to produce a search-optimized article.

---

## When to Use

Load this skill when:
- A new Coin68 article is about to be written
- Julius requests keyword research for a project
- Pipeline scheduler selects a project from Google Sheets queue

Do NOT use for:
- Post-writing audit (use `seo-audit/` instead)
- Non-Coin68 content (this skill is Coin68-specific)

---

## Key Principles

### Principle 1: SEO = GEO

Google's official guide (May 2026) states that optimizing for generative AI search **is** SEO. There is no separate discipline.

**How it works:**
- AI Overviews and AI Mode are built on top of Google's core Search ranking and quality systems
- Google uses **Retrieval-Augmented Generation (RAG)** — a technique that retrieves relevant web pages from the Search index, then reviews specific information from those pages to generate AI responses with clickable links
- If content doesn't rank well in traditional search, it **will not** appear in AI-generated answers
- Google also uses **query fan-out** — the AI model generates a set of concurrent, related queries to gather comprehensive information for a single response

**Implication for Coin68:**
Traditional SEO quality is the prerequisite. An article must be well-structured, factually accurate, and technically sound to have any chance of appearing in AI Overviews or AI Mode results.

> Source: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide

---

### Principle 2: Non-Commodity Content

Google defines **commodity content** as content based on common knowledge that could originate from anyone and adds little unique insight (e.g., "7 Tips for First-Time Homebuyers"). In contrast, **non-commodity content** provides unique expert or experienced takes that go beyond the ordinary.

**How GSRs choose content:**
- Generative Search Results (GSRs) are AI-generated responses that synthesize information from multiple web sources
- Unlike featured snippets (cite 1 source), GSRs pull from several sources and blend them
- AI systems look at a variety of sources, so having a unique viewpoint that stands out is valuable
- Content that is unique, compelling, and useful influences presence in generative AI search more than any other factor

**Implication for Coin68:**
The standard "[Project] la gi?" format is inherently commodity-like. To differentiate:
- Include specific, verified numbers (TVL, volume, user counts, funding amounts)
- Provide comparative analysis (how does this project differ from competitors?)
- Add first-hand technical analysis (architecture evaluation, mechanism breakdown)
- Cite primary sources (official docs, whitepapers) rather than secondary reporting

> Source: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide

---

### Principle 3: Query Fan-Out Optimization

When a user searches for "[Project] la gi?", Google's AI doesn't just answer that single query. It generates **fan-out queries** to build a comprehensive response.

**Example:**
- Original query: "Variational la gi?"
- Fan-out queries the AI might generate:
  - "Variational protocol tokenomics"
  - "Variational team founders"
  - "Variational investors funding round"
  - "Variational vs Hyperliquid comparison"
  - "How to use Variational exchange"

**Implication for Coin68:**
Articles that naturally cover these fan-out angles (tokenomics, team, investors, comparisons, how-to) are more likely to be sourced by AI responses. The article structure in Coin68's Review template already covers most of these — the key is ensuring each section is substantive enough to stand alone as an answer.

> Source: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide

---

### Principle 4: E-E-A-T Signals

GSRs favor content with strong **Experience, Expertise, Authoritativeness, and Trustworthiness** (E-E-A-T):

- **Experience:** Content based on first-hand use or analysis, not just summarizing other articles
- **Expertise:** Technical depth with correct terminology and accurate explanations
- **Authoritativeness:** Citing official, primary sources (project docs, whitepapers, official announcements)
- **Trustworthiness:** Verified facts, neutral tone, transparent about what is confirmed vs claimed

**Implication for Coin68:**
- Always cite official sources, not secondary reporting
- Use the kiem chung (verification) block to demonstrate fact-checking rigor
- Maintain neutral, analytical tone — no hype, no investment advice
- Correct use of crypto-native terminology signals expertise

> Source: https://sagepath-reply.com/blog/digital-marketing/optimize-content-generative-ai-search-engines/

---

### Principle 5: Content Structure for AI Parsability

AI models prioritize content that answers questions fast and is easy to parse.

**Best practices:**
- **Lead with clear, direct answers** — Use the inverted pyramid model: answer the main query in opening lines, then elaborate
- **Conversational headings** — Use headings that match how users phrase queries naturally (e.g., "[Project] la gi?" not just "Gioi thieu")
- **Each section can standalone** — AI may extract a single H2 section as an answer. Each section should be self-contained and informative
- **Organized by paragraphs and sections** — Clear headings that provide structure to navigate content
- **Semantic HTML principles** — Proper heading hierarchy (H1 > H2 > H3), descriptive headings, logical flow

**What NOT to do (Google Mythbusting):**
- Do NOT create LLMS.txt files or special AI markup — Google does not treat them specially
- Do NOT "chunk" content into tiny pieces for AI — Google understands nuance of multiple topics on a page
- Do NOT rewrite content just for AI systems — AI understands synonyms and general meanings
- Do NOT seek inauthentic "mentions" across the web — focus on high-quality content instead
- Do NOT overfocus on structured data — it helps with rich results but is not required for AI search
- Do NOT create separate content for every query variation — this violates Google's scaled content abuse spam policy

> Source: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
> Source: https://illex.substack.com/p/generative-search-optimization-gso

---

## Workflow

### Step 1: Keyword Research

#### Primary Keyword

The primary keyword for Coin68 Review articles follows a consistent pattern:

```
"[Project] la gi"
```

This is the core informational query that drives traffic to Coin68 project reviews.

**Examples:**
- "Variational la gi"
- "Phoenix la gi"
- "Belo la gi"

#### Secondary Keywords

Gather from 3 sources:

**a) Category terms** — From `working/Coin68/contents/published/published.md`:
- Identify which category tag the project belongs to (perp-dex, defi, layer-1, etc.)
- Use category name as secondary keyword
- Examples: "perp DEX", "DeFi protocol", "layer-2 Ethereum"

**b) Feature-specific terms** — From project documentation:
- Technical features or mechanisms unique to the project
- Examples: "matching engine", "liquidity aggregation", "zero-knowledge proof"

**c) Blockchain-specific terms** — From project info:
- Which blockchain(s) the project operates on
- Examples: "Solana", "Ethereum", "Base", "Arbitrum"

#### Long-tail Keywords (Query Fan-out Anticipation)

Predict the related queries AI will fan-out to. Use Vietnamese natural phrasing.

**Lưu ý:** Long-tail keywords viết không dấu vì người Việt thường search không dấu trên Google. Ví dụ: "Tokenomics cua Variational", không phải "Tokenomics của Variational".

- "Tokenomics cua [Project]"
- "Doi ngu phat trien [Project]"
- "Nha dau tu cua [Project]"
- "[Project] so voi [Competitor]"
- "Cach su dung [Project]"
- "Danh gia [Project] [year]"
- "[Project] co an toan khong"
- "[Category] tot nhat [year]" (e.g., "perp DEX tot nhat 2026")

---

### Step 2: Title Optimization

**Format:** `[Project] la gi? Tim hieu ve [short description]`

**Constraints:**
- Primary keyword ("[Project] la gi") at the beginning
- Under 60 characters (Google truncates around 60)
- Include core value proposition in description part
- Keep crypto-native terms in English (perp DEX, not "san giao dich vinh vien")

**Process:**
1. Generate 3 title variations
2. Check character count for each
3. Recommend the best one (shortest that captures key differentiator)

**Examples:**

Good:
```
Phoenix la gi? Tim hieu ve fully on-chain perp DEX tren Solana     (55 chars)
Variational la gi? Tim hieu ve giao thuc phai sinh da tai san      (57 chars)
```

Bad:
```
Phoenix: San Giao Dich Perpetual Tot Nhat Tren Solana!             (superlative, exclamation)
Tim hieu tat ca ve du an Phoenix va cong nghe blockchain Solana    (too long, keyword buried)
```

---

### Step 3: Meta Description

The meta description maps to the `description` field in article frontmatter.

**Constraints:**
- 150-160 characters
- Include primary keyword naturally
- Include core value proposition
- Informative and specific (not generic)
- Vietnamese, formal tone

**Template:**
```
[Project] la [category] [description ngan]. Tim hieu [diem noi bat 1], [diem noi bat 2] va [diem noi bat 3] cua du an.
```

**Example:**
```yaml
description: "Variational la giao thuc phai sinh phi tap trung tong hop thanh khoan tu crypto va TradFi. Tim hieu san pham, doi ngu va tokenomics cua du an."
```
(148 characters)

---

### Step 4: Competitor Analysis (Internal)

**Prefer** reading reference article notes from Research Dossier (source-researcher Phase 0.2).
Only re-read published articles directly if Dossier notes are insufficient for SEO comparison.

Compare with existing Coin68 published articles in the same category.

**Process:**

1. Read `working/Coin68/contents/published/published.md` — identify category tag
2. Find 2-3 published articles with the same tag
3. Read each article and note:

| Aspect | What to Look For |
|---|---|
| **Sections covered** | Which H2 sections are present? (team, investors, tokenomics, etc.) |
| **Keywords used** | What terms appear in title + headings? |
| **Data cited** | What specific numbers are included? (TVL, volume, funding, users) |
| **Sources cited** | Official docs? Whitepaper? Twitter? |
| **Length** | Word count and section depth |
| **Gaps** | What angles are NOT covered? |

4. Output gap analysis — uncovered angles = opportunities for the new article

**Example gap finding:**
```
Category: perp-dex
Published articles analyzed:
- phoenix.md: Covers architecture, matching engine, fees. No comparison with other perp DEXs.
- hyperliquid.md: Covers HLP vault, order types. No tokenomics section (TGE hadn't happened).

Gaps identified:
- No published article compares fee structures across perp DEXs
- Most articles lack specific volume/TVL numbers
- None discuss risk management mechanisms in depth
```

---

### Step 5: Content Angle Recommendation

Based on competitor gaps + project uniqueness, recommend what to emphasize.

**Non-commodity angle checklist:**
- What specific data can this article include that others don't?
- What technical mechanism is unique to this project?
- What comparison with competitors would be valuable?
- What first-hand analysis can be provided?

**Output format:**
```
Recommended angle: [1-2 sentences describing the unique angle]
Key differentiators to emphasize:
1. [Specific feature/data point]
2. [Specific feature/data point]
3. [Specific feature/data point]
```

**Example:**
```
Recommended angle: Nhấn mạnh Osero là infrastructure layer cho stablecoin yield, 
không phải app consumer — khác biệt với các bài yield app thông thường.
Key differentiators to emphasize:
1. SDK "10 dòng code" — rào cản tích hợp thấp nhất thị trường
2. Basel III-inspired risk framework — chuẩn ngân hàng áp dụng lên DeFi
3. $2.5B allocation capacity qua Sky Agent Network — quy mô institution-grade
```

---

## Output Format

The SEO brief should be delivered as a markdown block that content-writer can reference while drafting:

```markdown
## SEO Brief: [Project Name]

**Date:** YYYY-MM-DD
**Category:** [tag from published.md]
**Article type:** Review

### Keywords
- **Primary:** [Project] la gi
- **Secondary:** [list of 3-5 terms]
- **Long-tail (fan-out):** [list of 5-8 queries]

### Title (Recommended)
1. [Title option 1] (XX chars) <- recommended
2. [Title option 2] (XX chars)
3. [Title option 3] (XX chars)

### Meta Description
[150-160 char description for frontmatter]

### Competitor Analysis
| Article | Sections | Data Points | Gaps |
|---------|----------|-------------|------|
| [article-1.md] | [list] | [list] | [list] |
| [article-2.md] | [list] | [list] | [list] |

### Content Angle
**Recommended angle:** [description]
**Key differentiators:**
1. [point]
2. [point]
3. [point]

### Heading Suggestions (Query Fan-out Coverage)
- H2: [Project] la gi?
- H2: Diem noi bat cua [Project]
  - H3: [Feature matching fan-out query 1]
  - H3: [Feature matching fan-out query 2]
- H2: Tokenomics (covers "[Project] tokenomics" fan-out)
- H2: Doi ngu phat trien (covers "doi ngu [Project]" fan-out)
- H2: Nha dau tu (covers "nha dau tu [Project]" fan-out)
- H2: Tong ket
```

---

## Escalation

Escalate to `tasks/inbox/escalation-*.md` when:
- Project category does not match any tag in published.md index
- No published articles exist in the same category for comparison
- Project has very limited public information (no docs, no whitepaper)
- Primary keyword has extremely high competition and may need alternative approach

---

## References

These sources were used to compile the principles in this skill:

1. **Google Search Central** — "Optimizing your website for generative AI features on Google Search" (May 2026)
   - URL: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
   - Authority: Official Google documentation
   - Key topics: RAG, query fan-out, non-commodity content, mythbusting

2. **Sagepath Reply** — "How to Optimize Content for Generative AI Search Engines" (June 2025)
   - URL: https://sagepath-reply.com/blog/digital-marketing/optimize-content-generative-ai-search-engines/
   - Authority: Practitioner guide with real GSR citation examples
   - Key topics: GSR definition, E-E-A-T, content formatting, schema markup

3. **Illex / Mason Nguyen** — "Generative Search Optimization (GSO): A Step-by-Step Guide" (June 2025)
   - URL: https://illex.substack.com/p/generative-search-optimization-gso
   - Authority: Implementation guide from AWS Certified AI Practitioner
   - Key topics: Semantic HTML, declarative facts, schema markup, monitoring

---

**Maintainer:** Julius
**Last updated:** 2026-05-25
