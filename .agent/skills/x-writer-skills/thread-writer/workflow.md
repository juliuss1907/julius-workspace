# Workflow — Thread Writer

Advanced workflow for multi-tweet thread generation. Optimizes for flow, engagement, CT voice, and readability.

---

## Phase 1: Input Analysis

### Step 1.1: Read task frontmatter

Extract:
- `thread_type` — Which thread format to use
- `length` — short | medium | long
- `input` — Source material (article, topic, outline)
- `target` — Output file path
- `niche` — Audience context (crypto, solana, defi, etc.)

### Step 1.2: Determine thread length

Based on `length` field:

| Length | Tweet Count | Use When |
|---|---|---|
| short | 5-7 tweets | Simple topic, quick insight |
| medium | 8-12 tweets | Standard depth (default) |
| long | 13-15 tweets | Complex topic, comprehensive |

**If not specified:** Default to medium (8-12 tweets).

### Step 1.3: Identify core narrative

From input, extract:
- **Main message:** The one thing reader should remember
- **Key points:** 3-7 supporting ideas (one per tweet)
- **Desired outcome:** What should reader do after reading?
- **Crypto angle:** How does this connect to crypto?

---

## Phase 2: Type Selection & Planning

### Step 2.1: Load type guide

Based on `thread_type` from frontmatter, load:
- `types/tutorial.md`
- `types/breakdown.md`
- `types/story.md`
- `types/curated.md`
- `types/announcement.md`

### Step 2.2: Review type structure

Each type guide contains:
- Narrative arc pattern
- Hook examples
- Body structure
- Transition phrases
- Closing patterns
- CT voice calibration

Read entire guide before outlining.

### Step 2.3: Create thread outline

Map content to tweets:

**Example outline (10-tweet breakdown):**
```
1/10: Hook — Bold claim + crypto tie-in + 🧵👇
2/10: Context — Why this matters to CT
3/10: Point 1 — First key insight
4/10: Point 2 — Second key insight
5/10: Point 3 — Third key insight
6/10: Transition — "But here's the thing..."
7/10: Point 4 — Fourth key insight
8/10: Point 5 — Fifth key insight
9/10: Implication — What this means for crypto
10/10: CTA — Follow + bookmark + slang close
```

**Rules:**
- One idea per tweet
- Logical progression
- Natural transitions
- Crypto relevance maintained

---

## Phase 3: Hook Tweet (1/N)

### Step 3.1: Write hook

Hook must:
- Grab attention in first 10 words
- Create curiosity gap or bold claim
- Establish crypto relevance
- Include thread indicators (🧵👇)
- Use 1 Tier 1 slang term (optional but recommended)

**Hook patterns by type:**

**Tutorial:**
```
(1/n) Tutorial: [How to do X in crypto]

[Brief description of what they'll learn]

[Why it matters or result they'll get]

Save this thread 🧵👇
```

**Breakdown:**
```
(1/n) [Bold claim about crypto]

[Setup: why CT should care]

Here's what [most people miss / actually happened]:

Thread 🧵👇
```

**Story:**
```
(1/n) This is [person/project in crypto].

[Dramatic outcome or stat]

Here's what happened:

Thread 🧵👇
```

**Curated:**
```
(1/n) [N] [crypto category] [qualifier]

I [spent X hours / curated / tested] to [save you time / find alpha]

Save this thread 🧵👇
```

**Announcement:**
```
(1/n) Announcing [product/feature].

[One-line description]

[Key benefit for crypto users]

Thread 🧵👇
```

### Step 3.2: Add CT voice to hook

**Slang (1 term):**
```
✅ "gm frens, let's talk about X 🧵👇"
✅ "ser, this is important 🧵👇"
✅ "alpha thread on X incoming 🧵👇"
```

**Emoji (2-3 total):**
- 🧵 (mandatory)
- 👇 (mandatory)
- 1 emphasis emoji (🧠, 🚨, 🔥, etc.)

### Step 3.3: Verify hook length

```
Current length: [X] / 280 characters
```

Must be ≤ 280. Optimize if needed.

### Step 3.4: Verify crypto tie-in

Hook must establish crypto relevance:

**Direct:**
```
✅ "How to use Uniswap V4 hooks 🧵👇"
```

**Indirect:**
```
✅ "How to track alpha without burning out 🧵👇"
```

**Metaphorical:**
```
✅ "Building systems like composable protocols 🧵👇"
```

**If no crypto angle clear:**
→ Escalate (wrong audience)

---

