# config_helpers.py
from config import TOPICS, GLOBAL_SETTINGS, NEWS_SOURCES, SPAM_KEYWORDS, QUALITY_FILTERS, SOURCE_AUTHORITY


# ============================================================
# NEW: Topic-aware helpers
# ============================================================


def get_enabled_topics():
    """
    Get list of enabled topics

    Returns:
        dict: {topic_id: topic_config}
    """
    return {
        topic_id: topic
        for topic_id, topic in TOPICS.items()
        if topic['enabled']
    }


def get_topic_sources(topic_id, source_type=None):
    """
    Get sources for a specific topic

    Args:
        topic_id: Topic ID (e.g., 'crypto', 'tech')
        source_type: 'telegram' | 'websites' | 'rss' | None (all)

    Returns:
        dict or list: Sources for the topic
    """
    if topic_id not in TOPICS:
        return [] if source_type else {}

    topic = TOPICS[topic_id]
    if not topic['enabled']:
        return [] if source_type else {}

    sources = topic['sources']

    if source_type:
        return sources.get(source_type, [])
    else:
        return sources


def get_all_sources_by_type(source_type):
    """
    Get all sources of a specific type across all enabled topics

    Args:
        source_type: 'telegram' | 'websites' | 'rss'

    Returns:
        list: [(topic_id, source_config), ...]
    """
    all_sources = []

    for topic_id, topic in TOPICS.items():
        if not topic['enabled']:
            continue

        sources = topic['sources'].get(source_type, [])
        for source in sources:
            if source.get('enabled', True):
                # Add topic info to source for tracking
                source_with_topic = source.copy()
                source_with_topic['topic_id'] = topic_id
                source_with_topic['topic_name'] = topic['display_name']
                source_with_topic['topic_icon'] = topic['icon']
                all_sources.append((topic_id, source_with_topic))

    return all_sources


def get_topic_keywords(topic_id):
    """Get keywords for a specific topic"""
    if topic_id not in TOPICS:
        return {}

    topic = TOPICS[topic_id]
    if not topic['enabled']:
        return {}

    return topic['keywords']


# ============================================================
# BACKWARD COMPATIBLE: Legacy helpers
# ============================================================


def get_enabled_telegram_channels(category=None):
    """
    Get list of enabled Telegram channels

    Args:
        category: 'crypto' | 'tech' | None (all)

    Returns:
        List of channel dicts
    """
    if category:
        topic_id = category.lower()
        sources = get_topic_sources(topic_id, 'telegram')
        return [s for s in sources if s.get('enabled', True)]
    else:
        return [s for _, s in get_all_sources_by_type('telegram')]


def get_enabled_websites(scraper_type=None):
    """
    Get list of enabled websites

    Args:
        scraper_type: 'thefeed' | 'rss' | 'custom' | None (all)

    Returns:
        List of website dicts
    """
    websites = [s for _, s in get_all_sources_by_type('websites')]
    if scraper_type:
        websites = [w for w in websites if w.get('scraper') == scraper_type]
    return websites


def get_enabled_rss_feeds(category=None):
    """
    Get list of enabled RSS feeds

    Args:
        category: 'crypto' | 'tech' | None (all)

    Returns:
        List of feed dicts
    """
    if category:
        topic_id = category.lower()
        sources = get_topic_sources(topic_id, 'rss')
        return [s for s in sources if s.get('enabled', True)]
    else:
        return [s for _, s in get_all_sources_by_type('rss')]


def get_source_priority_multiplier(source_dict):
    """
    Get priority multiplier for a source

    Args:
        source_dict: Channel or website dict from config

    Returns:
        float: Combined multiplier
    """
    priority = source_dict.get('priority', 'medium')
    source_type = source_dict.get('type', 'news')

    priority_mult = SOURCE_AUTHORITY['priority_multiplier'].get(priority, 1.0)
    type_mult = SOURCE_AUTHORITY['type_multiplier'].get(source_type, 1.0)

    return priority_mult * type_mult


def is_spam(text):
    """Check if text contains spam keywords"""
    if not text:
        return False

    text_lower = text.lower()
    return any(keyword in text_lower for keyword in SPAM_KEYWORDS)


def passes_quality_filters(item):
    """Check if item passes quality filters"""
    # Text length
    text = item.get('summary', '') or item.get('title', '')
    if len(text) < QUALITY_FILTERS['min_text_length']:
        return False

    # Views/engagement
    engagement = item.get('engagement', {})
    if engagement.get('value', 0) < QUALITY_FILTERS['min_views']:
        return False

    # Link required
    if QUALITY_FILTERS['require_link'] and not item.get('link'):
        return False

    return True


def get_all_enabled_sources():
    """Get summary of all enabled sources across all topics"""
    enabled_topics = get_enabled_topics()

    summary = {
        'topics': {},
        'total': {
            'telegram': 0,
            'websites': 0,
            'rss': 0,
        }
    }

    for topic_id, topic in enabled_topics.items():
        telegram = topic['sources'].get('telegram', [])
        websites = topic['sources'].get('websites', [])
        rss = topic['sources'].get('rss', [])

        telegram_enabled = [s for s in telegram if s.get('enabled', True)]
        websites_enabled = [s for s in websites if s.get('enabled', True)]
        rss_enabled = [s for s in rss if s.get('enabled', True)]

        summary['topics'][topic_id] = {
            'name': topic['display_name'],
            'icon': topic['icon'],
            'telegram': len(telegram_enabled),
            'websites': len(websites_enabled),
            'rss': len(rss_enabled),
        }

        summary['total']['telegram'] += len(telegram_enabled)
        summary['total']['websites'] += len(websites_enabled)
        summary['total']['rss'] += len(rss_enabled)

    return summary
