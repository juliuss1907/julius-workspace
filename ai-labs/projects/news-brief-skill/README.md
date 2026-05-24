# News Brief Skill

Automated news aggregator and brief generator for Crypto & Tech news.

## Features

- **Multi-source scraping**: Telegram channels + websites (thefeed.today) + RSS feeds
- **Keyword-first prioritization**: Filter by topics you care about
- **Smart deduplication**: Merge items from multiple sources
- **Automated brief generation**: Vietnamese language output
- **Telegram delivery**: Send formatted briefs to Telegram chat

## Architecture

```
scrape.py → .state/raw-YYYY-MM-DD_HHmm.json → synthesize.py → Telegram
```

### Scrape Phase
- Scrape Telegram channels (Telethon)
- Scrape websites (Playwright)
- Scrape RSS feeds (feedparser)
- Merge + dedup
- Save JSON

### Synthesize Phase
- Load JSON
- Prioritize by keywords + engagement
- Select top stories + worth reading
- Format brief
- Send to Telegram

## Setup

### 1. Install dependencies

```bash
pip3 install -r requirements.txt
playwright install chromium
```

### 2. Configure sources

Edit `config.py`:

```python
# Add Telegram channels
NEWS_SOURCES = {
    'telegram': {
        'channels': {
            'crypto': [
                {
                    'username': 'thedefiedge',
                    'name': 'The DeFi Edge',
                    'priority': 'high',
                    'type': 'research',
                    'enabled': True
                },
                # Add more...
            ],
            'tech': [
                # Add tech channels...
            ]
        }
    },

    # Add websites
    'websites': {
        'sources': [
            {
                'name': 'thefeed.today',
                'url': 'https://thefeed.today/',
                'scraper': 'thefeed',
                'enabled': True,
                # ...
            }
        ]
    },

    # Add RSS feeds
    'rss': {
        'enabled': True,
        'feeds': {
            'crypto': [
                {
                    'name': 'CoinDesk',
                    'url': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
                    'priority': 'high',
                    'enabled': True
                },
                # Add more...
            ],
            'tech': [
                # Add tech feeds...
            ]
        }
    }
}

# Add keywords
KEYWORD_FILTERS = {
    'crypto': {
        'tier_1': {
            'keywords': ['ethereum', 'bitcoin', 'sec approval', 'etf'],
            'weight': 100,
        },
        # Add more tiers...
    },
    'tech': {
        # Add tech keywords...
    }
}
```

### 3. Setup Telegram authentication

Get API credentials:

1. Go to https://my.telegram.org/apps
2. Create new application
3. Copy `api_id` and `api_hash`

Set in config.py or environment:

```bash
export TELEGRAM_API_ID="your_api_id"
export TELEGRAM_API_HASH="your_api_hash"
export TELEGRAM_PHONE="+84..."
```

Authenticate:

```bash
python3 setup_telegram.py
# Enter code from Telegram when prompted
```

### 4. Setup Telegram bot (for sending briefs)

1. Create bot via @BotFather
2. Get bot token
3. Get chat ID (send message to bot, call `/getUpdates`)
4. Set in config.py:

```python
TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"
```

## Usage

### Manual run

```bash
# Scrape
python3 scrape.py

# Synthesize (with debug output)
python3 synthesize.py --debug
```

### Cron setup

```bash
crontab -e
```

Add:

```bash
# Scrape 3x daily
50 6 * * * cd /path/to/news-brief-skill && python3 scrape.py >> logs/scrape.log 2>&1
50 12 * * * cd /path/to/news-brief-skill && python3 scrape.py >> logs/scrape.log 2>&1
50 20 * * * cd /path/to/news-brief-skill && python3 scrape.py >> logs/scrape.log 2>&1

# Synthesize 10 min after scrape
0 7 * * * cd /path/to/news-brief-skill && python3 synthesize.py >> logs/synthesize.log 2>&1
0 13 * * * cd /path/to/news-brief-skill && python3 synthesize.py >> logs/synthesize.log 2>&1
0 21 * * * cd /path/to/news-brief-skill && python3 synthesize.py >> logs/synthesize.log 2>&1
```

## Configuration Guide

### Priority System

**Keyword matching** (0-100 points):
- Tier 1: 100 points (breaking news, major protocols)
- Tier 2: 70 points (emerging trends)
- Tier 3: 40 points (general topics)
- Negative: -50 points (spam, low quality)

**Engagement** (0-50 points):
- Telegram: normalized by views (1K-100K)
- thefeed: normalized by views (5K-5M) + engagement rate bonus
- RSS: based on source priority (10-30 points)

**Source authority** (0-15 points):
- Priority: high (1.5x), medium (1.0x), low (0.7x)
- Type: research (1.3x), news (1.0x), alpha (1.1x)

**Recency** (0-10 points):
- Last 3h: 10 points
- Last 6h: 7 points
- Last 12h: 3 points

### Selection Criteria

**Top stories** (2-5 items):
- Min score: 80
- Require keyword match: Yes
- Flexible category mix

**Worth reading** (3-5 per category):
- Min score: 40
- Require keyword match: No (allow high engagement)
- Balanced Crypto/Tech split

### Tuning

Adjust in `config.py`:

```python
# Make keyword matching stricter
KEYWORD_FILTERS['settings']['min_keyword_score'] = 40

# Give more weight to engagement
ENGAGEMENT_WEIGHTS['telegram']['views']['max_points'] = 70

# Require higher score for top stories
SELECTION_CRITERIA['top_stories']['min_score'] = 100
```

## Troubleshooting

### No items scraped

- Check if sources are enabled in config
- Verify Telegram authentication: `ls hermes_session.session`
- Check logs: `tail -f logs/scrape.log`

### Brief not sent

- Verify bot token and chat ID
- Check Telegram API limits
- Check logs: `tail -f logs/synthesize.log`

### Low quality items

- Add negative keywords to filter spam
- Increase `min_keyword_score` threshold
- Adjust `QUALITY_FILTERS` (min_text_length, min_views)

### Too few/many items

- Adjust `SELECTION_CRITERIA` min/max counts
- Lower/raise score thresholds
- Add/remove keywords

## File Structure

```
news-brief-skill/
├── config.py                    # Main configuration
├── config_helpers.py            # Config utilities
├── scrape.py                    # Main scraper
├── scrape_telegram.py           # Telegram scraper
├── scrape_thefeed.py            # thefeed.today scraper
├── scrape_rss.py                # RSS feed scraper
├── merge.py                     # Dedup logic
├── prioritize.py                # Keyword + engagement scoring
├── format.py                    # Brief formatting
├── send.py                      # Telegram sender
├── synthesize.py                # Main synthesizer
├── setup_telegram.py            # One-time auth
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── README.md                    # This file
├── .state/                      # Generated JSON files
│   ├── raw-YYYY-MM-DD_HHmm.json
│   └── last-run-timestamp.txt
├── logs/                        # Log files
│   ├── scrape.log
│   └── synthesize.log
└── hermes_session.session       # Telegram session (gitignored)
```

## Future Expansion

- Reddit scraper
- Custom website scraper (generic)
- Sentiment analysis
- Trend detection
- Multi-language support
- Web dashboard

## License

MIT
