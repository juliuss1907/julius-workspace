# 3-Tier Keyword-First Prioritization Algorithm

## Overview

This algorithm prioritizes news items based on **keyword matching** (weighted), **engagement** (normalized), **source authority**, and **recency**. It's the core innovation of the news-brief-system.

## Scoring Formula

**Total Score = Keyword Score (0-100) + Engagement Score (0-50) + Source Bonus (0-15) + Recency Bonus (0-10)**

---

## 1. Keyword Score (0-100 pts)

### Tier System

**Tier 1: Must-have (100 points)**
```
Keywords: ['bitcoin', 'ethereum', 'sec approval', 'etf']
Trigger: immediate (always include)
```

**Tier 2: High interest (70 points)**
```
Keywords: ['uniswap', 'aave', 'restaking', 'liquid staking']
Trigger: daily
```

**Tier 3: Worth tracking (40 points)**
```
Keywords: ['defi', 'dex', 'nft', 'layer 2']
Trigger: daily
```

**Negative: Spam filter (-50 points)**
```
Keywords: ['pump', 'dump', 'meme coin', 'get rich quick']
```

### Matching Logic

```python
# Case-insensitive
search_text = (title + summary).lower()

for keyword in tier_keywords:
    if keyword in search_text:
        matched_keywords.append(keyword)

keyword_score = tier_weight  # Use highest tier that matches
```

### Configuration Example

```python
KEYWORD_FILTERS = {
    'crypto': {
        'tier_1': {
            'keywords': ['ethereum', 'bitcoin'],
            'weight': 100
        },
        'tier_2': {
            'keywords': ['uniswap', 'aave'],
            'weight': 70
        }
    }
}
```

---

## 2. Engagement Score (0-50 pts)

### Normalized by Source

**Telegram channels:**
```
Views range: 1,000 - 100,000
Formula: (views - 1000) / (100000 - 1000) * 50
Max points: 50
```

**thefeed.today:**
```
Views range: 5,000 - 5,000,000
Formula: (views - 5000) / (5000000 - 5000) * 50
Bonus: engagement_rate > 5% → +10 pts
Max points: 60 (50 + bonus)
```

### Configuration

```python
ENGAGEMENT_WEIGHTS = {
    'telegram': {
        'views': {
            'weight': 1.0,
            'normalization': {'min': 1000, 'max': 100000, 'max_points': 50}
        }
    },
    'thefeed': {
        'views': {
            'weight': 1.0,
            'normalization': {'min': 5000, 'max': 5000000, 'max_points': 50}
        },
        'engagement_rate': {
            'weight': 10.0,
            'threshold': 5.0,
            'bonus_points': 10
        }
    }
}
```

---

## 3. Source Authority Bonus (0-15 pts)

### Priority Multiplier
```
high:    1.5x
medium:  1.0x
low:     0.7x
```

### Type Multiplier
```
research:   1.3x
alpha:      1.1x
news:       1.0x
community:  0.8x
```

### Calculation
```python
priority_mult = {'high': 1.5, 'medium': 1.0, 'low': 0.7}[priority]
type_mult = {'research': 1.3, 'alpha': 1.1, 'news': 1.0, 'community': 0.8}[source_type]

combined = priority_mult * type_mult
bonus = (combined - 1.0) * 15  # Max 15 points
```

### Configuration

```python
SOURCE_AUTHORITY = {
    'priority_multiplier': {'high': 1.5, 'medium': 1.0, 'low': 0.7},
    'type_multiplier': {'research': 1.3, 'alpha': 1.1, 'news': 1.0, 'community': 0.8},
    'max_bonus': 15
}
```

---

## 4. Recency Bonus (0-10 pts)

### Time-based Bonus
```
last 3h:   10 pts
last 6h:    7 pts
last 12h:   3 pts
older:      0 pts
```

### Configuration

```python
RECENCY_BONUS = {
    'last_3h': 10,
    'last_6h': 7,
    'last_12h': 3,
    'older': 0
}
```

---

## Selection Algorithm

### Top Stories (2-5 items, flexible)

```python
def select_top_stories(items):
    # 1. Include all breaking news (both categories)
    breaking = [i for i in items if i.get('breaking')]
    
    # 2. Fill remaining slots with highest total score
    non_breaking = [i for i in items if not i.get('breaking')]
    non_breaking.sort(key=lambda x: x['priority']['total_score'], reverse=True)
    
    selected = breaking + non_breaking[:max_stories - len(breaking)]
    return selected
```

**Key insight:** Natural mix emerges (not forced 50/50). Breaking news from either category gets priority.

### Worth Reading (7-10 items, 50/50 split)

```python
def select_worth_reading(items, top_stories, category):
    # 1. Filter by category and exclude top stories
    candidates = [i for i in items if i['category'] == category and i not in top_stories]
    
    # 2. Apply score threshold
    candidates = [i for i in candidates if i['priority']['total_score'] >= min_score]
    
    # 3. Take top N
    selected = candidates[:max_per_category]
    
    # 4. Ensure minimum
    while len(selected) < min_per_category and len(candidates) > len(selected):
        selected.append(candidates[len(selected)])
    
    return selected
```

**Result:**
- Crypto: 3-5 items (tier 2 + interesting tier 3)
- Tech: 3-5 items (tier 2 + interesting tier 3)
- Total: 7-10 items

---

## Priority Score Breakdown Example

```
Item: "Ethereum Layer 2 scaling solution launched"
Source: high-priority research channel
Engagement: 15K views
Age: 2h

Calculation:
• Keyword: "ethereum" (tier 1) + "layer 2" (tier 2) = 100 pts
• Engagement: (15K-1K)/99K * 50 = 7.1 pts
• Source: high (1.5x) * research (1.3x) = 1.95x → 14.3 pts
• Recency: last 3h = 10 pts
──────────────────────────────────────
Total: 100 + 7.1 + 14.3 + 10 = 131.4 pts
```

---

## Tuning Guide

**Too many items:**
- Lower `SELECTION_CRITERIA['top_stories']['max']`
- Increase `min_score` thresholds

**Too few items:**
- Add more sources in `NEWS_SOURCES`
- Lower `min_score` thresholds
- Add tier 2/3 keywords

**Spam getting through:**
- Add to `NEGATIVE_KEYWORDS`
- Increase `min_keyword_score`

**Category imbalance:**
- Adjust `select_worth_reading()` category logic
- Check source priority multipliers

**Low quality items:**
- Tighten `QUALITY_FILTERS` (min_views, min_text_length)
- Increase `min_keyword_score`

---

## Implementation

**Primary file:** `prioritize.py` - `calculate_priority_score()` function

**Key functions:**
- `calculate_keyword_score()` → keyword matching
- `calculate_engagement_score()` → normalized engagement
- `calculate_source_bonus()` → authority multipliers
- `calculate_recency_bonus()` → time-based bonus
- `select_top_stories()` → flexible top stories
- `select_worth_reading()` → 50/50 split

---

## Performance Characteristics

- **Scraping:** ~2-3 minutes (Telegram + thefeed)
- **Processing:** ~10-15 seconds (merge + prioritize)
- **Memory:** < 100MB (for ~500 items)
- **Disk:** ~50KB per JSON file

---

**Maintainer:** Markus + Julius  
**Last Updated:** 2026-05-23