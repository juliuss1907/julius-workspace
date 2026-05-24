# synthesize.py
from datetime import datetime, timezone
from config import STATE_DIR, LOGS_DIR, JSON_FRESHNESS_MINUTES, OUTPUT_SETTINGS, TOPICS
from prioritize import prioritize_items, select_stories, explain_score
from format import format_brief
from send import send_to_telegram, send_error_notification
from save_markdown import save_markdown
import json
import os
import glob
import sys
import argparse


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='News Brief Synthesizer')
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Show debug output with score breakdowns'
    )
    return parser.parse_args()


def find_latest_json():
    """Find latest scraped JSON file"""
    pattern = f"{STATE_DIR}/raw-*.json"
    files = glob.glob(pattern)
    return sorted(files)[-1] if files else None


def check_json_freshness(filepath, max_age_minutes=15):
    """Check if JSON file is fresh"""
    if not os.path.exists(filepath):
        return False, "File not found"

    file_mtime = os.path.getmtime(filepath)
    file_age = datetime.now().timestamp() - file_mtime

    if file_age > max_age_minutes * 60:
        return False, f"Too old ({file_age / 60:.1f} min)"

    return True, "OK"


def load_json(filepath):
    """Load and parse JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Normalize timestamps
    for item in data['items']:
        ts = item['timestamp']
        if isinstance(ts, str):
            item['timestamp'] = datetime.fromisoformat(ts)

    return data


def main(debug=False):
    """Entry point for synthesize"""
    print("=" * 60)
    print(f"News Brief Synthesizer — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. Find latest JSON
    json_file = find_latest_json()
    if not json_file:
        print("❌ No scraped data found")
        print("Run scrape.py first")
        send_error_notification("No scraped data found. Run scrape.py first.")
        return False

    print(f"📂 Found: {json_file}")

    # 2. Check freshness
    is_fresh, msg = check_json_freshness(json_file, JSON_FRESHNESS_MINUTES)
    if not is_fresh:
        print(f"⚠️  {msg}")
        # Continue anyway with warning

    # 3. Load data
    try:
        data = load_json(json_file)
        items = data['items']

        print(f"📊 Loaded {len(items)} items")

        # Show per-topic counts
        topic_counts = data.get('topic_counts', {})
        if topic_counts:
            for topic_id, count in topic_counts.items():
                topic = TOPICS.get(topic_id, {})
                icon = topic.get('icon', '📰')
                name = topic.get('display_name', topic_id)
                print(f"  {icon} {name}: {count}")
        else:
            # Backward compatibility
            print(f"  Crypto: {data.get('crypto_count', 0)}")
            print(f"  Tech: {data.get('tech_count', 0)}")

        print(f"  Scraped at: {data['scraped_at']}")

    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        send_error_notification(f"Error loading JSON: {e}")
        return False

    if not items:
        print("❌ No items to process")
        return False

    # 4. Prioritize
    print("\n🎯 Prioritizing items...")
    prioritized = prioritize_items(items)

    # Debug: show top 5 scores
    if debug:
        print("\n🔍 Top 5 items by score:")
        for item in prioritized[:5]:
            explain_score(item)

    # 5. Select stories
    print("\n📋 Selecting stories...")
    stories = select_stories(prioritized)

    print(f"  Top stories: {len(stories['top_stories'])}")
    for topic_id, topic in TOPICS.items():
        if topic['enabled']:
            key = f'{topic_id}_worth_reading'
            count = len(stories.get(key, []))
            print(f"  {topic['icon']} {topic['display_name']}: {count}")

    # 6. Format brief
    print("\n📝 Formatting brief...")
    brief = format_brief(stories, data['scraped_at'])
    print(f"  Brief length: {len(brief)} chars")

    # 7. Save to Markdown
    md_success = False
    md_path = None
    if OUTPUT_SETTINGS['markdown']['enabled']:
        md_success, md_path = save_markdown(brief, data['scraped_at'])
    else:
        print("\n📝 Markdown output disabled")

    # 8. Send to Telegram
    telegram_success = False
    if OUTPUT_SETTINGS['telegram']['enabled']:
        print("\n📤 Sending to Telegram...")
        telegram_success = send_to_telegram(brief)
    else:
        print("\n📤 Telegram delivery disabled")
        telegram_success = True  # Don't fail if intentionally disabled

    # 9. Update last-run timestamp
    if md_success or telegram_success:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(f"{STATE_DIR}/last-run-timestamp.txt", 'w') as f:
            f.write(datetime.now(timezone.utc).isoformat())

        print("\n✅ Brief delivered successfully")

        # Print delivery summary
        if md_success and md_path:
            print(f"  ✓ Markdown: {md_path}")
        if telegram_success and OUTPUT_SETTINGS['telegram']['enabled']:
            print(f"  ✓ Telegram: Sent")

        return True
    else:
        print("\n❌ Failed to deliver brief")
        return False


if __name__ == '__main__':
    args = parse_args()

    try:
        success = main(debug=args.debug)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

        os.makedirs(LOGS_DIR, exist_ok=True)
        with open(f"{LOGS_DIR}/synthesize-error.log", 'a') as f:
            f.write(f"\n{datetime.now().isoformat()}\n")
            f.write(f"{traceback.format_exc()}\n")

        send_error_notification(str(e))
        sys.exit(1)
