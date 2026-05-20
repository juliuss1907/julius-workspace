# thefeed.today — Read-Only X News Dashboard

**URL:** https://thefeed.today/

## What it is

A live dashboard that aggregates trending posts from X in real-time, organized by category. No API key, no auth, no rate limits — just open the page and extract.

## Why use it instead of X API

| Capability | X API Free Tier | thefeed.today |
|---|---|---|
| Auth required | Yes (OAuth 2.0 PKCE) | No |
| Rate limit | Severe (credits deplete fast) | None (browser-based) |
| POST tweets | No (free tier has no post credits) | N/A (read-only) |
| Category filter | Manual search | Built-in: Crypto, Tech, Breaking, Elon, Memes, Trump, Coin it |
| Pre-summarized | No (raw tweet JSON) | Yes (1-line summary per item) |
| Engagement metrics | Requires extra API calls | Views, likes, engagement rate included |
| Link to original | Available via API | "View ↗" button links to x.com |
| Cost | Free (limited) → $100/mo Basic | Free |

## Category Filters

| Filter | What it covers |
|---|---|
| **All** | Everything (unfiltered) |
| **Breaking** | High-signal news tagged as urgent |
| **Crypto** | DeFi, tokens, blockchain, exchanges, protocols, regulation |
| **Tech** | AI, startups, products, developer tools, launches |
| **Elon** | Elon Musk related |
| **Memes** | Humor, viral content |
| **Trump** | Political |
| **Coin it** | Memecoins, trading talk |

## Extraction Pattern

### Browser navigation
```
1. browser_navigate → https://thefeed.today/
2. Click filter button (e.g., "Crypto")
3. Scroll 3x to load ~20-50 items
4. Extract from table via browser_console
```

### JavaScript extraction (table structure)
```javascript
const rows = document.querySelectorAll('table tbody tr');
const data = [];
rows.forEach((row) => {
  const cells = row.querySelectorAll('td');
  if (cells.length >= 10) {
    data.push({
      summary: cells[2]?.innerText?.trim() || '',    // Summary
      category: cells[3]?.innerText?.trim() || '',    // Tag (Crypto/Tech/Breaking/...)
      posted: cells[4]?.innerText?.trim() || '',      // Relative time
      likes: cells[5]?.innerText?.trim() || '',       // Like count
      views: cells[6]?.innerText?.trim() || '',       // View count
      link: cells[9]?.querySelector('a')?.href || ''  // Link to x.com tweet (COLUMN 9!)
    });
  }
});
```

**CRITICAL:** The link column is at index **9**, not 8. Column 8 is Δ1H% (change percentage). Using index 8 returns empty strings.

## Page Structure

```
┌─────────────────────────────────┐
│ Price ticker bar                │  ← BTC, DOGE, TSLA, S&P 500, CRUDE, memecoins
├─────────────────────────────────┤
│ BREAKING (horizontal scroll)    │  ← Real-time breaking tweets
├─────────────────────────────────┤
│ Filter buttons                  │  ← All | Breaking | Crypto | Elon | Memes | Tech | Trump | Coin it
├─────────────────────────────────┤
│ Main table                      │  ← Bookmark | # | Summary | Category | Posted | Likes | Views | Δ1H | Δ1H% | View ↗
├─────────────────────────────────┤
│ Top Stories sidebar             │  ← Curated top stories
├─────────────────────────────────┤
│ Trending globe visualization    │  ← Geographic trending patterns
└─────────────────────────────────┘
```

## For Morning/News Briefing Use

thefeed.today is the primary data source for the `x-news-brief` skill. It replaces direct X API calls for read-only news aggregation because:

1. **No credits consumed** — browser extraction is free
2. **Pre-filtered** — Crypto/Tech buttons save query complexity
3. **Already summarized** — 1-line extraction is sufficient for briefing
4. **Links preserved** — can include original x.com URLs in brief

Limitation: Links are relative to thefeed.today ("View ↗" button), not direct x.com URLs. Extract the href from the `<a>` tag in column 9 of the table row.
