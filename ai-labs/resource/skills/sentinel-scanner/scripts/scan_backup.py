#!/usr/bin/env python3
"""
Sentinel Scanner — Crypto Twitter sentiment monitor
Scans KOL timelines and keyword searches to surface narratives and trends.
"""

import subprocess
import yaml
import re
import sys
import time
import random
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import argparse
import time
import random

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_CONFIG = PROJECT_DIR / "config.yaml"
DEFAULT_TEMPLATE = PROJECT_DIR / "templates" / "brief.j2"

def load_config(path: Path) -> dict:
    """Load YAML config file."""
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def parse_tweet_text(text: str) -> str:
    """Clean tweet text for display."""
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()


def run_twitter_cli(args: list, timeout: int = 60) -> dict:
    """Run twitter CLI and parse JSON output."""
    cmd = ["twitter"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            print(f"Warning: twitter CLI error ({args[0]}): {result.stderr[:200]}", file=sys.stderr)
            return {}
        # Parse YAML-like format or JSON
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


def fetch_user_tweets(username: str, count: int = 30, max_age_hours: int = 24) -> list:
    """Fetch recent tweets from a user."""
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
        except Exception as e:
            continue
    
    return tweets


def search_keyword(keyword: str, count: int = 50, max_age_hours: int = 24) -> list:
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
        except Exception as e:
            continue
    
    return tweets


def analyze_sentiment(text: str) -> str:
    """Simple keyword-based sentiment analysis."""
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


def detect_narratives(tweets: list, keywords: list) -> list:
    """Group tweets by keyword/narrative."""
    narratives = defaultdict(lambda: {'tweets': [], 'total_engagement': 0})
    
    for tweet in tweets:
        text_lower = tweet['text'].lower()
        matched = [kw for kw in keywords if kw.lower() in text_lower]
        
        for kw in matched:
            narratives[kw]['tweets'].append(tweet)
            narratives[kw]['total_engagement'] += tweet['engagement']
    
    result = []
    for topic, data in sorted(narratives.items(), key=lambda x: len(x[1]['tweets']), reverse=True):
        if not data['tweets']:
            continue
            
        top_tweet = max(data['tweets'], key=lambda t: t['engagement'])
        sample_text = ' '.join(t['text'] for t in data['tweets'][:5])
        
        result.append({
            'topic': topic,
            'tweet_count': len(data['tweets']),
            'total_engagement': data['total_engagement'],
            'top_tweet': top_tweet['text'],
            'top_author': top_tweet['author'],
            'top_engagement': top_tweet['engagement'],
            'sentiment': analyze_sentiment(sample_text)
        })
    
    return result


def find_contrarian_takes(all_tweets: list, min_engagement: int = 10) -> list:
    """Find tweets with high engagement that might be contrarian."""
    candidates = [t for t in all_tweets 
                  if t['engagement'] >= min_engagement 
                  and not t.get('is_retweet', False)]
    
    # Keywords indicating contrarian/unpopular opinion
    contrarian_keywords = [
        'bearish', 'overvalued', 'bubble', 'crash', 'sell', 'short',
        'fad', 'hype', 'overrated', 'disappointed', 'concern', 'risk',
        'disagree', 'wrong', 'skeptical', 'doubt', 'hesitant',
        'not convinced', 'overpriced', 'dump', 'correction', 'warning'
    ]
    
    result = []
    for tweet in candidates:
        text_lower = tweet['text'].lower()
        score = sum(1 for kw in contrarian_keywords if kw in text_lower)
        
        # High reply-to-like ratio = controversial
        if tweet['likes'] > 0 and tweet['replies'] / tweet['likes'] > 0.3:
            score += 2
        
        if score > 0:
            tweet['_contrarian_score'] = score
            result.append(tweet)
    
    return sorted(result, key=lambda t: (t.get('_contrarian_score', 0), t['engagement']), reverse=True)


def class_tier(username: str, config: dict) -> str:
    """Classify account tier."""
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
    return "?"


def render_simple_output(context: dict) -> str:
    """Render output without Jinja2."""
    lines = [
        f"🎯 *SENTINEL SCAN* — {context['date']}",
        ""
    ]
    
    # Narratives
    if context['narratives']:
        lines.append("📊 *Top Narratives*")
        for n in context['narratives'][:3]:
            emoji = {'positive': '🟢', 'negative': '🔴', 'neutral': '⚪'}.get(n['sentiment'], '⚪')
            lines.append(f"→ *{n['topic']}* — {n['tweet_count']} tweets {emoji}")
            preview = n['top_tweet'][:80] + ('...' if len(n['top_tweet']) > 80 else '')
            lines.append(f"  @{n['top_author']}: \"{preview}\"")
            lines.append("")
    
    # Contrarian takes
    if context['contrarian_takes']:
        lines.append("💡 *Contrarian Takes*")
        for t in context['contrarian_takes'][:2]:
            preview = t['text'][:100] + ('...' if len(t['text']) > 100 else '')
            lines.append(f"→ @{t['author']}: \"{preview}\"")
            lines.append(f"  👍 {t['likes']} | 🔁 {t['retweets']} | 💬 {t['replies']}")
            lines.append("")
    
    # KOL insights
    if context['kol_insights']:
        lines.append("🔥 *KOL Insights*")
        for k in context['kol_insights'][:5]:
            preview = k['text'][:80] + ('...' if len(k['text']) > 80 else '')
            lines.append(f"→ [{k.get('tier', '?')}] @{k['author']}: \"{preview}\"")
            lines.append(f"  👍 {k['likes']} | 🔁 {k['retweets']}")
            lines.append("")
    
    # Stats
    lines.append(f"—")
    lines.append(f"_Scanned {context['total_accounts']} accounts • {context['total_keywords']} keywords • {context['total_tweets']} tweets in {context['runtime']}s_")
    
    return '\n'.join(lines)


def scan_kols(individuals: dict, orgs_crypto: list, orgs_ai: list, 
              tweets_per_kol: int, max_age: int, min_engagement: int) -> list:
    """Scan all KOL timelines."""
    all_tweets = []
    
    # Build list of accounts to scan
    accounts = []
    
    for tier_name, tier_accounts in individuals.items():
        for acc in tier_accounts:
            accounts.append((acc, tier_name))
    
    for acc in orgs_crypto:
        accounts.append((acc, 'org_crypto'))
    
    for acc in orgs_ai:
        accounts.append((acc, 'org_ai'))
    
    print(f"Scanning {len(accounts)} accounts...", file=sys.stderr)
    
    # Sequential scan with delay (respect rate limits)
    for idx, (username, tier) in enumerate(accounts):
        try:
            tweets = fetch_user_tweets(username, tweets_per_kol, max_age)
            tweets = [t for t in tweets if t['engagement'] >= min_engagement]
            all_tweets.extend(tweets)
            print(f"  ✓ {username}: {len(tweets)} tweets", file=sys.stderr)
            
            # Delay between requests (2-4s) to avoid rate limits
            if idx < len(accounts) - 1:
                time.sleep(2 + random.random() * 2)
        except Exception as e:
            print(f"  ✗ {username}: {e}", file=sys.stderr)
            # Still delay on error
            if idx < len(accounts) - 1:
                time.sleep(2)
    
    return all_tweets


def scan_keywords(keywords: dict, tweets_per_kw: int, max_age: int) -> list:
    """Scan all keyword searches."""
    all_tweets = []
    keyword_list = []
    
    for cat, kws in keywords.items():
        keyword_list.extend(kws)
    
    print(f"\nScanning {len(keyword_list)} keywords...", file=sys.stderr)
    
    for idx, kw in enumerate(keyword_list):
        try:
            tweets = search_keyword(kw, tweets_per_kw, max_age)
            all_tweets.extend(tweets)
            print(f"  ✓ '{kw}': {len(tweets)} tweets", file=sys.stderr)
            
            # Delay between keyword searches (1-3s)
            if idx < len(keyword_list) - 1:
                time.sleep(1 + random.random() * 2)
        except Exception as e:
            print(f"  ✗ '{kw}': {e}", file=sys.stderr)
            if idx < len(keyword_list) - 1:
                time.sleep(1)
    
    return all_tweets


def main():
    parser = argparse.ArgumentParser(description='Sentinel Scanner - Crypto Twitter monitor')
    parser.add_argument('--config', '-c', type=Path, default=DEFAULT_CONFIG,
                        help='Config file path')
    parser.add_argument('--output', '-o', type=str, default='telegram',
                        choices=['telegram', 'markdown', 'json'],
                        help='Output format')
    parser.add_argument('--quick', '-q', action='store_true',
                        help='Quick scan: fewer tweets, smaller limits')
    args = parser.parse_args()
    
    global sentiment_keywords
    
    # Load config
    config = load_config(args.config)
    sentiment_keywords = config.get('sentiment', {})
    scan_config = config.get('scan', {})
    output_config = config.get('output', {})
    enabled = config.get('enabled_tiers', {})
    
    # Adjust for quick mode
    tweets_per_kol = 10 if args.quick else scan_config.get('tweets_per_kol', 30)
    tweets_per_kw = 20 if args.quick else scan_config.get('tweets_per_keyword', 50)
    min_engagement = scan_config.get('min_engagement', 50)
    max_age = scan_config.get('max_age_hours', 24)
    
    # Build account lists based on enabled tiers
    individuals = {}
    if enabled.get('individuals_tier1'):
        individuals['tier1'] = config['kols']['individuals'].get('tier1', [])
    if enabled.get('individuals_tier2'):
        individuals['tier2'] = config['kols']['individuals'].get('tier2', [])
    if enabled.get('individuals_tier3'):
        individuals['tier3'] = config['kols']['individuals'].get('tier3', [])
    
    orgs_crypto = config['kols'].get('organizations_crypto', []) if enabled.get('organizations_crypto') else []
    orgs_ai = config['kols'].get('organizations_ai', []) if enabled.get('organizations_ai') else []
    
    # Run scans
    start_time = datetime.now()
    
    kol_tweets = scan_kols(individuals, orgs_crypto, orgs_ai, 
                           tweets_per_kol, max_age, min_engagement)
    
    # Only search keywords if enabled
    keyword_tweets = []
    if config.get('enabled_categories', {}).get('evergreen', True) or \
       config.get('enabled_categories', {}).get('trending', True):
        keyword_tweets = scan_keywords(config.get('keywords', {}), tweets_per_kw, max_age)
    
    all_tweets = kol_tweets + keyword_tweets
    
    # Deduplicate by tweet ID
    seen = set()
    all_tweets = [t for t in all_tweets if t['id'] not in seen and not seen.add(t['id'])]
    
    # Analyze
    all_keywords = []
    if config.get('enabled_categories', {}).get('evergreen', True):
        all_keywords.extend(config['keywords'].get('evergreen', []))
    if config.get('enabled_categories', {}).get('trending', True):
        all_keywords.extend(config['keywords'].get('trending', []))
    
    narratives = detect_narratives(all_tweets, all_keywords)
    contrarian = find_contrarian_takes(all_tweets)
    
    # Build context
    runtime = (datetime.now() - start_time).total_seconds()
    context = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'narratives': narratives[:10],
        'contrarian_takes': contrarian[:3],
        'kol_insights': sorted(
            [t for t in kol_tweets if t['author'] in config['kols']['individuals'].get('tier1', [])],
            key=lambda t: t['engagement'],
            reverse=True
        )[:5],
        'total_accounts': len(individuals.get('tier1', [])) + len(individuals.get('tier2', [])) + 
                         len(individuals.get('tier3', [])) + len(orgs_crypto) + len(orgs_ai),
        'total_keywords': len(all_keywords),
        'total_tweets': len(all_tweets),
        'runtime': round(runtime, 1)
    }
    
    # Add tier info to insights
    for t in context['kol_insights']:
        t['tier'] = class_tier(t['author'], config)
    
    # Output
    if args.output == 'telegram':
        print(render_simple_output(context))
    elif args.output == 'json':
        import json
        print(json.dumps(context, indent=2))
    else:
        # Markdown
        print(render_simple_output(context).replace('*', ''))


if __name__ == '__main__':
    main()
