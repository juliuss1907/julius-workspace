# Reference — Prioritization Logic

Detailed explanation of 3-tier priority system for news selection.

## Overview

**Goal:** Select most important and interesting items from extracted news.
**Approach:** 3-tier priority applied to both Crypto and Tech categories.
**Output:** Top stories 2-5 (flexible), Đáng đọc 7-10 (50/50 split).

## 3-Tier Priority System

### Tier 1: Breaking News (Highest)

**Definition:** Items tagged "Breaking" on thefeed.today
**Rule:** Always include all Tier 1 in top stories. No view/engagement threshold.
**Why:** Time-sensitive, high impact, readers need to know immediately.
**Examples:** SEC approves ETFs, Binance settles DOJ, Solana network halts, OpenAI announces GPT-5.

### Tier 2: High Engagement (Medium-High)

**Thresholds:** Views > 5,000 AND Engagement rate > 5%
**Characteristics:** Viral momentum, community interest, credible sources, substantive content.
**Rule:** Sort by views descending. Top items go to "Top stories" (after Tier 1). Remaining go to "Đáng đọc".
**Why:** Proven community interest, likely discussed, worth reader's time.

### Tier 3: Narrative Shift (Medium)

**Definition:** Items with lower views but interesting angles — emerging topics, new perspectives, credible niche sources, early signals, contrarian takes.
**Rule:** Sort by engagement rate (quality over quantity). Include in "Đáng đọc" for diversity.
**Why:** Early signal of trends, adds diversity, helps readers stay ahead.

## Selection Algorithm

### Top Stories (2-5 items, flexible mix)
1. Include ALL Tier 1 (Breaking) from both categories
2. Fill remaining slots with highest Tier 2 (sorted by views, regardless of category)
3. Ensure minimum 2 stories (add Tier 3 if needed)

### Đáng Đọc (7-10 items, 50/50 split)
1. Separate by category (Crypto / Tech)
2. Add Tier 2 items not in top stories (max 3 each)
3. Add Tier 3 items for diversity (max 2 each)
4. Cap at 5 per category
5. If total < 7: add more from Tier 3

## Edge Cases

### Many breaking (>5 items) → Expand top stories to 6-7
### One category empty → Top stories all from other, adjust đáng đọc split
### Extreme imbalance (20 crypto, 2 tech) → Flexible top stories, adjust đáng đọc split, note in narrative
### Low engagement across board → Use Tier 3 (engagement rate) for selection

## Priority Score Helper

```python
def calculate_priority_score(item):
    """Score = (tier_weight * 1000) + (views / 1000) + (engagement_rate * 10)"""
    if item['breaking']: tier_weight = 1000
    elif item['views'] > 5000 and item['engagement_rate'] > 5.0: tier_weight = 100
    else: tier_weight = 10
    return (tier_weight * 1000) + (item['views'] / 1000) + (item['engagement_rate'] * 10)
```

## Quality Filters

**Exclude:** Views < 1,000, Engagement rate < 1%, Duplicate content, Spam/promotional, Off-topic.
**Spam detection:** Check for keywords like "buy now", "limited time", "click here", "free money".

## Balancing Principles

1. Breaking news always wins (Tier 1 overrides all)
2. Engagement signals quality (high views + high rate = valuable)
3. Diversity matters (include emerging topics from Tier 3)
4. Category balance (maintain 50/50 in đáng đọc)
5. Flexibility over rigidity (adjust to actual news distribution)

## Maintenance

**When to adjust:** Views threshold (5K) if inflation, engagement rate (5%) if platform changes, tier weights if balance feels off.
**How:** Monitor 1 week → identify patterns → adjust incrementally → test 3 days → document.

**Last updated:** 2026-05-19
