#!/usr/bin/env python3
"""
scrape_thefeed.py - Scrape thefeed.today using requests only
Uses regex to parse HTML without BeautifulSoup dependency.
"""

import requests
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


def extract_items_from_page_simple(html_content, filter_name, topic_id, source_config, max_items=25):
    """Extract items using regex - simple version when BeautifulSoup not available"""
    
    settings = source_config.get('settings', {})
    max_items = settings.get('max_items', max_items)
    
    print(f"  Extracting {filter_name} for {source_config['topic_name']}...")
    
    # Look for table rows containing data
    # Pattern: <tr>...</tr>
    row_pattern = r'<tr[^>]*>(.*?)</tr>'
    rows = re.findall(row_pattern, html_content, re.DOTALL)
    
    topic_name = source_config['topic_name']
    items = []
    
    for i, row in enumerate(rows[:max_items]):
        try:
            # Extract all cells
            cell_pattern = r'<td[^>]*>(.*?)</td>'
            cells = re.findall(cell_pattern, row, re.DOTALL)
            
            if len(cells) < 6:
                continue
            
            # Clean cell content (remove HTML tags)
            def clean_html(text):
                # Remove any HTML tags
                clean = re.sub(r'<[^>]+>', '', text)
                # Decode HTML entities
                clean = clean.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                return clean.strip()
            
            # Extract link - look for href in the row
            link_match = re.search(r'href="([^"]+x\.com[^"]*)"', row)
            if not link_match:
                # If no x.com link, use first href
                link_match = re.search(r'href="([^"]*)"', row)
            
            if not link_match:
                continue
                
            link = link_match.group(1)
            
            # Extract metrics
            views_text = clean_html(cells[6]) if len(cells) > 6 else ''
            likes_text = clean_html(cells[5]) if len(cells) > 5 else ''
            
            views = parse_number(views_text)
            likes = parse_number(likes_text)
            
            # Calculate engagement rate
            engagement_rate = (likes / views * 100) if views > 0 else 0
            
            # Build title from summary
            summary = clean_html(cells[2]) if len(cells) > 2 else ''
            title = summary[:120] + '...' if len(summary) > 120 else summary
            
            item = {
                'title': title,
                'summary': summary,
                'link': link,
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
            print(f"    Error parsing row {i}: {e}")
            continue
    
    print(f"    Extracted {len(items)} items")
    return items


def extract_items_from_page_beautifulsoup(html_content, filter_name, topic_id, source_config, max_items=25):
    """Extract items using BeautifulSoup if available"""
    
    try:
        from bs4 import BeautifulSoup
        use_bs4 = True
    except ImportError:
        print("  BeautifulSoup not available, using simple regex parser")
        use_bs4 = False
    
    if not use_bs4:
        return extract_items_from_page_simple(html_content, filter_name, topic_id, source_config, max_items)
    
    settings = source_config.get('settings', {})
    max_items = settings.get('max_items', max_items)
    
    print(f"  Extracting {filter_name} for {source_config['topic_name']}...")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the table containing items
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
        
        # Extract items from HTML using either BeautifulSoup or regex
        items = extract_items_from_page_beautifulsoup(
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
    
    print("🌐 Scraping thefeed.today (requests only)...")
    
    # Get all thefeed sources from config
    # get_all_sources_by_type returns: [(topic_id, source_config), ...]
    sources_list = get_all_sources_by_type('websites')
    
    all_items = []
    
    # Create session for requests
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Group sources by topic for cleaner output
    sources_by_topic = {}
    for topic_id, source_config in sources_list:
        if topic_id not in sources_by_topic:
            sources_by_topic[topic_id] = []
        sources_by_topic[topic_id].append(source_config)
    
    # Scrape each topic
    for topic_id, sources in sources_by_topic.items():
        if not sources:
            continue
            
        topic_name = sources[0]['topic_name']
        topic_icon = sources[0]['topic_icon']
        print(f"\n{topic_icon} {topic_name}")
        
        for source_config in sources:
            if not source_config.get('enabled', False):
                print(f"  Skipping disabled: {source_config['name']}")
                continue
            
            # Check if this is thefeed scraper
            if source_config.get('scraper') == 'thefeed' or 'thefeed' in source_config.get('url', ''):
                items = scrape_topic_source(session, topic_id, topic_name, source_config)
                all_items.extend(items)
            else:
                print(f"  Skipping non-thefeed source: {source_config['name']}")
                
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
    
    try:
        response = session.get(url, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Length: {len(response.text)} chars")
        
        # Try to find table structure with regex
        if 'tbody' in response.text:
            print("\n✓ Found tbody in HTML")
            
            # Count rows
            row_count = len(re.findall(r'<tr[^>]*>', response.text))
            print(f"Found {row_count} table rows")
            
            # Look for buttons/filters
            button_matches = re.findall(r'<button[^>]*>([^<]+)</button>', response.text)
            if button_matches:
                print(f"\nFound {len(button_matches)} buttons:")
                for i, btn_text in enumerate(button_matches[:10]):
                    print(f"  {i}: {btn_text.strip()}")
        else:
            print("\n✗ No tbody found")
        
        # Save HTML for inspection
        filename = 'debug_thefeed.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text[:50000])  # Save first 50KB
        print(f"\n💾 Saved HTML to: {filename}")
        
    except Exception as e:
        print(f"Error: {e}")


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
        for item in items[:5]:
            print(f"  - {item['title'][:80]}...")
