# Brief → blog: destination disambiguation & numbered-item mapping

Two traps that cost a round-trip when turning a news brief into blog posts for Julius.

## Destination disambiguation

Julius's phrasing maps to three flatly-different targets. Do not conflate them:

- **"viết ... vào folder blog" + "văn phong Coin68"** → write the Coin68-voice news post
  DIRECTLY to `working/Blog/Content/<kebab-slug>.md`. Format: `## title` (H2) + one
  `Meta:` line + body ending in "So what:". No YAML frontmatter, no kiểm chứng block,
  no sheet update. This is the news-blog flow, NOT the Coin68 calendar pipeline.
- **"cho blog" / "bài blog" (no Coin68 phrasing)** → Astro `src/content/writing/`
  with full frontmatter (`kind`/`category`/`readingMinutes`/`sources`), Julius's
  personal-blog voice.
- Do NOT route "văn phong Coin68" requests to `working/Coin68/contents/drafts/` — that
  folder belongs to the calendar-sheet review pipeline (kiểm chứng block +
  `sheet_client.py` update), a different workflow entirely.

The `working/Blog/Content/` convention is documented in coin68-writer's
"AI model launch news → Blog/Content" pitfall; this session confirmed the SAME
pattern applies to general news briefs (crypto short-squeeze, regulation, enterprise
AI market-share, executive changes) — not just AI model launches.

## Numbered brief → blog mapping

When Julius says "viết news số 1, 2, 3 và 7" (numbering items from a news brief), the
numbers map to the brief's SEQUENTIAL order across ALL sections. In current brief formats,
every item across Top Stories, Crypto, and Tech carries an explicit `### N. Tiêu đề` heading
(from 1 up to 12-15), so the mapping is direct and 1-to-1.

If an older or alternate brief only numbers Top Stories explicitly, the sequential order
still continues through subsequent sections. Always confirm the mapped headline in your
written post list before writing.

## Converting a brief item to a Coin68-voice news post

- brief headline → `## title` (H2), no ticker unless it's a token-specific story.
- brief bullets → flowing Vietnamese prose, keep bold on key numbers, English tech
  terms (short squeeze, 200-day MA, DCM, scaling) stay in English.
- brief "Tai sao dang chu y" → the "So what:" closing paragraph (rewrite, don't
  restate as a summary).
- brief "Nguon" → drop the explicit source line for the Blog/Content format (no
  `sources:` field there); keep facts attributable in the prose where relevant.