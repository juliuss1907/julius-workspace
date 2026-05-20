# Workflow — Post Writer

Advanced workflow for single tweet generation. Optimizes for engagement and character count.

---

## Phase 1: Input Analysis

### Step 1.1: Read task frontmatter

Extract:
- `post_type` — Which tweet format to use
- `input` — Source material (article, news, thought)
- `target` — Output file path
- `niche` — Audience context (crypto, solana, professional, etc.)

### Step 1.2: Identify core message

From input, extract:
- **Primary insight:** The one thing reader should remember
- **Supporting detail:** 1-2 facts or reasons (optional)
- **Desired action:** What should reader do after reading?

### Step 1.3: Determine intent

Map input to post type:

**If summarizing content** → tldr
**If sharing opinion on news** → hot-take
**If announcing something** → announcement
**If asking question** → engagement
**If reacting to tweet** → quote-tweet
**If casual/greeting** → freestyle

---

## Phase 2: Type Selection

### Step 2.1: Load type guide

Based on `post_type` from frontmatter, load:
- `types/tldr.md`
- `types/hot-take.md`
- `types/announcement.md`
- `types/engagement.md`
- `types/quote-tweet.md`
- `types/freestyle.md`

### Step 2.2: Review type patterns

Each type guide contains:
- Structure pattern
- Hook examples
- Emoji placement
- CTA patterns
- Real examples

Read entire guide before drafting.

---

## Phase 3: Drafting

### Step 3.1: Write hook (first 10 words)

Hook must:
- Grab attention immediately
- Set up the core message
- Match type pattern

**Examples by type:**
- **TL;DR:** "Luxx in 3 bullets"
- **Hot Take:** "Hot take: crypto's biggest competitor isn't..."
- **Announcement:** "🚀 BITMART JUST UNLEASHED..."
- **Engagement:** "Everyone was expecting 'bullish' after..."
- **Freestyle:** "gm my jpeg frens 🫡"

### Step 3.2: Develop body

Based on type:

**TL;DR:** Bullet list or numbered points
**Hot Take:** Claim → Reason → Implication
**Announcement:** What happened → Why it matters → Hype
**Engagement:** Setup → Data/Context → Question
**Quote Tweet:** Original context → Your take → Why it matters
**Freestyle:** Greeting → Thought → Vibe

### Step 3.3: Add CTA or question

End with one of:
- **Question:** "What do you guys think?"
- **CTA:** "Turn on notifications"
- **Cliffhanger:** "I'll share them soon"
- **Invitation:** "Let's talk about..."

---

## Phase 4: Optimization

### Step 4.1: Character count check

```
Current length: [X] / 280 characters
```

**If over 280:**
1. Remove filler words ("really", "very", "actually")
2. Shorten phrases ("in order to" → "to")
3. Use abbreviations where natural ("and" → "&")
4. Remove redundant adjectives

**If still over 280:**
→ Escalate to thread-writer (cannot fit in single tweet)

### Step 4.2: Emoji placement

Add 2-5 emojis strategically.

**CT-specific emojis (prioritize these):**
- **Hook emphasis:** 🚨, 👀, 🔥, ⚡
- **Research/alpha:** 🧠, 📝, 🔬
- **Community:** 🫡, 🤝, 💎
- **Engagement:** 🔄, 🔖, 👇
- **Negative:** 💀 (ngmi/rekt)

**Universal emojis (CT-compatible):**
- Positive: 🚀, 💎, ✨, 🌊
- Attention: 👀, 🚨, ⚡
- Question: 🤔, 💭

**Avoid (too corporate):**
- ❌ 🎉, 🌟, ✨, 👍, 😊, 🙏, 💯

**Placement rules:**
- Start of tweet (attention): 🚨, 🧠, 🔥
- Before key point (emphasis): 🎯, ⚡
- End of tweet (CTA): 🔄, 🔖, 🫡

**Frequency:**
- Serious topics: 1-2 emojis
- Standard posts: 2-4 emojis
- Hype topics: 4-5 emojis

See [/home/julius/julius-workspace/ai-labs/resource/skills/x-skills/emoji.md] for complete guide.

### Step 4.3: Line breaks

Add line breaks for readability:

**Pattern A: Hook + Body + CTA**
```
[Hook line]

[Body paragraph]

[CTA line]
```

**Pattern B: List format**
```
[Hook line]

- [Point 1]
- [Point 2]
- [Point 3]

[CTA line]
```

**Max 3-4 line breaks** (avoid wall of text, avoid too fragmented)

### Step 4.4: Slang integration

Based on `niche` from task and post type.

**CT slang tiers:**

**Tier 1 (use freely):**
- gm, gn, ser, fren, anon
- wagmi, ngmi, degen, based

**Tier 2 (with context):**
- aped in, rugged, jeet, cope
- pilled, send it, nuke, LFG, rekt, alpha

**Tier 3 (sparingly):**
- midcurve, gigabrain, skill issue
- mog, grok, schizo, maxi, bag, shill, hopium

