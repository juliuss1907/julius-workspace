# prioritize.py
from datetime import datetime, timezone
from config import (
    GLOBAL_SETTINGS,
    ENGAGEMENT_WEIGHTS,
    SOURCE_AUTHORITY,
    RECENCY_BONUS,
    TOP_STORIES_SETTINGS,
    TOPICS,
)
from config_helpers import get_topic_keywords, get_enabled_topics
import re

# ============================================================
# 1. KEYWORD MATCHING (per-topic)
# ============================================================


def calculate_keyword_score(item):
    """
    Calculate keyword match score using item's topic keywords

    Returns:
        tuple: (score, matched_keywords, tier)
    """
    # Get topic_id from item
    topic_id = item.get('topic_id')
    if not topic_id:
        # Fallback to category-based lookup
        topic_id = item.get('category', '').lower()

    filters = get_topic_keywords(topic_id)
    if not filters:
        return 0, [], None

    settings = GLOBAL_SETTINGS['keywords']

    # Text to search
    search_text = ''
    for field in settings['search_in']:
        search_text += ' ' + item.get(field, '')

    if not settings['case_sensitive']:
        search_text = search_text.lower()

    max_score = 0
    matched_keywords = []
    matched_tier = None

    # Check each tier (highest tier wins)
    for tier_name in ['tier_1', 'tier_2', 'tier_3']:
        tier = filters.get(tier_name, {})
        keywords = tier.get('keywords', [])
        weight = tier.get('weight', 0)

        for keyword in keywords:
            search_keyword = keyword if settings['case_sensitive'] else keyword.lower()

            if settings['match_whole_word']:
                pattern = r'\b' + re.escape(search_keyword) + r'\b'
                if re.search(pattern, search_text):
                    if weight > max_score:
                        max_score = weight
                        matched_tier = tier_name
                    matched_keywords.append(keyword)
            else:
                if search_keyword in search_text:
                    if weight > max_score:
                        max_score = weight
                        matched_tier = tier_name
                    matched_keywords.append(keyword)

    # Check negative keywords
    negative = filters.get('negative', {})
    for keyword in negative.get('keywords', []):
        search_keyword = keyword if settings['case_sensitive'] else keyword.lower()
        if search_keyword in search_text:
            max_score += negative['weight']
            matched_keywords.append(f"NEGATIVE:{keyword}")

    # Apply minimum threshold
    if max_score < settings['min_keyword_score']:
        max_score = 0

    return max_score, matched_keywords, matched_tier


# ============================================================
# 2. ENGAGEMENT SCORING
# ============================================================


def calculate_engagement_score(item):
    """Calculate engagement score based on views/reactions"""
    source = item['source']
    engagement = item.get('engagement', {})

    if source == 'telegram':
        weights = ENGAGEMENT_WEIGHTS['telegram']
        views = engagement.get('value', 0)

        norm = weights['views']['normalization']
        if views < norm['min']:
            score = 0
        elif views > norm['max']:
            score = norm['max_points']
        else:
            score = ((views - norm['min']) / (norm['max'] - norm['min'])) * norm['max_points']

        return score * weights['views']['weight']

    elif source == 'website':
        source_name = item.get('source_name', '')

        if source_name == 'thefeed':
            weights = ENGAGEMENT_WEIGHTS['thefeed']
            views = engagement.get('value', 0)

            norm = weights['views']['normalization']
            if views < norm['min']:
                score = 0
            elif views > norm['max']:
                score = norm['max_points']
            else:
                score = ((views - norm['min']) / (norm['max'] - norm['min'])) * norm['max_points']

            score *= weights['views']['weight']

            # Engagement rate bonus
            eng_rate = item.get('engagement_rate', 0)
            if eng_rate > weights['engagement_rate']['threshold']:
                score += weights['engagement_rate']['bonus_points']

            return score

        else:
            return ENGAGEMENT_WEIGHTS['website']['default_score']

    elif source == 'rss':
        # RSS feeds don't have engagement metrics
        # Use source priority as base score
        rss_weights = ENGAGEMENT_WEIGHTS['rss']
        priority = item.get('source_priority', 'medium')
        return rss_weights.get(f'{priority}_priority', rss_weights['medium_priority'])

    return 0


# ============================================================
# 3. SOURCE AUTHORITY
# ============================================================


def calculate_source_bonus(item):
    """Calculate source authority bonus"""
    priority = item.get('source_priority', 'medium')
    source_type = item.get('source_type', 'news')

    priority_mult = SOURCE_AUTHORITY['priority_multiplier'].get(priority, 1.0)
    type_mult = SOURCE_AUTHORITY['type_multiplier'].get(source_type, 1.0)

    combined = priority_mult * type_mult
    bonus = (combined - 1.0) * SOURCE_AUTHORITY['max_bonus']

    return max(bonus, 0)


# ============================================================
# 4. RECENCY BONUS
# ============================================================


def calculate_recency_bonus(item):
    """Calculate recency bonus"""
    now = datetime.now(timezone.utc)
    timestamp = item['timestamp']

    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    age_hours = (now - timestamp).total_seconds() / 3600

    if age_hours < 3:
        return RECENCY_BONUS['last_3h']
    elif age_hours < 6:
        return RECENCY_BONUS['last_6h']
    elif age_hours < 12:
        return RECENCY_BONUS['last_12h']
    else:
        return RECENCY_BONUS['older']


# ============================================================
# 5. TOTAL PRIORITY SCORE
# ============================================================


