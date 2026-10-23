# Workflow — X News Brief

10-phase workflow for automated crypto + tech news briefing from thefeed.today.

---

## Phase 1: Initialization

### Step 1.1: Load last run state

Read timestamp from:
```
.state/last-run-timestamp.txt
```

**If file exists:**
```python
with open('.state/last-run-timestamp.txt', 'r') as f:
    last_timestamp = datetime.fromisoformat(f.read().strip())
```

**If file doesn't exist (first run):**
```python
last_timestamp = datetime.now(timezone.utc) - timedelta(hours=24)
# Create .state/ directory
os.makedirs('.state', exist_ok=True)
```

### Step 1.2: Determine session

Based on current time (ICT):

```python
from datetime import datetime
import pytz

ict = pytz.timezone('Asia/Bangkok')
now = datetime.now(ict)
hour = now.hour

if hour == 7:
    session_icon = "☀️"
elif hour == 13:
    session_icon = "🌤"
elif hour == 21:
    session_icon = "🌙"
else:
    # Shouldn't happen (cron-triggered)
    session_icon = "🌤"  # Default
```

### Step 1.3: Initialize data structures

```python
crypto_items = []
tech_items = []
all_items = []
```

---

## Phase 2: Browser Launch

### Step 2.1: Launch Playwright

```python
from playwright.sync_api import sync_playwright

playwright = sync_playwright().start()
browser = playwright.chromium.launch(
    headless=True,
    args=['--no-sandbox', '--disable-setuid-sandbox']
)
context = browser.new_context(
    viewport={'width': 1920, 'height': 1080},
    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
)
page = context.new_page()
```

### Step 2.2: Navigate to thefeed.today

```python
try:
    page.goto("https://thefeed.today/", timeout=30000)
    page.wait_for_load_state("networkidle")
except Exception as e:
    # Error handling: retry once
    time.sleep(30)
    page.goto("https://thefeed.today/", timeout=30000)
    page.wait_for_load_state("networkidle")
```

---

## Phase 3: Crypto Extraction

### Step 3.1: Click "Crypto" filter

```python
try:
    # Wait for page load
    page.wait_for_selector('[data-testid="feed-item"]', timeout=10000)
    
    # Click Crypto filter
    crypto_button = page.locator('button:has-text("Crypto")')
    crypto_button.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")
except Exception as e:
    print(f"Crypto filter failed: {e}")
    # Continue to Tech (don't fail entire run)
```

### Step 3.2: Scroll and extract Crypto items

```python
# Scroll 3 times to load ~20 items
for i in range(3):
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000)

# Extract items
crypto_items = extract_items(page, category='Crypto')
print(f"Extracted {len(crypto_items)} crypto items")
```

---

## Phase 4: Tech Extraction

### Step 4.1: Reload page for Tech filter

```python
# Reload to reset filters
page.goto("https://thefeed.today/", timeout=30000)
page.wait_for_load_state("networkidle")
```

### Step 4.2: Click "Tech" filter

```python
try:
    # Wait for page load
    page.wait_for_selector('[data-testid="feed-item"]', timeout=10000)
    
    # Click Tech filter
    tech_button = page.locator('button:has-text("Tech")')
    tech_button.click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")
except Exception as e:
    print(f"Tech filter failed: {e}")
    # Continue with Crypto only
```

### Step 4.3: Scroll and extract Tech items

```python
# Scroll 3 times to load ~20 items
for i in range(3):
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000)

# Extract items
tech_items = extract_items(page, category='Tech')
print(f"Extracted {len(tech_items)} tech items")
```

---

## Phase 5: Item Extraction (Helper Function)

### Step 5.1: Extract items function

