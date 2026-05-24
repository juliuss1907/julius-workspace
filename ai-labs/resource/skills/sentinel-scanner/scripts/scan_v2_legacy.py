#!/usr/bin/env python3
"""
Sentinel Scanner v2 — Enhanced with Funding Raises & Tiered KOL Analysis
"""

import subprocess
import yaml
import re
import sys
import os
import time
import random
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import argparse

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_CONFIG = PROJECT_DIR / "config.yaml"
DEFAULT_OUTPUT_DIR = Path("/home/julius/julius-workspace/working/X/report/daily")

# Global for sentiment keywords
sentiment_keywords = {}

def load_config(path: Path) -> dict:
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def parse_tweet_text(text: str) -> str:
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()

def run_twitter_cli(args: list, timeout: int = 60) -> dict:
    cmd = ["twitter"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            print(f"Warning: twitter CLI error ({args[0]}): {result.stderr[:200]}", file=sys.stderr)
            return {}
        try:
            return yaml.safe_load(result.stdout) or {}
        except:
            return {}
    except subprocess.TimeoutExpired:
        print(f"Warning: twitter CLI timeout for {args[0]}", file=sys.stderr)
        return {}
    except FileNotFoundError:
        print("Error: 'twitter' CLI not found. Install via: pipx install twitter-cli", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Warning: twitter CLI error: {e}", file=sys.stderr)
        return {}

def fetch_user_tweets(username: str, count: int = 10, max_age_hours: int = 24) -> list:
    data = run_twitter_cli(["user-posts", username, "-n", str(count)])
    
    if not data or 'data' not in data:
        return []
    
    tweets = []
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    
    for tweet in data['data'][:count]:
        try:
            created = tweet.get('createdAtISO', '')
            tweet_time = datetime.fromisoformat(created.replace('+00:00', ''))
            if tweet_time < cutoff:
                continue
                
            metrics = tweet.get('metrics', {})
            tweets.append({
                'id': str(tweet.get('id', '')),
                'author': tweet.get('author', {}).get('screenName', username),
                'text': parse_tweet_text(tweet.get('text', '')),
                'created_at': created,
                'likes': metrics.get('likes', 0),
                'retweets': metrics.get('retweets', 0),
                'replies': metrics.get('replies', 0),
                'engagement': metrics.get('likes', 0) + metrics.get('retweets', 0) + metrics.get('replies', 0),
                'is_retweet': tweet.get('isRetweet', False)
            })
        except Exception:
            continue
    
    return tweets

def search_keyword(keyword: str, count: int = 20, max_age_hours: int = 24) -> list:
    """Search tweets by keyword."""
    data = run_twitter_cli(["search", keyword, "-n", str(count)])
    
    if not data or 'data' not in data:
        return []
    
    tweets = []
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    
    for tweet in data['data'][:count]:
        try:
            created = tweet.get('createdAtISO', '')
            tweet_time = datetime.fromisoformat(created.replace('+00:00', ''))
            if tweet_time < cutoff:
                continue
                
            metrics = tweet.get('metrics', {})
            tweets.append({
                'id': str(tweet.get('id', '')),
                'author': tweet.get('author', {}).get('screenName', 'unknown'),
                'text': parse_tweet_text(tweet.get('text', '')),
                'created_at': created,
                'likes': metrics.get('likes', 0),
                'retweets': metrics.get('retweets', 0),
                'replies': metrics.get('replies', 0),
                'engagement': metrics.get('likes', 0) + metrics.get('retweets', 0) + metrics.get('replies', 0),
                'is_retweet': tweet.get('isRetweet', False)
            })
        except Exception:
            continue
    
    return tweets

def parse_funding_info(text: str) -> dict:
    """Extract funding information from tweet text."""
    funding_patterns = [
        r'(\$[\d,.]+[MK]?)\s*(?:funding|raise|raised|investment|invested)',
        r'(?:funding|raise|raised)\s*(\$[\d,.]+[MK]?)',
        r'(\$[\d,.]+[MK]?)\s*(?:seed|Series\s*[A-Z]|pre-seed|angel)',
        r'(\$[\d,.]+[MK]?)\s*(?:valuation|valued\s*at)',
    ]
    
    amount = None
    for pattern in funding_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount = match.group(1)
            break
    
    # Try to find project/company name
    project_patterns = [
        r'(?:funding|raised|investment).*?(?:for|at|in)\s+@?(\w+)',
        r'(\w+)\s+(?:closes?|completes?|announces?)\s+(?:\$|funding)',
        r'(\w+)\s+raises\s+(?:\$|\d)',
    ]
    
    project = None
    for pattern in project_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            project = match.group(1)
            break
    
    if amount and ('funding' in text.lower() or 'raise' in text.lower() or 
                   'seed' in text.lower() or 'series' in text.lower()):
        return {'amount': amount, 'project': project}
    
    return None

def analyze_sentiment(text: str) -> str:
    global sentiment_keywords
    text_lower = text.lower()
    
    pos = sentiment_keywords.get('positive_keywords', [])
    neg = sentiment_keywords.get('negative_keywords', [])
    
    pos_score = sum(1 for w in pos if w.lower() in text_lower)
    neg_score = sum(1 for w in neg if w.lower() in text_lower)
    
    if pos_score > neg_score:
        return 'positive'
    elif neg_score > pos_score:
        return 'negative'
    return 'neutral'

def classify_tier(username: str, config: dict) -> str:
    indiv = config['kols'].get('individuals', {})
    
    if username in indiv.get('tier1', []):
        return "T1"
    elif username in indiv.get('tier2', []):
        return "T2"
    elif username in indiv.get('tier3', []):
        return "T3"
    elif username in config['kols'].get('organizations_crypto', []):
        return "Org-Crypto"
    elif username in config['kols'].get('organizations_ai', []):
        return "Org-AI"
    elif username in config['kols'].get('fundrasing', []):
        return "Funding"
    return "?"

def detect_breaking_news(all_tweets: list) -> list:
    """Detect potential breaking news."""
    news_keywords = ['breaking', 'announcing', 'launched', 'partnership', 
                     'acquisition', 'hack', 'exploit', 'scam', 'arrested',
                     'sec', 'regulatory', 'approval', 'rejected']
    
    candidates = [t for t in all_tweets if t['engagement'] >= 100 and not t.get('is_retweet', False)]
    
    news = []
    for tweet in candidates:
        text_lower = tweet['text'].lower()
        score = sum(2 for kw in news_keywords[:5] if kw in text_lower)  # announcements
        score += sum(3 for kw in news_keywords[5:] if kw in text_lower)  # urgent news
        
        if score > 0:
            tweet['_news_score'] = score
            news.append(tweet)
    
    return sorted(news, key=lambda t: (t.get('_news_score', 0), t['engagement']), reverse=True)[:5]

def group_kol_by_tier(kol_tweets: list, config: dict) -> dict:
    """Group KOL tweets by tier with analysis."""
    grouped = defaultdict(list)
    
    for tweet in kol_tweets:
        tier = classify_tier(tweet['author'], config)
        tweet['tier'] = tier
        grouped[tier].append(tweet)
    
    # Sort each tier by engagement
    for tier in grouped:
        grouped[tier] = sorted(grouped[tier], key=lambda t: t['engagement'], reverse=True)
    
    return dict(grouped)

def analyze_narrative_sentiment(narrative: dict) -> str:
    """Analyze overall narrative sentiment."""
    texts = [t['text'].lower() for t in narrative.get('tweets', [])[:10]]
    full_text = ' '.join(texts)
    
    bullish = ['bullish', 'buy', 'long', 'moon', 'pump', 'breakout', 'growth']
    bearish = ['bearish', 'sell', 'short', 'dump', 'crash', 'bubble', 'correction']
    
    b_score = sum(full_text.count(w) for w in bullish)
    be_score = sum(full_text.count(w) for w in bearish)
    
    if b_score > be_score * 1.5:
        return "Bullish momentum"
    elif be_score > b_score * 1.5:
        return "Bearish concerns"
    elif b_score > 0 or be_score > 0:
        return "Mixed sentiment"
    return "Neutral discussion"

def detect_funding_raises(tweets: list) -> list:
    """Detect and extract funding announcements."""
    funding_list = []
    
    for tweet in tweets:
        info = parse_funding_info(tweet['text'])
        if info:
            info['tweet'] = tweet
            info['author'] = tweet['author']
            funding_list.append(info)
    
    return funding_list

def generate_executive_summary(narratives: list, kol_by_tier: dict, 
                               funding: list, breaking: list) -> str:
    """Generate executive summary."""
    summary_parts = []
    
    # Top themes
    if narratives:
        top_3 = [n['topic'] for n in narratives[:3]]
        summary_parts.append(f"Top themes: {', '.join(top_3)}")
    
    # Notable KOL activity
    tier1_count = len(kol_by_tier.get('T1', []))
    if tier1_count > 0:
        summary_parts.append(f"Tier 1 KOLs active: {tier1_count}")
    
    # Funding activity
    if funding:
        summary_parts.append(f"{len(funding)} funding rounds announced")
    
    # Urgent news
    if breaking:
        urgent = [b for b in breaking if b.get('_news_score', 0) >= 3]
        if urgent:
            summary_parts.append(f"⚠️ {len(urgent)} potential breaking news items")
    
    return " | ".join(summary_parts) if summary_parts else "No major trends detected"

def render_enhanced_output(context: dict) -> str:
    """Render enhanced Telegram output with all sections."""
    lines = [
        f"🎯 *SENTINEL SCAN* — {context['date']}",
        "",
        f"📋 *Executive Summary*: {context['executive_summary']}",
        "",
    ]
    
    # Breaking News
    if context.get('breaking_news'):
        lines.append("🗞️ *Breaking News*")
        for news in context['breaking_news'][:3]:
            preview = news['text'][:150] + ('...' if len(news['text']) > 150 else '')
            lines.append(f"→ @{news['author']}: \"{preview}\"")
            lines.append(f"  👍 {news['likes']} | 🔁 {news['retweets']}")
            lines.append("")
    
    # Funding Raises
    if context.get('funding_raises'):
        lines.append("💰 *Funding Raises*")
        for deal in context['funding_raises'][:5]:
            project = deal.get('project', 'Unknown Project')
            amount = deal.get('amount', 'Undisclosed')
            lines.append(f"→ {project}: *{amount}*")
            lines.append(f"  Announced by @{deal['author']}")
            lines.append("")
    
    # Tier 1 KOLs
    tier1 = context.get('kol_by_tier', {}).get('T1', [])
    if tier1:
        lines.append("👑 *Tier 1 KOL Insights*")
        for k in tier1[:5]:
            preview = k['text'][:120] + ('...' if len(k['text']) > 120 else '')
            sentiment = context.get('kol_sentiments', {}).get(k['author'], 'neutral')
            emoji = {'positive': '🟢', 'negative': '🔴', 'neutral': '⚪'}.get(sentiment, '⚪')
            lines.append(f"→ {emoji} @{k['author']}")
            lines.append(f"  \"{preview}\"")
            lines.append(f"  👍 {k['likes']} | 🔁 {k['retweets']}")
            lines.append("")
    
    # Tier 2 KOLs
    tier2 = context.get('kol_by_tier', {}).get('T2', [])
    if tier2:
        lines.append("⭐ *Tier 2 KOLs*")
        for k in tier2[:3]:
            preview = k['text'][:100] + ('...' if len(k['text']) > 100 else '')
            lines.append(f"→ @{k['author']}: \"{preview}\"")
            lines.append(f"  👍 {k['likes']}")
            lines.append("")
    
    # Organizations
    org_crypto = context.get('kol_by_tier', {}).get('Org-Crypto', [])
    org_ai = context.get('kol_by_tier', {}).get('Org-AI', [])
    if org_crypto or org_ai:
        lines.append("🏢 *Organizations*")
        for org in (org_crypto + org_ai)[:4]:
            preview = org['text'][:100] + ('...' if len(org['text']) > 100 else '')
            lines.append(f"→ @{org['author']}: \"{preview}\"")
            lines.append("")
    
    # Top Narratives
    if context.get('narratives'):
        lines.append("📊 *Top Narratives*")
        for n in context['narratives'][:5]:
            emoji = {'positive': '🟢', 'negative': '🔴', 'neutral': '⚪'}.get(n.get('sentiment', 'neutral'), '⚪')
            momentum = analyze_narrative_sentiment(n)
            lines.append(f"→ *{n['topic']}* — {n['tweet_count']} tweets {emoji}")
            lines.append(f"  {momentum}")
            if n.get('top_author'):
                lines.append(f"  Top: @{n['top_author']}")
            lines.append("")
    
    # Contrarian Takes
    if context.get('contrarian_takes'):
        lines.append("💡 *Contrarian Takes*")
        for t in context['contrarian_takes'][:2]:
            preview = t['text'][:120] + ('...' if len(t['text']) > 120 else '')
            lines.append(f"→ @{t['author']}: \"{preview}\"")
            lines.append(f"  Engagement: {t['engagement']}")
            lines.append("")
    
    # Stats
    lines.append(f"—")
    lines.append(f"_Accounts: {context.get('total_accounts', 0)} | "
                 f"Tweets: {context.get('total_tweets', 0)} | "
                 f"Runtime: {context.get('runtime', 0)}s_")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Sentinel Scanner v2 - Enhanced')
    parser.add_argument('--config', '-c', type=Path, default=DEFAULT_CONFIG,
                        help='Config file path')
    parser.add_argument('--output', '-o', type=str, default='telegram',
                        choices=['telegram', 'markdown', 'json'],
                        help='Output format')
    parser.add_argument('--quick', '-q', action='store_true',
                        help='Quick scan mode')
    args = parser.parse_args()
    
    global sentiment_keywords
    
    # Load config
    config = load_config(args.config)
    sentiment_keywords = config.get('sentiment', {})
    scan_config = config.get('scan', {})
    enabled = config.get('enabled_tiers', {})
    
    # Adjust for quick mode
    tweets_per_kol = 5 if args.quick else 10
    tweets_per_kw = 10 if args.quick else 20
    min_engagement = scan_config.get('min_engagement', 50)
    max_age = scan_config.get('max_age_hours', 24)
    
    start_time = datetime.now()
    all_tweets = []
    
    # --- SCAN KOLS BY TIER ---
    print("Scanning KOLs...", file=sys.stderr)
    
    # Build account lists
    accounts = []
    indiv = config['kols'].get('individuals', {})
    
    if enabled.get('individuals_tier1'):
        for acc in indiv.get('tier1', []):
            accounts.append((acc, 'T1'))
    if enabled.get('individuals_tier2'):
        for acc in indiv.get('tier2', []):
            accounts.append((acc, 'T2'))
    if enabled.get('individuals_tier3'):
        for acc in indiv.get('tier3', []):
            accounts.append((acc, 'T3'))
    
    if enabled.get('organizations_crypto'):
        for acc in config['kols'].get('organizations_crypto', []):
            accounts.append((acc, 'Org-Crypto'))
    if enabled.get('organizations_ai'):
        for acc in config['kols'].get('organizations_ai', []):
            accounts.append((acc, 'Org-AI'))
    
    # SCAN KOLs
    for username, tier in accounts:
        try:
            tweets = fetch_user_tweets(username, tweets_per_kol, max_age)
            tweets = [t for t in tweets if t['engagement'] >= min_engagement]
            all_tweets.extend(tweets)
            print(f"  ✓ {username} ({tier}): {len(tweets)} tweets", file=sys.stderr)
            # Rate limit protection
            time.sleep(random.uniform(2, 4))
        except Exception as e:
            print(f"  ✗ {username}: {e}", file=sys.stderr)
    
    # --- SCAN FUNDING RAISE ACCOUNTS ---
    funding_accounts = config['kols'].get('fundrasing', [])
    funding_tweets = []
    
    if funding_accounts:
        print("\nScanning Funding Raise accounts...", file=sys.stderr)
        for username in funding_accounts:
            try:
                tweets = fetch_user_tweets(username, 20, 48)  # Lookback 48h for funding
                # Lower threshold for funding tweets
                tweets = [t for t in tweets if t['engagement'] >= 10]
                funding_tweets.extend(tweets)
                print(f"  ✓ {username}: {len(tweets)} tweets", file=sys.stderr)
                time.sleep(random.uniform(1, 2))
            except Exception as e:
                print(f"  ✗ {username}: {e}", file=sys.stderr)
    
    # --- SCAN KEYWORDS ---
    print("\nScanning keywords...", file=sys.stderr)
    keyword_tweets = []
    all_keywords = []
    
    if config.get('enabled_categories', {}).get('evergreen', True):
        all_keywords.extend(config['keywords'].get('evergreen', []))
    if config.get('enabled_categories', {}).get('trending', True):
        all_keywords.extend(config['keywords'].get('trending', []))
    
    for kw in all_keywords:
        try:
            tweets = fetch_user_tweets(kw, tweets_per_kw, max_age) if len(kw) > 15 else \
                     search_keyword(kw, tweets_per_kw, max_age)
            keyword_tweets.extend(tweets)
            print(f"  ✓ '{kw}': {len(tweets)} tweets", file=sys.stderr)
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            print(f"  ✗ '{kw}': {e}", file=sys.stderr)
    
    # --- ANALYZE ---
    print("\nAnalyzing...", file=sys.stderr)
    
    # Combine and deduplicate
    all_tweets += funding_tweets + keyword_tweets
    seen = set()
    all_tweets = [t for t in all_tweets if t['id'] not in seen and not seen.add(t['id'])]
    
    # Group by tier
    kol_by_tier = group_kol_by_tier([t for t in all_tweets 
                                    if classify_tier(t['author'], config) not in ['?', 'Funding']], config)
    
    # Detect funding raises
    funding_raises = detect_funding_raises(funding_tweets)
    
    # Detect breaking news
    breaking_news = detect_breaking_news(all_tweets)
    
    # Detect narratives
    narratives = []
    kw_map = defaultdict(lambda: {'tweets': [], 'engagement': 0})
    
    for tweet in all_tweets:
        text_lower = tweet['text'].lower()
        for kw in all_keywords:
            if kw.lower() in text_lower:
                kw_map[kw]['tweets'].append(tweet)
                kw_map[kw]['engagement'] += tweet['engagement']
    
    for topic, data in sorted(kw_map.items(), key=lambda x: len(x[1]['tweets']), reverse=True)[:10]:
        if data['tweets']:
            sample = data['tweets'][:5]
            sentiments = [analyze_sentiment(t['text']) for t in sample]
            dominant = max(set(sentiments), key=sentiments.count)
            
            narratives.append({
                'topic': topic,
                'tweet_count': len(data['tweets']),
                'total_engagement': data['engagement'],
                'sentiment': dominant,
                'top_author': max(sample, key=lambda t: t['engagement'])['author'] if sample else None,
                'tweets': data['tweets']
            })
    
    # Find contrarian takes
    contrarian = [t for t in all_tweets 
                  if t['engagement'] >= 20 and not t.get('is_retweet')]
    contrarian_keywords = ['bearish', 'overvalued', 'bubble', 'crash', 'sell', 
                          'short', 'fad', 'hype', 'overrated', 'disappointed', 
                          'concern', 'risk', 'disagree', 'skeptical', 'warning']
    
    result = []
    for t in contrarian:
        text_lower = t['text'].lower()
        score = sum(1 for kw in contrarian_keywords if kw in text_lower)
        if t['likes'] > 0 and t['replies'] / t['likes'] > 0.3:
            score += 2
        if score > 0:
            t['_contrarian_score'] = score
            result.append(t)
    
    contrarian = sorted(result, key=lambda t: (t.get('_contrarian_score', 0), t['engagement']), 
                       reverse=True)[:3]
    
    # --- BUILD CONTEXT ---
    runtime = (datetime.now() - start_time).total_seconds()
    
    context = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'executive_summary': generate_executive_summary(narratives, kol_by_tier, funding_raises, breaking_news),
        'breaking_news': breaking_news,
        'funding_raises': funding_raises,
        'kol_by_tier': kol_by_tier,
        'narratives': narratives,
        'contrarian_takes': contrarian,
        'total_accounts': len(accounts) + len(funding_accounts),
        'total_keywords': len(all_keywords),
        'total_tweets': len(all_tweets),
        'runtime': round(runtime, 1)
    }
    
    # --- GENERATE FULL MARKDOWN REPORT ---
    date_str = datetime.now().strftime('%d-%m-%Y')
    full_report = generate_full_report(context)
    
    # --- SAVE TO FILE ---
    output_dir = DEFAULT_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    
    report_filename = f"{date_str}-daily-report.md"
    report_path = output_dir / report_filename
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(full_report)
    
    print(f"\n📄 Full report saved to: {report_path}", file=sys.stderr)
    
    # --- GENERATE HIGHLIGHTS FOR TELEGRAM ---
    highlights = generate_highlights(context)
    
    # --- OUTPUT ---
    if args.output == 'telegram':
        print(highlights)
    elif args.output == 'json':
        import json
        output_data = {
            'highlights': highlights,
            'report_path': str(report_path),
            'context': context
        }
        print(json.dumps(output_data, indent=2, default=str))
    else:
        print(full_report)


def generate_full_report(context: dict) -> str:
    """Generate detailed Markdown report."""
    lines = [
        f"# Sentinel Scan Daily Report",
        f"",
        f"**Date:** {context['date']}",
        f"**Runtime:** {context['runtime']}s",
        f"**Total Accounts Scanned:** {context['total_accounts']}",
        f"**Total Keywords:** {context['total_keywords']}",
        f"**Total Tweets Analyzed:** {context['total_tweets']}",
        f"",
        f"---",
        f"",
    ]
    
    # Breaking News
    if context.get('breaking_news'):
        lines.extend([
            f"## 🗞️ Breaking News",
            f""
        ])
        for news in context['breaking_news'][:5]:
            lines.append(f"- **@{news['author']}**: {news['text'][:200]}...")
            lines.append(f"  Engagement: 👍 {news.get('likes', 0)} | 🔁 {news.get('retweets', 0)}")
            lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
    
    # Funding Raises
    if context.get('funding_raises'):
        lines.extend([
            f"## 💰 Funding Raises",
            f""
        ])
        for fund in context['funding_raises'][:10]:
            lines.append(f"- **{fund.get('project', 'Unknown')}**: {fund.get('amount', 'Amount TBA')}")
            lines.append(f"  Source: @{fund.get('source', 'unknown')}")
            lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
    
    # KOL by Tier
    lines.extend([
        f"## 👑 KOL Summary by Tier",
        f""
    ])
    
    # Group by tier
    tiers_grouped = defaultdict(list)
    for kol in context.get('kol_insights', []):
        tier = kol.get('tier', '?')
        if 'T1' in tier:
            tier_cat = 'Tier 1 - Elite'
        elif 'T2' in tier:
            tier_cat = 'Tier 2 - Experts'
        elif 'T3' in tier:
            tier_cat = 'Tier 3 - Emerging'
        elif 'Org-Crypto' in tier:
            tier_cat = 'Organizations - Crypto'
        elif 'Org-AI' in tier:
            tier_cat = 'Organizations - AI/Tech'
        else:
            tier_cat = 'Others'
        tiers_grouped[tier_cat].append(kol)
    
    for tier_name in ['Tier 1 - Elite', 'Tier 2 - Experts', 'Tier 3 - Emerging', 
                      'Organizations - Crypto', 'Organizations - AI/Tech', 'Others']:
        if tier_name in tiers_grouped:
            lines.append(f"### {tier_name}")
            lines.append(f"")
            for kol in tiers_grouped[tier_name][:10]:
                lines.append(f"**@{kol['author']}**:")
                lines.append(f"> {kol['text'][:300]}...")
                lines.append(f"")
                lines.append(f"👍 {kol.get('likes', 0)} | 🔁 {kol.get('retweets', 0)} | 💬 {kol.get('replies', 0)}")
                lines.append(f"")
                lines.append(f"**Analysis:** {kol.get('analysis', 'N/A')}")
                lines.append(f"")
            lines.append(f"---")
            lines.append(f"")
    
    # Market Narratives
    if context.get('narratives'):
        lines.extend([
            f"## 📊 Market Narratives",
            f""
        ])
        for nar in context['narratives'][:10]:
            emoji = {'positive': '🟢', 'negative': '🔴', 'neutral': '⚪'}.get(nar.get('sentiment'), '⚪')
            lines.append(f"### {emoji} {nar['topic']} ({nar['tweet_count']} tweets)")
            lines.append(f"")
            lines.append(f"**Top Tweet**: @{nar['top_author']}")
            lines.append(f"> {nar['top_tweet'][:200]}...")
            lines.append(f"")
            lines.append(f"**Engagement:** {nar['total_engagement']} | **Sentiment:** {nar.get('sentiment', 'neutral')}")
            if nar.get('detailed_summary'):
                lines.append(f"")
                lines.append(f"**Summary:** {nar['detailed_summary']}")
            lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
    
    # Contrarian Takes
    if context.get('contrarian_takes'):
        lines.extend([
            f"## 💡 Contrarian Takes & Debates",
            f""
        ])
        for take in context['contrarian_takes'][:5]:
            lines.append(f"**@{take['author']}**:")
            lines.append(f"> {take['text'][:300]}...")
            lines.append(f"")
            lines.append(f"👍 {take.get('likes', 0)} | 🔁 {take.get('retweets', 0)} | 💬 {take.get('replies', 0)}")
            lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
    
    # Executive Summary
    lines.extend([
        f"## 📝 Executive Summary",
        f""
    ])
    exec_summary = generate_executive_summary(
        context.get('narratives', []), 
        context.get('kol_insights', []),
        context.get('funding_raises', []),
        context.get('breaking_news', [])
    )
    lines.append(exec_summary)
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"*Report generated by Sentinel Scanner v2*")
    
    return '\n'.join(lines)


