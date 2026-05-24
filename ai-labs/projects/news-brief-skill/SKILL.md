---
name: news-brief-skill
aliases: ["news-brief", "brief", "tin tức", "news-aggregator"]
agent: Hermes (local)
description: Multi-topic automated news aggregator with keyword-first prioritization, supporting Telegram channels, websites, and RSS feeds. Delivers briefs in Vietnamese to Telegram and Markdown files.
purpose: Automated multi-topic news briefing system
trigger: Cron (3x daily — 7:00, 13:00, 21:00 ICT)
output: Telegram message + Markdown file
version: 2.0
last_updated: 2026-05-23
---

# SKILL — News Brief

**Agent:** Hermes (local)  
**Purpose:** Multi-topic automated news aggregator and brief generator  
**Trigger:** Cron (3x daily)  
**Output:** Telegram message + Markdown file  
**Version:** 2.0  
**Last updated:** 2026-05-23

---

## Overview

News Brief Skill is a flexible, multi-topic news aggregation system that:
- Scrapes from multiple sources (Telegram, websites, RSS)
- Prioritizes content using keyword-first approach
- Supports unlimited custom topics
- Delivers briefs in Vietnamese
- Outputs to both Telegram and Markdown files

---

## Key Features

### Multi-topic Architecture
- Define unlimited topics (Crypto, Tech, AI Safety, Climate, etc.)
- Each topic has independent sources and keywords
- Per-topic selection criteria
- Cross-topic "Top Stories" section

### Keyword-first Prioritization
- 3-tier keyword system (100/70/40 points)
- Negative keywords for spam filtering
- Engagement scoring (views, reactions)
- Source authority weighting
- Recency bonus

### Multi-source Scraping
- **Telegram channels** via Telethon
- **Websites** via Playwright (thefeed.today, custom sites)
- **RSS feeds** via feedparser
- Automatic deduplication across sources

### Flexible Output
- Telegram delivery with Markdown formatting
- Markdown file output with configurable path
- Auto-generated index.md
- Configurable retention policy

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│ TOPICS CONFIGURATION                                │
│ ├─ crypto (sources + keywords)                      │
│ ├─ tech (sources + keywords)                        │
│ ├─ ai_safety (sources + keywords)                   │
│ └─ ... (unlimited topics)                           │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ SCRAPE PHASE (scrape.py)                            │
│ ├─ Telegram: scrape_telegram.py                     │
│ ├─ Websites: scrape_thefeed.py                      │
│ ├─ RSS: scrape_rss.py                               │
│ └─ Merge + Dedup → JSON                             │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ SYNTHESIZE PHASE (synthesize.py)                    │
│ ├─ Load JSON                                        │
│ ├─ Prioritize (keyword + engagement)                │
│ ├─ Select (top stories + per-topic)                 │
│ ├─ Format (Vietnamese)                              │
│ └─ Deliver (Telegram + Markdown)                    │
└─────────────────────────────────────────────────────┘
```

---

## Schedule

| Time (ICT) | Session | Coverage | Cron Expression |
|------------|---------|----------|-----------------|
| 7:00 | ☀️ Morning | Overnight + Asia morning | `0 7 * * *` |
| 13:00 | 🌤️ Midday | US morning news | `0 13 * * *` |
| 21:00 | 🌙 Wrap | US afternoon + day recap | `0 21 * * *` |

**Workflow:**
- **06:50** — Scrape runs (10 min before)
- **07:00** — Synthesize runs → Brief delivered

---

## Configuration

### Topics Structure

```python
TOPICS = {
    'crypto': {
        'enabled': True,
        'display_name': 'Crypto',
        'icon': '🪙',
        'description': 'Cryptocurrency, DeFi, blockchain',
        
        'sources': {
            'telegram': [...],
            'websites': [...],
            'rss': [...]
        },
        
        'keywords': {
            'tier_1': {'keywords': [...], 'weight': 100},
            'tier_2': {'keywords': [...], 'weight': 70},
            'tier_3': {'keywords': [...], 'weight': 40},
            'negative': {'keywords': [...], 'weight': -50}
        },
        
        'selection': {
            'worth_reading': {
                'min': 3,
                'max': 5,
                'min_score': 40
            }
        }
    },
    # Add more topics...
}
```

### Global Settings

```python
GLOBAL_SETTINGS = {
    'telegram_api': {...},
    'rss': {...},
    'keywords': {...},
    'engagement': {...},
    'source_authority': {...},
    'recency': {...},
}
```

### Output Settings

```python
OUTPUT_SETTINGS = {
    'telegram': {
        'enabled': True,
        'bot_token': '...',
        'chat_id': '...'
    },
    'markdown': {
        'enabled': True,
        'path': '~/Documents/news-briefs',
        'filename_format': '{date}/{session}.md',
        'keep_days': 30,
        'create_index': True
    }
}
```

---

## Prioritization Logic

### Score Calculation

```
total_score = keyword_score + engagement_score + source_bonus + recency_bonus
```

**Keyword Score (0-100 points):**
- Tier 1: 100 points (breaking news, major events)
- Tier 2: 70 points (emerging trends)
- Tier 3: 40 points (general topics)
- Negative: -50 points (spam, low quality)

**Engagement Score (0-50 points):**
- Telegram: normalized by views (1K-100K)
- thefeed: normalized by views (5K-5M) + engagement rate bonus
- RSS: authority-based (high=30, medium=20, low=10)

**Source Bonus (0-15 points):**
- Priority: high (1.5x), medium (1.0x), low (0.7x)
- Type: research (1.3x), news (1.0x), alpha (1.1x)

**Recency Bonus (0-10 points):**
- Last 3h: 10 points
- Last 6h: 7 points
- Last 12h: 3 points

### Selection Criteria

**Top Stories (cross-topic):**
- Min score: 80
- Require keyword match: Yes
- Breaking news override: Yes
- Count: 2-5 items (flexible)

**Worth Reading (per topic):**
- Min score: 40 (configurable per topic)
- Require keyword match: No
- Count: 3-5 items per topic (configurable)

---

## Output Format

### Brief Structure

```
☀️ NEWS BRIEF — SANG
07:00 23/05/2026

