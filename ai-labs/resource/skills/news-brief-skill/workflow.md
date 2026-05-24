# Workflow — News Brief Skill v2.0

Detailed workflow documentation for multi-topic news aggregation system.

---

## Overview

The workflow consists of two main phases:

1. **Scrape Phase** — Collect news from all sources
2. **Synthesize Phase** — Prioritize, select, format, and deliver

Each phase runs independently via cron jobs.

---

## Phase 1: Scrape Phase

**Trigger:** Cron at 06:50, 12:50, 20:50 ICT
**Duration:** ~1-2 minutes
**Output:** `.state/raw-YYYY-MM-DD_HHmm.json`

### Step 1.1: Initialize

```python
# scrape.py

# Load enabled topics
enabled_topics = get_enabled_topics()

# Print summary
for topic_id, topic in enabled_topics.items():
    print(f"{topic['icon']} {topic['display_name']}")
    print(f"  Telegram: {count_sources(topic, 'telegram')}")
    print(f"  Websites: {count_sources(topic, 'websites')}")
    print(f"  RSS: {count_sources(topic, 'rss')}")
```

### Step 1.2: Scrape Telegram

```python
# scrape_telegram.py

# For each enabled topic
for topic_id, topic in enabled_topics.items():
    telegram_channels = topic['sources']['telegram']
    
    for channel in telegram_channels:
        if not channel['enabled']:
            continue
        
        entity = await client.get_entity(channel['username'])
        
        async for message in client.iter_messages(entity, limit=50):
            item = {
                'title': message.text[:100],
                'summary': message.text[:300],
                'link': f"https://t.me/{channel['username']}/{message.id}",
                'source': 'telegram',
                'topic_id': topic_id,
                'topic_name': topic['display_name'],
                'timestamp': message.date,
                'engagement': {'type': 'views', 'value': message.views},
            }
            
            if passes_quality_filters(item):
                items.append(item)
```

### Step 1.3: Scrape Websites

```python
# scrape_thefeed.py

# For each enabled topic with thefeed source
for topic_id, source in thefeed_sources:
    filter_name = source['settings']['filter']
    
    # Navigate and click filter
    page.goto("https://thefeed.today/")
    page.click(f"button:has-text('{filter_name}')")
    
    # Extract items with topic tracking
    items = extract_items(page, topic_id, source['topic_name'])
```

### Step 1.4: Scrape RSS

```python
# scrape_rss.py

# For each enabled topic
for topic_id, sources in by_topic.items():
    for feed in sources:
        parsed = feedparser.parse(feed['url'])
        
        for entry in parsed.entries:
            item = {
                'title': entry.title,
                'summary': clean_html(entry.summary),
                'link': entry.link,
                'source': 'rss',
                'topic_id': topic_id,
                'topic_name': topic_name,
                'timestamp': parse_timestamp(entry),
                'engagement': {'type': 'authority', 'value': 0},
            }
            items.append(item)
```

### Step 1.5: Merge and Dedup

```python
# merge.py

# Combine all sources
all_items = telegram_items + website_items + rss_items

# Sort by source priority
sorted_items = sorted(all_items, key=get_source_priority_score, reverse=True)

# Deduplicate by URL similarity
unique_items = deduplicate(sorted_items)

# Filter by 24h window
recent_items = filter_by_time_window(unique_items, hours=24)

# Sort by timestamp (newest first)
final_items = sorted(recent_items, key=lambda x: x['timestamp'], reverse=True)
```

### Step 1.6: Save JSON

```python
# scrape.py

data = {
    'scraped_at': datetime.now(timezone.utc).isoformat(),
    'total_items': len(final_items),
    'topic_counts': {topic_id: count for ...},
    'sources': {source: count for ...},
    'items': final_items
}

# Atomic write
save_json(final_items, f".state/raw-{timestamp}.json")
```

---

## Phase 2: Synthesize Phase

**Trigger:** Cron at 07:00, 13:00, 21:00 ICT
**Duration:** ~10-20 seconds
**Output:** Telegram message + Markdown file

### Step 2.1: Load JSON

```python
# synthesize.py

# Find latest JSON
json_file = find_latest_json()

# Check freshness (< 15 min old)
is_fresh, msg = check_json_freshness(json_file, 15)

# Load data
data = load_json(json_file)
items = data['items']
```

### Step 2.2: Prioritize Items

```python
# prioritize.py

for item in items:
    # 1. Keyword score (0-100) — per-topic keywords
    keyword_score = calculate_keyword_score(item)
    
    # 2. Engagement score (0-50)
    engagement_score = calculate_engagement_score(item)
    
    # 3. Source bonus (0-15)
    source_bonus = calculate_source_bonus(item)
    
    # 4. Recency bonus (0-10)
    recency_bonus = calculate_recency_bonus(item)
    
    # 5. Total
    total = keyword_score + engagement_score + source_bonus + recency_bonus
    
    item['priority'] = {
        'total_score': total,
        'keyword_score': keyword_score,
        'engagement_score': engagement_score,
        'source_bonus': source_bonus,
        'recency_bonus': recency_bonus,
    }

# Sort by total score
items.sort(key=lambda x: x['priority']['total_score'], reverse=True)
```

### Step 2.3: Select Stories