def generate_highlights(context: dict) -> str:
    """Generate Telegram-friendly highlights."""
    lines = [
        f"🎯 *SENTINEL SCAN HIGHLIGHTS* — {context['date']}",
        f"",
    ]
    
    # Top 3 Key Insights
    lines.append(f"🔥 *3 THINGS TO KNOW*")
    lines.append(f"")
    
    kol_highlights = context.get('kol_insights', [])[:3]
    for i, kol in enumerate(kol_highlights, 1):
        text_preview = kol['text'][:100] if len(kol['text']) > 100 else kol['text']
        lines.append(f"{i}. *@{kol['author']}* ({kol.get('tier', '?')}): \"{text_preview}...\"")
        lines.append(f"   👍 {kol.get('likes', 0)} | 🔁 {kol.get('retweets', 0)}")
        lines.append(f"")
    
    # Funding Alert
    if context.get('funding_raises'):
        lines.append(f"💰 *FUNDING ALERT*")
        lines.append(f"")
        for fund in context['funding_raises'][:2]:
            proj = fund.get('project', 'Unknown')
            amount = fund.get('amount', 'TBA')
            lines.append(f"→ *{proj}*: {amount}")
        lines.append(f"")
    
    # Trending Narratives
    lines.append(f"📊 *TRENDING*")
    lines.append(f"")
    for nar in context.get('narratives', [])[:3]:
        emoji = {'positive': '🟢', 'negative': '🔴', 'neutral': '⚪'}.get(nar.get('sentiment'), '⚪')
        lines.append(f"{emoji} *{nar['topic']}* — {nar['tweet_count']} tweets")
    lines.append(f"")
    
    # CTA
    lines.append(f"📄 *Full report saved to:*")
    lines.append(f"`working/X/report/daily/{context['date']}-daily-report.md`")
    lines.append(f"")
    lines.append(f"— _Scanned {context['total_accounts']} accounts • {context['total_keywords']} keywords • {context['total_tweets']} tweets_")
    
    return '\n'.join(lines)



if __name__ == '__main__':
    main()