```python
def extract_items(page, category):
    """Extract items from current page with category tag"""
    items = []
    
    # Adjust selectors based on actual thefeed.today HTML
    feed_items = page.locator('[data-testid="feed-item"]').all()
    
    for item in feed_items[:20]:  # Top 20 items
        try:
            # Extract data
            title = item.locator('.item-title').text_content().strip()
            summary = item.locator('.item-summary').text_content().strip()
            views_text = item.locator('.views-count').text_content().strip()
            link = item.locator('a.item-link').get_attribute('href')
            timestamp_text = item.locator('.timestamp').text_content().strip()
            
            # Parse views (e.g., "1.2M" → 1200000)
            views = parse_views(views_text)
            
            # Parse timestamp
            item_timestamp = parse_timestamp(timestamp_text)
            
            # Check for breaking tag
            breaking = 'Breaking' in item.text_content()
            
            # Calculate engagement rate if available
            likes_text = item.locator('.likes-count').text_content().strip()
            likes = parse_number(likes_text)
            engagement_rate = (likes / views * 100) if views > 0 else 0
            
            items.append({
                'title': title,
                'summary': summary,
                'views': views,
                'likes': likes,
                'engagement_rate': engagement_rate,
                'link': link,
                'timestamp': item_timestamp,
                'breaking': breaking,
                'category': category  # Tag with category
            })
        except Exception as e:
            # Skip malformed items
            continue
    
    return items
```

### Step 5.2: Helper functions

```python
def parse_views(text):
    """Parse views like '1.2M' → 1200000"""
    text = text.replace(',', '').strip()
    if 'M' in text:
        return int(float(text.replace('M', '')) * 1_000_000)
    elif 'K' in text:
        return int(float(text.replace('K', '')) * 1_000)
    else:
        return int(text)

def parse_number(text):
    """Parse number like '12.5K' → 12500"""
    text = text.replace(',', '').strip()
    if 'K' in text:
        return int(float(text.replace('K', '')) * 1_000)
    else:
        return int(text)

def parse_timestamp(text):
    """Parse relative time like '2h ago' → datetime"""
    now = datetime.now(timezone.utc)
    
    if 'just now' in text.lower():
        return now
    elif 'h ago' in text:
        hours = int(text.split('h')[0].strip())
        return now - timedelta(hours=hours)
    elif 'd ago' in text:
        days = int(text.split('d')[0].strip())
        return now - timedelta(days=days)
    elif 'm ago' in text:
        minutes = int(text.split('m')[0].strip())
        return now - timedelta(minutes=minutes)
    else:
        # Fallback: assume recent
        return now
```

---

## Phase 6: Merge & Deduplication

### Step 6.1: Merge both categories

```python
all_items = crypto_items + tech_items
print(f"Total items before dedup: {len(all_items)}")
```

### Step 6.2: Deduplicate by link

```python
# Remove duplicates (same item in both Crypto and Tech)
seen_links = set()
unique_items = []

for item in all_items:
    if item['link'] not in seen_links:
        seen_links.add(item['link'])
        unique_items.append(item)

all_items = unique_items
print(f"Total items after dedup: {len(all_items)}")
```

### Step 6.3: Filter by timestamp

```python
new_items = [
    item for item in all_items
    if item['timestamp'] > last_timestamp
]

print(f"New items since last run: {len(new_items)}")
```

### Step 6.4: Handle no new items

```python
if len(new_items) == 0:
    # Send "no new news" message
    message = f"""
✖️ X News Brief {session_icon} — {now.strftime('%A, %d %B %Y')}

No new crypto/tech news since last check ({last_timestamp.strftime('%H:%M %p')}).

Last item: {last_timestamp.strftime('%Y-%m-%d %H:%M:%S ICT')}
"""
    send_telegram(message)
    browser.close()
    playwright.stop()
    return
```

### Step 6.5: Sort by timestamp (newest first)

```python
new_items.sort(key=lambda x: x['timestamp'], reverse=True)
```

---

## Phase 7: Prioritization

### Step 7.1: Separate by category

```python
new_crypto = [item for item in new_items if item['category'] == 'Crypto']
new_tech = [item for item in new_items if item['category'] == 'Tech']

print(f"New crypto: {len(new_crypto)}, New tech: {len(new_tech)}")
```

### Step 7.2: Apply 3-tier priority to each category

```python
def prioritize_items(items):
    """Apply 3-tier priority to items"""
    breaking = [item for item in items if item['breaking']]
    
    high_engagement = [
        item for item in items
        if item['views'] > 5000 and item['engagement_rate'] > 5.0
    ]
    high_engagement.sort(key=lambda x: x['views'], reverse=True)
    
    narrative = [
        item for item in items
        if item not in breaking and item not in high_engagement
    ]
    narrative.sort(key=lambda x: x['engagement_rate'], reverse=True)
    
    return {
        'breaking': breaking,
        'high_engagement': high_engagement,
        'narrative': narrative
    }

crypto_priority = prioritize_items(new_crypto)
tech_priority = prioritize_items(new_tech)
```

