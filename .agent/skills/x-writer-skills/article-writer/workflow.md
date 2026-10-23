# Workflow — X Article Writer

Universal workflow for all 4 styles. Style-specific differences handled in style guides.

---

## Phase 1: Setup

### Step 1.1: Read task frontmatter

Extract:
- `style` — Which author voice to emulate
- `topic` — Main subject of article
- `target` — Output file path
- `deadline` — When due

### Step 1.2: Load style guide

Based on `style:` field, load corresponding file:
- `gideon` → `styles/gideon-style.md`
- `stacy` → `styles/stacy-style.md`
- `jeff` → `styles/jeff-style.md`
- `warhol` → `styles/warhol-style.md`

Read entire style guide before proceeding.

### Step 1.3: Determine length

Based on topic complexity:
- **Single insight or pattern:** 800-1200 words
- **Multi-faceted analysis:** 1200-1800 words
- **Comprehensive deep dive:** 1800-2500 words

→ Length follows content depth, not style preference.

---

## Phase 2: Research

### Step 2.1: Gather sources

**Required:**
- 2-3 primary sources (announcements, official docs, original research)
- 1-2 secondary sources (analyses, news coverage)

**Style-specific requirements:**

**Gideon style:**
- Reddit threads (community sentiment)
- Twitter quotes from real users
- Personal anecdotes (if Julius has experience)

**Stacy style:**
- Data tables (TVL, volumes, metrics)
- Regulatory filings, licenses
- Academic papers, institutional reports

