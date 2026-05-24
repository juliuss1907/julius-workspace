---
name: news-brief-system
category: workflows
description: Multi-source news aggregator with keyword-first prioritization for Crypto + Tech briefings. Scrapes Telegram + websites, 3-tier selection, bilingual output.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [news, aggregation, crypto, tech, telegram, scraping, automation]
    related_skills: [x-news-brief, sentinel-scanner]
---

# News Brief System

Multi-source news aggregator for automated Crypto + Tech briefings with keyword-first prioritization.

## Overview

Scrapes multiple sources (Telegram channels, websites via Playwright), applies 3-tier priority scoring (keyword match + engagement + recency), deduplicates, and delivers bilingual briefs (Vietnamese + English terminology) via Telegram.

**Core innovation:** Keyword-first prioritization weights tier-1 keywords (100pts), tier-2 (70pts), tier-3 (40pts), plus engagement normalization and source authority multipliers.

## When to Use

- Need automated news briefings from multiple sources
- Want keyword-driven prioritization (not just engagement)
- Require deduplication across channels
- Need bilingual output (Vietnamese + English terminology)
- Schedule: 3x daily or on-demand

## Architecture

```
scrape.py → merge.py → prioritize.py → format.py → send.py
     ↓            ↓           ↓           ↓         ↓
Telegram   Deduplicate   3-tier      Bilingual  Telegram
Website    (domain+      scoring     brief      delivery
           title)       (keyword
                       + engagement
                       + recency)
```

## Key Components

### 1. Multi-Source Scraping
- **Telegram:** Telethon async client, rate-limited
- **Websites:** Playwright browser automation
- **RSS:** Future expansion

### 2. Deduplication Logic
- Same link → dedup
- Same domain + 80% title similarity → dedup
- Source authority decides winner (research > news > community)

### 3. 3-Tier Priority Scoring
```
Total = Keyword (0-100) + Engagement (0-50) + Source (0-15) + Recency (0-10)

Keyword tiers:
- tier_1: weight 100 (must-have: bitcoin, ethereum, sec approval)
- tier_2: weight 70 (emerging: defi, layer2, restaking)
- tier_3: weight 40 (general: nft, gamefi, metaverse)
- negative: weight -50 (spam, pump)

Engagement normalization:
- Telegram: 1K-100K views → 0-50 pts
- thefeed: 5K-5M views → 0-50 pts
- Bonus: engagement rate > 5% → +10 pts

Source authority:
- priority: high (1.5x), medium (1.0x), low (0.7x)
- type: research (1.3x), alpha (1.1x), news (1.0x), community (0.8x)
- Max bonus: 15 pts

Recency bonus:
- last 3h: 10 pts
- last 6h: 7 pts
- last 12h: 3 pts
- older: 0 pts
```

### 4. Selection Algorithm

**Top stories (2-5 items):**
- Include all breaking news (both categories)
- Fill remaining with highest total score
- Flexible category mix (not forced 50/50)

**Worth reading (7-10 items, 50/50 split):**
- Crypto: 3-5 items (tier 2 + interesting tier 3)
- Tech: 3-5 items (tier 2 + interesting tier 3)
- Require keyword match: No (allow high engagement)
- Adjust if category imbalance extreme

### 5. Bilingual Output
- **Language:** Vietnamese (100%)
- **Terminology:** English terms kept (protocol names, company names, technical acronyms)
- **Tone:** Casual, informative, minimal slang (ser, alpha, based)
- **Format:** Markdown for Telegram

## File Structure

```
news-brief-system/
├── SKILL.md                     # This file
├── config.py                    # Sources, keywords, weights
├── config_helpers.py            # Config utilities
├── scrape.py                    # Main orchestrator
├── scrape_telegram.py           # Telegram scraper
├── scrape_thefeed.py            # thefeed.today scraper
├── merge.py                     # Deduplication
├── prioritize.py                # 3-tier scoring
├── format.py                    # Brief formatting
├── send.py                      # Telegram delivery
├── setup_telegram.py            # One-time auth
├── requirements.txt
├── .gitignore
└── .state/                      # Generated JSON + timestamp
```

## Configuration

**Add Telegram channels:**
```python
NEWS_SOURCES['telegram']['channels']['crypto'].append({
    'username': 'thedefiedge',
    'name': 'The DeFi Edge',
    'priority': 'high',
    'type': 'research',
    'enabled': True
})
```

**Add keywords:**
```python
KEYWORD_FILTERS['crypto']['tier_1']['keywords'].extend(['ethereum', 'bitcoin', 'sec'])
```

**Adjust weights:**
```python
KEYWORD_FILTERS['crypto']['tier_1']['weight'] = 120  # Increase
ENGAGEMENT_WEIGHTS['telegram']['views']['max_points'] = 60  # More weight
```

## Workflow

1. **Scrape:** Run `scrape.py` (fetch from all enabled sources)
2. **Merge:** Deduplicate using domain + title similarity
3. **Prioritize:** Calculate 3-tier scores for all items
4. **Select:** Apply selection algorithm for top stories + worth reading
5. **Format:** Generate bilingual brief
6. **Send:** Deliver to Telegram
7. **Update:** Save timestamp to `.state/`

## Quality Standards

- [ ] All items newer than last run timestamp
- [ ] Breaking news always included
- [ ] Top stories: flexible 2-5 items (highest priority)
- [ ] Worth reading: 7-10 items (50/50 Crypto/Tech split)
- [ ] Bilingual: Vietnamese + English terminology
- [ ] Links all functional
- [ ] Timestamp updated after successful run

## Common Pitfalls

1. **Too many items:** Lower `SELECTION_CRITERIA` max counts or increase `min_score` thresholds
2. **Too few items:** Add more sources or lower thresholds
3. **Category imbalance:** Adjust category selection in `select_worth_reading()`
4. **Spam getting through:** Add to `NEGATIVE_KEYWORDS`, increase `min_keyword_score`
5. **Rate limits:** Increase `rate_limit_delay` in config
6. **Duplicate items:** Check `merge.py` similarity threshold (currently 80%)

## Extension Points

**Add new scraper:**
1. Create `scrape_newsource.py` with `async def scrape()` returning items
2. Add to `NEWS_SOURCES` config
3. Update `scrape.py` to call it

**Add new keyword tier:**
1. Add to `KEYWORD_FILTERS[category]['tier_4']`
2. Update `prioritize.py` to check it

**Change output format:**
1. Edit `format.py`
2. Adjust `send.py` if needed

## Implementation Location

Full implementation at `~/julius-workspace/ai-labs/projects/x-news-brief/`

## Cron Setup

```bash
# Scrape 3x daily
50 6,12,20 * * * cd ~/julius-workspace/ai-labs/projects/x-news-brief && python3 scrape.py
# Synthesize 10 min after
0 7,13,21 * * * cd ~/julius-workspace/ai-labs/projects/x-news-brief && python3 synthesize.py
```

## Verification

```bash
cd ~/julius-workspace/ai-labs/projects/x-news-brief
python3 scrape.py
python3 synthesize.py --debug
```

Check `.state/` for JSON output and timestamps.

## Maintainers

Julius (original architect) + Markus (implementation)

**Last Updated:** 2026-05-23