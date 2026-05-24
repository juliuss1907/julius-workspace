---
name: thread-writer
description: Write multi-tweet threads (5–15 tweets) for X across 5 types — tutorial, breakdown, story, curated, announcement. CT voice native with hook optimization and numbered formatting.
agent: Hermes (local)
purpose: Write multi-tweet threads for X (Twitter)
version: 2.0
last_updated: 2026-05-19
---

# SKILL — Thread Writer

**Agent:** Hermes (local)  
**Purpose:** Write multi-tweet threads for X (Twitter)  
**Version:** 2.0 (CT Voice Native)  
**Last updated:** 2026-05-19

---

## Role

Write high-quality multi-tweet threads (5-15 tweets) for X platform across 5 distinct thread types. Each type serves a different purpose and follows specific narrative structures.

Thread Writer handles:
- Type-based thread generation (5 distinct formats)
- Multi-tweet flow and transitions
- Hook optimization and engagement
- Numbered tweet formatting (1/N, 2/N, etc.)
- CT voice integration (slang, emoji, tone)

---

## When to Use

Load this skill when:
- Task `domain: x` in frontmatter
- Task `skill: thread-writer` in frontmatter
- Task `thread_type: <type>` specified
- Content requires 5+ tweets to explain

Do NOT use for:
- Single tweets (use `post-writer`)
- X long-form articles (use `article-writer`)
- Other platforms

---

## CT Voice Integration

**This skill follows CT (Crypto Twitter) voice guidelines.**

See master guides:
- [/home/julius/julius-workspace/ai-labs/resource/skills/x-skills/SKILL.md] — Content type selection + CT voice overview
- [/home/julius/julius-workspace/ai-labs/resource/skills/x-skills/slang.md] — CT slang lexicon
- [/home/julius/julius-workspace/ai-labs/resource/skills/x-skills/emoji.md] — CT emoji guide

### CT Tie-In Rule for Threads

**Every CT thread must connect to crypto.**

Threads have flexibility, but crypto connection must be clear:

**Direct (crypto-native topic):**
- Protocol tutorials
- DeFi breakdowns
- Crypto case studies

**Indirect (general topic, crypto lens):**
- "How to research alpha in 5 steps"
- "Productivity for managing 10+ degen plays"
- "Tools for crypto research"

**Metaphorical (crypto concepts explain topic):**
- "Learning like liquidity mining"
- "Building systems like composable protocols"

**Hook tweet (1/N) must establish crypto relevance.**

### Slang Usage in Threads

**Frequency:** 2-3 slang terms per thread (not per tweet)

**Distribution:**
- **Hook tweet (1/N):** 1 slang term (establish CT voice)
- **Body tweets (2 to N-1):** 1-2 slang terms (spread across tweets)
- **Closing tweet (N/N):** 1 slang term (community vibe)

**Tier usage:**
- **Tier 1 (primary):** gm, ser, fren, anon, wagmi, ngmi, degen, based
- **Tier 2 (occasional):** aped in, rugged, jeet, cope, pilled, send it, nuke, LFG
- **Tier 3 (rare):** Only if thread audience clearly knows

**Avoid:**
- Slang in every tweet (too much)
- Clustering slang in one tweet
- Tier 3 without context

See [/home/julius/julius-workspace/ai-labs/resource/skills/x-skills/slang.md] for full lexicon.

### Emoji Usage in Threads

**Frequency:** 3-6 emojis per thread (not every tweet)

**Placement:**
- **Hook tweet (1/N):** 2-3 emojis (🧵👇 mandatory + emphasis)
- **Body tweets (2 to N-1):** 0-1 emoji per tweet (selective)
- **Closing tweet (N/N):** 1-2 emojis (CTA)

**CT-specific emojis for threads:**
- 🧵 (thread indicator — mandatory in hook)
- 👇 (read below — mandatory in hook)
- 🧠 (research/alpha)
- 🫡 (respect/closing)
- 🤝 (collaboration)
- 🎯 (key insight)

**Avoid:**
- Emoji in every tweet
- Multiple emojis per tweet (except hook)
- Corporate emojis (🎉, 🌟, ✨)

See [/home/julius/julius-workspace/ai-labs/resource/skills/x-skills/emoji.md] for full guide.

---

## Thread Types

Julius specifies type in task frontmatter:

```yaml
---
type: task
task_type: thread
domain: x
skill: thread-writer
thread_type: tutorial | breakdown | story | curated | announcement
length: short | medium | long
target: working/X/content/draft/<slug>.md
---
```

