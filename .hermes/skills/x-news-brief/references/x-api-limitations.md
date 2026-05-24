# X API Limitations & Workarounds

**Last updated:** 2026-05-19

---

## Why We Don't Use X API Directly

The X (Twitter) API is split into access tiers. Our current setup is on the **Free Tier**, which imposes hard limits that make automated content workflows impossible without upgrades.

### Tier Comparison

| Feature | Free Tier | Basic ($100/mo) | Pro ($5,000/mo) |
|---|---|---|---|
| Read posts/timeline | ~100 req/month | 10,000 req/month | 1,000,000 req/month |
| Post / Reply / DM | **0 credits** | 3,000 posts/month | 300,000 posts/month |
| Media upload | Limited | ✓ | ✓ |
| Search (v2) | Limited | ✓ | ✓ |
| Stream/filtered | ✗ | ✗ | ✓ |

**Our status:** Read works (whoami, timeline). All POST operations return `403 — CreditsDepleted` — not a transient error, but a tier limitation. The Free Tier simply does not include write access.

---

## Error #1: xurl POST → `CreditsDepleted`

```
$ xurl post "test tweet"
Error: 403 — "You currently have access to a subset of X API V2 endpoints
and limited v1.1 endpoints (e.g. media post) only."
```

**Root cause:** Free Tier. Not rate-limited — zero credits allocated for POST from day one.

**Workaround:** Write content locally (drafts), post manually. No code change can fix this without upgrading.

**Upgrade path:** X API Basic Tier ($100/month) unlocks 3,000 posts/month via OAuth 1.0a User Context.

---

## Error #2: Browser Scraping x.com → Empty Pages

Attempting to scrape `x.com` via Playwright/headless browser produces empty or partial results:

**Why it fails:**
- **JavaScript rendering** — X.com is a React SPA; almost no content in static HTML
- **Cloudflare anti-bot** — Fingerprinting detects headless browsers (missing WebGL, canvas noise, etc.)
- **Rate limit shadow-ban** — Rapid requests from same IP return empty pages without error codes
- **Login walls** — Many pages require authentication even for viewing

**Mitigations tried (all unreliable):**
- Stealth plugins (Playwright-stealth) — works briefly, then detected
- Real browser profile cookies — expire quickly
- Slower request pacing — still zero content after JS render fails

**Verdict:** Not viable for automated monitoring. Cost of maintaining evasion outweighs value.

---

## Error #3: xAI/Grok `x_search` → 403

```
403 — Resource has been exhausted or No active subscription
```

**Root cause:** xAI API requires a paid subscription for `x_search` access. The tool is available in Hermes but blocked by the account tier.

**Note:** This is separate from X API — xAI is a different service with its own billing, even though both are under the X Corp umbrella.

---

## Our Solution: thefeed.today

Rather than fight API limitations, we use [thefeed.today](https://thefeed.today) as a proxy:

| Concern | thefeed.today | X API |
|---|---|---|
| Auth required | ✗ | ✓ (OAuth) |
| Rate limits | ✗ | ✓ (strict tiers) |
| Browser scraping needed | ✓ (once per run) | ✗ (API calls) |
| Pre-summarized content | ✓ | ✗ (raw tweets) |
| Category filters | ✓ (Crypto, Tech, AI) | ✗ |
| Engagement metrics | ✓ (views, likes, rate) | Requires separate calls |
| Breaking news tags | ✓ | ✗ |

**Trade-off:** Requires browser automation (Playwright) to load the page and extract content. Adds ~30-60 seconds per run but completely bypasses API limitations.

**Fallback plan:** If thefeed.today changes its structure or goes down, we have two options:
1. Upgrade X API to Basic ($100/mo) for direct v2 search access
2. Switch to Nitter instances or RSS-to-X bridges (less reliable)

---

## When to Revisit

Re-evaluate direct X API usage when:
- X API Basic Tier becomes affordable/justified by content volume
- X introduces a new free tier with write access
- thefeed.today shuts down or changes beyond easy extraction
- We need real-time data (sub-30-minute latency)
