#!/usr/bin/env python3
"""
test_scrape.py - Test scraper without Telegram dependencies
"""

from scrape_thefeed import scrape_thefeed
from scrape_rss import scrape_rss
from merge import merge_and_dedup_multi, filter_by_time_window, sort_by_timestamp
from datetime import datetime, timezone
from config import STATE_DIR, TIME_WINDOW_HOURS
import json
import os


def test_scrape():
    """Test scrape thefeed + RSS without Telegram"""
    print("=" * 60)
    print(f"Test News Scraper — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    all_items = []
    source_stats = {}
    
    # 1. thefeed.today
    print("\n" + "=" * 60)
    print("Scraping thefeed.today...")
    try:
        thefeed_items = scrape_thefeed()
        all_items.extend(thefeed_items)
        source_stats['thefeed'] = len(thefeed_items)
        print(f"  ✓ Got {len(thefeed_items)} items")
    except Exception as e:
        print(f"  ✗ thefeed error: {e}")
        source_stats['thefeed'] = 0
    
    # 2. RSS feeds
    print("\n" + "=" * 60)
    print("Scraping RSS feeds...")
    try:
        rss_items = scrape_rss()
        all_items.extend(rss_items)
        source_stats['rss'] = len(rss_items)
        print(f"  ✓ Got {len(rss_items)} items")
    except Exception as e:
        print(f"  ✗ RSS error: {e}")
        source_stats['rss'] = 0
    
    if not all_items:
        print("\nNo items scraped")
        return
    
    # 3. Merge and dedup
    print("\n" + "=" * 60)
    print("Processing...")
    unique_items = merge_and_dedup_multi(all_items)
    
    # 4. Filter by time window
    recent_items = filter_by_time_window(unique_items, hours=TIME_WINDOW_HOURS)
    
    # 5. Sort by timestamp
    sorted_items = sort_by_timestamp(recent_items)
    
    # 6. Save JSON
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    filename = f"{STATE_DIR}/raw-{timestamp}.json"
    save_json(sorted_items, filename)
    
    # 7. Summary
    print("\n" + "=" * 60)
    print("Final Summary:")
    print(f"  Sources:")
    for source, count in source_stats.items():
        print(f"    {source}: {count} items")
    print(f"  Total raw: {sum(source_stats.values())}")
    print(f"  After dedup: {len(unique_items)}")
    print(f"  After {TIME_WINDOW_HOURS}h filter: {len(recent_items)}")
    
    print("=" * 60)


def save_json(items, filename):
    """Save items to JSON file (atomic write)"""
    os.makedirs(STATE_DIR, exist_ok=True)
    
    # Count by topic
    topic_counts = {}
    for item in items:
        topic_id = item.get('topic_id', 'unknown')
        topic_counts[topic_id] = topic_counts.get(topic_id, 0) + 1
    
    data = {
        'scraped_at': datetime.now(timezone.utc).isoformat(),
        'total_items': len(items),
        'topic_counts': topic_counts,
        'sources': {},
        'items': items
    }
    
    # Count by source
    for item in items:
        source = item['source']
        source_name = item.get('source_name', source)
        key = f"{source}:{source_name}"
        data['sources'][key] = data['sources'].get(key, 0) + 1
    
    # Atomic write
    tmp_file = f"{filename}.tmp"
    with open(tmp_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    os.rename(tmp_file, filename)
    print(f"Saved to: {filename}")


if __name__ == '__main__':
    test_scrape()
