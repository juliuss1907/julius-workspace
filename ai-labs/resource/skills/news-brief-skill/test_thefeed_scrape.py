#!/usr/bin/env python3
"""
Simple test for thefeed scraper without any dependencies beyond requests
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import re

def test_thefeed_simple():
    """Test scraping thefeed.today with pure regex"""
    
    print("🌐 Testing thefeed.today scraper...")
    
    url = "https://thefeed.today/"
    
    try:
        # Fetch page
        print(f"  Fetching {url}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        html = response.text
        print(f"  ✓ Got page: {len(html)} chars")
        
        # Look for table structure
        if '<tbody>' in html:
            print("  ✓ Found tbody")
        else:
            print("  ✗ No tbody found")
            return False
        
        # Extract rows
        row_pattern = r'<tr[^>]*>(.*?)</tr>'
        rows = re.findall(row_pattern, html, re.DOTALL)
        print(f"  ✓ Found {len(rows)} table rows")
        
        if not rows:
            return False
        
        # Test parsing first few rows
        items = []
        for i, row in enumerate(rows[:5]):
            try:
                # Extract cells
                cell_pattern = r'<td[^>]*>(.*?)</td>'
                cells = re.findall(cell_pattern, row, re.DOTALL)
                
                if len(cells) < 6:
                    continue
                
                # Clean HTML
                def clean(text):
                    text = re.sub(r'<[^>]+>', '', text)
                    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                    return text.strip()
                
                # Extract link
                link_match = re.search(r'href="([^"]+)"', row)
                if not link_match:
                    continue
                
                link = link_match.group(1)
                title = clean(cells[2])[:100] + "..." if len(clean(cells[2])) > 100 else clean(cells[2])
                
                item = {
                    'title': title,
                    'link': link,
                    'views': clean(cells[6]) if len(cells) > 6 else '',
                    'likes': clean(cells[5]) if len(cells) > 5 else '',
                }
                
                items.append(item)
                print(f"  Row {i}: {item['title'][:60]}...")
                
            except Exception as e:
                print(f"  Error parsing row {i}: {e}")
                continue
        
        print(f"\n✅ Successfully parsed {len(items)} items from thefeed.today")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_thefeed_simple()
    if success:
        print("\n🎯 Test PASSED - thefeed scraper works!")
    else:
        print("\n❌ Test FAILED")
        sys.exit(1)