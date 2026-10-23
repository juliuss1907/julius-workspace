# SKILL — Coin68 SEO Audit

**Agent:** Hermes (local)
**Purpose:** Post-writing SEO & content quality audit for Coin68 draft articles
**Version:** 1.2
**Last updated:** 2026-05-26

---

## Role

Audit SEO and content quality of a Coin68 draft article **after** content-writer has completed it, **before** presenting to Julius for review. The audit produces a structured report with pass/fail per criterion and specific action items.

---

## When to Use

Load this skill when:
- Content-writer has finished a draft in `working/Coin68/contents/drafts/`
- Julius requests an SEO review on an existing article
- Quality check step in the pipeline workflow

Do NOT use for:
- Pre-writing keyword research (use `seo-optimizer/` instead)
- Non-Coin68 content
- Articles that haven't been drafted yet

---

## Key Principles

### Why Audit Matters for AI Search

Google's generative AI features (AI Overviews, AI Mode) use **RAG (Retrieval-Augmented Generation)** to pull content from the Search index. Content must meet traditional SEO quality standards **before** it can appear in AI-generated answers.

An article that fails basic SEO checks — missing meta description, broken heading hierarchy, vague claims without data — will not rank in traditional search and therefore will not be sourced by AI responses.

### What AI Systems Look For

When Google's AI generates a response, it evaluates retrieved content for:
- **Direct answers** — Can a specific section answer a query on its own?
- **Factual specificity** — Are claims backed by numbers and sources?
- **Structural clarity** — Is the content organized with clear headings and logical flow?
- **Trustworthiness** — Are sources cited? Is tone neutral and authoritative?

These are the same attributes this audit checks.

> Source: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide

---

## Audit Categories

12 categories organized in 2 groups:

**SEO Categories (1-6):** Technical SEO, search visibility, AI parsability
**Quality Categories (7-12):** Content integrity, consistency, readability

---

### 1. Keyword Placement

| Check | Criteria | Status |
|---|---|---|
| Primary keyword in H1 title | "[Project] là gì" appears in the H1 | |
| Primary keyword in first paragraph | Opening paragraph contains project name + "là" definition | |
| Primary keyword in meta description | Frontmatter `description` field contains project name | |
| Natural keyword distribution | Primary keyword appears 3-5 times total, not forced | |
| Secondary keywords in headings | At least 1 H2 or H3 contains a category or feature term | |
| No keyword stuffing | No unnatural repetition, density below 2-3% | |

**Common issues in Coin68 articles:**
- Title too long (keyword gets truncated by Google)
- First paragraph is a generic intro instead of directly answering "[Project] là gì?"
- Secondary keywords missing from headings entirely

---

### 2. Title & Meta

| Check | Criteria | Status |
|---|---|---|
| Title format | Follows "[Project] là gì? Tìm hiểu về [description]" | |
| Title length | Under 60 characters | |
| Primary keyword position | "[Project] là gì" at the beginning of title | |
| Meta description exists | Frontmatter `description` field is present and non-empty | |
| Meta description length | 150-160 characters | |
| Meta description quality | Contains primary keyword + value proposition, is specific not generic | |

**How to check title length:**
Count characters in the frontmatter `title` field. If it exceeds 60, suggest a shorter alternative that preserves the primary keyword and core differentiator.

---

### 3. Heading Structure

| Check | Criteria | Status |
|---|---|---|
| Single H1 | Exactly one H1 (the article title) | |
| H2 for major sections | All major sections use H2 | |
| H3 for sub-sections | Feature lists, product components use H3 under H2 | |
| No level skips | No H1 → H3 without H2 in between | |
| Descriptive headings | Headings describe content, not generic ("Tính năng", "Tổng quan") | |
| Conversational where appropriate | Key sections use question-style headings matching search queries | |

**Good heading examples:**
```
## Variational là gì?                          (matches primary query)
## Điểm nổi bật của Variational                (descriptive)
### Cơ chế tổng hợp thanh khoản                (specific feature name)
## Đội ngũ phát triển                          (matches fan-out query)
```

**Bad heading examples:**
```
## Giới thiệu                                  (too generic)
## Tính năng                                   (not specific to project)
### Feature 1                                  (not descriptive)
```

---

### 4. Content Quality for AI Search

| Check | Criteria | Status |
|---|---|---|
| Direct answer in first paragraph | First paragraph directly answers "[Project] là gì?" in 2-3 sentences | |
| Standalone sections | Each H2 section makes sense if extracted alone as an AI answer | |
| Specific data | Article includes verifiable numbers (TVL, volume, funding, user count) | |
| Sources cited | Factual claims reference official sources (docs, whitepaper, announcements) | |
| No vague claims | No unsupported superlatives ("tốt nhất", "nhanh nhất", "an toàn nhất") | |
| Word count | 1000-2000 words for Review type | |