### Step 7.3: Select top stories (2-5, flexible mix)

```python
top_stories = []

# Add all breaking from both categories
top_stories.extend(crypto_priority['breaking'])
top_stories.extend(tech_priority['breaking'])

# Fill remaining slots with highest engagement (regardless of category)
all_high_engagement = (
    crypto_priority['high_engagement'] + 
    tech_priority['high_engagement']
)
all_high_engagement.sort(key=lambda x: x['views'], reverse=True)

remaining_slots = 5 - len(top_stories)
if remaining_slots > 0:
    top_stories.extend(all_high_engagement[:remaining_slots])

# Ensure at least 2 stories
if len(top_stories) < 2:
    all_narrative = crypto_priority['narrative'] + tech_priority['narrative']
    all_narrative.sort(key=lambda x: x['engagement_rate'], reverse=True)
    top_stories.extend(all_narrative[:2 - len(top_stories)])

print(f"Top stories: {len(top_stories)}")
```

### Step 7.4: Select đáng đọc (7-10, 50/50 split)

```python
# Crypto đáng đọc (3-5 items)
crypto_dang_doc = []
crypto_dang_doc.extend([
    item for item in crypto_priority['high_engagement']
    if item not in top_stories
][:3])
crypto_dang_doc.extend(crypto_priority['narrative'][:2])
crypto_dang_doc = crypto_dang_doc[:5]  # Max 5

# Tech đáng đọc (3-5 items)
tech_dang_doc = []
tech_dang_doc.extend([
    item for item in tech_priority['high_engagement']
    if item not in top_stories
][:3])
tech_dang_doc.extend(tech_priority['narrative'][:2])
tech_dang_doc = tech_dang_doc[:5]  # Max 5

# Ensure total is 7-10
total_dang_doc = len(crypto_dang_doc) + len(tech_dang_doc)
if total_dang_doc < 7:
    # Add more from narrative
    needed = 7 - total_dang_doc
    extra_crypto = crypto_priority['narrative'][2:2 + needed // 2]
    extra_tech = tech_priority['narrative'][2:2 + (needed - len(extra_crypto))]
    crypto_dang_doc.extend(extra_crypto)
    tech_dang_doc.extend(extra_tech)

print(f"Đáng đọc - Crypto: {len(crypto_dang_doc)}, Tech: {len(tech_dang_doc)}")
```

---

## Phase 8: Narrative Synthesis

### Step 8.1: Synthesize crypto narrative

```python
crypto_narrative = synthesize_narrative(
    new_crypto,
    crypto_priority,
    category='Crypto'
)
```

### Step 8.2: Synthesize tech narrative

```python
tech_narrative = synthesize_narrative(
    new_tech,
    tech_priority,
    category='Tech'
)
```

### Step 8.3: Narrative synthesis function

```python
def synthesize_narrative(items, priority, category):
    """
    Synthesize 1-2 sentences about category narrative.
    
    Args:
        items: All new items in category
        priority: Prioritized items dict
        category: 'Crypto' or 'Tech'
    
    Returns:
        str: 1-2 sentences narrative
    """
    if len(items) == 0:
        return f"No major {category.lower()} developments this session."
    
    # Extract topics
    topics = extract_topics(items)
    
    # Identify dominant theme
    dominant = topics[0] if topics else "general updates"
    
    # Count breaking
    breaking_count = len(priority['breaking'])
    
    # Construct narrative
    if breaking_count > 0:
        narrative = f"{breaking_count} breaking {category.lower()} stories. "
    else:
        narrative = ""
    
    narrative += f"{dominant.capitalize()} dominates discussion with {len([i for i in items if dominant.lower() in i['title'].lower()])} mentions."
    
    return narrative

def extract_topics(items):
    """Extract top topics from items"""
    # Simple keyword extraction
    keywords = {}
    for item in items:
        words = item['title'].lower().split()
        for word in words:
            if len(word) > 4:  # Skip short words
                keywords[word] = keywords.get(word, 0) + 1
    
    # Sort by frequency
    sorted_topics = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
    return [topic for topic, count in sorted_topics[:3]]
```

### Step 8.4: Write TL;DR

