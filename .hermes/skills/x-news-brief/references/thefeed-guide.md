# Reference — Using thefeed.today

Guide to extracting data from thefeed.today for news briefing.

## Site Overview

**URL:** https://thefeed.today/
**Purpose:** Real-time X (Twitter) trends aggregator

**Key features:** Pre-summarized tweets (1-line per item), category filters (Crypto, Tech, News), engagement metrics (views, likes, engagement rate), breaking news tags, no auth required, no rate limits.

## Page Structure (as of 2026-05-22)

The site uses a plain HTML `<table>` with `<thead>` / `<tbody>` / `<tr>` / `<td>` structure. **There are no `data-testid` attributes.** The old `.item-summary`, `.item-title`, `.item-*` classes DO NOT EXIST.

**Table columns:** Bookmark | # | SUMMARY | CATEGORY | POSTED | LIKES | VIEWS | Δ1H | Δ1H%

**Category filter buttons** are plain `<button>` elements in a horizontal scroll bar near the header. Found via:
```js
document.querySelectorAll('button').filter(b => 
  ['Crypto','Tech','News','All'].includes(b.textContent.trim())
)
```

**Breaking items:** Items with category "Breaking" (td[3]) should be classified by their summary content. If clearly crypto-related → treat as Crypto with `breaking=true`. Same for Tech.

## Data Extraction (working method — browser_console JS)

### Step 1: Navigate + Apply Filter via JS

Navigate to `https://thefeed.today/`, wait for load, then click filter via JS (NOT Playwright selectors — the buttons have no distinguishing attributes):

```js
// Click Crypto filter
document.querySelectorAll('button').forEach(b => { 
  if (b.textContent.trim() === 'Crypto') b.click(); 
});
```

Wait 2-3 seconds for table to reload. Then repeat for Tech.

### Step 2: Extract items (no scrolling needed)

The table is fully rendered on filter click — scrolling is NOT necessary. Extract directly via `browser_console`:

```js
new Promise(r => setTimeout(r, 2500)).then(() => {
  const rows = document.querySelectorAll('tbody tr');
  return JSON.stringify([...rows].slice(0, 25).map(row => {
    const cells = row.querySelectorAll('td');
    if (cells.length < 6) return null;
    const links = row.querySelectorAll('a');
    const xLink = [...links].find(a => a.href && a.href.includes('x.com'));
    return {
      summary: cells[2]?.textContent?.trim() || '',
      category: cells[3]?.textContent?.trim() || '',
      posted: cells[4]?.textContent?.trim() || '',
      likes: cells[5]?.textContent?.trim() || '',
      views: cells[6]?.textContent?.trim() || '',
      delta_1h: cells[7]?.textContent?.trim() || '',
      delta_pct: cells[8]?.textContent?.trim() || '',
      link: xLink?.href || ''
    };
  }).filter(Boolean));
})
```

Note: Links are extracted in the same pass via `row.querySelectorAll('a')` filtered for `x.com` href.

### Step 3: Switch category

To get Tech items, navigate fresh or click Tech button similarly:
```js
document.querySelectorAll('button').forEach(b => { 
  if (b.textContent.trim() === 'Tech') b.click(); 
});
```

### Item Components (actual)

| Component | Source | Format | Notes |
|-----------|--------|--------|-------|
| Summary | `td[2]` textContent | 1-line summary | May contain "Requote:" prefix |
| Category | `td[3]` textContent | "Crypto" / "Tech" / "Breaking" | Normalize "Breaking" to actual domain |
| Posted | `td[4]` textContent | "8h ago", "23h ago" | Relative time |
| Likes | `td[5]` textContent | "1.8K", "205.6K", "839" | Parse with parse_number() |
| Views | `td[6]` textContent | "942.6K", "19.0M" | Parse with parse_number() |
| Δ1H | `td[7]` textContent | "▲ 83.6K" / "▼ 1.2K" | Optional — momentum signal |
| Δ1H% | `td[8]` textContent | "▲ 9.7%" / "▼ 0.3%" | Optional — momentum signal |
| Link | `a[href*="x.com"]` | Full X.com URL | Found in any cell within the row |

## Parsing Helpers

```python
def parse_number(text):
    """Parse '1.2M'→1200000, '500K'→500000, '1,234'→1234"""
    text = text.replace(',', '').strip()
    if 'M' in text: return int(float(text.replace('M','')) * 1_000_000)
    elif 'K' in text: return int(float(text.replace('K','')) * 1_000)
    else: return int(text)

def parse_relative_time(text):
    """Parse '2h ago' → now-2hours, '1d ago' → now-1day"""
    now = datetime.now(timezone.utc)
    text = text.lower().strip()
    if 'h ago' in text: return now - timedelta(hours=int(text.split('h')[0]))
    elif 'd ago' in text: return now - timedelta(days=int(text.split('d')[0]))
    elif 'm ago' in text: return now - timedelta(minutes=int(text.split('m')[0]))
    else: return now

def calculate_engagement_rate(likes, views):
    """(likes / views) * 100"""
    return (likes / views) * 100 if views > 0 else 0.0
```

## Thin Window Handling

Overnight windows (7AM run, ~10h since last run) often produce fewer items. When total new items < 15:

- Relax the 5% engagement threshold — use views-based ranking only
- Đáng đọc can go below 7 items (natural, not inflated)
- Narrative pulse still useful even with fewer items — focus on themes
- TL;DR should still cover both categories even if thin

## Error Handling

- **Filter button not found:** Try clicking by text content via JS. If still fails, continue without that category.
- **Item extraction fails:** Skip malformed row, continue with remaining.
- **No items loaded:** Check if table `<tbody>` exists. If not, page structure may have changed.
- **Category "Breaking" mixed in:** Classify by summary content (Crypto vs Tech domain).

## Maintenance

Update this guide when: HTML structure changes, table columns shift, selectors break, new features added.

**Last updated:** 2026-05-22