**Standalone section heuristic:**
1. Section có ít nhất 3 câu không? (quá ngắn = không standalone)
2. Câu đầu tiên có nhắc tên project không? (thiếu context = không standalone)
3. Section có chứa ít nhất 1 data point cụ thể không? (quá chung chung = không standalone)

Scoring: 3/3 = standalone; 2/3 = marginal; ≤1/3 = not standalone

**Non-commodity content signals:**
- Does the article include data that cannot be easily generated by AI? (specific on-chain metrics, proprietary analysis)
- Does it provide comparison or context that generic articles lack?
- Does it demonstrate understanding beyond surface-level description?

---

### 5. Frontmatter SEO Fields

| Check | Criteria | Status |
|---|---|---|
| `title` field | Present, optimized, under 60 chars | |
| `description` field | Present, 150-160 chars, contains primary keyword | |
| `tags` field | Present, matches category from published.md index | |
| `source` field | Present if article has been published (canonical URL) | |
| `created` field | Present with valid date (YYYY-MM-DD) | |

**Required frontmatter example:**
```yaml
---
title: "Variational là gì? Tìm hiểu về giao thức phái sinh phi tập trung đa tài sản"
source: "https://coin68.com/variational-la-gi/"
published: 2025-12-01
created: 2026-05-22
description: "Variational là giao thức phái sinh phi tập trung tổng hợp thanh khoản từ crypto và TradFi. Tìm hiểu sản phẩm, đội ngũ và tokenomics của dự án."
tags:
  - "perp-dex"
  - "infrastructure"
---
```

---

### 6. Authority & Trust Signals

| Check | Criteria | Status |
|---|---|---|
| Author attribution | Article clearly attributed to Coin68 | |
| Project verifiable presence | Project has docs, GitHub, X, or official website accessible | |
| Reputation signals | Partnerships, audits, notable backers mentioned where applicable | |
| Genuine expertise demonstrated | Content goes beyond surface-level description, shows technical understanding | |

**What this category covers:**
Authority & Trust focuses on whether the article demonstrates credibility as a source. This is what Google evaluates when deciding whether to cite content in AI responses.

**What this category does NOT cover (moved to dedicated categories):**
- Neutral tone → Category 8 (Tone & Voice)
- Crypto terminology → Category 9 (Terminology Consistency)
- Source attribution → Category 10 (Source Attribution)

> Source: https://sagepath-reply.com/blog/digital-marketing/optimize-content-generative-ai-search-engines/

---

### 7. Structure & Completeness

| Check | Criteria | Status |
|---|---|---|
| Required sections present | "là gì?", "Điểm nổi bật", "Đội ngũ", "Nhà đầu tư", "Tổng kết" | |
| Optional sections justified | Tokenomics only if has token; Sản phẩm chính only if multi-product | |
| No placeholder text | No "[TBD]", "[TODO]", "[cần bổ sung]" anywhere in article | |
| Gaps from Dossier addressed | All gaps either filled or marked "chưa công bố" | |
| No orphan H3 | Every H3 has a parent H2 | |
| Section order correct | là gì? → Điểm nổi bật → [optional] → Đội ngũ → NĐT → [Token] → Tổng kết → Cross-links | |
| Có thể bạn quan tâm present | Internal linking section with 2-3 related articles | |

**Section order reference:**
```
H1: [Project] là gì? Tìm hiểu về ...
  H2: [Project] là gì?
  H2: Điểm nổi bật của [Project]
    H3: [Feature 1]
    H3: [Feature 2]
  H2: [Sản phẩm chính / Cơ chế hoạt động] (optional)
  H2: Đội ngũ phát triển
  H2: Nhà đầu tư [và đối tác]
  H2: Tokenomics (optional, only if has token)
  H2: Tổng kết
  H2: Có thể bạn quan tâm
```

---

### 8. Tone & Voice

| Check | Criteria | Status |
|---|---|---|
| No hype language | No "cách mạng", "đột phá", "tuyệt vời", "game-changing", "revolutionary" | |
| No investment advice | No "nên mua", "cơ hội tốt", "đừng bỏ lỡ", "đáng để đầu tư" | |
| No FUD without evidence | No "scam", "rug pull" without cited source | |
| No exclamation marks | Except in direct quotes | |
| Analytical tone consistent | Entire article maintains formal, analytical voice | |
| No unverified superlatives | No "tốt nhất", "nhanh nhất", "an toàn nhất" without supporting data | |

**Detection patterns:**

