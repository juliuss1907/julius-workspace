# scrape_rss.py
import feedparser
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from config import GLOBAL_SETTINGS
from config_helpers import get_all_sources_by_type, passes_quality_filters
import time
import re
import html


def parse_rss_timestamp(entry):
    """
    Parse timestamp from RSS entry

    RSS feeds use different timestamp fields:
    - published_parsed
    - updated_parsed
    - created_parsed
    """
    # Try different timestamp fields
    for field in ['published_parsed', 'updated_parsed', 'created_parsed']:
        if hasattr(entry, field):
            time_struct = getattr(entry, field)
            if time_struct:
                try:
                    return datetime(*time_struct[:6], tzinfo=timezone.utc)
                except:
                    pass

    # Fallback: current time
    return datetime.now(timezone.utc)


def extract_summary(entry):
    """
    Extract summary from RSS entry

    Different feeds use different fields:
    - summary
    - description
    - content
    """
    # Try summary first
    if hasattr(entry, 'summary') and entry.summary:
        return entry.summary

    # Try description
    if hasattr(entry, 'description') and entry.description:
        return entry.description

    # Try content
    if hasattr(entry, 'content') and entry.content:
        # content is usually a list of dicts
        if isinstance(entry.content, list) and len(entry.content) > 0:
            return entry.content[0].get('value', '')

    # Fallback: empty
    return ''


def clean_html(text):
    """Remove HTML tags from text"""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entities
    text = html.unescape(text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text


def scrape_rss_feed_for_topic(feed_config, topic_id, topic_name, cutoff_time):
    """
    Scrape items from an RSS feed for a specific topic

    Args:
        feed_config: Feed dict from config
        topic_id: Topic ID
        topic_name: Topic display name
        cutoff_time: Only get items after this time

    Returns:
        List of items
    """
    feed_name = feed_config['name']
    feed_url = feed_config['url']
    settings = GLOBAL_SETTINGS['rss']

    items = []

    try:
        print(f"  {feed_name}: Fetching...")

        # Parse RSS feed
        feed = feedparser.parse(feed_url)

        # Check for errors
        if feed.bozo:
            # bozo = 1 means malformed feed, but might still be usable
            if hasattr(feed, 'bozo_exception'):
                print(f"    Warning: {feed.bozo_exception}")

        # Get entries
        entries = feed.entries[:settings['max_items_per_feed']]

        for entry in entries:
            # Extract fields
            title = entry.get('title', '').strip()
            if not title:
                continue

            link = entry.get('link', '').strip()
            if not link:
                continue

            # Extract and clean summary
            summary = extract_summary(entry)
            summary = clean_html(summary)

            # Parse timestamp
            timestamp = parse_rss_timestamp(entry)

            # Filter by time window
            if timestamp < cutoff_time:
                continue

            # Build item
            item = {
                'title': title[:100],
                'summary': summary[:300],
                'link': link,
                'source': 'rss',
                'source_name': feed_name.lower().replace(' ', '_'),
                'source_display_name': feed_name,
                'source_priority': feed_config['priority'],
                'source_type': 'news',  # RSS feeds are typically news
                'topic_id': topic_id,
                'topic_name': topic_name,
                'category': topic_name,  # Backward compatibility
                'timestamp': timestamp,
                'engagement': {
                    'type': 'authority',  # RSS doesn't have views
                    'value': 0
                },
                'breaking': False,
            }

            # Quality filter
            if passes_quality_filters(item):
                items.append(item)

        print(f"    {feed_name}: {len(items)} items")

    except Exception as e:
        print(f"    {feed_name}: Error - {e}")

    return items


def scrape_all_rss():
    """Scrape all enabled RSS feeds across all topics"""
    print("Scraping RSS feeds...")

    settings = GLOBAL_SETTINGS['rss']
    cutoff = datetime.now(timezone.utc) - timedelta(hours=settings['time_window_hours'])

    # Get all RSS sources with topic info
    rss_sources = get_all_sources_by_type('rss')

    if not rss_sources:
        print("  No RSS feeds enabled")
        return []

    all_items = []

    # Group by topic for display
    by_topic = defaultdict(list)
    for topic_id, source in rss_sources:
        by_topic[topic_id].append(source)

    # Scrape each topic
    for topic_id, sources in by_topic.items():
        topic_name = sources[0]['topic_name']
        topic_icon = sources[0].get('topic_icon', '📰')
        print(f"{topic_icon} {topic_name} RSS feeds ({len(sources)}):")

        for source in sources:
            items = scrape_rss_feed_for_topic(source, topic_id, topic_name, cutoff)
            all_items.extend(items)
            time.sleep(0.5)  # Be nice to servers

    print(f"Total RSS items: {len(all_items)}")
    return all_items


def scrape_rss():
    """Sync wrapper"""
    return scrape_all_rss()