## Phase 4: Body Tweets (2 to N-1)

### Step 4.1: Draft each body tweet

For each tweet in outline:

**Structure:**
```
(X/N) [Transition phrase if needed]

[Main point — 1-2 sentences]

[Supporting detail or example]

[Optional: cliffhanger to next tweet]
```

**One idea per tweet:**
- Don't cram multiple points
- If too long, split into 2 tweets
- Adjust numbering accordingly

### Step 4.2: Add transitions

Use transition phrases to connect tweets:

**Common transitions:**
- "Here's why:"
- "But here's the thing:"
- "The result?"
- "Here's what happened next:"
- "This is where it gets interesting:"
- "Let me explain:"
- "Fast forward:"

**Placement:** Start of tweet or after numbering.

### Step 4.3: Create engagement hooks

Every 3-4 tweets, add engagement element:

**Mid-thread hooks:**
- Rhetorical question
- Surprising stat
- Cliffhanger
- "You won't believe what happened next"
- Crypto-specific insight

**Purpose:** Keep reader scrolling.

### Step 4.4: Add CT voice to body (selective)

**Slang (1-2 terms across all body tweets):**
- Spread naturally (not clustered)
- Prefer Tier 1
- Use Tier 2 only if contextual

**Placement examples:**
```
(5/10) This is where most people get rekt.

[Explanation]
```

```
(7/10) The data is actually based.

[Supporting evidence]
```

**Emoji (0-1 per tweet, selective):**
- Use sparingly (not every tweet)
- Emphasis only (🎯, ⚡, 💀)
- Avoid hype emojis unless warranted

### Step 4.5: Verify each tweet length

Each tweet must be ≤ 280 characters.

**If over:**
1. Remove filler words
2. Shorten phrases
3. Split into 2 tweets (adjust numbering)

---

## Phase 5: Closing Tweet (N/N)

### Step 5.1: Choose closing pattern

Based on type:

**Tutorial:** Summary + CTA
```
(N/N) That's it!

You now know how to [do X in crypto].

Follow @handle for more tutorials 🫡

Retweet if helpful 🔄
```

**Breakdown:** Implication + CTA
```
(N/N) So what does this mean for crypto?

[Key takeaway]

Follow @handle for more analysis 🫡

Bookmark this thread 🔖
```

**Story:** Resolution + lesson
```
(N/N) The lesson?

[Key insight for crypto]

Follow @handle for more stories 🫡

Share if valuable 🔄
```

**Curated:** Bonus + CTA
```
(N/N) Bonus:

[Extra resource or tip]

Follow @handle for more curated lists 🫡

Retweet to help others 🔄
```

**Announcement:** CTA + link
```
(N/N) Ready to try it?

[Link or next step]

Follow @handle for updates 🫡

Share with frens 🔄
```

### Step 5.2: Add CT voice to closing

**Slang (1 term):**
```
✅ "wagmi frens 🫡"
✅ "LFG, let's build 🫡"
✅ "Follow for more alpha 🫡"
```

**Emoji (1-2 total):**
- 🫡 (respect/closing — recommended)
- 🔄 (retweet CTA)
- 🔖 (bookmark CTA)

### Step 5.3: Add engagement CTAs

Include 2-3 of:
- **Follow:** "Follow @handle for more"
- **Retweet:** "Retweet if helpful"
- **Bookmark:** "Bookmark for later"
- **Reply:** "Drop your thoughts below"

### Step 5.4: Verify closing length

Must be ≤ 280 characters.

---

## Phase 6: CT Voice Polish

### Step 6.1: Slang distribution check

Count slang across entire thread:

**Target:** 2-3 slang terms total

**Distribution:**
- Hook (1/N): 1 term
- Body (2 to N-1): 1-2 terms (spread across tweets)
- Closing (N/N): 1 term

**Tier balance:**
- Tier 1: 80-90% of slang
- Tier 2: 10-20% of slang
- Tier 3: 0% (avoid in threads)

**Check for:**
- [ ] Not clustered (max 1 slang per tweet)
- [ ] Natural placement (not forced)
- [ ] Tier 1 primarily

**If slang count is off:**
- Too few (< 2): Add Tier 1 in hook or closing
- Too many (> 3): Remove Tier 2, keep Tier 1

### Step 6.2: Emoji distribution check

Count emoji across entire thread:

**Target:** 3-6 emojis total

**Distribution:**
- Hook (1/N): 2-3 emojis (🧵👇 + emphasis)
- Body (2 to N-1): 0-1 emoji per tweet (selective)
- Closing (N/N): 1-2 emojis (CTA)