**Jeff style:**
- Tool documentation
- Pricing pages
- Performance benchmarks
- Personal testing results (Julius's setup)

**Warhol style:**
- Historical price/ROI data
- Case studies of failures
- Counter-narratives from skeptics

### Step 2.2: Verify facts

For each key claim, note:
- Source URL or reference
- Date accessed
- Confidence level (confirmed / claimed / unverified)

### Step 2.3: Identify angle

Based on style, find the angle:

**Gideon:** What pain point does this solve for overwhelmed retail?
**Stacy:** What contrarian insight do other analysts miss?
**Jeff:** What did I try that worked/failed, and what did I learn?
**Warhol:** What pattern of failure or hidden risk should investors see?

---

## Phase 3: Outline

### Step 3.1: Choose structure (style-specific)

Each style has a default structure (see style guides). Adapt based on topic.

### Step 3.2: Map content to sections

For each section:
- 1-2 sentence summary
- Key points to cover
- Sources to reference

### Step 3.3: Estimate length per section

Distribute total word count across sections proportionally.

---

## Phase 4: Draft

### Step 4.1: Write frontmatter

```yaml
---
type: article
platform: x
style: <style>
topic: <main-topic>
status: draft
created: YYYY-MM-DD
---
```

### Step 4.2: Write title

Style-specific title patterns (see style guides).

Universal rules:
- Under 70 characters
- Declarative or curiosity-gap
- No clickbait
- No emoji

### Step 4.3: Write opening

Style-specific opening patterns:
- **Gideon:** Personal pain point or relatable frustration
- **Stacy:** Contrarian thesis statement
- **Jeff:** Discovery moment or "I've been doing X wrong"
- **Warhol:** Provocative claim or surprising data point

### Step 4.4: Write body

Follow style-specific structure. Maintain voice throughout.

### Step 4.5: Write closing

Style-specific closing patterns:
- **Gideon:** Actionable takeaway + soft CTA
- **Stacy:** Implications + nuanced conclusion
- **Jeff:** Lessons learned + what's next
- **Warhol:** Pattern recognition + how to avoid

---

## Phase 5: Verification

### Step 5.1: Fact-check

Go through line by line:
- [ ] Every number has a source
- [ ] Every claim about projects/people verified
- [ ] No speculation presented as fact

### Step 5.2: Style consistency check

Re-read style guide. Verify:
- [ ] Voice matches throughout
- [ ] Sentence patterns align with style
- [ ] No anti-patterns from style guide

### Step 5.3: Format check

- [ ] Frontmatter complete
- [ ] Headers follow H2/H3 hierarchy
- [ ] No markdown images
- [ ] No emoji in headers
- [ ] Citations included where needed

## Phase 6: CT Voice Polish

### Step 6.1: Slang distribution check

Verify slang usage across article:

**Target:** 5-10 slang terms total

**Distribution:**
- Opening section: 1-2 terms
- Body sections: 3-6 terms (spread evenly)
- Closing section: 1-2 terms

**Tier balance:**
- Tier 1 (universal): 60-70% of slang
- Tier 2 (common): 20-30% of slang
- Tier 3 (niche): 0-10% of slang

**Check for:**
- [ ] Not clustered (max 2 slang terms per paragraph)
- [ ] Natural placement (not forced)
- [ ] Tier 3 slang explained or contextual

**If slang count is off:**
- Too few (< 5): Add Tier 1 slang in opening/closing
- Too many (> 10): Remove Tier 2/3, keep Tier 1

### Step 6.2: Emoji placement check

Verify emoji usage:

**Target:** 5-10 emojis total

**Placement:**
- Headers: 0-1 emoji per header (not every header)
- Body: Rare (emphasis only)
- Closing: 1-2 emojis (CTA)

**CT-appropriate emojis:**
- ✅ 🧠, 🎯, 🔬, 📝, 🫡, 🤝
- ⚠️ 🚀, 🔥 (only if genuinely warranted)
- ❌ 🎉, 🌟, ✨, 👍 (too corporate)

**Check for:**
- [ ] Not in every header
- [ ] Not multiple per paragraph
- [ ] CT-specific emojis prioritized

**If emoji count is off:**
- Too few (< 5): Add to key headers or closing
- Too many (> 10): Remove from body, keep headers + closing

### Step 6.3: CT tie-in verification

Verify crypto connection is clear:

**Opening paragraph check:**
- [ ] Crypto relevance established in first 2-3 sentences
- [ ] Connection type clear (direct/indirect/metaphorical)

**If crypto tie-in is weak:**
1. Rewrite opening to establish relevance
2. Add crypto examples throughout body
3. Frame insights through crypto lens

**Example fixes:**

**Weak opening:**
```
"Productivity is important for everyone. Here are 5 systems I use."
```

**Strong opening:**
```
"Managing 10+ degen plays requires systems. Here are 5 frameworks I use to track alpha without burning out."
```

### Step 6.4: Tone calibration by style

Verify tone matches selected style:

**Gideon (empathetic teacher):**
- [ ] Warm, encouraging language
- [ ] "You" and "we" language
- [ ] Tier 1 slang primarily
- [ ] Minimal emoji (5-7 total)

**Stacy (analytical researcher):**
- [ ] Data-driven, precise language
- [ ] Less slang overall (3-5 total)
- [ ] Minimal emoji (3-5 total)
- [ ] Professional but CT-aware

**Jeff (transparent builder):**
- [ ] Direct, honest language
- [ ] "I" and "we" language
- [ ] Tier 1 + Tier 2 slang (6-8 total)
- [ ] Moderate emoji (6-8 total)

**Warhol (skeptical critic):**
- [ ] Sharp, contrarian language
- [ ] Sarcasm when appropriate
- [ ] Tier 2 + Tier 3 slang (7-10 total)
- [ ] Selective emoji (5-7 total)

**If tone doesn't match style:**
- Review style guide (styles/<style>.md)
- Adjust language, slang, emoji accordingly

---

## Phase 7: Polish

### Step 7.1: Read for flow

Read article aloud (mentally). Mark places where:
- Sentences are too long
- Transitions are abrupt
- Voice slips out of style

### Step 7.2: Tighten

Cut:
- Redundant sentences
- Weak qualifiers ("might be", "could potentially")
- Filler phrases ("it's important to note")

### Step 7.3: Strengthen

Replace:
- Vague claims with specific examples
- Generic terms with precise ones
- Passive voice with active where appropriate

---

## Phase 8: Delivery

### Step 8.1: Save to target path

```bash
cd ~/julius-workspace/working/X/contents/draft
# File: <slug>.md
```

### Step 8.2: Update task file

In Section 5: Notes:
```markdown
**Output location:** working/X/contents/draft/<slug>.md
**Style used:** <style>
**Word count:** [actual count]
**Sources:** [list key sources]
**Length category:** short | medium | long
```

### Step 8.3: Notify Julius

```
[TASK COMPLETE]
Task: Write X article about <topic>
Style: <style>
Output: working/X/contents/draft/<slug>.md
Word count: <X> words
Ready for review.
```

---

## Error Handling

### If style is unclear or mixed

Escalate immediately. Do not attempt to mix styles unilaterally.

### If sources contradict

Note conflict in article, present multiple perspectives. For factual disputes, escalate.

### If length seems wrong

Re-evaluate topic complexity. If genuinely too thin or too dense, escalate to confirm scope adjustment.

---

**Last updated:** 2026-05-18
