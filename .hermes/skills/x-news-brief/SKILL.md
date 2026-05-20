---
name: x-news-brief
aliases: ["x-morning-news", "brief CT", "tin sáng", "x-news"]
agent: Hermes (local)
purpose: Automated crypto + tech news briefing from X via thefeed.today
trigger: Cron (3x daily — 7:00, 13:00, 21:00 ICT)
output: Telegram message
version: 1.0
last_updated: 2026-05-19
---

# SKILL — X News Brief

**Agent:** Hermes (local)  
**Purpose:** Automated crypto + tech news briefing from X (via thefeed.today)  
**Trigger:** Cron (3x daily)  
**Output:** Telegram message  
**Version:** 1.0  
**Last updated:** 2026-05-19

---

## Role

Monitor crypto and tech news on X via thefeed.today and deliver concise briefings to Julius 3 times per day. Each brief covers new developments since last run, prioritized by breaking news, engagement, and narrative shifts.

Hermes handles:
- Browser automation (Playwright)
- Dual-category extraction (Crypto + Tech)
- Content filtering and deduplication
- Prioritization (3-tier logic)
- Brief synthesis (separate narratives)
- Telegram delivery

---

## Schedule

| Time (ICT) | Session | Coverage | Cron Expression |
|---|---|---|---|
| 7:00 | ☀️ Morning | Overnight + Asia morning | `0 7 * * *` |
| 13:00 | 🌤 Midday | US morning news | `0 13 * * *` |
| 21:00 | 🌙 Wrap | US afternoon + day recap | `0 21 * * *` |

**Deduplication:** Each run only reports items newer than last run's timestamp.

---

## Data Source

**thefeed.today**

**Categories covered:**
- **Crypto:** DeFi, tokens, blockchain, exchanges, protocols
- **Tech:** AI, startups, products, developer tools, launches

**Why this source:**
- ✅ No rate limits (vs X API free tier exhausted)
- ✅ No authentication required
- ✅ Pre-summarized tweets (1-line per item)
- ✅ Category filters (Crypto + Tech buttons)
- ✅ Engagement metrics (views, likes, engagement rate)
- ✅ Breaking news tags

**Extraction order:**
1. Crypto filter first
2. Tech filter second
3. Merge and deduplicate

---

## Output Specification

**Format:** Telegram message (Markdown)

**Structure:**
```
✖️ X News Brief [☀️ / 🌤 / 🌙] — [Day], [Date]

🔥 Top 2-5 stories (flexible mix)
• [Story] — [Summary] ([views])

🧠 Narrative pulse
Crypto: [1-2 sentences]
Tech: [1-2 sentences]

📌 Đáng đọc (7-10 items, 50/50 split)

Crypto:
• [Item] — [Why interesting] [Link]
• [Item] — [Why interesting] [Link]

Tech:
• [Item] — [Why interesting] [Link]
• [Item] — [Why interesting] [Link]

TL;DR: [1 dòng covering both categories]
```

**Length targets:**
- Top stories: 2-5 items (flexible, highest priority wins)
- Đáng đọc Crypto: 3-5 items
- Đáng đọc Tech: 3-5 items
- Total đáng đọc: 7-10 items (50/50 split)
- Total message: ~500-800 words

**CT Voice:**
- Casual, informative tone
- Minimal slang (1-2 terms max: ser, alpha, based)
- Emoji for section markers only
- No hype, no speculation

---

## Prioritization Logic

**3-tier priority system (applied to both categories):**

### Tier 1: Breaking News (Highest)
- Items tagged "Breaking" on thefeed
- Always include if present
- No view threshold

### Tier 2: High Engagement
- Views > 5K
- Engagement rate > 5%
- Sort by views descending

### Tier 3: Narrative Shift
- New topics not seen in previous runs
- Emerging trends
- Lower views but interesting angle

**Selection algorithm:**

