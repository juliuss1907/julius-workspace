# Reference — Using thefeed.today

Guide to extracting data from thefeed.today for news briefing.

## Site Overview

**URL:** https://thefeed.today/
**Purpose:** Real-time X (Twitter) trends aggregator

**Key features:** Pre-summarized tweets (1-line per item), category filters (Crypto, Tech, News), engagement metrics (views, likes, engagement rate), breaking news tags, no auth required, no rate limits.

## Page Structure

**Feed item structure:** Avatar + Author → Summary text → Category tag + Time ago → Views + Engagement % + Link

**Category filters:** All (default), Crypto, Tech, News, Sports, Entertainment, Politics, General
**For this skill, use:** Crypto + Tech

## Data Extraction

### Item Components

| Component | Selector | Format |
|-----------|----------|--------|
| Author/Source | `.item-title` or `[data-author]` | "Author" or "@handle" |
| Summary | `.item-summary` or `[data-summary]` | 1-line text |
| Views | `.views-count` or `[data-views]` | "1.2M" / "500K" / "1234" |
| Likes | `.likes-count` or `[data-likes]` | "12.5K" / "1234" |
| Engagement Rate | `.engagement-rate` or calculate | "12.3%" |
| Link | `a.item-link` href | Full X.com URL |
| Timestamp | `.timestamp` or `[data-time]` | "2h ago", "1d ago" |
| Breaking Tag | `.breaking-tag` or text check | Boolean |
| Category | `.category-tag` or filter context | "Crypto" / "Tech" |

## Extraction Strategy

### Step 1: Navigate + Apply Filter
```python
page.goto("https://thefeed.today/")
page.wait_for_load_state("networkidle")
crypto_button = page.locator('button:has-text("Crypto")')
crypto_button.click()
page.wait_for_timeout(2000)
```

### Step 2: Scroll to load (~20-30 items)
```python
for i in range(3):
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000)
```

### Step 3: Extract items (top 20)
```python
items = page.locator('[data-testid="feed-item"]').all()
for item in items[:20]:
    # Extract each component, skip malformed
```

## Parsing Helpers

```python
def parse_number(text):
    """Parse '1.2M'→1200000, '500K'→500000, '1,234'→1234"""
    text = text.replace(',', '').strip()
    if 'M' in text: return int(float(text.replace('M','')) * 1_000_000)
    elif 'K' in text: return int(float(text.replace('K','')) * 1_000)
    else: return int(text)

def parse_timestamp(text):
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

## Error Handling

- **Filter button not found:** Try alternative selector, continue without that category
- **Item extraction fails:** Skip malformed item, continue with remaining
- **No items loaded:** Retry with different selector, raise if still empty

## Maintenance

Update this guide when: HTML structure changes, selectors stop working, new features added, extraction logic needs adjustment.

**Last updated:** 2026-05-19
