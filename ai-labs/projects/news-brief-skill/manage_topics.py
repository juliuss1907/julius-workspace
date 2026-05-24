# manage_topics.py
import sys
from config import TOPICS
from config_helpers import get_all_enabled_sources


def list_topics():
    """List all topics and their status"""
    print("=" * 60)
    print("Available Topics")
    print("=" * 60)

    for topic_id, topic in TOPICS.items():
        status = "✅ ENABLED" if topic['enabled'] else "❌ DISABLED"
        print(f"\n{topic['icon']} {topic['display_name']} ({topic_id})")
        print(f"  Status: {status}")
        print(f"  Description: {topic['description']}")

        if topic['enabled']:
            sources = topic['sources']
            telegram = [s for s in sources.get('telegram', []) if s.get('enabled', True)]
            websites = [s for s in sources.get('websites', []) if s.get('enabled', True)]
            rss = [s for s in sources.get('rss', []) if s.get('enabled', True)]

            print(f"  Sources:")
            print(f"    Telegram: {len(telegram)}")
            print(f"    Websites: {len(websites)}")
            print(f"    RSS: {len(rss)}")

            # Keywords summary
            keywords = topic['keywords']
            tier1_count = len(keywords.get('tier_1', {}).get('keywords', []))
            tier2_count = len(keywords.get('tier_2', {}).get('keywords', []))
            tier3_count = len(keywords.get('tier_3', {}).get('keywords', []))

            print(f"  Keywords:")
            print(f"    Tier 1: {tier1_count}")
            print(f"    Tier 2: {tier2_count}")
            print(f"    Tier 3: {tier3_count}")

    print("\n" + "=" * 60)


def show_summary():
    """Show summary of enabled sources"""
    summary = get_all_enabled_sources()

    print("=" * 60)
    print("Enabled Sources Summary")
    print("=" * 60)

    for topic_id, info in summary['topics'].items():
        print(f"\n{info['icon']} {info['name']}:")
        print(f"  Telegram: {info['telegram']}")
        print(f"  Websites: {info['websites']}")
        print(f"  RSS: {info['rss']}")

    print(f"\n📊 Total:")
    print(f"  Telegram channels: {summary['total']['telegram']}")
    print(f"  Websites: {summary['total']['websites']}")
    print(f"  RSS feeds: {summary['total']['rss']}")
    print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 manage_topics.py list      # List all topics")
        print("  python3 manage_topics.py summary   # Show enabled sources summary")
        return

    command = sys.argv[1]

    if command == 'list':
        list_topics()
    elif command == 'summary':
        show_summary()
    else:
        print(f"Unknown command: {command}")


if __name__ == '__main__':
    main()