```python
# 1-line summary covering both categories
crypto_count = len(new_crypto)
tech_count = len(new_tech)
breaking_total = len(crypto_priority['breaking']) + len(tech_priority['breaking'])

tldr = f"{breaking_total} breaking, {crypto_count} crypto + {tech_count} tech updates. {crypto_narrative.split('.')[0]}. {tech_narrative.split('.')[0]}."
```

---

## Phase 9: Format & Deliver

### Step 9.1: Format message

```python
message = f"""
✖️ X News Brief {session_icon} — {now.strftime('%A, %d %B %Y')}

🔥 Top {len(top_stories)} stories
"""

for story in top_stories:
    message += f"• {story['title']} — {story['summary']} ({format_views(story['views'])})\n"

message += f"""

🧠 Narrative pulse
Crypto: {crypto_narrative}
Tech: {tech_narrative}

📌 Đáng đọc ({len(crypto_dang_doc) + len(tech_dang_doc)} items)

Crypto:
"""

for item in crypto_dang_doc:
    message += f"• {item['title']} — {explain_why_interesting(item)} [Link]({item['link']})\n"

message += "\nTech:\n"

for item in tech_dang_doc:
    message += f"• {item['title']} — {explain_why_interesting(item)} [Link]({item['link']})\n"

message += f"""

TL;DR: {tldr}
"""
```

### Step 9.2: Helper functions

```python
def format_views(views):
    """Format views: 1200000 → '1.2M'"""
    if views >= 1_000_000:
        return f"{views / 1_000_000:.1f}M"
    elif views >= 1_000:
        return f"{views / 1_000:.1f}K"
    else:
        return str(views)

def explain_why_interesting(item):
    """Generate 1-line why this item is interesting"""
    if item['breaking']:
        return "Breaking news"
    elif item['engagement_rate'] > 10:
        return f"High engagement ({item['engagement_rate']:.1f}%)"
    elif item['views'] > 100000:
        return "Viral momentum"
    else:
        return "Emerging topic"
```

### Step 9.3: Send to Telegram

```python
# Hermes has Telegram credentials configured
send_telegram(message)
print(f"Brief delivered successfully at {now.isoformat()}")
```

---

## Phase 10: State Update & Cleanup

### Step 10.1: Update timestamp

```python
# Get timestamp of newest item
newest_timestamp = new_items[0]['timestamp']

# Write to state file
with open('.state/last-run-timestamp.txt', 'w') as f:
    f.write(newest_timestamp.isoformat())

print(f"Timestamp updated: {newest_timestamp.isoformat()}")
```

### Step 10.2: Cleanup

```python
# Close browser
browser.close()
playwright.stop()
```

### Step 10.3: Log completion

```python
print(f"""
[{now.isoformat()}] X News Brief {session_icon} completed
  - Total new items: {len(new_items)}
  - Crypto: {len(new_crypto)} ({len(crypto_priority['breaking'])} breaking)
  - Tech: {len(new_tech)} ({len(tech_priority['breaking'])} breaking)
  - Top stories: {len(top_stories)}
  - Đáng đọc: {len(crypto_dang_doc)} crypto + {len(tech_dang_doc)} tech
""")
```

---

## Error Handling

### Retry Logic

```python
def run_with_retry(func, max_retries=1):
    """Retry function once on failure"""
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries:
                # Final failure
                send_error_notification(e)
                raise
            else:
                # Retry after delay
                print(f"Attempt {attempt + 1} failed, retrying in 30s...")
                time.sleep(30)
```

### Error Notification

```python
def send_error_notification(error):
    """Send error to Julius via Telegram"""
    message = f"""
⚠️ X News Brief Error

Session: {session_icon}
Time: {datetime.now().isoformat()}
Error: {str(error)}

Will retry on next cron run.
"""
    send_telegram(message)
```

### Partial Failure Handling

```python
# If one category fails, continue with the other
if len(crypto_items) == 0 and len(tech_items) > 0:
    message_prefix = "⚠️ Crypto news unavailable this run.\n\n"
elif len(tech_items) == 0 and len(crypto_items) > 0:
    message_prefix = "⚠️ Tech news unavailable this run.\n\n"
else:
    message_prefix = ""

# Prepend to final message
message = message_prefix + message
```

---

**Last updated:** 2026-05-19