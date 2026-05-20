---
name: coin68-writer
description: Write Vietnamese crypto articles for Coin68 — project reviews, news, and deep-dives following editorial standards.
version: 1.1
last_updated: 2026-05-19
maintainer: Julius
agent: Hermes (local)
---

# SKILL — Coin68 Writer

## Role

Write high-quality Vietnamese articles about crypto projects for Coin68 publication. Follow Coin68's editorial standards, voice, and structure conventions.

Coin68 Writer handles:
- Project research and fact verification
- Vietnamese content writing (formal, analytical tone)
- Structure following Coin68 conventions
- Crypto-native terminology (keep English terms where appropriate)
- Quality assurance with kiểm chứng block before delivery

## When to Use

Load this skill when:
- Task `domain: coin68` in frontmatter
- Task `skill: coin68-writer` in frontmatter
- User asks to write a Coin68 article about a crypto project

Do NOT use for:
- X/Twitter content → use `x-post-writer` instead (CT voice, not Coin68 voice)
- Substack content
- Non-crypto content

When adapting a Coin68 article into an X thread or hot-take, load `x-post-writer` — the two skills have fundamentally different voices. Coin68 is analytical-neutral; X is degen-ct.

## Article Types

| Type | Vietnamese | Length | Use Case |
|---|---|---|---|
| **News** | Tin tức | 300-600 words | Quick event coverage, announcements |
| **Review** | Review dự án | 800-1500 words | "[Project] là gì?" encyclopedia-style |
| **Deep-dive** | Phân tích chuyên sâu | 1200-3000 words | Tokenomics, on-chain analysis, ecosystem |

## Input

### Required
- Project name
- Project category (from published.md tag list)
- Source material (docs, blog, whitepaper URLs)

### Recommended
- Team info
- Investor/funding info
- Tokenomics data
- Reference articles from same category (read 2-3 from `working/Coin68/contents/published/`)

## Output

### Location
`working/Coin68/contents/drafts/<project-slug>.md`

### Format
- YAML frontmatter + Vietnamese markdown body
- 1000-2000 words (for Review type)
- No images (Julius adds post-draft)
- kiểm chứng block at end of every draft

## Workflow

1. **Read category index** — `working/Coin68/contents/published/published.md` — match project to closest tag
2. **Read 2-3 reference articles** from same category in `working/Coin68/contents/published/` — extract structure patterns
3. **Gather sources** — navigate docs/blog URLs, extract content (prefer browser tools; web_search is unreliable)
4. **Write draft** following structure in [references/article-structure.md](references/article-structure.md)
5. **Append kiểm chứng block** — track what's verified vs needs Julius input (see format below)
6. **Write to** `working/Coin68/contents/drafts/<project-slug>.md`

## Kiểm Chứng Block Format

Every draft MUST end with:

```markdown
## 🔍 Kiểm chứng thông tin (NỘI BỘ)

| Mục | Trạng thái | Ghi chú |
|-----|-----------|--------|
| [Claim] | ✅/⚠️/❌ | [Source or reason] |
```

- ✅ Đã xác minh — has specific source
- ⚠️ Cần cập nhật — has source but may be stale
- ❌ Chưa có — needs Julius to supplement

## Quality Standards

**Content:**
- [ ] Factually accurate (all claims verified against source)
- [ ] Complete (no placeholders or TODOs)
- [ ] Neutral tone (no hype, no FUD, no investment advice)
- [ ] Proper Vietnamese grammar
- [ ] Crypto terms in English (staking, liquidity pool, smart contract — no forced translations)

**Structure:**
- [ ] Follows template from references/article-structure.md
- [ ] All required sections present (intro, body, team, investors, tổng kết, disclaimer)
- [ ] Proper heading hierarchy (H1 → H2 → H3)
- [ ] Logical flow

**Format:**
- [ ] Frontmatter complete (title, source, published, created, description, tags)
- [ ] Bold for project name (first mention) and key numbers
- [ ] No emoji in body
- [ ] No markdown images
- [ ] Kiểm chứng block appended

## Pitfalls

- **web_search unreliable**: Firecrawl backend can fail silently with `'NoneType' object has no attribute 'status_code'`. Fall back to `browser_navigate` + `browser_console` to extract content from documentation sites. Browser tools are slower but reliable for docs/blog content.
- **Wrong path trap**: Coin68 AGENTS.md at `working/Coin68/AGENTS.md` references paths as `content/` (singular). Actual filesystem uses `contents/` (plural). Always verify with `search_files` if a path 404s rather than assuming the file doesn't exist.
- **Category index is sparse**: `published.md` is a simple tag list (~40 hashtags). Match the closest existing tag; escalate to inbox only if genuinely no fit.
- **Don't generate images**: Coin68 image handling is Julius's responsibility post-draft. Never use `image_generate` for Coin68 articles.
- **Missing team/funding info**: When docs don't provide team or investor details, use the standard fallback sentences from the article structure reference. Don't make up information.

## Escalation

Escalate to `tasks/inbox/escalation-*.md` when:
- Project belongs to a genuinely new category not in published.md
- Source material contradicts itself and can't be resolved
- Cannot verify key claims
- Source material is not in Vietnamese or English

## References

- [references/article-structure.md](references/article-structure.md) — Canonical article structure (extracted from N1 Chain, Fermah, Converge)
- `working/Coin68/AGENTS.md` — Domain rules (⚠️ `content/` vs `contents/` path bug)
- `working/Coin68/contents/published/published.md` — Category index