# merge.py
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse
from config_helpers import get_source_priority_multiplier
import re


def extract_domain(url):
    """Extract domain from URL"""
    try:
        return urlparse(url).netloc
    except:
        return ''


def normalize_title(title):
    """Normalize title for comparison"""
    normalized = re.sub(r'[^\w\s]', '', title.lower())
    return ' '.join(normalized.split())


def are_duplicates(item1, item2):
    """Check if two items are duplicates"""
    # Same link
    if item1['link'] == item2['link']:
        return True

    # Same domain + similar title
    domain1 = extract_domain(item1['link'])
    domain2 = extract_domain(item2['link'])

    if domain1 and domain2 and domain1 == domain2:
        title1 = normalize_title(item1['title'])
        title2 = normalize_title(item2['title'])

        words1 = set(title1.split())
        words2 = set(title2.split())

        if len(words1) > 0 and len(words2) > 0:
            overlap = len(words1 & words2) / max(len(words1), len(words2))
            if overlap > 0.8:
                return True

    return False


def get_source_priority_score(item):
    """Get priority score for source comparison"""
    base_score = get_source_priority_multiplier(item)

    # Research channels get boost
    if item['source'] == 'telegram' and item.get('source_type') == 'research':
        base_score *= 1.5

    # Higher engagement wins
    engagement = item.get('engagement', {}).get('value', 0)
    if item['source'] == 'telegram':
        base_score += min(engagement / 10_000, 1.0)
    elif item['source'] == 'website':
        base_score += min(engagement / 100_000, 1.0)

    return base_score


def merge_and_dedup_multi(all_items):
    """Merge items from multiple sources and deduplicate"""
    print("Merging and deduplicating...")

    # Sort by source priority
    sorted_items = sorted(
        all_items,
        key=get_source_priority_score,
        reverse=True
    )

    unique_items = []

    for item in sorted_items:
        is_dup = False
        for existing in unique_items:
            if are_duplicates(item, existing):
                is_dup = True
                break

        if not is_dup:
            unique_items.append(item)

    print(f"  Before dedup: {len(all_items)}")
    print(f"  After dedup: {len(unique_items)}")
    print(f"  Removed: {len(all_items) - len(unique_items)}")

    return unique_items


def filter_by_time_window(items, hours=24):
    """Filter items within time window"""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    filtered = []
    for item in items:
        ts = item['timestamp']
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        if ts > cutoff:
            item['timestamp'] = ts
            filtered.append(item)

    print(f"  Time window filter ({hours}h): {len(items)} -> {len(filtered)}")
    return filtered


def sort_by_timestamp(items):
    """Sort items by timestamp (newest first)"""
    return sorted(items, key=lambda x: x['timestamp'], reverse=True)
