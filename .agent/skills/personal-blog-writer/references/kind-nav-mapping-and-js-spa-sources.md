# Kind mapping & JS-SPA source recovery (observed 2026-09-04)

Two reusable lessons from a "news brief → draft blog posts" session.

## kind ↔ nav mapping (Julius's vocabulary)

Julius names the blog sections by their nav labels, not the `kind` field. Map:

- "Bài viết" / "articles" / "long-form" → `kind: essay`
- "Tin tức" / "news" → `kind: news`
- "Góc nhìn" / "opinion" → `kind: opinion`

So "viết dạng long-form, thuộc category articles" for a brief item means write that
item as `kind: essay`, NOT `kind: news`. Trap: the URL `/articles/<slug>/` is shared
by ALL kinds (see `entryPath` in `src/lib/content.ts`), so an "articles" URL must NOT
be read as the kind. When Julius says "long-form" and points at a brief item that is
analysis rather than a news event, default to `kind: essay` + the topic category
(e.g. macro/rates → `finance`).

## Corporate announcement pages that are JS-rendered SPAs

`openai.com/index/*` announcement pages (e.g. gpt-6-astra) return "This page couldn't
load" with empty title via web_extract — the real content is client-rendered. Do NOT
treat them as dead ends. The official headline figures (benchmark scores) are
recoverable from two cheap sources:

1. `web_search` for the exact announcement title — the search snippet of the official
   page itself often carries the numbers (observed: "98% FrontierMath Tier 4, 99.9%
   ARC-AGI-3, 100% ExploitBench").
2. Analysis outlets that quote the official release: kie.ai, VentureBeat, Wccftech,
   DataCamp. web_extract on those works (server-rendered HTML).

Keep the official `openai.com` URL as the primary `sources:` entry anyway; the
analysis outlet is the actually-read alternate. In the reply report, say the official
page is JS-rendered and was read via search snippet + secondary quoting rather than a
direct extract.

## X/tweet recovery via twitter-cli (cross-ref)

For a CEO's announcement tweet (e.g. Sam Altman's "GPT-6 Astra is here"), the direct
paths fail, but `twitter -c tweet <id>` (or non-compact `twitter tweet <id>` for full
text) reads it without the X API. Full chain already documented in
`x-content-extraction.md` — this session confirmed it end-to-end on the Altman tweet.