#!/usr/bin/env python3
"""
scrape_thefeed.py - Scrape thefeed.today using requests + BeautifulSoup
No playwright/browser needed.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from config_helpers import get_all_sources_by_type, passes_quality_filters
import json
import time
import re


def parse_number(text):
    """Parse '1.2M' -> 1200000"""
    if not text:
        return 0
    text = text.replace(',', '').strip()
    try:
        if 'M' in text:
            return int(float(text.replace('M', '')) * 1_000_000)
        elif 'K' in text:
            return int(float(text.replace('K', '')) * 1_000)
        else:
            return int(text)
    except:
        return 0


def parse_relative_time(text):
    """Parse '2h ago' -> datetime"""
    now = datetime.now(timezone.utc)
    if not text:
        return now

    text = text.lower().strip()
    try:
        if 'h ago' in text:
            hours = int(text.split('h')[0].strip())
            return now - timedelta(hours=hours)
        elif 'd ago' in text:
            days = int(text.split('d')[0].strip())
            return now - timedelta(days=days)
        elif 'm ago' in text:
            minutes = int(text.split('m')[0].strip())
            return now - timedelta(minutes=minutes)
        else:
            return now
    except:
        return now


def extract_items_from_page(html_content, filter_name, topic_id, source_config, max_items=25):
    """Extract items from HTML content using BeautifulSoup"""
    
    settings = source_config.get('settings', {})
    max_items = settings.get('max_items', max_items)
    
    print(f"  Extracting {filter_name} for {source_config['topic_name']}...")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the table containing items
    # thefeed.today structure: table with tbody containing tr rows
    tbody = soup.find('tbody')
    if not tbody:
        print(f"    Error: Could not find table body in HTML")
        return []
    
    rows = tbody.find_all('tr', limit=max_items)
    
    # Parse and normalize
    topic_name = source_config['topic_name']
    items = []
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 6:
            continue
            
        # Extract data from cells
        try:
            # Get all links in the row
            links = row.find_all('a')
            x_link = None
            for link in links:
                href = link.get('href', '')
                if href and 'x.com' in href:
                    x_link = href
                    break
            
            if not x_link:
                # If no X link, use the first link or skip
                if links:
                    x_link = links[0].get('href', '')
                else:
                    continue
            
            # Extract metrics
            views_text = cells[6].text.strip() if len(cells) > 6 else ''
            likes_text = cells[5].text.strip() if len(cells) > 5 else ''
            
            views = parse_number(views_text)
            likes = parse_number(likes_text)
            
            # Calculate engagement rate
            engagement_rate = (likes / views * 100) if views > 0 else 0
            
            # Build title from summary (first sentence or trimmed summary)
            summary = cells[2].text.strip() if len(cells) > 2 else ''
            title = summary[:120] + '...' if len(summary) > 120 else summary
            
            item = {
                'title': title,
                'summary': summary,
                'link': x_link,
                'source': 'thefeed.today',
                'topic_id': topic_id,
                'topic_name': topic_name,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'engagement': {
                    'type': 'views_with_rate',
                    'value': views,
                    'rate': engagement_rate
                },
                'raw_metrics': {
                    'views': views,
                    'likes': likes,
                    'engagement_rate': engagement_rate
                }
            }
            
            if passes_quality_filters(item):
                items.append(item)
                
        except Exception as e:
            print(f"    Error parsing row: {e}")
            continue
    
    print(f"    Extracted {len(items)} items")
    return items


def scrape_topic_source(session, topic_id, topic_name, source_config):
    """Scrape a single topic source"""
    
    settings = source_config.get('settings', {})
    filter_name = settings.get('filter', 'Crypto')
    use_browser = settings.get('use_browser', False)
    
    if use_browser:
        # Skip browser-based sources for now
        print(f"  Skipping browser-based source: {source_config['name']}")
        return []
    
    url = source_config['url']
    
    try:
        print(f"  Scraping {source_config['name']}...")
        
        # Add headers to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"    ✓ Got page: {len(response.text)} chars")
        
        # Extract items from HTML
        items = extract_items_from_page(
            response.text, 
            filter_name, 
            topic_id, 
            source_config,
            max_items=settings.get('max_items', 25)
        )
        
        return items
        
    except Exception as e:
        print(f"    ❌ Error scraping {url}: {e}")
        return []


def scrape_thefeed():
    """Scrape all thefeed.today sources"""
    
    print("🌐 Scraping thefeed.today (requests + BeautifulSoup)...")
    
    # Get all thefeed sources from config
    sources_by_topic = get_all_sources_by_type('websites', scraper='thefeed')
    
    all_items = []
    
    # Create session for requests
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Scrape each topic
    for topic_id, sources in sources_by_topic.items():
        topic_name = sources[0]['topic_name'] if sources else topic_id
        print(f"\n{sources[0]['topic_icon'] if sources else ''} {topic_name}")
        
        for source_config in sources:
            if not source_config['enabled']:
                print(f"  Skipping disabled: {source_config['name']}")
                continue
                
            items = scrape_topic_source(session, topic_id, topic_name, source_config)
            all_items.extend(items)
            
            # Be polite, add delay
            time.sleep(1)
    
    print(f"\n✅ thefeed scraper completed: {len(all_items)} items")
    return all_items


def debug_scrape(url='https://thefeed.today/'):
    """Debug function to inspect page structure"""
    
    print(f"🔍 Debugging: {url}")
    
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = session.get(url, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Length: {len(response.text)} chars")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Print page structure
    print("\n--- Page Structure ---")
    
    # Find all buttons (filters)
    buttons = soup.find_all('button')
    print(f"\nFound {len(buttons)} buttons:")
    for i, btn in enumerate(buttons[:10]):  # First 10
        print(f"  {i}: {btn.text.strip()}")
    
    # Find table
    table = soup.find('table')
    if table:
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            print(f"\nFound table with {len(rows)} rows")
            
            # Print first row structure
            if rows:
                first_row = rows[0]
                cells = first_row.find_all(['td', 'th'])
                print(f"First row has {len(cells)} cells:")
                for i, cell in enumerate(cells):
                    print(f"  Cell {i}: {cell.text[:50]}...")
        else:
            print("No tbody found")
    else:
        print("No table found")
    
    # Save HTML for inspection
    filename = 'debug_thefeed.html'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"\n💾 Saved HTML to: {filename}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Debug page structure')
    args = parser.parse_args()
    
    if args.debug:
        debug_scrape()
    else:
        items = scrape_thefeed()
        print(f"\nExtracted {len(items)} items:")
        for item in items[:3]:
            print(f"  - {item['title'][:60]}...")