**CT-appropriate emojis:**
- ✅ 🧵, 👇, 🧠, 🫡, 🤝, 🎯, 🔬, 📝
- ⚠️ 🚀, 🔥 (only if genuinely warranted)
- ❌ 🎉, 🌟, ✨ (too corporate)

**Check for:**
- [ ] 🧵👇 in hook (mandatory)
- [ ] Not in every tweet
- [ ] CT-specific emojis prioritized

**If emoji count is off:**
- Too few (< 3): Add to key body tweets or closing
- Too many (> 6): Remove from body, keep hook + closing

### Step 6.3: Crypto tie-in verification

Verify crypto connection maintained throughout:

**Hook check:**
- [ ] Crypto relevance established in first tweet

**Body check:**
- [ ] Crypto examples or context in 50%+ of tweets
- [ ] Insights framed through crypto lens

**Closing check:**
- [ ] Takeaway relevant to crypto audience

**If crypto tie-in is weak:**
1. Add crypto examples to body tweets
2. Frame insights through crypto lens
3. Strengthen closing with crypto implication

---

## Phase 7: Flow Verification

### Step 7.1: Read full thread

Read all tweets in sequence. Check:
- [ ] Logical progression
- [ ] Smooth transitions
- [ ] No jarring jumps
- [ ] Consistent voice
- [ ] Crypto relevance maintained

### Step 7.2: Engagement check

Verify thread has:
- [ ] Strong hook (tweet 1)
- [ ] Mid-thread hooks (every 3-4 tweets)
- [ ] Clear CTA (final tweet)

### Step 7.3: Length verification

Count tweets:
- **Short:** 5-7 tweets ✓
- **Medium:** 8-12 tweets ✓
- **Long:** 13-15 tweets ✓

If outside range, adjust or escalate.

### Step 7.4: Type consistency

Re-read type guide. Verify:
- [ ] Follows type structure
- [ ] Hook matches type pattern
- [ ] CTA appropriate for type

---

## Phase 8: Formatting

### Step 8.1: Number all tweets

Format: `(X/N)` at start of each tweet.

**Example:**
```
(1/10) Hook tweet...
(2/10) First point...
(3/10) Second point...
...
(10/10) Closing tweet...
```

### Step 8.2: Add thread indicators

- **Tweet 1:** Include 🧵👇
- **Tweets 2-N:** No thread emoji

### Step 8.3: Line breaks

Add line breaks for readability:

**Pattern:**
```
(X/N) [Opening line]

[Main content paragraph]

[Closing line or transition]
```

**Max 3-4 line breaks per tweet.**

---

## Phase 9: Delivery

### Step 9.1: Format output

```markdown
---
type: thread
platform: x
thread_type: <type>
length: <short|medium|long>
tweet_count: <N>
topic: <topic-slug>
status: draft
created: YYYY-MM-DD
---

# Thread: [Title]

## Tweet 1/N
[Content]

## Tweet 2/N
[Content]

...

## Tweet N/N
[Content]
```

### Step 9.2: Save to target path

```bash
cd ~/julius-workspace/working/X/contents/threads
# File: <slug>.md
```

### Step 9.3: Update task file

In task Section 5: Notes:
```markdown
**Output location:** working/X/contents/threads/<slug>.md
**Thread type:** <type>
**Tweet count:** <N>
**Length tier:** <short|medium|long>
**CT voice:** Slang count: <X>, Emoji count: <Y>
**Crypto tie-in:** <direct|indirect|metaphorical>
```

### Step 9.4: Notify Julius

```
[TASK COMPLETE]
Task: Write X thread about <topic>
Type: <thread_type>
Output: working/X/contents/threads/<slug>.md
Tweet count: <N>
CT voice integrated.
Ready for review.
```

---

## Error Handling

### If thread too long

After drafting, if exceeds 15 tweets:
1. Identify least essential tweets
2. Merge or remove
3. If cannot reduce → escalate (suggest article instead)

### If thread too short

After drafting, if under 5 tweets:
1. Expand key points
2. Add examples or details
3. If cannot expand → escalate (suggest single post instead)

### If type unclear

If input doesn't clearly map to one type:
1. Escalate to Julius
2. Suggest 2 possible types with reasoning
3. Wait for clarification

### If no crypto tie-in

If topic has no crypto angle:
1. Escalate to Julius
2. Explain why crypto connection unclear
3. Suggest reframing or different audience

---

**Last updated:** 2026-05-19
