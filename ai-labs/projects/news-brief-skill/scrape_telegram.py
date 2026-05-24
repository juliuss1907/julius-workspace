# scrape_telegram.py
from telethon import TelegramClient
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from config import GLOBAL_SETTINGS, TELEGRAM_API_ID, TELEGRAM_API_HASH
from config_helpers import (
    get_all_sources_by_type,
    is_spam,
    passes_quality_filters
)
import asyncio

client = TelegramClient('hermes_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)


async def scrape_channel(channel_config, topic_id, topic_name, cutoff_time):
    """
    Scrape messages from a Telegram channel

    Args:
        channel_config: Channel dict from config
        topic_id: Topic ID (e.g., 'crypto', 'tech')
        topic_name: Topic display name
        cutoff_time: Only get messages after this time

    Returns:
        List of items
    """
    username = channel_config['username']
    settings = GLOBAL_SETTINGS['telegram_api']

    items = []

    try:
        entity = await client.get_entity(username)

        message_count = 0
        async for message in client.iter_messages(
            entity,
            offset_date=cutoff_time,
            limit=settings['max_messages_per_channel']
        ):
            message_count += 1

            # Skip if no text
            if not message.text and not message.message:
                if settings['skip_media_only']:
                    continue

            text = message.text or message.message

            # Skip spam
            if settings['skip_spam'] and is_spam(text):
                continue

            # Extract title and summary
            lines = text.split('\n')
            title = lines[0][:100] if lines else text[:100]
            summary = text[:300]

            item = {
                'title': title.strip(),
                'summary': summary.strip(),
                'link': f"https://t.me/{username}/{message.id}",
                'source': 'telegram',
                'source_name': username,
                'source_display_name': channel_config['name'],
                'source_priority': channel_config['priority'],
                'source_type': channel_config['type'],
                'topic_id': topic_id,
                'topic_name': topic_name,
                'category': topic_name,  # Backward compatibility
                'timestamp': message.date.replace(tzinfo=timezone.utc),
                'engagement': {
                    'type': 'views',
                    'value': message.views or 0
                },
                'breaking': False,
            }

            # Quality filter
            if passes_quality_filters(item):
                items.append(item)

        print(f"  @{username} ({channel_config['name']}): {len(items)} items (scanned {message_count})")

    except ValueError:
        print(f"  @{username}: Channel not found or private")
    except Exception as e:
        print(f"  @{username}: Error - {e}")

    return items


async def scrape_all_telegram():
    """Scrape all enabled Telegram channels across all topics"""
    await client.start()

    settings = GLOBAL_SETTINGS['telegram_api']
    cutoff = datetime.now(timezone.utc) - timedelta(hours=settings['time_window_hours'])

    all_items = []

    print("Scraping Telegram channels...")

    # Get all telegram sources with topic info
    telegram_sources = get_all_sources_by_type('telegram')

    if not telegram_sources:
        print("  No Telegram channels enabled")
        await client.disconnect()
        return []

    # Group by topic for display
    by_topic = defaultdict(list)
    for topic_id, source in telegram_sources:
        by_topic[topic_id].append(source)

    # Scrape each topic
    for topic_id, sources in by_topic.items():
        topic_name = sources[0]['topic_name']
        topic_icon = sources[0].get('topic_icon', '📰')
        print(f"{topic_icon} {topic_name} channels ({len(sources)}):")

        for source in sources:
            items = await scrape_channel(source, topic_id, topic_name, cutoff)
            all_items.extend(items)

    await client.disconnect()

    print(f"Total Telegram items: {len(all_items)}")
    return all_items


def scrape_telegram():
    """Sync wrapper"""
    return asyncio.run(scrape_all_telegram())
