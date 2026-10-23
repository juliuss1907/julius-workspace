# Two build/validation failures from a 2-article batch (2026-09-28)

## 1. Missing `publishedAt` — misleading error, aborts the whole batch

Both posts in a two-article batch were written without `publishedAt`. `npm run
build` failed on the FIRST file before ever reaching the second:

```
[InvalidContentEntryDataError] writing → amodei-trump-dinner data does not match collection schema.
  publishedAt**: Expected type "date", received "object"
  Location: .../src/content/writing/amodei-trump-dinner.md:0:0
```

The trap: a missing field is reported as `received "object"` (the schema reads
absence as an object) and points at file position `0:0`, NOT at the field. It
looks like a YAML type problem in the title block, not a missing key.

**Rule:** write `publishedAt: YYYY-MM-DD` in the first draft of every file. The
schema block in SKILL.md shows it, but when authoring a fresh batch it is easy
to omit because the surrounding prose is the focus.

**Batch implication:** `astro check` aborts on the first invalid entry, so a
single missing field masks every other problem. Fix frontmatter across the whole
batch before re-running, rather than one file per build attempt.

## 2. `re.MULTILINE` missing in a hand-written line-anchored parser

Writing a Markdown parser for a Jina-reader page (`parse_aiweekly_markdown` in
`news-brief-skill/scrape_web_sources.py`), the group-header regex looked
correct and matched in isolation, but never matched inside the document:

```python
AIWEEKLY_GROUP = re.compile(
    r'^(?P<domain>\S+)\s+(?P<age>\d+)(?P<unit>[hdm])\s+ago(?:\s+\S+)?\s+\d+\s*$'
)
```

`^`/`$` anchor to the whole string without `re.MULTILINE`, so mid-document lines
never matched and the parser returned zero items. Passing `re.MULTILINE` fixed
it. Regression test caught it immediately.

**Rule:** any `^`/`$` pattern applied to a multi-line document needs
`re.MULTILINE`. Test the regex against a realistic multi-line fixture, not a
single line — a single-line test passes while the real parse returns nothing.

## 3. Relative-age parsing direction

Same parser, second bug found by the test after the first was fixed: to find
the "freshest" group on the page from `"3h ago"` / `"2d ago"` markers, use
`max(published_at)`, not `min`. The lead block above the first group header
borrows the freshest age on the page.

Together these two bugs produced a parser that looked right, passed a naive
single-line probe, and returned `[]` on real input. A live-fetch smoke test
against the actual page is what made the failure visible.
