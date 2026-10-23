# SKILL — Coin68 Writer

**Agent:** Hermes (local)
**Purpose:** Write Vietnamese crypto articles for Coin68
**Version:** 2.2
**Last updated:** 2026-05-26

---

## Role

Write high-quality Vietnamese articles about crypto projects for Coin68 publication. Follow Coin68's editorial standards, voice, and structure conventions.

Coin68 Writer handles:
- Project research and fact verification
- Vietnamese content writing (formal, analytical tone)
- Structure following Coin68 conventions
- Crypto-native terminology (keep English terms where appropriate)
- Quality assurance before delivery

---

## When to Use

Load this skill when:
- Task `domain: coin68` in frontmatter
- Task `skill: coin68-writer` in frontmatter
- Task type is article about crypto project

Do NOT use for:
- X content (use `x-article-writer` or `thread-writer`)
- Substack content (use `substack-writer`)
- Non-crypto content

---

## Article Types

Coin68 publishes 3 types of articles:

| Type | Vietnamese | Length | Use Case |
|---|---|---|---|
| **News** | Tin tức | 300-600 words | Quick event coverage, announcements |
| **Review** | Review dự án | 800-1500 words | "[Project] là gì?" encyclopedia-style |
| **Deep-dive** | Phân tích chuyên sâu | 1200-3000 words | Tokenomics, on-chain analysis, ecosystem |

**Current template:** Review dự án only (News and Deep-dive templates TBD)

---

## Input

### Required
- Project name
- Project description (1-2 sentences)
- Category (perpdex, defi, layer1, layer2, etc.)
- **Research Dossier** (from `source-researcher/` skill) — contains verified sources, key metrics, cross-links, gaps
- **SEO Brief** (from `seo-optimizer/` skill) — contains keywords, optimized title, meta description, competitor gaps

### Optional but recommended
- Project website/docs
- Whitepaper
- Team info
- Investor info
- Tokenomics data
- Context files from `working/Coin68/context/`
- Concepts from `knowledge-base/wiki/concepts/`

### Fallback Mode (standalone)

Nếu Research Dossier hoặc SEO Brief không có sẵn:
- Content-writer tự research từ URLs được cung cấp (theo `source-researcher/SKILL.md` workflow)
- Tự generate title, meta description, keywords
- Ghi chú trong output: "Written without Dossier/SEO Brief — recommend re-running pipeline"

---

## Output

### Location
`working/Coin68/contents/drafts/<project-slug>.md`

### Format
- Markdown file with YAML frontmatter
- Vietnamese language (formal, analytical)
- 1000-2000 words (for Review type)
- Proper heading hierarchy (H1 → H2 → H3)
- Meta description in frontmatter (150-160 chars)
- Internal linking section ("Có thể bạn quan tâm")
- No images in markdown (Julius adds separately)

---

## Workflow

See [workflow.md](workflow.md) for detailed step-by-step process.

### Quick Workflow

1. **Đọc Research Dossier** (từ source-researcher) + **SEO Brief** (từ seo-optimizer)
2. **Viết outline** dựa trên dossier (sections nào có, sections nào thiếu)
3. **Viết draft** theo template (templates.md)
4. **Thêm "Có thể bạn quan tâm"** (cross-links từ dossier)
5. **Append kiểm chứng thông tin block**
6. **Tự review:** grammar, tone, terminology → sửa
7. **Output** ra `working/Coin68/contents/drafts/<project-slug>.md`

---

## Quality Standards

Before marking article done, verify:

**Content:**
- [ ] Factually accurate (all claims verified)
- [ ] Complete (no placeholders or TODOs)
- [ ] Neutral tone (no hype, no FUD)
- [ ] Proper Vietnamese grammar
- [ ] Crypto terms handled correctly (see Style Guide)

**Structure:**
- [ ] Follows template (required sections present)
- [ ] Proper heading hierarchy (H1 → H2 → H3)
- [ ] Logical flow (intro → features → team → conclusion)
- [ ] Appropriate length (1000-2000 words for Review)

**Format:**
- [ ] Frontmatter complete (including `description` field)
- [ ] Meta description 150-160 chars
- [ ] Internal linking section present
- [ ] Bold used correctly (project name first mention, key numbers)
- [ ] Bullet points for lists
- [ ] No markdown images (Julius adds separately)
- [ ] No emoji

---

## Style Guide

### Language
- **Primary:** Vietnamese (formal, analytical)
- **Crypto-native terms:** Keep in English
  - Use: perp DEX, matching engine, liquidity pool, staking, tokenomics
  - Avoid forced translations: "sàn giao dịch vĩnh viễn", "hồ thanh khoản"

### Tone
- Analytical, neutral
- No hype: avoid "revolutionary", "game-changing", "to the moon"
- No FUD: avoid "scam", "rug pull" without evidence
- No investment advice: never "should buy", "good entry point"

### Formatting
- **Bold:** Project name (first mention), key numbers
- *Italic:* Technical terms on first use (with brief explanation)
- **Bullet points:** For lists of features, team members, investors
- No emoji
- No exclamation marks (except in direct quotes)

### Terminology
See [templates.md](templates.md) for full terminology guide.

---

## Kiểm Chứng Block

Mọi draft **PHẢI** kết thúc bằng block kiểm chứng thông tin. Block này là nội bộ (không publish), giúp Julius review độ tin cậy.

**Format:**

```markdown
## Kiểm chứng thông tin (NỘI BỘ)

| Mục | Trạng thái | Ghi chú |
|-----|-----------|--------|
| [Claim 1] | ✅/⚠️/❌ | [Source URL hoặc lý do] |
| [Claim 2] | ✅/⚠️/❌ | [Source URL hoặc lý do] |
```

**Trạng thái:**
- ✅ Đã xác minh — có nguồn chính thức (docs / blog / site)
- ⚠️ Cần cập nhật — nguồn có thể đã cũ
- ❌ Chưa có nguồn — cần Julius bổ sung

**Nếu có Research Dossier:** Lấy trạng thái trực tiếp từ Dossier Verification Table.
**Nếu standalone:** Tự verify theo `source-researcher/` Phase 4 logic.

---

## Escalation

Escalate to `tasks/inbox/escalation-*.md` when:

- Source material contradicts itself
- Cannot verify key claims (team, investors, tokenomics)
- Project category unclear (not in Coin68 published index)
- Source material is not in Vietnamese or English
- Project involves sensitive topics (regulation, hacks, controversies)

---

## References

- [workflow.md](workflow.md) — Step-by-step writing process
- [examples.md](examples.md) — Good vs bad articles
- [templates.md](templates.md) — Article structure templates
- `working/Coin68/AGENTS.md` — Domain-specific rules
- `working/Coin68/contents/published/published.md` — Category index

## Related Skills

This skill works in a pipeline with sibling skills:
- **source-researcher/** — Collects & verifies sources before writing (input to this skill)
- **seo-optimizer/** — Generates SEO brief before writing (input to this skill)
- **seo-audit/** — Audits draft after writing (QA for this skill's output)

---

**Maintainer:** Julius
**Last updated:** 2026-05-26
