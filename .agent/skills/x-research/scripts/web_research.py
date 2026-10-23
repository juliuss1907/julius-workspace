#!/usr/bin/env python3
"""
Stage 2: Web Research
Search and scrape web sources via Firecrawl localhost
"""

import json
import logging
import requests
import time
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def run_web_research(topic: str, config: dict, output_path: Path) -> List[Dict[str, Any]]:
    """
    Execute web research via Firecrawl localhost.
    """
    logger.info(f"Searching web for: {topic}")

    firecrawl_base = config['firecrawl']['base_url']
    max_sources = config['research']['web_sources']

    # Step 1: Search for URLs
    urls = search_urls(topic, firecrawl_base, max_sources, config)

    if not urls:
        logger.warning("No URLs found via Firecrawl search. Trying fallback...")
        urls = fallback_search(topic, config)

    if not urls:
        logger.error("No web sources found")
        return []

    logger.info(f"Found {len(urls)} URLs to scrape")

    # Step 2: Scrape each URL
    web_sources = []
    domain_count = {}
    domain_limit = config.get('processing', {}).get('domain_limit', 2)

    for url in urls:
        domain = urlparse(url).netloc

        if domain_count.get(domain, 0) >= domain_limit:
            continue

        source = scrape_url(url, firecrawl_base, config)

        if source:
            web_sources.append(source)
            domain_count[domain] = domain_count.get(domain, 0) + 1

            if len(web_sources) >= max_sources:
                break

    logger.info(f"Scraped {len(web_sources)} web sources")

    # Save to JSON
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(web_sources, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved web sources to {output_path}")

    return web_sources


def search_urls(topic: str, base_url: str, limit: int, config: dict) -> List[str]:
    """Search for URLs via Firecrawl /v1/search endpoint."""
    search_endpoint = f"{base_url}/v1/search"

    payload = {
        "query": topic,
        "limit": limit * 2
    }

    try:
        response = requests.post(
            search_endpoint,
            json=payload,
            timeout=config['firecrawl']['timeout']
        )

        response.raise_for_status()
        data = response.json()

        urls = []
        for result in data.get('data', []):
            url = result.get('url')
            if url:
                urls.append(url)

        logger.info(f"Firecrawl search returned {len(urls)} URLs")
        return urls

    except requests.exceptions.RequestException as e:
        logger.error(f"Firecrawl search failed: {e}")
        return []


def scrape_url(url: str, base_url: str, config: dict) -> Dict[str, Any]:
    """Scrape a single URL via Firecrawl /v1/scrape endpoint."""
    scrape_endpoint = f"{base_url}/v1/scrape"

    payload = {
        "url": url,
        "formats": config['firecrawl']['formats'],
        "waitFor": config['firecrawl']['wait_for']
    }

    retries = config['firecrawl']['retries']
    retry_delay = config['firecrawl']['retry_delay']

    for attempt in range(retries):
        try:
            response = requests.post(
                scrape_endpoint,
                json=payload,
                timeout=config['firecrawl']['timeout']
            )

            response.raise_for_status()
            data = response.json()

            content = data.get('data', {}).get('markdown', '')

            if config.get('processing', {}).get('filter_low_quality', True):
                min_length = config.get('processing', {}).get('min_content_length', 200)
                if len(content) < min_length:
                    return None

            source = {
                'url': url,
                'title': data.get('data', {}).get('title', ''),
                'markdown': content,
                'scraped_at': data.get('data', {}).get('scraped_at', ''),
                'domain': urlparse(url).netloc
            }

            logger.info(f"Scraped {url} ({len(content)} chars)")
            return source

        except requests.exceptions.RequestException as e:
            logger.warning(f"Scrape attempt {attempt+1}/{retries} failed for {url}: {e}")
            if attempt < retries - 1:
                time.sleep(retry_delay)
            continue

    logger.error(f"Failed to scrape {url} after {retries} attempts")
    return None


def fallback_search(topic: str, config: dict) -> List[str]:
    """Fallback search using built-in web_search tool if Firecrawl is down."""
    if not config['firecrawl']['fallback_enabled']:
        return []

    logger.info("Using fallback search method...")
    logger.warning("Fallback search not implemented yet")
    return []
