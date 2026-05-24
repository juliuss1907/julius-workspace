#!/usr/bin/env python3
"""
Sentinel Scanner v3 - Clean rewrite
Output: Telegram (stdout) + Markdown file + JSON data
"""

import subprocess
import yaml
import json
import re
import sys
import os
import time
import random
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_CONFIG = PROJECT_DIR / "config.yaml"
DAILY_REPORT_DIR = Path("/home/julius/julius-workspace/working/X/report/daily")

# Ensure output dir exists
DAILY_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def run_twitter(args: list, timeout: int = 60) -> dict:
    """Run twitter CLI."""
    cmd = ["twitter"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            return {}
        return yaml.safe_load(result.stdout) or {}
    except:
        return {}


def parse_tweet(tweet: dict, default_author: str = "unknown") -> dict:
    """Normalize tweet data."""
    metrics = tweet.get("metrics", {})
    text = tweet.get("text", "")
    # Remove URLs
    text = re.sub(r'http\S+', '', text).strip()
    
    return {
        "id": str(tweet.get("id", "")),
        "author": tweet.get("author", {}).get("screenName", default_author),
        "text": text[:500],  # Limit length
        "likes": metrics.get("likes", 0),
        "retweets": metrics.get("retweets", 0),
        "replies": metrics.get("replies", 0),
        "views": metrics.get("views", 0),  # Add views
        "engagement": metrics.get("likes", 0) + metrics.get("retweets", 0) + metrics.get("replies", 0),
        "created_at": tweet.get("createdAtISO", ""),
    }


def fetch_user_posts(username: str, count: int = 10, max_age: int = 24) -> list:
    """Fetch user posts."""
    data = run_twitter(["user-posts", username, "-n", str(count)])
    if not data or "data" not in data:
        return []
    
    tweets = []
    cutoff = datetime.now() - timedelta(hours=max_age)
    
    for t in data["data"][:count]:
        try:
            created = t.get("createdAtISO", "").replace("+00:00", "")
            if not created:
                continue
            tweet_time = datetime.fromisoformat(created)
            if tweet_time < cutoff:
                continue
            tweets.append(parse_tweet(t, username))
        except:
            continue
    
    return tweets


def is_product_update(text: str) -> bool:
    """Detect if tweet is about product update or announcement."""
    product_keywords = [
        "launch", "announcing", "launched", "new feature", "product update",
        "now live", "shipping", "released", "release", "update", "v2", "v3",
        "version", "beta", "alpha", "mainnet", "testnet", "integration",
        "partnership", "collaboration", "new partnership"
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in product_keywords)


def search_keyword(keyword: str, count: int = 20, max_age: int = 24) -> list:
    """Search by keyword."""
    data = run_twitter(["search", keyword, "-n", str(count)])
    if not data or "data" not in data:
        return []
    
    tweets = []
    cutoff = datetime.now() - timedelta(hours=max_age)
    
    for t in data["data"][:count]:
        try:
            created = t.get("createdAtISO", "").replace("+00:00", "")
            if not created:
                continue
            tweet_time = datetime.fromisoformat(created)
            if tweet_time < cutoff:
                continue
            tweets.append(parse_tweet(t, "unknown"))
        except:
            continue
    
    return tweets


def load_config(path: Path) -> dict:
    """Load YAML config."""
    with open(path) as f:
        return yaml.safe_load(f)


def analyze_sentiment(text: str) -> str:
    """Simple sentiment check."""
    text_lower = text.lower()
    pos_words = ["bullish", "buy", "long", "moon", "pump", "growth", "opportunity"]
    neg_words = ["bearish", "sell", "short", "dump", "crash", "panic", "fud"]
    
    pos_score = sum(1 for w in pos_words if w in text_lower)
    neg_score = sum(1 for w in neg_words if w in text_lower)
    
    if pos_score > neg_score:
        return "positive"
    elif neg_score > pos_score:
        return "negative"
    return "neutral"


def detect_breaking_news(tweets: list) -> list:
    """Find high-engagement announcements."""
    keywords = ["announce", "launch", "partnership", "funding", "acquired", "hack", "security"]
    news = []
    for t in tweets:
        if t["engagement"] > 100:
            text_lower = t["text"].lower()
            if any(k in text_lower for k in keywords):
                news.append(t)
    return sorted(news, key=lambda x: x["engagement"], reverse=True)[:5]


def detect_funding(text: str) -> dict:
    """Extract funding info including project name."""
    # Extract amount
    amount_patterns = [
        r"(\$[\d,.]+[MK]?)\s+(?:seed|series|funding|raised|investment|round)",
        r"(?:raised|secures?)\s+(\$[\d,.]+[MK]?)",
    ]
    amount = None
    for p in amount_patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            amount = m.group(1)
            break
    
    # Extract project name - look for @mentions at start or common patterns
    project = None
    # Pattern 1: @name at beginning
    name_match = re.search(r'^@[\w_]+', text)
    if name_match:
        project = name_match.group(0)[1:]  # Remove @
    else:
        # Pattern 2: "@name raised" or "@name secured"
        raised_match = re.search(r'@([\w_]+)\s+(?:raised|secured|announced)', text, re.IGNORECASE)
        if raised_match:
            project = raised_match.group(1)
    
    if amount:
        return {
            "amount": amount,
            "project": project or "Unknown",
            "text": text
        }
    return None


def generate_markdown_report(context: dict) -> str:
    """Generate full Markdown report."""
    lines = [
        f"# Sentinel Scan Report - {context['date']}",
        f"",
        f"**Runtime:** {context['runtime']}s | **Accounts:** {context['total_accounts']} | **Tweets:** {context['total_tweets']}",
        f"",
        "---",
        "",
    ]
    
    # Breaking News
    if context.get("breaking_news"):
        lines.extend(["## 🗞️ Breaking News", ""])
        for news in context["breaking_news"][:5]:
            lines.append(f"- **@{news['author']}**: {news['text'][:250]}...")
            lines.append(f"  [Link](https://x.com/{news['author']}/status/{news['id']})")
            lines.append(f"  Engagement: 👍{news['likes']} 🔁{news['retweets']}")
            lines.append("")
        lines.extend(["---", ""])
    
    # Funding
    if context.get("funding"):
        lines.extend(["## 💰 Funding Raises", ""])
        for f in context["funding"][:5]:
            project = f.get('project', 'Unknown')
            amount = f.get('amount', 'N/A')
            text = f['text'][:250] if len(f['text']) > 250 else f['text']
            # Format: @project - $X: Description...
            lines.append(f"- **@{project} - {amount}**: {text}...")
            lines.append(f"  [Link](https://x.com/{f.get('source', 'unknown')}/status/{f.get('id', '')})")
            lines.append("")
        lines.extend(["---", ""])
    
    # KOL by Tier - Filter by views
    if context.get("kol_by_tier"):
        lines.extend(["## 👑 KOL Summary", ""])
        
        # Define view thresholds per tier — from config.yaml
        view_thresholds = context.get("view_thresholds", {})
        
        for tier, kols in context["kol_by_tier"].items():
            # Skip organizations here - handle separately
            if tier in ["Org-Crypto", "Org-AI"]:
                continue
                
            threshold = view_thresholds.get(tier, 5000)
            # Filter by views
            filtered_kols = [k for k in kols if k.get("views", 0) >= threshold]
            
            if not filtered_kols:
                continue
                
            lines.append(f"### {tier} (>{threshold:,} views)")
            lines.append("")
            for kol in filtered_kols:
                lines.append(f"**@{kol['author']}** 👍{kol['likes']} 🔁{kol['retweets']} 👁️{kol.get('views', 0):,}")
                lines.append(f"> {kol['text'][:300]}...")
                lines.append(f"[Xem tweet](https://x.com/{kol['author']}/status/{kol['id']})")
                lines.append("")
        
        # Organizations - only with product updates
        org_tiers = ["Org-Crypto", "Org-AI"]
        for tier in org_tiers:
            if tier not in context["kol_by_tier"]:
                continue
            kols = context["kol_by_tier"][tier]
            # Filter only product updates
            product_updates = [k for k in kols if k.get("is_product_update", False)]
            if not product_updates:
                continue
            lines.append(f"### {tier} - Product Updates")
            lines.append("")
            for kol in product_updates[:10]:  # Max 10
                lines.append(f"**@{kol['author']}** 👍{kol['likes']} 🔁{kol['retweets']}")
                lines.append(f"> {kol['text'][:300]}...")
                lines.append(f"[Xem tweet](https://x.com/{kol['author']}/status/{kol['id']})")
                lines.append("")
        
        lines.extend(["---", ""])
    
    # Narratives
    if context.get("narratives"):
        lines.extend(["## 📊 Market Narratives", ""])
        for n in context["narratives"][:10]:
            emoji = {"positive": "🟢", "negative": "🔴", "neutral": "⚪"}.get(n["sentiment"], "⚪")
            lines.append(f"### {emoji} {n['topic'].upper()} ({n['count']} tweets)")
            lines.append("")
            # Show 3-5 tweets as bullet points
            for tweet in n["tweets"][:5]:
                text_preview = tweet['text'][:120] if len(tweet['text']) > 120 else tweet['text']
                lines.append(f"- **@{tweet['author']}**: {text_preview}...")
                lines.append(f"  [Link](https://x.com/{tweet['author']}/status/{tweet['id']}) 👍{tweet['likes']} 🔁{tweet['retweets']}")
                lines.append("")
            lines.append("")
        lines.extend(["---", ""])
    
    # Contrarian
    if context.get("contrarian"):
        lines.extend(["## 💡 Contrarian Takes", ""])
        for t in context["contrarian"][:3]:
            lines.append(f"**@{t['author']}**: {t['text'][:250]}...")
            lines.append(f"[Link](https://x.com/{t['author']}/status/{t['id']})")
            lines.append("")
    
    # Executive Summary
    lines.extend(["## 📝 Executive Summary", "", context.get("summary", "N/A"), ""])
    lines.append("---")
    lines.append("*Generated by Sentinel Scanner v3*")
    
    return "\n".join(lines)


def generate_telegram_highlights(context: dict) -> str:
    """Generate short Telegram message."""
    lines = [
        f"🎯 *SENTINEL SCAN* — {context['date']}",
        "",
        "🔥 *Key Insights:*",
    ]
    
    # Top 3 KOLs
    for kol in context.get("top_kols", [])[:3]:
        text = kol["text"][:80] + "..." if len(kol["text"]) > 80 else kol["text"]
        lines.append(f"• *@{kol['author']}*: \"{text}\" 👍{kol['likes']}")
    
    lines.append("")
    
    # Hot narratives
    if context.get("narratives"):
        lines.append("📊 *Trending:*")
        for n in context["narratives"][:3]:
            emoji = {"positive": "🟢", "negative": "🔴", "neutral": "⚪"}.get(n["sentiment"], "⚪")
            lines.append(f"{emoji} *{n['topic']}* — {n['count']} tweets")
    
    # Funding alert
    if context.get("funding"):
        lines.append("")
        lines.append("💰 *Funding:*")
        for f in context["funding"][:2]:
            lines.append(f"→ {f.get('amount', 'New funding')} detected")
    
    lines.append("")
    lines.append(f"📄 *Full report:* `{context['report_path']}`")
    lines.append(f"⏱️ Runtime: {context['runtime']}s")
    
    return "\n".join(lines)


def main():
    config = load_config(DEFAULT_CONFIG)
    is_quick = config.get("quick-mode", False)
    
    start_time = datetime.now()
    
    all_tweets = []
    funding_tweets = []
    
    # Scan KOLs
    print("Scanning KOLs...", file=sys.stderr)
    kols = []
    
    indiv = config["kols"].get("individuals", {})
    enabled = config.get("enabled_tiers", {})
    
    if enabled.get("individuals_tier1"):
        kols.extend([(u, "T1") for u in indiv.get("tier1", [])])
    if enabled.get("individuals_tier2"):
        kols.extend([(u, "T2") for u in indiv.get("tier2", [])])
    if enabled.get("individuals_tier3"):
        kols.extend([(u, "T3") for u in indiv.get("tier3", [])])
    if enabled.get("organizations_crypto"):
        kols.extend([(u, "Org-Crypto") for u in config["kols"].get("organizations_crypto", [])])
    if enabled.get("organizations_ai"):
        kols.extend([(u, "Org-AI") for u in config["kols"].get("organizations_ai", [])])
    
    # Quick mode: fewer accounts
    if is_quick:
        kols = kols[:15]  # Only first 15
    
    tweets_per_account = 5 if is_quick else 10
    min_engagement = config.get("scan", {}).get("min_engagement", 50)
    
    for username, tier in kols:
        tweets = fetch_user_posts(username, tweets_per_account)
        tweets = [t for t in tweets if t["engagement"] >= min_engagement]
        for t in tweets:
            t["tier"] = tier
            # For organizations, check if this is a product update
            if "Org-" in tier:
                t["is_product_update"] = is_product_update(t["text"])
        all_tweets.extend(tweets)
        print(f"  ✓ {username} ({tier}): {len(tweets)}", file=sys.stderr)
        time.sleep(random.uniform(1, 2))  # Rate limit
    
    # Scan Funding accounts (special handling)
    funding_accounts = config["kols"].get("fundrasing", [])
    if funding_accounts:
        print("Scanning Funding accounts...", file=sys.stderr)
        for username in funding_accounts:
            tweets = fetch_user_posts(username, 20, 48)  # 48h lookback
            for t in tweets:
                fund_info = detect_funding(t["text"])
                if fund_info:
                    t["funding"] = fund_info
                    funding_tweets.append(t)
            time.sleep(1)
    
    # Scan Keywords
    print("Scanning keywords...", file=sys.stderr)
    keywords = []
    if config.get("enabled_categories", {}).get("evergreen"):
        keywords.extend(config["keywords"].get("evergreen", []))
    if config.get("enabled_categories", {}).get("trending"):
        keywords.extend(config["keywords"].get("trending", []))
    
    if is_quick:
        keywords = keywords[:10]
    
    tweets_per_kw = 10 if is_quick else 20
    
    for kw in keywords:
        tweets = search_keyword(kw, tweets_per_kw)
        all_tweets.extend(tweets)
        print(f"  ✓ '{kw}': {len(tweets)}", file=sys.stderr)
        time.sleep(random.uniform(1, 2))
    
    # Deduplicate
    seen = set()
    all_tweets = [t for t in all_tweets if t["id"] not in seen and not seen.add(t["id"])]
    
    # Analysis
    breaking_news = detect_breaking_news(all_tweets)
    
    # Group by tier
    kol_by_tier = defaultdict(list)
    for t in all_tweets:
        if "tier" in t:
            kol_by_tier[t["tier"]].append(t)
    
    # Sort by engagement
    for tier in kol_by_tier:
        kol_by_tier[tier].sort(key=lambda x: x["engagement"], reverse=True)
    
    # Top KOLs overall
    top_kols = sorted([t for t in all_tweets if "tier" in t and "T1" in t["tier"]], 
                      key=lambda x: x["engagement"], reverse=True)[:10]
    
    # Narratives
    narratives = defaultdict(lambda: {"count": 0, "tweets": [], "sentiments": []})
    keyword_list = [k.lower() for k in keywords]
    
    for t in all_tweets:
        text_lower = t["text"].lower()
        for kw in keyword_list:
            if kw in text_lower:
                narratives[kw]["count"] += 1
                narratives[kw]["tweets"].append(t)
                narratives[kw]["sentiments"].append(analyze_sentiment(t["text"]))
    
    # Format narratives - include top 3-5 tweets per topic
    narrative_list = []
    for topic, data in sorted(narratives.items(), key=lambda x: x[1]["count"], reverse=True)[:10]:
        if data["count"] < 3:
            continue
        
        # Get top 3-5 tweets by engagement
        sorted_tweets = sorted(data["tweets"], key=lambda x: x["engagement"], reverse=True)
        top_tweets = sorted_tweets[:5]  # Max 5 tweets
        
        sentiments = data["sentiments"]
        sentiment = max(set(sentiments), key=sentiments.count) if sentiments else "neutral"
        
        narrative_list.append({
            "topic": topic,
            "count": data["count"],
            "sentiment": sentiment,
            "tweets": [{  # Store multiple tweets
                "author": t["author"],
                "text": t["text"],
                "id": t["id"],
                "likes": t["likes"],
                "retweets": t["retweets"]
            } for t in top_tweets],
        })
    
    # Contrarian takes (high replies relative to likes)
    contrarian = [t for t in all_tweets if t["likes"] > 50 and t["replies"] > t["likes"] * 0.2]
    contrarian.sort(key=lambda x: x["engagement"], reverse=True)
    
    # Executive summary
    summary_parts = []
    if narrative_list:
        top_nar = narrative_list[0]
        summary_parts.append(f"🔥 Top narrative: *{top_nar['topic']}* với {top_nar['count']} tweets ({top_nar['sentiment']})")
    if breaking_news:
        summary_parts.append(f"🗞️ {len(breaking_news)} breaking news items detected")
    if funding_tweets:
        summary_parts.append(f"💰 {len(funding_tweets)} funding announcements")
    
    summary = "\n\n".join(summary_parts) if summary_parts else "No major signals today."
    
    runtime = (datetime.now() - start_time).total_seconds()
    date_str = datetime.now().strftime("%d-%m-%Y")
    
    # Context
    context = {
        "date": date_str,
        "runtime": round(runtime, 1),
        "total_accounts": len(kols),
        "total_tweets": len(all_tweets),
        "breaking_news": breaking_news,
        "funding": [{"amount": t["funding"]["amount"], "project": t["funding"]["project"], "text": t["text"], "source": t["author"], "id": t["id"]} for t in funding_tweets[:5]],
        "kol_by_tier": dict(kol_by_tier),
        "top_kols": top_kols,
        "narratives": narrative_list,
        "contrarian": contrarian[:5],
        "summary": summary,
        "view_thresholds": config.get("view_thresholds", {}),
    }
    
    # Generate files
    report_md = generate_markdown_report(context)
    
    # Save Markdown report
    report_filename = f"{date_str}-daily-report.md"
    report_path = DAILY_REPORT_DIR / report_filename
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    
    context["report_path"] = str(report_path)
    
    # Save JSON data
    json_path = DAILY_REPORT_DIR / f"{date_str}-data.json"
    with open(json_path, "w") as f:
        json.dump(context, f, indent=2, default=str)
    
    # Generate Telegram message AFTER setting report_path
    telegram_msg = generate_telegram_highlights(context)
    
    print(f"\n✅ Report saved: {report_path}", file=sys.stderr)
    print(f"✅ Data saved: {json_path}", file=sys.stderr)
    
    # Output Telegram format to stdout
    print("\n" + telegram_msg)


if __name__ == "__main__":
    main()
