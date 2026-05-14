# AGENTS.md — X (Twitter)

> Inherits from: workspace/AGENTS.md
> Domain: X (Twitter) content production — posts, threads, articles.

---

## 1. CONTEXT

Julius posts on X in **English**, following crypto-native + tech culture norms. Voice: **Educator, Guider, and Reviewer**. Audience: global crypto/AI/tech community.

The 3 content types serve distinct purposes:

| Type | Purpose | Length | Use case |
|---|---|---|---|
| **Post** | Quote-tweet style commentary, sharing perspective on others' work | 1 tweet (≤280 chars) | "Saw this article — here's my take..." |
| **Thread** | How-to guides, step-by-step content, content roundups | 5-15 connected tweets | Airdrop guides, setup walkthroughs, content compilations |
| **Article** | Long-form takes, original research, deep perspectives | 800-2500 words | Personal takes, research pieces, retrospectives |

---

## 2. INPUT/OUTPUT

| Input | Output location |
|---|---|
| Source URL/article (for Post) | `working/X/content/draft/post-<slug>.md` |
| Topic + outline (for Thread) | `working/X/content/draft/thread-<slug>.md` |
| Research notes (for Article) | `working/X/content/draft/article-<slug>.md` |
| Image assets per content piece | `working/X/images/<post-or-thread-or-article>-<slug>/` |

### Image folder rule
For each new content piece, Hermes creates a sibling folder in `images/` matching the content slug. Example:
- Content: `working/X/content/thread-rag-explained.md`
- Images: `working/X/images/thread-rag-explained/`

If no images needed, create empty folder with `.gitkeep`.

---

## 3. STYLE & FORMAT

### Universal X voice
- **Crypto-native English**: anon, gm, ngmi, bullish/bearish, alpha, etc. — use naturally, not forced
- **Educator tone**: explain to non-experts without being condescending
- **Guider tone**: when sharing how-to, be specific and actionable
- **Reviewer tone**: when commenting on others' work, be thoughtful and fair
- **No hype**: avoid "🚀🚀🚀", "TO THE MOON", "next 100x"
- **No financial advice**: never "buy this", "ape in", "guaranteed gains"

### Type-specific format

#### Post (single tweet)
- ≤280 chars
- Format: `[hook]\n\n[your take]\n\n[link or quote-tweet ref]`
- Use line breaks for visual hierarchy
- Tag relevant accounts only when adding value (not for clout)

#### Thread (multi-tweet)
- Tweet 1 = hook + value promise: "Here's how to [X] in 7 steps:"
- Tweets 2-N = one main idea per tweet, numbered or bulleted
- Last tweet = recap + CTA (follow, RT, link to longer content)
- Each tweet ≤280 chars; use line breaks within tweets

In the markdown file, separate tweets clearly:
```
## Tweet 1/8 (Hook)
<content>

## Tweet 2/8
<content>
```

#### Article (long-form)
- Title: declarative, specific, no clickbait
- Opening: hook + thesis in 2-3 lines
- Body: H2 headers for sections, short paragraphs (2-4 sentences)
- Conclusion: synthesis + reader takeaway

---

## 4. WORKFLOW

When Hermes receives an X task:

1. **Identify content type** from task: post / thread / article
2. **Load corresponding skill**:
   - Post: no skill needed (Hermes default)
   - Thread: `ai-labs/resource/skills/thread-writer/SKILL.md`
   - Article: `ai-labs/resource/skills/article-writer/SKILL.md`
3. **For Post**: read source URL/article, draft commentary, suggest 2-3 variations
4. **For Thread**: outline structure → write tweets → verify each ≤280 chars
5. **For Article**: research → outline → draft → polish
6. **Create image folder** matching content slug (empty `.gitkeep` if no images)
7. **Write to corresponding file** in `working/X/content/draft`
8. **Notify Julius** with preview

---

## 5. SKILL DEFAULTS

| Type | Default skill |
|---|---|
| Post | None (use Hermes baseline) |
| Thread | `thread-writer` |
| Article | `article-writer` |
| Research-heavy article | `researcher` (load first), then `article-writer` |

---

## 6. BOUNDARIES (overrides parent)

- **Language**: English (overrides parent default if parent is VN)
- **Quote-tweet posts**: Always include the original URL or quoted text in the markdown file so Julius knows context when posting
- **Thread length**: Hard cap 15 tweets. If exceeds, propose splitting into 2 threads or converting to article
- **No copyright issues**: For Posts referencing others' content, clearly attribute via @ mention or URL
- **Crypto disclaimers**: Threads/Articles touching specific projects should end with: "Not financial advice. DYOR." (or similar)

---

## 7. EXAMPLES

### Good

**Post example:**
> Task: "Comment on Vitalik's latest blog about rollups"
> Action: Read source → draft 3 variations:
> 1. Educator angle: explain key insight to non-technical
> 2. Guider angle: extract action item for builders
> 3. Reviewer angle: where you agree/disagree
> → Save to `post-vitalik-rollups-take.md` with all 3 variants for Julius to pick

**Thread example:**
> Task: "Thread: how to claim XYZ airdrop"
> Action: Load thread-writer skill → outline 8 tweets:
> 1. Hook (what + why care)
> 2-6. Steps with screenshots
> 7. Common mistakes
> 8. Recap + follow CTA
> → Save to `thread-xyz-airdrop-guide.md`, create `images/thread-xyz-airdrop-guide/` folder

### Bad

**Anti-example A — Treating thread as article**
> Task: "Thread about MEV"
> Bad: Hermes writes 2000-word essay in thread file
> Why bad: Threads are tweet-by-tweet, ≤280 chars each. Article format is wrong here.

**Anti-example B — Hype voice**
> Post: "🚀🚀🚀 SOLANA IS GOING TO FLIP ETH 🚀🚀🚀 NGMI IF YOU'RE NOT IN!"
> Why bad: Julius's voice is educator/guider/reviewer, not shitposter. No hype, no FUD.

**Anti-example C — Forgetting image folder**
> Hermes writes thread file but no `images/thread-<slug>/` folder
> Why bad: Convention requires sibling image folder, even if empty (`.gitkeep`).

---

## 8. ESCALATE WHEN

- Source URL is paywalled or inaccessible
- Topic overlaps with Coin68 territory (decide: cross-post or differentiate?)
- Thread would exceed 15 tweets
- Sensitive topic (politics, controversies) — confirm angle with Julius first
- Quote-tweet target is a personal/heated discussion (avoid getting Julius into beef)