> ⚠️ **Path convention:** Output always goes to the path specified in the task's `target` field. The project AGENTS.md defines the canonical directory structure — verify target path against AGENTS.md before writing. The project uses `content/` (singular), not `contents/` (plural). Drafts live under `content/draft/`.

### 5 Available Types

| Type | Purpose | Length | Best For |
|---|---|---|---|
| **tutorial** | Step-by-step guide | 6-12 tweets | How-to, walkthroughs, technical guides |
| **breakdown** | Explain complex topic | 8-15 tweets | Analysis, education, deep dives |
| **story** | Narrative arc | 8-12 tweets | Case studies, drama, personal journeys |
| **curated** | List/compilation | 6-12 tweets | Resources, tools, recommendations |
| **announcement** | Product launch | 5-8 tweets | Features, updates, releases |

→ See [types/](types/) folder for detailed type guides.

---

## Length Tiers

User specifies length in task frontmatter:

| Length | Tweet Count | When to Use |
|---|---|---|
| **short** | 5-7 tweets | Quick insight, simple topic |
| **medium** | 8-12 tweets | Standard depth, most common |
| **long** | 13-15 tweets | Comprehensive, complex topic |

**Default:** medium (8-12 tweets) if not specified.

---

## Universal Thread Mechanics

Regardless of type, all threads must follow:

### Tweet Numbering
- **Format:** `(1/N)` at start of each tweet
- **Hook tweet:** `(1/n)` or `(1/10)` depending on known length
- **Body tweets:** `(2/10)`, `(3/10)`, etc.
- **Final tweet:** `(10/10)` with clear end marker

### Character Limits
- **Per tweet:** 280 characters max
- **Optimal:** 240-270 characters (leaves room for retweets)
- **If exceeds:** Split into 2 tweets, adjust numbering

### Thread Indicators
- **Hook tweet:** Include 🧵 emoji + 👇 emoji (mandatory)
- **Body tweets:** No thread emoji (already in thread)
- **Final tweet:** Optional "End of thread" or CTA

### Reply Structure
- Each tweet replies to previous tweet
- Maintain clear parent-child relationship
- No orphaned tweets

---

## Quality Standards

Before marking thread done, verify:

**CT Voice:**
- [ ] Crypto tie-in clear in hook tweet
- [ ] Slang used naturally (2-3 per thread)
- [ ] Emoji usage appropriate (3-6 per thread)
- [ ] Tone matches CT spectrum (chill/informed)

**Structure:**
- [ ] Hook tweet grabs attention
- [ ] Each tweet = one clear idea
- [ ] Smooth transitions between tweets
- [ ] Closing tweet has CTA or summary

**Format:**
- [ ] All tweets numbered (1/N, 2/N, etc.)
- [ ] Each tweet under 280 characters
- [ ] Thread emoji (🧵👇) in hook only
- [ ] Line breaks for readability

**Engagement:**
- [ ] Hook creates curiosity gap
- [ ] Mid-thread engagement hooks (questions, cliffhangers)
- [ ] Final tweet invites action (follow, retweet, bookmark)

**Type consistency:**
- [ ] Follows type-specific structure
- [ ] Matches type voice and tone
- [ ] Uses type-appropriate transitions

---

## Type Selection Guide

When unsure which type to use:

| Input | Likely Type |
|---|---|
| "How to do X" | tutorial |
| "Explain Y" or "Why Z happened" | breakdown |
| "This person did X, here's what happened" | story |
| "Top N tools/resources" | curated |
| "We're launching X" | announcement |

---

## Escalation

Escalate to `tasks/inbox/escalation-*.md` when:

- Thread type unclear or mixed
- Topic too complex for 15 tweets (suggest article instead)
- Requires fact-checking beyond available sources
- Sensitive topic (political, controversial)
- No crypto tie-in possible (wrong audience)

---

## References

- [workflow.md](workflow.md) — Universal workflow for all types
- [types/tutorial.md](types/tutorial.md) — Step-by-step guide format
- [types/breakdown.md](types/breakdown.md) — Analysis/explanation format
- [types/story.md](types/story.md) — Narrative format
- [types/curated.md](types/curated.md) — List/compilation format
- [types/announcement.md](types/announcement.md) — Product launch format
- [examples.md](examples.md) — Real thread examples per type

---

**Maintainer:** Julius  
**Last updated:** 2026-05-19