# SKILL — X Article Writer

**Agent:** Hermes (local)  
**Purpose:** Write long-form articles for X (Twitter) Premium  
**Version:** 1.0  
**Last updated:** 2026-05-18

---

## Role

Write high-quality long-form articles for X platform following one of 4 predefined author styles. Each style targets a different audience and serves a different purpose.

X Article Writer handles:
- Style-based article generation (4 distinct voices)
- Research and source verification
- Format optimization for X long-form
- Quality assurance before delivery

---

## When to Use

Load this skill when:
- Task `domain: x` in frontmatter
- Task `skill: x-article-writer` in frontmatter
- Task `style: <author-name>` specified

Do NOT use for:
- X threads (use `thread-writer`)
- X posts (single tweets, use baseline writing)
- Coin68 articles (use `coin68-writer`)
- Substack essays (use `substack-writer`)
## CT Voice Integration

**This skill follows CT (Crypto Twitter) voice guidelines.**

See master guides:
- [../SKILL.md](../SKILL.md) — Content type selection + CT voice overview
- [../slang.md](../slang.md) — CT slang lexicon
- [../emoji.md](../emoji.md) — CT emoji guide

### CT Tie-In Rule for Articles

**Every CT article must connect to crypto.**

Articles have more flexibility than posts/threads, but crypto connection must be clear:

**Direct (crypto-native topic):**
- Protocol deep dives
- DeFi mechanism explanations
- Crypto market analysis

**Indirect (general topic, crypto lens):**
- "How to build a personal brand in crypto"
- "Productivity systems for managing 10+ degen plays"
- "Research methods for alpha hunting"

**Metaphorical (crypto concepts explain topic):**
- "Building systems like composable protocols"
- "Learning frameworks as liquidity pools"

**Opening paragraph must establish crypto relevance.**

### Slang Usage in Articles

**Frequency:** 5-10 slang terms per article (natural distribution)

**Distribution strategy:**
- **Opening (1-2):** Establish CT voice early
- **Body (3-6):** Spread naturally, not clustered
- **Closing (1-2):** Community vibe

**Tier usage:**
- **Tier 1 (freely):** gm, ser, fren, anon, wagmi, ngmi, degen, based
- **Tier 2 (with context):** aped in, rugged, jeet, cope, pilled, send it, nuke, LFG
- **Tier 3 (explain first):** midcurve, gigabrain, skill issue, mog, grok

**Style-specific adjustments:**
- **Gideon:** More Tier 1 (accessible)
- **Stacy:** Less slang overall (analytical)
- **Jeff:** Tier 1 + Tier 2 (builder voice)
- **Warhol:** More Tier 2 + Tier 3 (edgy)

See [/home/julius/julius-workspace/ai-labs/resource/skills/x-skills/slang.md] for full lexicon.

### Emoji Usage in Articles

**Frequency:** 5-10 emojis total (minimal compared to posts/threads)

**Placement:**
- **Headers (0-1 per header):** Section markers
- **Key points (rare):** Emphasis only
- **Closing (1-2):** CTA

**CT-specific emojis for articles:**
- 🧠 (research/deep dive headers)
- 🎯 (key insight emphasis)
- 🔬 (analysis sections)
- 📝 (note/documentation)
- 🫡 (closing CTA)

**Avoid in articles:**
- Hype emojis (🚀, 🔥) unless genuinely warranted
- Multiple emojis per paragraph
- Emoji in every header

See [/home/julius/julius-workspace/ai-labs/resource/skills/x-skills/emoji.md] for full guide.
---

## Style Selection

Julius specifies style in task frontmatter:

```yaml
---
type: task
task_type: article
domain: x
skill: x-article-writer
style: gideon | stacy | jeff | warhol
target: working/X/contents/draft/<slug>.md
---
```

### 4 Available Styles