**Top stories (2-5 total, flexible mix):**
- Include all Tier 1 (Breaking) from both categories
- Fill remaining slots with highest Tier 2 (regardless of category)
- Natural mix emerges (not forced 50/50)

**Đáng đọc (7-10 total, 50/50 split):**
- Crypto: 3-5 items (Tier 2 + interesting Tier 3)
- Tech: 3-5 items (Tier 2 + interesting Tier 3)
- Adjust if one category has significantly more breaking news

**Narrative pulse:**
- Separate synthesis for each category
- Crypto: 1-2 sentences on DeFi/blockchain trends
- Tech: 1-2 sentences on AI/product trends

---

## State Management

**Location:**
```
ai-labs/resource/skills/x-news-brief/.state/
└── last-run-timestamp.txt
```

**Format:**
```
2026-05-19T07:00:00+07:00
```

**Behavior:**
- Read at start of each run
- Update after successful extraction
- If missing (first run): set to 24 hours ago
- Single timestamp for both categories (simpler dedup)

---

## Error Handling

### Scenario A: No new items
**Action:** Send brief with message:
```
No new crypto/tech news since last check (7:00 AM).

Last item: [timestamp]
```

### Scenario B: thefeed.today down
**Action:**
1. Retry once after 30 seconds
2. If still fails: Send error notification
3. Skip this run, try again next cron

### Scenario C: One category fails
**Action:**
1. Continue with successful category
2. Note in brief: "Tech news unavailable this run"
3. Don't skip entire brief

### Scenario D: Extraction fails
**Action:**
1. Log error locally
2. Retry once
3. If still fails: Send error notification
4. Skip this run

### Scenario E: Telegram delivery fails
**Action:**
1. Log locally
2. Retry on next cron run
3. Don't update timestamp (will re-send same items)

---

## Dependencies

**Required:**
- Playwright (browser automation)
- Python 3.9+
- Telegram bot (Hermes has credentials)

**Optional:**
- BeautifulSoup (HTML parsing fallback)

---

## Workflow

See [workflow.md](workflow.md) for detailed 10-phase process.

**Quick summary:**
1. Load last run timestamp
2. Launch browser → thefeed.today
3. Extract Crypto filter (scroll & extract)
4. Extract Tech filter (scroll & extract)
5. Merge & dedup vs timestamp
6. Prioritize (3-tier, both categories)
7. Synthesize brief (separate narratives)
8. Deliver to Telegram
9. Update timestamp

---

## Quality Standards

Before delivering brief, verify:

**Content:**
- [ ] All items newer than last run
- [ ] Breaking news included (if any, both categories)
- [ ] Top stories flexible mix (highest priority)
- [ ] Đáng đọc split 50/50 (Crypto 3-5, Tech 3-5)
- [ ] Narrative pulse separate (Crypto + Tech)
- [ ] TL;DR covers both categories

**Format:**
- [ ] Session icon correct (☀️🌤🌙)
- [ ] Date/day correct
- [ ] Sections clearly separated (Crypto / Tech)
- [ ] All links working
- [ ] Markdown formatted properly
- [ ] CT voice appropriate (minimal slang)

**Delivery:**
- [ ] Telegram message sent successfully
- [ ] Timestamp updated
- [ ] No errors logged

---

## Escalation

Escalate to Julius when:
- thefeed.today structure changes (extraction breaks)
- Consistent delivery failures (3+ runs)
- Unclear how to prioritize (all items low engagement)
- Narrative pulse unclear (no obvious trend)
- Category imbalance extreme (e.g., 0 crypto items)

---

## References

- [workflow.md](workflow.md) — Detailed 10-phase process
- [output-template.md](output-template.md) — Template with examples
- [examples.md](examples.md) — Sample briefs (3 sessions)
- [references/thefeed-guide.md](references/thefeed-guide.md) — Using thefeed.today
- [references/prioritization.md](references/prioritization.md) — 3-tier logic details

---

**Maintainer:** Julius  
**Last updated:** 2026-05-19