Hype words to flag:
```
cực kỳ, tuyệt vời, đột phá, cách mạng, bùng nổ, siêu, khủng,
game-changing, revolutionary, disruptive, incredible, amazing
```

Investment advice patterns:
```
nên mua, đáng đầu tư, cơ hội, đừng bỏ lỡ, entry point,
tiềm năng tăng giá, x10, moon, gem
```

---

### 9. Terminology Consistency

| Check | Criteria | Status |
|---|---|---|
| English crypto terms kept | perp DEX, matching engine, liquidity pool, staking, tokenomics | |
| No forced translations | Not "sàn giao dịch vĩnh viễn", "hồ thanh khoản", "kinh tế token" | |
| Acceptable Vietnamese OK | "phí gas", "cầu" (bridge), "mã nguồn mở", "quản trị" are fine | |
| Consistent throughout | Same term used consistently, not switching between variants | |
| Project name consistent | Same casing/spelling throughout article | |

**Reference:** Cross-check against Terminology Guide in `content-writer/templates.md`.

**Common mistakes:**
```
❌ "sàn giao dịch vĩnh viễn phi tập trung" → ✅ "perp DEX"
❌ "hồ thanh khoản" → ✅ "liquidity pool"
❌ "kinh tế token" → ✅ "tokenomics"
❌ "sách trắng" → ✅ "whitepaper"
❌ "thả rơi" → ✅ "airdrop"
```

---

### 10. Source Attribution

| Check | Criteria | Status |
|---|---|---|
| Claims attributed | Factual claims use "Theo [source]...", "Dự án cho biết...", "Theo whitepaper..." | |
| No naked assertions | Specific numbers/dates always have source context | |
| Verification block present | Kiểm chứng block appended at end of article | |
| Block matches content | Every major claim in article has corresponding row in verification block | |
| Official sources preferred | Primary sources (docs, blog) cited over secondary (news articles) | |

**Attribution patterns (good):**
```
Theo whitepaper, Phoenix sử dụng matching engine kép...
Dự án cho biết đã huy động được $21 triệu trong vòng Series A.
Theo CoinDesk, vòng gọi vốn do Electric Capital dẫn đầu.
```

**Naked assertions (bad):**
```
Phoenix đã huy động $21 triệu.          (no source context)
Đội ngũ có kinh nghiệm 10 năm.          (unverified claim)
Dự án có 100k users.                     (no source, no date)
```

---

### 11. Data & Numbers Validation

| Check | Criteria | Status |
|---|---|---|
| Numbers have units | "$21 triệu" not just "21 triệu"; "1,000,000,000 tokens" not "1 triệu" | |
| Vietnamese number format | "$21 triệu" not "$21 million"; "1 tỷ" not "1 billion" | |
| Percentages valid | Token allocation percentages add up (≤ 100%) | |
| Dates formatted correctly | Q2/2026, tháng 4/2026, 15/05/2026 — not "April 2026" | |
| Comma for thousands | 1,000,000 not 1.000.000 | |
| Key numbers bold | Per style guide — funding amount, token supply, user count in bold | |

**Number format examples:**
```
✅ Dự án đã huy động được **$21 triệu** trong vòng Series A.
✅ **Tổng cung:** 1,000,000,000 PHNX
✅ Dự kiến ra mắt mainnet trong Q2/2026.
✅ Team allocation: 20% (vesting 4 năm)

❌ Dự án đã huy động được 21 million dollars.
❌ Tổng cung: 1.000.000.000 PHNX
❌ Dự kiến ra mắt mainnet trong April 2026.
```

---

### 12. Readability

| Check | Criteria | Status |
|---|---|---|
| No wall-of-text paragraphs | Max 4-5 sentences per paragraph | |
| Sentence variety | Mix of short (10-15 words) and medium (20-30 words) sentences | |
| Section balance | No single section > 300 words (unless justified by complexity) | |
| Opening answers query | First paragraph directly answers "[Project] là gì?" | |
| Logical transitions | Sections flow naturally, no abrupt topic jumps | |
| Target audience appropriate | Written for crypto-literate Vietnamese reader | |

**Readability red flags:**
- A paragraph with 6+ sentences → break it up
- Three consecutive sentences all > 30 words → vary length
- H2 section with 400+ words and no H3 sub-headings → needs structure
- Opening paragraph that doesn't mention the project name until sentence 3+

---

## Audit Modes

### Quick Mode

**For:** Standard Review articles (1000-2000 words)
**Categories:** 2 (Title & Meta), 3 (Heading Structure), 5 (Frontmatter Fields)
**Plus:** 1 critical check from C7: "No placeholder text"
**Total:** ~19 checks
**When to use:** Default for standard Review articles without special requirements