```python
# prioritize.py

# 1. Top Stories (cross-topic, highest priority)
top_stories = select_top_stories(items)  # 2-5 items

# 2. Worth Reading (per topic)
for topic_id, topic in enabled_topics.items():
    topic_items = [i for i in items if i['topic_id'] == topic_id]
    worth_reading = select_worth_reading_for_topic(
        topic_items, top_stories, topic['selection']['worth_reading']
    )
    result[f'{topic_id}_worth_reading'] = worth_reading
```

### Step 2.4: Format Brief

```python
# format.py

# Header with session icon
brief = f"{session_icon} *NEWS BRIEF — {session_name.upper()}*\n"

# Top Stories section
brief += "🔥 *TOP STORIES*\n"
for story in top_stories:
    brief += format_top_story(story)

# Per-topic Worth Reading sections
for topic_id, topic in enabled_topics.items():
    brief += f"{topic['icon']} *{topic['display_name'].upper()} — DANG DOC*\n"
    for story in worth_reading[topic_id]:
        brief += format_short_story(story)

# Footer
brief += f"Generated by Hermes · {total_items} items"
```

### Step 2.5: Deliver

```python
# synthesize.py

# 1. Save Markdown
if OUTPUT_SETTINGS['markdown']['enabled']:
    md_success, md_path = save_markdown(brief, scraped_at)

# 2. Send Telegram
if OUTPUT_SETTINGS['telegram']['enabled']:
    telegram_success = send_to_telegram(brief)

# 3. Update state
with open('.state/last-run-timestamp.txt', 'w') as f:
    f.write(datetime.now(timezone.utc).isoformat())
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│ TOPICS CONFIG                                       │
│ ├─ crypto (telegram, websites, rss, keywords)       │
│ ├─ tech (telegram, websites, rss, keywords)         │
│ └─ ai_safety (...)                                  │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ SCRAPE PHASE                                        │
│                                                     │
│ Telegram (95 items)                                 │
│ ├─ crypto: 60 items                                 │
│ ├─ tech: 30 items                                   │
│ └─ ai_safety: 5 items                               │
│                                                     │
│ Websites (50 items)                                 │
│ ├─ crypto: 25 items                                 │
│ └─ tech: 25 items                                   │
│                                                     │
│ RSS (45 items)                                      │
│ ├─ crypto: 27 items                                 │
│ └─ tech: 18 items                                   │
│                                                     │
│ Total: 190 items                                    │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ MERGE & DEDUP                                       │
│ • Remove duplicates by URL similarity               │
│ • Priority: Telegram > RSS > Websites               │
│ • 190 → 165 items (25 duplicates)                   │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ TIME FILTER (24h window)                            │
│ • 165 → 120 items (45 too old)                      │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ SAVE JSON                                           │
│ .state/raw-2026-05-23_0650.json                     │
│ • 120 items                                         │
│ • crypto: 65, tech: 50, ai_safety: 5                │
└──────────────┬──────────────────────────────────────┘
               │
               ▼ (10 minutes later)
┌─────────────────────────────────────────────────────┐
│ SYNTHESIZE PHASE                                    │
│                                                     │
│ PRIORITIZE                                          │
│ ├─ Calculate scores (keyword + engagement + ...)    │
│ └─ Sort by total score                              │
│                                                     │
│ SELECT                                              │
│ ├─ Top stories: 5 items (cross-topic)               │
│ ├─ crypto_worth_reading: 5 items                    │
│ ├─ tech_worth_reading: 5 items                      │
│ └─ ai_safety_worth_reading: 2 items                 │
│                                                     │
│ FORMAT                                              │
│ ├─ Vietnamese language                              │
│ ├─ Markdown formatting                              │
│ └─ Session icon                                     │
│                                                     │
│ DELIVER                                             │
│ ├─ Save Markdown file                               │
│ └─ Send Telegram message                            │
└─────────────────────────────────────────────────────┘
```

---

## Error Handling

### Scrape Phase Errors

**Telegram connection failure:**
- Log error, continue with other sources
- Other scrapers still run independently

**Website scraping timeout:**
- 30s timeout per page load
- Skip source on failure, continue

**RSS feed parse error:**
- Log warning for malformed feeds
- Skip individual feed, continue with others

### Synthesize Phase Errors

**JSON file missing:**
- Send error notification via Telegram
- Exit with failure code

**JSON file stale (>15 min old):**
- Log warning, continue anyway
- Brief still generated from available data

**Telegram delivery failure:**
- Markdown still saved successfully
- Error notification sent if possible

---

## Monitoring

### Health Checks

```bash
# Check last scrape time
stat .state/raw-*.json | tail -1

# Check last synthesize time
cat .state/last-run-timestamp.txt

# Check logs for errors
grep "Error" logs/scrape.log
grep "Error" logs/synthesize.log
```

### Metrics to Track

- **Scrape success rate:** % of sources that returned items
- **Dedup rate:** % of items removed as duplicates
- **Selection rate:** % of items that made it to brief
- **Delivery success:** Telegram + Markdown success rate

---

## Maintenance Tasks

### Daily
- Check logs for errors
- Verify briefs delivered on time

### Weekly
- Review topic performance (items per topic)
- Adjust keywords based on quality
- Check source health (channels still active?)

### Monthly
- Cleanup old JSON files (>30 days)
- Review and update source list
- Tune prioritization weights
- Archive old briefs

---

**Last updated:** 2026-05-23