━━━━━━━━━━━━━━

🔥 TOP STORIES
• [Cross-topic, highest priority items]

━━━━━━━━━━━━━━

🪙 CRYPTO — DANG DOC
• [Crypto-specific items]

💻 TECH — DANG DOC
• [Tech-specific items]

🛡️ AI SAFETY — DANG DOC
• [AI Safety-specific items]

━━━━━━━━━━━━━━
Generated by Hermes · N items
```

### Markdown File Output

Files saved to configured path:
```
~/Documents/news-briefs/
├── index.md
├── 2026-05-23/
│   ├── morning.md
│   ├── midday.md
│   └── wrap.md
└── 2026-05-24/
    └── ...
```

---

## Usage

### Manual Run

```bash
# Scrape
python3 scrape.py

# Synthesize
python3 synthesize.py

# Synthesize with debug output
python3 synthesize.py --debug
```

### Cron Setup

```bash
# Scrape (3x daily, 10 min before synthesize)
50 6,12,20 * * * cd /path/to/skill && python3 scrape.py >> logs/scrape.log 2>&1

# Synthesize (3x daily)
0 7,13,21 * * * cd /path/to/skill && python3 synthesize.py >> logs/synthesize.log 2>&1
```

### Management Tools

```bash
# Show topic statistics
python3 manage_topics.py list

# Show enabled sources summary
python3 manage_topics.py summary

# Show markdown archive stats
python3 manage_briefs.py stats