### Standard Mode

**For:** Most articles (recommended default for quality assurance)
**Categories:** 1-6 (SEO) + 7 (Structure & Completeness) + 9 (Terminology) + 10 (Source Attribution)
**Total:** 9 categories, ~45 checks
**When to use:** Default for articles going through the full pipeline

### Full Mode

**For:** Deep-dive, flagship, high-priority articles
**Categories:** All 1-12
**Total:** 12 categories, ~60 checks

**Preconditions (must meet at least 1):**
- Bài ≥ 2000 từ (deep-dive, flagship)
- Julius explicitly requests Full audit
- High-priority project từ pipeline (Priority = High in Google Sheet)
- Không auto-run Full trên mọi bài — resource-intensive

---

## Output Format

The audit report should be delivered as a structured markdown block:

```markdown
## SEO Audit Report: [Project Name]

**Date:** YYYY-MM-DD
**Draft:** working/Coin68/contents/drafts/[slug].md
**Mode:** Quick / Standard / Full
**Overall:** PASS / NEEDS WORK / FAIL
**Score:** X/[3+1 | 9 | 12] categories passed

### Results

| # | Category | Status | Issues |
|---|----------|--------|--------|
| 1 | Keyword Placement | pass/warn/fail | [specific issues or "No issues"] |
| 2 | Title & Meta | pass/warn/fail | [specific issues or "No issues"] |
| 3 | Heading Structure | pass/warn/fail | [specific issues or "No issues"] |
| 4 | Content Quality for AI | pass/warn/fail | [specific issues or "No issues"] |
| 5 | Frontmatter Fields | pass/warn/fail | [specific issues or "No issues"] |
| 6 | Authority & Trust | pass/warn/fail | [specific issues or "No issues"] |
| 7 | Structure & Completeness | pass/warn/fail | [specific issues or "No issues"] |
| 8 | Tone & Voice | pass/warn/fail | [specific issues or "No issues"] |
| 9 | Terminology Consistency | pass/warn/fail | [specific issues or "No issues"] |
| 10 | Source Attribution | pass/warn/fail | [specific issues or "No issues"] |
| 11 | Data & Numbers | pass/warn/fail | [specific issues or "No issues"] |
| 12 | Readability | pass/warn/fail | [specific issues or "No issues"] |

(In Quick/Standard mode, only checked categories are included in table)

### Action Items (if any)

1. [Specific fix: what to change and where]
2. [Specific fix: what to change and where]
3. [Specific fix: what to change and where]

### Summary

[1-2 sentences summarizing overall readiness and priority fixes]
```

**Scoring:**
- **PASS** — All checked categories pass. Ready for Julius review.
- **NEEDS WORK** — 1-2 categories have warnings. Can proceed but should fix before publishing.
- **FAIL** — 3+ categories fail or any critical issue found. Must fix before presenting to Julius.

**Status per category:**
- **pass** — All checks in this category met
- **warn** — Minor issues that don't block publishing but should be fixed
- **fail** — Critical issues that will harm SEO performance or content quality

---

## Post-Audit Flow

| Result | Action |
|--------|--------|
| **PASS** | Gửi Julius review |
| **NEEDS WORK** | Content-writer tự fix action items → re-run audit |
| **FAIL** | Content-writer fix critical issues → escalate nếu không tự fix được |

---

## Escalation

Escalate to `tasks/inbox/escalation-*.md` when:
- Draft is missing frontmatter entirely (structural issue, not SEO issue)
- Article category doesn't exist in published.md index
- Article contains potential investment advice or promotional language that needs Julius's judgment
- Word count is far outside expected range (< 500 or > 3000 for Review type)
- Content-writer cannot resolve FAIL issues after 2 attempts

---

## References

These sources were used to compile the audit criteria in this skill:

1. **Google Search Central** — "Optimizing your website for generative AI features on Google Search" (May 2026)
   - URL: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
   - Key topics: Content quality for AI, heading structure, non-commodity content

2. **Sagepath Reply** — "How to Optimize Content for Generative AI Search Engines" (June 2025)
   - URL: https://sagepath-reply.com/blog/digital-marketing/optimize-content-generative-ai-search-engines/
   - Key topics: E-E-A-T, content formatting, schema markup, conversational headings

3. **Illex / Mason Nguyen** — "Generative Search Optimization (GSO): A Step-by-Step Guide" (June 2025)
   - URL: https://illex.substack.com/p/generative-search-optimization-gso
   - Key topics: Semantic HTML, declarative facts, standalone paragraphs, metadata

---

**Maintainer:** Julius
**Last updated:** 2026-05-26