**Frequency rules:**
- **Standard post:** 1-2 slang terms (Tier 1 primarily)
- **Serious topic:** 0-1 slang term (Tier 1 only)
- **Hype topic:** 2-3 slang terms (Tier 1 + Tier 2)

**Placement strategy:**

**Opening (establish CT voice):**
```
✅ "gm frens, let's talk about X"
✅ "ser, this is important"
❌ "Good morning everyone" (too formal)
```

**Mid-content (emphasis):**
```
✅ "this is actually based"
✅ "if you don't get this, ngmi"
❌ "this is good" (too bland)
```

**Closing (community vibe):**
```
✅ "wagmi frens 🫡"
✅ "LFG"
❌ "Thank you for reading" (too formal)
```

**Natural combinations:**
- gm + frens: "gm frens 🫡"
- ser + based: "ser, this is based"
- wagmi + LFG: "wagmi, LFG!"
- degen + aped in: "full degen, aped in"

**Avoid awkward combos:**
- ❌ ser + fuck (tone clash)
- ❌ wagmi + ngmi (contradictory)
- ❌ gm + rekt (mood clash)

**Rule:** Slang should feel natural, not forced. If it doesn't fit, skip it.

See [/home/julius/julius-workspace/ai-labs/resource/skills/x-skills/slang.md] for complete lexicon.

### Step 4.5: Hashtag decision

**Use hashtags when:**
- Announcement (product launch, event)
- Engagement (want broader reach)
- Niche-specific (crypto project, trend)

**Hashtag rules:**
- Max 2-3 per tweet
- Place at end
- Use established tags (#DeFi, #Solana, #Bitcoin)

**Skip hashtags when:**
- Freestyle/casual
- Quote tweet (context already clear)
- Professional tone

### Step 4.5: CT tie-in verification

**Rule:** Every CT post must connect to crypto.

**Verify connection type:**

**Direct (topic is crypto-native):**
```
✅ "How to use Uniswap V4"
✅ "Solana fees vs Ethereum"
✅ "Why most airdrops fail"
```

**Indirect (general topic, crypto lens):**
```
❌ "How to use Obsidian for productivity"
✅ "How to use Obsidian to track alpha"

❌ "Best note-taking apps"
✅ "Best tools for degen research"
```

**Metaphorical (crypto concepts explain topic):**
```
✅ "Building a brand = liquidity mining"
✅ "Learning AI = farming airdrops early"
✅ "Networking = protocol composability"
```

**If no crypto angle:**
1. Ask: "Why does CT care about this?"
2. If no good answer → wrong audience
3. If there's a reason → make it explicit in opening

**Example fix:**
```
Original: "5 productivity tips"
CT version: "5 productivity tips for managing 10+ degen plays"
```

See [/home/julius/julius-workspace/ai-labs/resource/skills/x-skills/SKILL.md] for CT tie-in rule details.
---

## Phase 5: Verification

### Step 5.1: Read aloud test

Read tweet aloud (mentally). Check:
- [ ] Flows naturally
- [ ] No awkward phrasing
- [ ] Emoji placement makes sense

### Step 5.2: Engagement check

Verify tweet ends with:
- [ ] Question OR
- [ ] Call-to-action OR
- [ ] Cliffhanger/teaser

### Step 5.3: Final character count

```
Final length: [X] / 280 characters
```

Must be ≤ 280.

### Step 5.4: Type consistency

Re-read type guide. Verify:
- [ ] Follows type structure
- [ ] Hook matches type pattern
- [ ] CTA appropriate for type

---

## Phase 6: Delivery

### Step 6.1: Format output

```markdown
---
type: post
platform: x
post_type: <type>
topic: <topic-slug>
status: draft
created: YYYY-MM-DD
char_count: <X>
---

[Tweet content here]
```

### Step 6.2: Save to target path

```bash
cd ~/julius-workspace/working/X/contents/posts
# File: <slug>.md
```

### Step 6.3: Update task file

In task Section 5: Notes:
```markdown
**Output location:** working/X/contents/posts/<slug>.md
**Post type:** <type>
**Character count:** <X> / 280
**Emoji count:** <N>
**Hashtags:** <list or "none">
```

### Step 6.4: Notify Julius

```
[TASK COMPLETE]
Task: Write X post about <topic>
Type: <post_type>
Output: working/X/contents/posts/<slug>.md
Char count: <X> / 280
Ready for review.
```

---

## Error Handling

### If cannot fit in 280 characters

After optimization, if still over:
1. Note in task: "Content too long for single tweet"
2. Escalate to thread-writer
3. Suggest: "Convert to 2-3 tweet thread?"

### If type unclear

If input doesn't clearly map to one type:
1. Escalate to Julius
2. Suggest 2 possible types with reasoning
3. Wait for clarification

### If sensitive topic

Political, controversial, or high-risk:
1. Flag in task notes
2. Draft conservatively (neutral tone)
3. Escalate for Julius review before posting

---

**Last updated:** 2026-05-19