# Cleanup old briefs
python3 manage_briefs.py cleanup 60
```

---

## Adding New Topics

### Step 1: Define Topic in config.py

```python
TOPICS = {
    # ... existing topics ...
    
    'climate_tech': {
        'enabled': True,
        'display_name': 'Climate Tech',
        'icon': '🌱',
        'description': 'Climate technology, sustainability',
        
        'sources': {
            'telegram': [
                {
                    'username': 'climatetechnews',
                    'name': 'Climate Tech News',
                    'priority': 'high',
                    'type': 'news',
                    'enabled': True
                }
            ],
            'websites': [],
            'rss': [
                {
                    'name': 'CleanTechnica',
                    'url': 'https://cleantechnica.com/feed/',
                    'priority': 'high',
                    'enabled': True
                }
            ]
        },
        
        'keywords': {
            'tier_1': {
                'keywords': ['carbon capture', 'renewable energy', 'ev'],
                'weight': 100
            },
            'tier_2': {
                'keywords': ['sustainability', 'green tech'],
                'weight': 70
            },
            'tier_3': {
                'keywords': ['environment', 'clean energy'],
                'weight': 40
            },
            'negative': {
                'keywords': ['greenwashing'],
                'weight': -50
            }
        },
        
        'selection': {
            'worth_reading': {
                'min': 2,
                'max': 4,
                'min_score': 40
            }
        }
    }
}
```

### Step 2: Test

```bash
# Check topic is recognized
python3 manage_topics.py list

# Run scrape
python3 scrape.py

# Run synthesize
python3 synthesize.py
```

**No code changes needed!** The system automatically:
- Scrapes sources from new topic
- Applies topic-specific keywords
- Creates dedicated section in brief

---

## Troubleshooting

### No items scraped

**Check:**
- Topics enabled: `python3 manage_topics.py list`
- Sources enabled in each topic
- Telegram authentication: `ls hermes_session.session`
- Logs: `tail -f logs/scrape.log`

**Fix:**
- Enable topics in config.py
- Run `python3 setup_telegram.py` for auth
- Check source URLs are valid

### Low quality items

**Adjust:**
- Increase `min_keyword_score` in GLOBAL_SETTINGS
- Add negative keywords
- Raise `min_score` in selection criteria
- Adjust QUALITY_FILTERS (min_text_length, min_views)

### Too few/many items

**Adjust per topic:**
```python
'selection': {
    'worth_reading': {
        'min': 0,  # Lower for flexible
        'max': 10, # Raise for more items
        'min_score': 40
    }
}
```

### Brief not delivered

**Check:**
- Telegram bot token and chat_id in config
- Markdown path exists and writable
- Logs: `tail -f logs/synthesize.log`

---

## File Structure

```
news-brief-skill/
├── config.py                    # Main configuration
├── config_helpers.py            # Config utilities
├── scrape.py                    # Main scraper
├── scrape_telegram.py           # Telegram scraper
├── scrape_thefeed.py            # thefeed.today scraper
├── scrape_rss.py                # RSS scraper
├── merge.py                     # Deduplication logic
├── prioritize.py                # Keyword + engagement scoring
├── format.py                    # Brief formatting
├── send.py                      # Telegram delivery
├── save_markdown.py             # Markdown file output
├── synthesize.py                # Main synthesizer
├── setup_telegram.py            # One-time Telegram auth
├── manage_topics.py             # Topic management CLI
├── manage_briefs.py             # Brief archive management CLI
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── README.md                    # Setup guide
├── SKILL.md                     # This file
├── workflow.md                  # Detailed workflow
├── examples.md                  # Example briefs
├── .state/                      # Generated files
│   ├── raw-*.json
│   └── last-run-timestamp.txt
├── logs/                        # Log files
│   ├── scrape.log
│   └── synthesize.log
└── hermes_session.session       # Telegram session (gitignored)
```

---

## Dependencies

- Python 3.9+
- telethon (Telegram API)
- playwright (Web scraping)
- feedparser (RSS parsing)
- requests (HTTP)

---

## Version History

**v2.0 (2026-05-23)**
- Multi-topic architecture
- Keyword-first prioritization
- Markdown file output
- Per-topic configuration
- Adaptive selection limits

**v1.0 (2026-05-19)**
- Initial release
- Crypto + Tech only
- Telegram + thefeed.today
- Telegram output only

---

## References

- [workflow.md](workflow.md) — Detailed workflow documentation
- [examples.md](examples.md) — Example briefs for all sessions
- [README.md](README.md) — Setup and installation guide

---

**Maintainer:** Julius  
**Last updated:** 2026-05-23
