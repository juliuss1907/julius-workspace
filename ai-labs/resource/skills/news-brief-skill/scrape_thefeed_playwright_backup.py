# scrape_thefeed.py
from playwright.sync_api import sync_playwright
from datetime import datetime, timezone, timedelta
from config_helpers import get_all_sources_by_type, passes_quality_filters
import json
import time


def parse_number(text):
    """Parse '1.2M' -> 1200000"""
    if not text:
        return 0
    text = text.replace(',', '').strip()
    try:
        if 'M' in text:
            return int(float(text.replace('M', '')) * 1_000_000)
        elif 'K' in text:
            return int(float(text.replace('K', '')) * 1_000)
        else:
            return int(text)
    except:
        return 0


def parse_relative_time(text):
    """Parse '2h ago' -> datetime"""
    now = datetime.now(timezone.utc)
    if not text:
        return now

    text = text.lower().strip()
    try:
        if 'h ago' in text:
            hours = int(text.split('h')[0].strip())
            return now - timedelta(hours=hours)
        elif 'd ago' in text:
            days = int(text.split('d')[0].strip())
            return now - timedelta(days=days)
        elif 'm ago' in text:
            minutes = int(text.split('m')[0].strip())
            return now - timedelta(minutes=minutes)
        else:
            return now
    except:
        return now


def extract_category_items_for_topic(page, filter_name, topic_id, source_config):
    """Extract items from thefeed.today for a specific topic"""
    settings = source_config['settings']

    print(f"  Extracting {filter_name} for {source_config['topic_name']}...")

    # Click category filter
    page.evaluate(f"""
    document.querySelectorAll('button').forEach(b => {{
        if (b.textContent.trim() === '{filter_name}') b.click();
    }});
    """)

    time.sleep(3)

    # Extract via browser_console
    max_items = settings.get('max_items', 25)
    js_code = f"""
    new Promise(r => setTimeout(r, 1000)).then(() => {{
        const rows = document.querySelectorAll('tbody tr');
        return JSON.stringify([...rows].slice(0, {max_items}).map(row => {{
            const cells = row.querySelectorAll('td');
            if (cells.length < 6) return null;
            const links = row.querySelectorAll('a');
            const xLink = [...links].find(a => a.href && a.href.includes('x.com'));
            return {{
                summary: cells[2]?.textContent?.trim() || '',
                category: cells[3]?.textContent?.trim() || '',
                posted: cells[4]?.textContent?.trim() || '',
                likes: cells[5]?.textContent?.trim() || '',
                views: cells[6]?.textContent?.trim() || '',
                delta_1h: cells[7]?.textContent?.trim() || '',
                delta_pct: cells[8]?.textContent?.trim() || '',
                link: xLink?.href || ''
            }};
        }}).filter(Boolean));
    }})
    """

    try:
        result = page.evaluate(js_code)
        raw_items = json.loads(result)
    except Exception as e:
        print(f"    Error extracting: {e}")
        return []

    # Parse and normalize
    topic_name = source_config['topic_name']
    items = []
    for raw in raw_items:
        views = parse_number(raw['views'])
        likes = parse_number(raw['likes'])
        engagement_rate = (likes / views * 100) if views > 0 else 0.0
        timestamp = parse_relative_time(raw['posted'])
        breaking = raw['category'].lower() == 'breaking'

        item = {
            'title': raw['summary'][:100],
            'summary': raw['summary'][:300],
            'link': raw['link'],
            'source': 'website',
            'source_name': 'thefeed',
            'source_display_name': source_config['name'],
            'source_priority': source_config['priority'],
            'source_type': source_config['type'],
            'topic_id': topic_id,
            'topic_name': topic_name,
            'category': topic_name,  # Backward compatibility
            'timestamp': timestamp,
            'engagement': {
                'type': 'views',
                'value': views
            },
            'engagement_rate': engagement_rate,
            'breaking': breaking
        }

        if passes_quality_filters(item):
            items.append(item)

    print(f"    Extracted {len(items)} items")
    return items


def scrape_thefeed():
    """Scrape thefeed.today for all enabled topics"""
    # Get all thefeed sources across topics
    thefeed_sources = [
        (topic_id, source)
        for topic_id, source in get_all_sources_by_type('websites')
        if source.get('scraper') == 'thefeed'
    ]

    if not thefeed_sources:
        print("thefeed.today is disabled in config")
        return []

    print("Scraping thefeed.today...")

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()

    all_items = []

    try:
        # Navigate once
        page.goto("https://thefeed.today/", timeout=30000)
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # Extract for each topic's filter
        for topic_id, source in thefeed_sources:
            settings = source['settings']
            filter_name = settings['filter']

            items = extract_category_items_for_topic(
                page,
                filter_name,
                topic_id,
                source
            )
            all_items.extend(items)

    except Exception as e:
        print(f"  Error: {e}")

    finally:
        browser.close()
        playwright.stop()

    print(f"Total thefeed items: {len(all_items)}")
    return all_items
