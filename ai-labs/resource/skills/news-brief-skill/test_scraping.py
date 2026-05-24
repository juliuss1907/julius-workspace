#!/usr/bin/env python3
"""Test script for news brief scraper without playwright dependencies."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# Load config
from config import TOPICS

def test_scrape_thefeed():
    """Simulate scraping thefeed.today for crypto news."""
    print("🌐 Scraping thefeed.today (Crypto filter)...")
    
    try:
        # For now, let's simulate scraping by returning some sample data
        # In real usage, this would use requests + BeautifulSoup
        
        # Sample data structure
        items = [
            {
                'title': 'Bitcoin ETF inflows surge past $500M as institutional adoption accelerates',
                'summary': 'Major financial institutions continue pouring capital into Bitcoin ETFs, with net inflows exceeding $500 million in the past 24 hours. Analysts point to increased institutional confidence in crypto as a legitimate asset class.',
                'link': 'https://example.com/news/bitcoin-etf-inflows',
                'source': 'thefeed.today',
                'topic_id': 'crypto',
                'topic_name': 'Crypto',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'engagement': {'type': 'views', 'value': 15000}
            },
            {
                'title': 'Ethereum layer-2 solutions reach all-time high in daily transactions',
                'summary': 'Layer-2 networks built on Ethereum have processed over 10 million transactions in the past day, showcasing the ecosystem\'s scalability improvements and growing user adoption.',
                'link': 'https://example.com/news/eth-l2-growth',
                'source': 'thefeed.today',
                'topic_id': 'crypto',
                'topic_name': 'Crypto',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'engagement': {'type': 'views', 'value': 8500}
            },
            {
                'title': 'Solana validator performance metrics improved by 40% after latest upgrade',
                'summary': 'The recent network upgrade has significantly improved Solana\'s validator efficiency, reducing latency and increasing transaction throughput across the blockchain.',
                'link': 'https://example.com/news/solana-upgrade',
                'source': 'thefeed.today',
                'topic_id': 'crypto',
                'topic_name': 'Crypto',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'engagement': {'type': 'views', 'value': 12000}
            }
        ]
        
        print(f"✅ Scraped {len(items)} items from thefeed.today")
        return items
        
    except Exception as e:
        print(f"❌ Error scraping thefeed: {e}")
        return []

def test_scrape_rss():
    """Simulate RSS scraping."""
    print("📡 Scraping RSS feeds...")
    
    try:
        # Sample RSS data
        items = [
            {
                'title': 'Major DeFi protocol announces $50M ecosystem fund',
                'summary': 'A leading decentralized finance protocol has launched a substantial fund to support developers and projects building on its platform, signaling confidence in DeFi\'s future growth.',
                'link': 'https://example.com/news/defi-fund',
                'source': 'rss',
                'topic_id': 'crypto',
                'topic_name': 'Crypto',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'engagement': {'type': 'authority', 'value': 30}  # high authority
            },
            {
                'title': 'CBDC pilots expand across Southeast Asia as nations explore digital currencies',
                'summary': 'Central banks in the region are accelerating CBDC research initiatives, with multiple pilot programs demonstrating the potential for digital fiat currencies in cross-border payments.',
                'link': 'https://example.com/news/cbdc-asia',
                'source': 'rss',
                'topic_id': 'crypto',
                'topic_name': 'Crypto',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'engagement': {'type': 'authority', 'value': 25}  # medium authority
            }
        ]
        
        print(f"✅ Scraped {len(items)} items from RSS")
        return items
        
    except Exception as e:
        print(f"❌ Error scraping RSS: {e}")
        return []

def save_test_data(items):
    """Save test data to JSON file."""
    os.makedirs('.state', exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    filename = f'.state/raw-{timestamp}.json'
    
    data = {
        'scraped_at': datetime.now(timezone.utc).isoformat(),
        'total_items': len(items),
        'topic_counts': {'crypto': len(items)},
        'sources': {'thefeed.today': 3, 'rss': 2},
        'items': items
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(items)} items to {filename}")
    return filename

def run_test_scraping():
    """Run full test scraping workflow."""
    print("🚀 Starting test news scraper...\n")
    
    all_items = []
    
    # Scrape thefeed
    thefeed_items = test_scrape_thefeed()
    all_items.extend(thefeed_items)
    
    # Scrape RSS
    rss_items = test_scrape_rss()
    all_items.extend(rss_items)
    
    # Save results
    print(f"\n✅ Test scrape complete: {len(all_items)} total items")
    
    # Save to JSON
    json_file = save_test_data(all_items)
    
    # Print summary
    print(f"\n📊 Scraping Summary:")
    print(f"   Total items: {len(all_items)}")
    print(f"   Sources: thefeed.today ({len(thefeed_items)}), RSS ({len(rss_items)})")
    print(f"   Topic: Crypto")
    print(f"\n💾 JSON saved to: {json_file}")
    
    return json_file

if __name__ == '__main__':
    json_file = run_test_scraping()
    print(f"\n✨ Ready for synthesize phase!")
    print(f"   Run: python3 synthesize.py")