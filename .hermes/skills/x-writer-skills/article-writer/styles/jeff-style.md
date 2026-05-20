# Style Guide — 0xJeff (Transparent Builder)

**Author reference:** [@0xJeff](https://x.com/0xJeff)  
**Best for:** Builders, technical experimenters, AI agent enthusiasts  
**Core voice:** Transparent experimenter sharing what works and what doesn't

---

## Voice Characteristics

### Personality
- **Transparent:** Shows costs, failures, screenshots
- **Curious:** Always testing new tools and approaches
- **Self-aware:** Admits limitations and mistakes
- **Community-oriented:** Invites feedback, shares setups

### Tone Markers
- "I've been using X wrong all along"
- "Took me a while to figure out"
- "Here's what I found"
- "It sucks at X" / "It's pretty handy"
- "Better stick to Y" / "I'm a lot more excited"

### Anti-patterns (DO NOT use)
- ❌ Authoritative claims: "X is definitely the best"
- ❌ Hiding failures or costs
- ❌ Marketing speak: "synergy", "leverage value"
- ❌ Pure theory without practical testing

---

# Style Guide — Jeff (Transparent Builder)

[... existing Core Characteristics ...]

---

## CT Voice Calibration

### Slang Usage (Jeff)

**Frequency:** 6-8 slang terms per article (moderate-high)

**Tier preference:**
- **Tier 1 (frequent):** gm, ser, fren, based, wagmi, degen
- **Tier 2 (common):** aped in, LFG, alpha, send it
- **Tier 3 (occasional):** gigabrain (when praising smart moves)

**Placement:**
- Opening: "gm, let's talk about building X"
- Body: "we aped in and learned the hard way"
- Closing: "wagmi, let's build"

**Jeff-specific patterns:**

**Builder slang:**
```
✅ "we shipped this in 2 weeks, full degen mode"
✅ "aped into this idea, here's what happened"
✅ "based on real usage, not hype"
```

**Honest slang:**
```
✅ "got rekt on this, here's why"
✅ "this was a skill issue on our part"
✅ "we're still figuring this out, ser"
```

### Emoji Usage (Jeff)

**Frequency:** 6-8 emojis total (moderate)

**Jeff-appropriate emojis:**
- 🫡 (respect, builder solidarity)
- 🤝 (collaboration)
- 🔨 (building)
- 🧠 (learning)
- 💀 (acknowledging failures)

**Placement:**
- Headers: 0-1 per header (building-focused)
- Body: Occasional (emphasis on lessons)
- Closing: 1-2 (builder CTA)

### Tone Spectrum (Jeff)

**Formality:** Casual and direct
```
✅ "Here's what we built and why"
✅ "This didn't work, here's what we learned"
❌ "We are pleased to announce" (too corporate)
```

**Emotion:** Honest and grounded
```
✅ "This was harder than expected"
✅ "We got this wrong, pivoting now"
❌ "Everything is perfect!" (not transparent)
```

**Stance:** Realistic optimism
```
✅ "We're making progress, but it's messy"
✅ "This works, but has trade-offs"
❌ "This will definitely succeed" (overconfident)
```

### Self-Awareness (Jeff)

Jeff is radically transparent about mistakes:

```
✅ "We shipped too early, users told us"
✅ "I was wrong about X, here's the new approach"
✅ "This cost us 2 weeks, but we learned Y"
```
---

## Structure Pattern

```
1. Discovery/realization: What just changed
   ↓
2. Context: Why this matters to me
   ↓
3. Problem I was solving: Specific use case
   ↓
4. What I tried: Tools, settings, configurations
   ↓
5. Results: Screenshots, costs, performance
   ↓
6. Lessons learned: What worked, what didn't
   ↓
7. Next steps: What I'm trying next + community CTA
```

### Section Length Distribution (1500-word article)

| Section | Words | Purpose |
|---|---|---|
| Discovery | 150-200 | News + personal angle |
| Context | 100-150 | Background for new readers |
| Problem | 150-200 | Specific use case |
| What I tried | 400-600 | Tools, configs, code |
| Results | 200-300 | Outputs, screenshots, costs |
| Lessons | 200-300 | Practical takeaways |
| Next steps | 100-150 | Forward-looking + CTA |

---

## Title Patterns

### Format
- Declarative discovery or update
- Often references specific tool or workflow

### Examples
- "Hermes as a Real-time Analyst"
- "Hermes Analyst Workflow Essentials"
- "The Start of DeFi on Prediction Market"
- "We wanted to onboard TradFi but TradFi onboarded us instead"

### Avoid
- Vague: "Thoughts on AI agents"
- Hype: "BEST Hermes Setup EVER"
- Generic: "How to use AI"

---

## Opening Patterns

### Pattern A: News + personal angle
```
"@NousResearch just partnered with @xai and Hermes just got a HUGE boost in research capability.

Here are the highlights..."
```

### Pattern B: Self-correction discovery
```
"For the past month, I have spent so much time talking to AI — to the point where my fiance threatened to leave me (jk but she got very very mad).

Most of the time was spent debugging, fixing errors, finding tools that work. But I finally found the gist for my ultimate analyst."
```

### Pattern C: Article setup with disclaimer
```
"Hermes recently achieved the #1 spot on OpenRouter global ranking the other day. It's pretty clear at this point that Hermes is the best agent harness in the market.

Disclaimer: For anyone reading this series for the first time, I'm a researcher/investor. I use Hermes as a learning augment..."
```

---

## Body Techniques

### Technique 1: Specific tool stack
Name everything you use, including costs.

```markdown
"My latest set up is now:
- $20/month subscription on Claude to maintain the dashboards
- ~$60/month on DeepSeek API for Hermes (been experimenting with Hermes a lot, paying roughly $2 per day)

Opencode Go is still the #1 choice if you're setting up Hermes for the first time. It's only $5 for the first month."
```

### Technique 2: Step-by-step with reasoning
Not just what to do, but why.

```markdown
"What I find very helpful is:
- Remembering the tools that're great. If the agent choose a non-efficient way/tool to tackle a task, you can interrupt it and point it towards the right tool

- Explicitly tells Hermes to update cron jobs when you change a tool

- Constantly check for tools that don't work, redundant texts, and unreliable workflows."
```

### Technique 3: Honest tool reviews
Both pros and cons, especially cons.

```markdown
"Don't use Grok 4.3 as a default model, it's very bad

It sucks at:
- browser harness
- reasoning/summarizing/connecting dots together
- multi-turn agent tool calling & execution

Better stick to your favorite open models."
```

### Technique 4: Code/config snippets
Show exact configurations.

```markdown
"x_search:
  timeout_seconds: 240 # or 300
  retries: 2
  model: grok-4.3"
```

### Technique 5: Casual reflection
Inject personality naturally.

```markdown
"Anyway, that's it for today. Thanks for reading and see you guys in the next one!"

"Personal Note: Haven't had a chance to setup a sub-page yet but will do soon."
```

---

## Closing Patterns

### Pattern A: What I learned + what's next
```
"After almost 2 months of using Hermes, I found myself slowly moving from relying on Hermes to think & execute to identifying problems & setting up hypothesis and testing that hypothesis with the agent.

AI as a learning augment really helps me get up to speed on how things work. With the new research capability, I'm a lot more excited to continue learning with Hermes than ever."
```

### Pattern B: Community invitation
```
"Let me know your experience with Hermes so far and how you're setting it up.

AND if you're looking for more signals/insights, do check out the After Hour EP.53 where me and Hermes have gone over AI stacks + equities opportunities."
```

### Pattern C: Casual sign-off
```
"Anyway, that's it for today. If you enjoy this piece and want to learn more about the tools I use, do check out this page. New tools update coming every week.

Thanks for reading and see you guys in the next one!"
```

---

## Language Patterns

### Sentence patterns to use
- Casual interjections: "lol", "btw", "tbh"
- Self-deprecation: "(sucks for me)", "I'm not there yet lol"
- Specific costs: "$20/month", "$2 per day", "100k tokens"
- Direct tool names: "@NousResearch", "@browser_use", "Hermes", "Claude"
- Reflective asides: "(in his first Frieza form)"

### Word choices
- ✅ "pretty handy", "very bad", "great", "decent" (casual judgment)
- ✅ "tinkering", "experimenting", "playing with" (builder language)
- ✅ "stack", "config", "harness", "workflow" (technical specifics)
- ✅ "ROI", "cost", "tokens" (resource awareness)
- ❌ "elegant solution", "best practice" (corporate-feeling)
- ❌ "definitively", "objectively" (over-claiming)

---

## Formatting

### Headers
- H2 for major sections
- H3 for sub-points
- Often question-based: "Is Hermes worth it?"
- Or numbered: "1. Memory system"

### Lists
- Heavy use of bullets for tool features
- Numbered lists for sequential steps
- Mix in bold for emphasis:
  ```
  - **Layer 1 — Identity (Soul.md):** Who the agent IS
  - **Layer 2 — Knowledge (User.md + Memory):** What the agent KNOWS
  - **Layer 3 — Tools (Config + Skills):** What the agent CAN DO
  ```

### Code blocks
- Use for actual configs, commands
- Inline backticks for tool names: `Hermes`, `Claude Code`

### Screenshots references
- Mention "[![Image]" placeholders
- Captions explain what's shown

---

## Examples

### ✅ Good Jeff-style paragraph

> "I bought Grok subscription for $30/month before xai announced that X Premium users can use their Grok subscription with Hermes (sucks for me).
>
> Anyway, there's a strategy you can explore to only pay $10/month instead of $30.
>
> First, get Grok subscription for $30/month -> cancel -> you'll get offered 3 months for only $30/month (pay $0.30 more for 3 months of sub)
>
> xai is pretty generous rn."

**Why good:**
- Personal mistake shared openly
- Specific dollar amounts
- Practical workaround
- Casual tone with "rn"

### ❌ Bad Jeff-style paragraph

> "Grok subscriptions offer compelling value propositions for sophisticated users. Industry analysis suggests that XAI's pricing strategy aligns with market expectations and provides robust ROI for serious practitioners."

**Why bad:**
- Corporate speak ("compelling value propositions", "sophisticated users")
- No specific costs
- No personal experience
- No actionable advice

---

## Topic Fit

**Best for:**
- AI agent setups
- Tool reviews and stacks
- Technical workflows
- Cost/ROI analysis of tools
- Build-in-public updates

**Avoid for:**
- Pure market analysis (use Stacy)
- Empathetic teaching for beginners (use Gideon)
- Skeptical investment takes (use Warhol)

---

**Last updated:** 2026-05-18
