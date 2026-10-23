---
name: sentinel-scanner
description: >
  Daily sentiment scanner for Crypto Twitter. Tracks KOL timelines and keyword
  narratives to identify hot topics, contrarian takes, and emerging trends.
  Triggers: "scan crypto twitter", "what's CT talking about", "morning briefing",
  "sentiment check", "narrative scan", "who's bullish", "trending crypto".
metadata:
  version: "1.0.0"
  author: "Markus / Hermes"
  created: "2026-05-20"
---

# Sentinel Scanner

## Purpose

Automated daily scan of Crypto Twitter sentiment and narratives. 
Tracks 80+ accounts (KOLs, project founders, researchers, institutions) 
and 50+ keywords to surface what's hot, what's contrarian, and what KOLs 
are signaling.

## When to Use

- Morning briefing: "What's CT talking about today?"
- Pre-trade research: "What's the sentiment on Ethereum L2s?"
- Narrative discovery: "What trends are emerging this week?"
- Contrarian hunting: "Who's saying something different?"

## Trigger Phrases

```
"Scan crypto twitter"
"What's CT talking about"
"Morning briefing"
"Sentiment check"
"Narrative scan"
"Run sentinel scanner"
"Check crypto Twitter"
```

## How to Run

### Manual (one-time scan)

```bash
cd ~/julius-workspace/ai-labs/resource/skills/sentinel-scanner
python scripts/scan.py
```

### Via Hermes

```
@Markus Run sentinel scanner
```

### Scheduled (cron)

See `cron/` for scheduling setup to run 8am daily.

## Data Sources

### Accounts Scanned

- **27 Tier 1 KOLs**: Vitalik, Saylor, CZ, Raoul Pal, Balaji, etc.
- **21 Tier 2 Experts**: DeFi analysts, on-chain researchers, builders
- **17 Tier 3 Emerging** (optional): Contrarian voices, early signals
- **4 Crypto Orgs**: Arkham, Messari, Binance, OpenClaw
- **14 AI Orgs**: OpenAI, Anthropic, xAI, HuggingFace, etc.

### Keywords Monitored

- **37 Evergreen**: DeFi, L2s, Bitcoin ETF, RWAs, MEV, etc.
- **19 Trending**: Updated weekly (EigenLayer, Farcaster, etc.)

## Output Sections

```
🎯 SENTINEL SCAN — 2026-05-20

📊 TOP NARRATIVES
→ 3 hottest topics with tweet counts and sentiment

💡 CONTRARIAN TAKES  
→ 2 takes going against consensus

🔥 KOL INSIGHTS
→ Notable tweets from Tier 1 accounts

⚡ EMERGING TRENDS
→ New narratives gaining traction
```

## Configuration

Edit `config.yaml` to customize:

```yaml
# Add/remove accounts
kols:
  individuals:
    tier1:
      - "NewKOL"
      
# Add/remove keywords  
keywords:
  trending:
    - "NewHotTopic"

# Adjust thresholds
scan:
  tweets_per_kol: 30
  min_engagement: 50
  max_age_hours: 24
```

## Technical Notes

- **Tool**: `twitter` CLI (from Agent Reach)
- **Rate limits**: Respected via built-in delays
- **Runtime**: ~2-3 minutes for full scan
- **Output**: Telegram-formatted brief + JSON data

## Files

```
sentinel-scanner/
├── SKILL.md              # This file
├── config.yaml           # Account/keyword lists
├── scripts/
│   ├── scan.py          # Core scanning logic
│   └── install.sh       # Setup dependencies
├── templates/
│   └── brief.j2         # Output template
└── cron/
    └── daily.sh         # Cron job example
```

## Limitations

- Requires `twitter` CLI installed (via Agent Reach)
- X may rate-limit on aggressive scans
- No historical comparison (stateless)
- Sentiment analysis is keyword-based (not NLP)

## Future Improvements

- [ ] Persistent state for trend comparison
- [ ] LLM-based sentiment analysis
- [ ] Price correlation (coingecko integration)
- [ ] Automatic trending keyword discovery