def calculate_priority_score(item):
    """
    Calculate total priority score

    Returns:
        dict: Priority breakdown
    """
    # Breaking news override
    if item.get('breaking'):
        return {
            'total_score': 200,
            'keyword_score': 100,
            'engagement_score': 50,
            'source_bonus': 15,
            'recency_bonus': 10,
            'matched_keywords': ['BREAKING'],
            'keyword_tier': 'breaking',
        }

    # Calculate components
    keyword_score, matched_keywords, keyword_tier = calculate_keyword_score(item)
    engagement_score = calculate_engagement_score(item)
    source_bonus = calculate_source_bonus(item)
    recency_bonus = calculate_recency_bonus(item)

    total = keyword_score + engagement_score + source_bonus + recency_bonus

    return {
        'total_score': total,
        'keyword_score': keyword_score,
        'engagement_score': engagement_score,
        'source_bonus': source_bonus,
        'recency_bonus': recency_bonus,
        'matched_keywords': matched_keywords,
        'keyword_tier': keyword_tier,
    }


# ============================================================
# 6. PRIORITIZATION
# ============================================================


def prioritize_items(items):
    """Calculate priority scores for all items"""
    for item in items:
        priority = calculate_priority_score(item)
        item['priority'] = priority

    items.sort(key=lambda x: x['priority']['total_score'], reverse=True)

    return items


# ============================================================
# 7. SELECTION (multi-topic)
# ============================================================


def select_top_stories(items):
    """Select top stories (cross-topic)"""
    criteria = TOP_STORIES_SETTINGS

    candidates = []
    for item in items:
        priority = item['priority']

        # Breaking always included
        if item.get('breaking'):
            candidates.append(item)
            continue

        # Check score threshold
        if priority['total_score'] < criteria['min_score']:
            continue

        # Check keyword requirement
        if criteria['require_keyword_match']:
            if priority['keyword_score'] <= 0:
                continue

        candidates.append(item)

    # Take top N
    selected = candidates[:criteria['max']]

    # Ensure minimum
    if len(selected) < criteria['min']:
        for item in items:
            if item not in selected:
                selected.append(item)
                if len(selected) >= criteria['min']:
                    break

    return selected


def select_worth_reading_for_topic(topic_items, top_stories, criteria):
    """
    Select worth reading items for a specific topic

    Args:
        topic_items: Items belonging to this topic
        top_stories: Items already in top stories (exclude these)
        criteria: Selection criteria from topic config

    Returns:
        list: Selected items
    """
    # Filter out items already in top stories
    candidates = [
        item for item in topic_items
        if item not in top_stories
    ]

    # Filter by score
    candidates = [
        item for item in candidates
        if item['priority']['total_score'] >= criteria['min_score']
    ]

    # Take top N
    selected = candidates[:criteria['max']]

    # Ensure minimum
    if len(selected) < criteria['min']:
        remaining = [
            item for item in topic_items
            if item not in top_stories
            and item not in selected
        ]
        needed = criteria['min'] - len(selected)
        selected.extend(remaining[:needed])

    return selected


def select_stories(items):
    """
    Main selection function with multi-topic support

    Returns:
        dict: {
            'top_stories': [...],
            '<topic_id>_worth_reading': [...],
            ...
        }
    """
    # 1. Select top stories (cross-topic)
    top_stories = select_top_stories(items)

    result = {'top_stories': top_stories}

    # 2. Select worth reading for each enabled topic
    enabled_topics = get_enabled_topics()

    for topic_id, topic in enabled_topics.items():
        # Filter items by topic
        topic_items = [
            item for item in items
            if item.get('topic_id') == topic_id
        ]

        # Select worth reading
        criteria = topic['selection']['worth_reading']
        worth_reading = select_worth_reading_for_topic(
            topic_items,
            top_stories,
            criteria
        )

        result[f'{topic_id}_worth_reading'] = worth_reading

    # Backward compatibility aliases
    if 'crypto_worth_reading' in result:
        pass  # Already there
    if 'tech_worth_reading' in result:
        pass  # Already there

    return result


# ============================================================
# DEBUG HELPER
# ============================================================


def explain_score(item):
    """Print detailed score breakdown"""
    priority = item['priority']

    print(f"\n{'=' * 70}")
    print(f"{item['title'][:60]}")
    print(f"{'=' * 70}")
    print(f"Source: {item['source']} / {item.get('source_display_name', item['source_name'])}")
    print(f"Topic: {item.get('topic_name', item.get('category', '?'))} ({item.get('topic_id', '?')})")
    print(f"Breaking: {item.get('breaking', False)}")

    print(f"\nPRIORITY BREAKDOWN:")
    print(f"  Keyword score: {priority['keyword_score']:6.1f} (tier: {priority['keyword_tier']})")
    print(f"  Engagement score: {priority['engagement_score']:6.1f}")
    print(f"  Source bonus: {priority['source_bonus']:6.1f}")
    print(f"  Recency bonus: {priority['recency_bonus']:6.1f}")
    print(f"  {'-' * 40}")
    print(f"  TOTAL SCORE: {priority['total_score']:6.1f}")

    if priority['matched_keywords']:
        print(f"\nMatched keywords:")
        for kw in priority['matched_keywords'][:5]:
            print(f"  - {kw}")
        if len(priority['matched_keywords']) > 5:
            print(f"  ... and {len(priority['matched_keywords']) - 5} more")

    print(f"\nEngagement:")
    print(f"  Views: {item['engagement']['value']:,}")
    if item.get('engagement_rate'):
        print(f"  Rate: {item['engagement_rate']:.2f}%")

    age = (datetime.now(timezone.utc) - item['timestamp']).total_seconds() / 3600
    print(f"\nAge: {age:.1f} hours")

    print(f"{'=' * 70}")
