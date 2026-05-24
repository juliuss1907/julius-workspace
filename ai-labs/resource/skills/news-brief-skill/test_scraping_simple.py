#!/usr/bin/env python3
"""Simple test script for news brief skill without external dependencies."""

import json
import os
from datetime import datetime, timezone

def run_simple_test():
    """Create test data for synthesize.py"""
    print("🧪 Creating test data for news brief skill...")
    
    # Sample crypto news items
    items = [
        {
            'title': 'Bitcoin ETFs attract $500M inflows as institutional adoption accelerates',
            'summary': 'Major financial institutions continue pouring capital into Bitcoin ETFs, with net inflows exceeding $500 million in the past 24 hours according to on-chain data analysts.',
            'link': 'https://example.com/news/bitcoin-etf-inflows',
            'source': 'thefeed.today',
            'topic_id': 'crypto',
            'topic_name': 'Crypto',
            'timestamp': '2026-05-24T13:30:00+00:00',
            'engagement': {'type': 'views', 'value': 25000}
        },
        {
            'title': 'Ethereum Layer 2 solutions process record 10M daily transactions',
            'summary': 'Layer-2 networks built on Ethereum including Arbitrum and Optimism have processed over 10 million transactions in the past day, demonstrating massive scalability improvements.',
            'link': 'https://example.com/news/eth-l2-growth',
            'source': 'thefeed.today',
            'topic_id': 'crypto',
            'topic_name': 'Crypto',
            'timestamp': '2026-05-24T12:45:00+00:00',
            'engagement': {'type': 'views', 'value': 18000}
        },
        {
            'title': 'Major DeFi protocol launches $50M ecosystem development fund',
            'summary': 'A leading decentralized finance protocol announced a substantial fund to support developers building on its platform, aiming to accelerate DeFi innovation and adoption.',
            'link': 'https://example.com/news/defi-fund',
            'source': 'RSS',
            'topic_id': 'crypto',
            'topic_name': 'Crypto',
            'timestamp': '2026-05-24T11:20:00+00:00',
            'engagement': {'type': 'authority', 'value': 30}
        },
        {
            'title': 'Solana validator performance improved 40% after network upgrade',
            'summary': 'Performance metrics show significant improvements following the latest network upgrade, with reduced latency and increased transaction throughput across the Solana blockchain.',
            'link': 'https://example.com/news/solana-upgrade',
            'source': 'thefeed.today',
            'topic_id': 'crypto',
            'topic_name': 'Crypto',
            'timestamp': '2026-05-24T10:15:00+00:00',
            'engagement': {'type': 'views', 'value': 12000}
        },
        {
            'title': 'CBDC pilot programs expand across Southeast Asian nations',
            'summary': 'Central banks in the region are accelerating CBDC research with multiple pilot programs demonstrating potential for digital fiat currencies in cross-border payments.',
            'link': 'https://example.com/news/cbdc-asia',
            'source': 'RSS',
            'topic_id': 'crypto',
            'topic_name': 'Crypto',
            'timestamp': '2026-05-24T09:30:00+00:00',
            'engagement': {'type': 'authority', 'value': 25}
        }
    ]
    
    # Create output directory
    os.makedirs('.state', exist_ok=True)
    
    # Save to JSON file
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    filename = f'.state/raw-{timestamp}.json'
    
    data = {
        'scraped_at': datetime.now(timezone.utc).isoformat(),
        'total_items': len(items),
        'topic_counts': {'crypto': len(items)},
        'sources': {
            'thefeed.today': 3,
            'RSS': 2
        },
        'items': items
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Test data saved: {filename}")
    print(f"   Items: {len(items)}")
    print(f"   Topic: Crypto")
    print(f"\n🎯 Next: Run python3 synthesize.py")
    
    return filename

if __name__ == '__main__':
    run_simple_test()
