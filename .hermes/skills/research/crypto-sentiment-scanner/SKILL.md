---
name: crypto-sentiment-scanner
description: >
  Monitor Crypto Twitter (X) sentiment and narratives. Scans KOL timelines and
  keyword searches to surface trending topics, contrarian takes, and KOL signals.
  Uses twitter CLI (free) for data collection, LLM for synthesis.
  Triggers: "scan CT", "crypto twitter sentiment", "what's CT saying",
  "narrative check", "KOL scanner", "twitter scan".
triggers:
  - scan crypto twitter
  - CT sentiment check
  - what's the narrative
  - scan CT today
  - KOL timeline scan
  - twitter sentiment
---

# Crypto Sentiment Scanner

## Overview

Tool for monitoring Crypto Twitter (X) sentiment via automated scanning. Collects
data from KOL timelines and keyword searches, then synthesizes into actionable
briefs.

## Data Collection Strategy

**Use `twitter` CLI (Agent Reach)** — FREE, no API credits needed
- Installation: `pipx install twitter-cli` (via Agent Reach)
- Commands: `twitter user-tweets @KOL`, `twitter search "keyword"`

**NOT `x_search` tool** — Requires xAI/Grok subscription ($30/month)

## Key Implementation Lessons

### Rate Limiting

X API rate-limits bulk requests. Add **random delays**:

```python
import time
import random

# Between account scans
time.sleep(random.uniform(5, 10))

# Between keyword searches  
time.sleep(random.uniform(1, 3))
```

Without delays, scanning 50+ accounts triggers 429 errors.

### Config Structure

```yaml
kols:
  individuals:
    tier1: []    # 100K+ followers, market-moving
    tier2: []    # 10K-100K, quality analysis
    tier3: []    # Emerging voices
  organizations_crypto: []  # Messari, Arkham, etc.
  organizations_ai: []    # OpenAI, Anthropic, etc.

keywords:
  evergreen: []   # Always relevant (DeFi, L2s, etc.)
  trending: []    # Update weekly

scan:
  tweets_per_kol: 10        # 10-30 optimal
  tweets_per_keyword: 20    # 20-50 optimal
  max_age_hours: 24         # Only recent tweets
  min_engagement: 50        # Filter noise
  max_tweets_to_analyze: 300 # Limit for LLM
```

### Recommended Parameters

| Mode | tweets_per_kol | tweets_per_keyword | accounts | runtime |
|------|---------------|-------------------|----------|---------|
| Quick | 10 | 20 | Tier 1 only | ~2 min |
| Standard | 20 | 30 | T1 + T2 | ~5 min |
| Deep | 30 | 50 | All tiers | ~8 min |

## Analysis Pipeline

1. **Collect** → `twitter` CLI (raw JSON)
2. **Filter** → Age, engagement threshold
3. **Group** → By keyword/narrative matching
4. **Sentiment** → Simple keyword counting (pos/neg/neutral)
5. **Synthesize** → LLM (DeepSeek recommended) for final brief

## Output Format (Telegram)

```
🎯 SENTINEL SCAN — 2026-05-20

📊 Top Narratives
→ *Topic* — N tweets 🟢
  @author: "tweet preview..."

💡 Contrarian Takes
→ @author: "unpopular opinion..."

🔥 KOL Insights
→ [T1] @author: "insight..."
```

## User Preferences (Julius)

- **Synthesis model**: DeepSeek (not Grok)
- **Collection**: twitter CLI only (free)
- **Scan frequency**: Daily morning brief
- **Focus**: Narratives + contrarian takes

## References

- `twitter` CLI docs: via `agent-reach install`
- Agent Reach: https://github.com/Panniantong/Agent-Reach