| Style | Author | Best For | Audience |
|---|---|---|---|
| **gideon** | Gideon Ng | Empathetic teaching, anti-hype | Retail overwhelmed by tools/trends |
| **stacy** | Stacy Muur | Analytical research, data-driven | Institutional + sophisticated retail |
| **jeff** | 0xJeff | Transparent experimentation | Builders, technical experimenters |
| **warhol** | DeFi Warhol | Skeptical analysis, critical | Investors burned by narratives |

→ See [styles/](styles/) folder for detailed style guides.

---

## Common Elements (All Styles)

Regardless of style, all X articles must have:

### Frontmatter
```yaml
---
type: article
platform: x
style: gideon | stacy | jeff | warhol
topic: <main-topic>
status: draft
created: YYYY-MM-DD
---
```

### Structure
- **Title:** Declarative, specific, under 70 characters
- **Opening:** Hook + thesis in 2-3 lines
- **Body:** H2 sections (style-dependent)
- **Closing:** Style-appropriate conclusion

### Length
- **Short:** 800-1200 words (quick insight)
- **Medium:** 1200-1800 words (standard analysis)
- **Long:** 1800-2500 words (deep research)

→ Length determined by topic complexity, not style.

### Universal Rules
- **Language:** English (crypto-native culture)
- **No emoji** in headers or as decoration
- **Sparse use** of emoji in body (only for emphasis, max 3-5 per article)
- **No exclamation marks** (except in direct quotes)
- **Citations:** Link to sources when making factual claims

---

## Workflow

See [workflow.md](workflow.md) for detailed step-by-step process (universal across styles).

**Quick summary:**
1. **Read style guide** (`styles/<style>.md`)
2. **Research** topic + sources
3. **Outline** following style structure
4. **Draft** with style-specific voice
5. **Verify** facts and citations
6. **Polish** for style consistency

---

## Quality Standards

Before marking article done, verify:

**Content:**
- [ ] Factually accurate (claims sourced)
- [ ] Complete (no placeholders)
- [ ] Style-consistent (matches chosen voice)
- [ ] Length appropriate for topic complexity

**Format:**
- [ ] Frontmatter complete with `style:` field
- [ ] Title under 70 characters
- [ ] H2/H3 hierarchy correct
- [ ] No markdown images (Julius adds separately)
- [ ] No emoji in headers

**Style-specific:**
- [ ] Matches voice patterns of chosen author
- [ ] Uses style-appropriate structure
- [ ] Avoids style anti-patterns (see style guide)

---

## Style Comparison Quick Reference

| Aspect | Gideon | Stacy | Jeff | Warhol |
|---|---|---|---|---|
| **Tone** | Empathetic teacher | Neutral analyst | Transparent builder | Skeptical critic |
| **Opening** | Pain point + personal story | Contrarian thesis | Discovery moment | Provocative claim |
| **Data** | Anecdotal + community quotes | Institutional + tables | Tool-specific + screenshots | Comparative ROI tables |
| **Structure** | Problem → Framework → Solution | Thesis → Analysis → Implications | Discovery → Build → Share | Claim → Evidence → Nuance |
| **CTA** | Soft (newsletter, free guide) | None | Community feedback | Disclosure only |
| **Vulnerability** | High ("I was stuck too") | Low (professional) | Medium ("I tried, failed") | Low-medium ("I'm a holder") |

---

## Escalation

Escalate to `tasks/inbox/escalation-*.md` when:

- Style not specified in task frontmatter
- Topic doesn't fit any of the 4 styles well
- Cannot verify key claims (factual accuracy at risk)
- Topic is sensitive (political, regulatory, controversial)
- Style mixing requested (escalate to confirm approach)

---

## References

- [workflow.md](workflow.md) — Universal workflow for all styles
- [styles/gideon-style.md](styles/gideon-style.md) — Empathetic teacher style
- [styles/stacy-style.md](styles/stacy-style.md) — Analytical research style
- [styles/jeff-style.md](styles/jeff-style.md) — Transparent builder style
- [styles/warhol-style.md](styles/warhol-style.md) — Skeptical critic style
- [templates.md](templates.md) — Article structure templates per style

---

**Maintainer:** Julius  
**Last updated:** 2026-05-18
