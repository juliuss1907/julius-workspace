# AGENTS.md — Substack

> Inherits from: workspace/AGENTS.md
> Domain: Long-form newsletter publishing on Substack.

---

## 1. CONTEXT

Julius publishes on Substack in **English**, **on-demand cadence** (no fixed schedule). Topics span 3 main areas:

| Topic | Examples |
|---|---|
| **Crypto** | Industry takes, retrospectives, framework explainers |
| **Tech** | Software/system observations, builder-focused essays |
| **AI** | AI systems, agents, prompt engineering, personal AI workflows |

**Format**: Free-style. No fixed structure (unlike Coin68 review template). Each essay finds its own form.

---

## 2. INPUT/OUTPUT

| Input | Output location |
|---|---|
| Topic prompt or rough notes from Julius | `working/Substack/content/draft/<essay-slug>.md` |
| Reference materials (links, quotes) | Read from raw input or KB (read-only) |
| Cover image | `working/Substack/images/<essay-slug>-cover.png` (or .jpg) |

---

## 3. STYLE & FORMAT

### Voice
- **Long-form essayist**: think long, edit ruthlessly. Quality over volume.
- **Builder + observer**: Julius writes from experience (what he's building, learning, noticing) — not from authority position
- **Conversational but precise**: contractions OK, but each claim should hold up to scrutiny
- **Specific over general**: name names, link sources, give concrete examples

### Length
- No hard floor or ceiling
- Short essays (800-1500 words) are valid if the idea is tight
- Long essays (3000-5000+ words) are valid if the depth justifies it
- **Length should match the idea, not the other way around**

### Format defaults
- **Title**: declarative or curiosity-gap, NOT clickbait
- **Subtitle**: 1-line value promise
- **Section headers** (H2): only if essay > 1500 words; shorter pieces flow as continuous prose
- **Pull quotes**: use sparingly for impact
- **Footer**: optional CTA (subscribe, reply, share)

---

## 4. WORKFLOW

When Hermes receives a Substack task:

1. **Read the prompt or notes** Julius provides
2. **Determine essay shape**:
   - Argument essay (thesis → support → counter → conclusion)?
   - Narrative essay (story-driven, anecdotes leading to insight)?
   - Listicle/framework (numbered points expanding a model)?
   - Reaction piece (commenting on external trigger)?
3. **Load `substack-writer` skill** if needed for structure guidance
4. **For research-heavy essays**: load `researcher` skill first to gather + verify sources
5. **Draft to `working/Substack/content/draft/<essay-slug>.md`**
6. **Self-edit pass** before notifying Julius:
   - Cut redundant sentences
   - Replace vague claims with specifics
   - Verify every name/number/quote
7. **Notify Julius** with title proposal + 2-3 sentence summary

---

## 5. SKILL DEFAULTS

| Essay type | Skill chain |
|---|---|
| Standard essay | `ai-labs/resource/skills/substack-writer/SKILL.md` |
| Research-heavy | `researcher` → `substack-writer` |
| Crypto/AI/Tech analysis with data | `researcher` → `substack-writer` (verify data) |

---

## 6. BOUNDARIES (overrides parent)

- **Language**: English (overrides parent default)
- **No template forcing**: Don't apply Coin68's strict review template here. Let form follow content.
- **No SEO optimization required** (Substack readership is subscription-based, not search-driven). Skip `seo-optimizer` unless Julius explicitly requests.
- **Personal voice**: Use first person ("I"), share Julius's experience. Don't ghostwrite as if speaking from generic authority.
- **External quotes**: When citing others, use blockquote format and link to source. Never paraphrase as if it's Julius's idea.

---

## 7. EXAMPLES

### Good

**Argument essay:**
> Topic: "Why I'm bearish on AI agent frameworks"
> Action:
> 1. Shape = argument essay
> 2. Outline: thesis (frameworks add abstraction tax) → 3 supporting examples from Julius's own experiments → counter (when frameworks DO help) → conclusion (when to use vs. avoid)
> 3. Draft, self-edit, notify Julius with title + summary

**Reaction piece:**
> Topic: "Reacting to OpenAI's new Agents API"
> Action:
> 1. Shape = reaction piece
> 2. Read OpenAI's announcement
> 3. Frame the take: how does this fit into Julius's mental model of agent stacks?
> 4. Short essay (1000-1500 words) — quick turnaround for timeliness

### Bad

**Anti-example A — Forced template**
> Topic: "Thoughts on context windows"
> Bad: Hermes applies Coin68's strict 9-section template
> Why bad: Substack is free-form. Forcing a template kills the essayist voice.

**Anti-example B — Generic AI authority voice**
> Opening: "In today's rapidly evolving AI landscape, context windows have become a critical consideration..."
> Why bad: Generic LLM filler. Substack voice is personal: "I keep running into the same wall with context windows..."

**Anti-example C — Padding for length**
> 3000-word essay where the core idea fits in 1200 words
> Why bad: Length should match idea. Cut, don't pad.

**Anti-example D — Hidden quotes**
> Hermes paraphrases Vitalik's argument without attribution
> Why bad: Always cite. Use blockquote + link.

---

## 8. ESCALATE WHEN

- Topic crosses sensitive territory (politics, public figures, controversies) — confirm angle
- Source material is paywalled and Hermes can't access full context
- Essay length plan exceeds 5000 words — confirm scope
- Topic significantly overlaps with a recent Coin68 article — clarify if repurposing or fresh take
- Julius's notes are too sparse to determine essay shape (escalate with shape options)
