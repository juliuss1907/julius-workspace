# SKILL — Post Writer

**Agent:** Hermes (local)  
**Purpose:** Write single tweets for X (Twitter)  
**Version:** 1.0  
**Last updated:** 2026-05-19

---

## Role

Write high-quality single tweets (280 characters max) for X platform across 6 distinct post types. Each type serves a different purpose and follows specific patterns.

Post Writer handles:
- Type-based tweet generation (6 distinct intents)
- Character count optimization
- Engagement optimization (hooks, CTAs, questions)
- Niche-appropriate slang and emoji usage

---

## When to Use

Load this skill when:
- Task `domain: x` in frontmatter
- Task `skill: post-writer` in frontmatter
- Task `type: <post-type>` specified

Do NOT use for:
- X threads (use `thread-writer`)
- X long-form articles (use `x-article-writer`)
- Other platforms (Coin68, Substack, etc.)

---

## Post Types

Julius specifies type in task frontmatter:

```yaml
---
type: task
task_type: post
domain: x
skill: post-writer
post_type: tldr | hot-take | announcement | engagement | quote-tweet | freestyle
target: working/X/contents/posts/<slug>.md
---
```

### 6 Available Types

| Type | Purpose | Best For | Example |
|---|---|---|---|
| **tldr** | Summarize content | Article recap, product features | "Luxx in 3 bullets..." |
| **hot-take** | Share opinion | React to news, contrarian view | "Hot take: crypto's biggest competitor..." |
| **announcement** | Share update | Launch, milestone, event | "BITMART JUST UNLEASHED..." |
| **engagement** | Start conversation | Question, poll, debate | "Do you think we've hit the bottom..." |
| **quote-tweet** | React to post | Commentary on someone's tweet | (Reacts to original with added context) |
| **freestyle** | Casual thought | GM, random insight, vibe | "gm my jpeg frens..." |

→ See [types/](types/) folder for detailed type guides.

---

## Universal Rules

Regardless of type, all posts must:

### Character Limit
- **Hard limit:** 280 characters total
- **Optimal:** 240-270 characters (leaves room for retweets with comments)
- **If exceeds:** Convert to thread (escalate to thread-writer)

### Emoji Usage
- **Selective, not stuffed:** 2-5 emojis max per tweet
- **Strategic placement:** Hook, emphasis, or CTA
- **Avoid:** Emoji in every sentence, emoji as words

### Engagement Optimization
- **End with:** Question OR call-to-action OR cliffhanger
- **Hook first 10 words:** Grab attention immediately
- **Line breaks:** Use for readability (max 3-4 lines)

### Niche Slang
Mix according to topic/audience:

**Crypto/Solana:**
- "ser", "aped in", "rugged", "degen", "gm/gn", "wagmi", "ngmi"

**General crypto:**
- "bullish", "bearish", "rekt", "moon", "diamond hands"

**Professional:**
- Minimal slang, focus on clarity

→ **Rule:** Use slang naturally, not forced. 1-2 per tweet max.

---

## CT Voice Integration

**This skill follows CT (Crypto Twitter) voice guidelines.**

See master guides:
- [../SKILL.md](../SKILL.md) — Content type selection + CT voice overview
- [../slang.md](../slang.md) — CT slang lexicon
- [../emoji.md](../emoji.md) — CT emoji guide
- [ct-voice-guide.md](ct-voice-guide.md) — Tone calibration for posts

### CT Tie-In Rule

**Every CT post must connect to crypto in at least one way.**

**Connection types:**
- **Direct:** Topic is crypto-native ("How to use Uniswap")
- **Indirect:** General topic framed through crypto lens ("Obsidian for tracking alpha")
- **Metaphorical:** Use crypto concepts to explain ("Building brand = liquidity mining")

**If no crypto angle exists:** Wrong audience. Don't force it.

### Slang Usage in Posts

**Frequency:** 1-2 slang terms per tweet (max)

**Tiers:**
- **Tier 1 (use freely):** gm, ser, fren, anon, wagmi, ngmi, degen, based
- **Tier 2 (with context):** aped in, rugged, jeet, cope, pilled, send it, nuke, LFG
- **Tier 3 (sparingly):** midcurve, gigabrain, skill issue, mog, grok

**Placement:**
- Opening (establish voice): "gm frens", "ser"
- Mid-content (emphasis): "this is based"
- Closing (community): "wagmi", "LFG"

See [../slang.md](../slang.md) for full lexicon.

### Emoji Usage in Posts

**Frequency:** 2-5 emojis per tweet

**CT-specific emojis:**
- 🧠 (alpha/research)
- 🫡 (salute/respect)
- 🤝 (collab)
- 💀 (ngmi/rekt)
- 🧵 (thread - not for posts)

**Placement:**
- Hook (attention): 🚨, 👀, 🔥
- Emphasis (key point): 🎯, ⚡, 💎
- CTA (engagement): 🔄, 🔖, 👇

See [../emoji.md](../emoji.md) for full guide.
---

## Workflow

See [workflow.md](workflow.md) for detailed step-by-step process.

**Quick summary:**
1. **Read input** (article, news, thought)
2. **Determine type** (based on intent)
3. **Load type guide** (types/<type>.md)
4. **Extract key point** (1 core message)
5. **Draft tweet** (follow type pattern)
6. **Optimize** (char count, engagement, emoji)
7. **Verify** (length, clarity, CTA)

---

## Quality Standards

Before marking post done, verify:

**Content:**
- [ ] Single clear message (not multiple ideas)
- [ ] Factually accurate (if making claims)
- [ ] Type-appropriate structure

**Format:**
- [ ] Under 280 characters
- [ ] 2-5 emojis (selective placement)
- [ ] Line breaks for readability
- [ ] Ends with question or CTA

**Engagement:**
- [ ] Hook in first 10 words
- [ ] Clear value or insight
- [ ] Invites response or action

**Niche fit:**
- [ ] Slang appropriate for audience
- [ ] Tone matches topic (hype vs professional)
- [ ] Hashtags relevant (if used)

---

## Type Selection Guide

When unsure which type to use:

| Input | Likely Type |
|---|---|
| Long article or thread to summarize | tldr |
| News event + your opinion | hot-take |
| Product launch or milestone | announcement |
| Want to start discussion | engagement |
| Reacting to someone's tweet | quote-tweet |
| Morning greeting or casual thought | freestyle |

---

## Escalation

Escalate to `tasks/inbox/escalation-*.md` when:

- Tweet exceeds 280 chars and cannot be shortened → Convert to thread
- Type unclear or mixed intent
- Sensitive topic (political, controversial)
- Requires fact-checking beyond available sources

---

## References

- [workflow.md](workflow.md) — Universal workflow for all types
- [types/tldr.md](types/tldr.md) — Summary format
- [types/hot-take.md](types/hot-take.md) — Opinion format
- [types/announcement.md](types/announcement.md) — Launch format
- [types/engagement.md](types/engagement.md) — Question format
- [types/quote-tweet.md](types/quote-tweet.md) — Reaction format
- [types/freestyle.md](types/freestyle.md) — Casual format
- [examples.md](examples.md) — Real tweet examples per type

---

**Maintainer:** Julius  
**Last updated:** 2026-05-19
