# scrape.py
from scrape_telegram import scrape_telegram
from scrape_thefeed import scrape_thefeed
from merge import merge_and_dedup_multi, filter_by_time_window, sort_by_timestamp
from datetime import datetime, timezone
from config import STATE_DIR, LOGS_DIR, NEWS_SOURCES, TIME_WINDOW_HOURS, TOPICS
from config_helpers import get_all_enabled_sources
import json
import os


def scrape_all_sources():
    """Scrape from all enabled sources"""
    all_items = []
    source_stats = {}

    # 1. Telegram
    if NEWS_SOURCES['telegram']['enabled']:
        print("\n" + "=" * 60)
        try:
            telegram_items = scrape_telegram()
            all_items.extend(telegram_items)
            source_stats['telegram'] = len(telegram_items)
        except Exception as e:
            print(f"Telegram scrape failed: {e}")
            source_stats['telegram'] = 0
    else:
        print("\nTelegram scraping disabled")
        source_stats['telegram'] = 0

    # 2. Websites - thefeed.today
    if NEWS_SOURCES['websites']['enabled']:
        print("\n" + "=" * 60)
        try:
            thefeed_items = scrape_thefeed()
            all_items.extend(thefeed_items)
            source_stats['thefeed'] = len(thefeed_items)
        except Exception as e:
            print(f"thefeed scrape failed: {e}")
            source_stats['thefeed'] = 0
    else:
        print("\nWebsite scraping disabled")
        source_stats['thefeed'] = 0

    # 3. RSS feeds
    if NEWS_SOURCES.get('rss', {}).get('enabled'):
        print("\n" + "=" * 60)
        try:
            from scrape_rss import scrape_rss
            rss_items = scrape_rss()
            all_items.extend(rss_items)
            source_stats['rss'] = len(rss_items)
        except ImportError:
            print("RSS scraper not available. Install: pip install feedparser")
            source_stats['rss'] = 0
        except Exception as e:
            print(f"RSS scrape failed: {e}")
            source_stats['rss'] = 0
    else:
        source_stats['rss'] = 0

    return all_items, source_stats


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
        # Backward compatibility
        'crypto_count': topic_counts.get('crypto', 0),
        'tech_count': topic_counts.get('tech', 0),
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


def main():
    """Main scrape function"""
    print("=" * 60)
    print(f"News Brief Scraper — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Print enabled topics and sources
    summary = get_all_enabled_sources()

    print(f"\nEnabled topics:")
    for topic_id, topic_info in summary['topics'].items():
        print(f"  {topic_info['icon']} {topic_info['name']}:")
        print(f"    Telegram: {topic_info['telegram']}")
        print(f"    Websites: {topic_info['websites']}")
        print(f"    RSS: {topic_info['rss']}")

    print(f"\nTotal sources:")
    print(f"  Telegram channels: {summary['total']['telegram']}")
    print(f"  Websites: {summary['total']['websites']}")
    print(f"  RSS feeds: {summary['total']['rss']}")

    if all(v == 0 for v in summary['total'].values()):
        print("\nNo sources enabled. Please configure TOPICS in config.py")
        return

    try:
        # 1. Scrape all sources
        all_items, source_stats = scrape_all_sources()

        if not all_items:
            print("\nNo items scraped")
            return

        # 2. Merge and dedup
        print("\n" + "=" * 60)
        print("Processing...")
        unique_items = merge_and_dedup_multi(all_items)

        # 3. Filter by time window
        recent_items = filter_by_time_window(unique_items, hours=TIME_WINDOW_HOURS)

        # 4. Sort by timestamp
        sorted_items = sort_by_timestamp(recent_items)

        # 5. Save JSON
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
        filename = f"{STATE_DIR}/raw-{timestamp}.json"
        save_json(sorted_items, filename)

        # 6. Summary
        print("\n" + "=" * 60)
        print("Final Summary:")
        print(f"  Sources:")
        for source, count in source_stats.items():
            print(f"    {source}: {count} items")
        print(f"  Total raw: {sum(source_stats.values())}")
        print(f"  After dedup: {len(unique_items)}")
        print(f"  After {TIME_WINDOW_HOURS}h filter: {len(recent_items)}")

        # Per-topic breakdown
        print(f"  By topic:")
        for topic_id, topic in TOPICS.items():
            if topic['enabled']:
                count = len([i for i in sorted_items if i.get('topic_id') == topic_id])
                print(f"    {topic['icon']} {topic['display_name']}: {count}")

        print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

        os.makedirs(LOGS_DIR, exist_ok=True)
        with open(f"{LOGS_DIR}/scrape-error.log", 'a') as f:
            f.write(f"\n{datetime.now().isoformat()}\n")
            f.write(f"{traceback.format_exc()}\n")


if __name__ == '__main__':
    main()
