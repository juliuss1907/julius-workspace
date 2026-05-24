#!/usr/bin/env python3
"""
Stage 1: X/Twitter Research
Search tweets via xurl CLI and extract structured data
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def run_x_research(topic: str, config: dict, output_path: Path) -> List[Dict[str, Any]]:
    """
    Execute X/Twitter research via xurl CLI.

    Args:
        topic: Research topic/keyword
        config: Configuration dict
        output_path: Path to save tweets.json

    Returns:
        List of tweet dicts with extracted fields
    """
    logger.info(f"Searching X for: {topic}")

    # Build xurl command
    tweet_limit = config['research']['tweet_limit']
    search_tool = config['x_twitter']['search_tool']

    cmd = [
        search_tool,
        "search",
        topic,
        "-n", str(tweet_limit),
        "--json"
    ]

    logger.debug(f"Running command: {' '.join(cmd)}")

    try:
        # Execute xurl search
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=config['x_twitter']['timeout'],
            check=True
        )

        raw_output = result.stdout
        logger.debug(f"xurl output length: {len(raw_output)} chars")

        # Parse xurl output
        tweets = parse_xurl_output(raw_output, config)

        if not tweets:
            logger.warning("No tweets found. Trying keyword variations...")
            tweets = try_keyword_variations(topic, config)

        # Filter by relevance score
        min_score = config['research']['min_relevance_score']
        filtered_tweets = [t for t in tweets if t.get('relevance_score', 0) >= min_score]

        logger.info(f"Collected {len(filtered_tweets)} tweets (filtered from {len(tweets)})")

        # Save to JSON
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_tweets, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved tweets to {output_path}")

        return filtered_tweets

    except subprocess.TimeoutExpired:
        logger.error(f"xurl search timed out after {config['x_twitter']['timeout']}s")
        return []
    except subprocess.CalledProcessError as e:
        logger.error(f"xurl search failed: {e.stderr}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in X research: {e}", exc_info=True)
        return []


def parse_xurl_output(raw_output: str, config: dict) -> List[Dict[str, Any]]:
    """
    Parse twitter CLI JSON output into structured tweet dicts.
    Expected format: {"ok": true, "data": [...]}
    """
    tweets = []
    
    try:
        parsed = json.loads(raw_output)
        
        if not parsed.get('ok', False):
            logger.warning(f"Twitter CLI returned ok=false")
            return []
        
        tweet_list = parsed.get('data', [])
        
        for tweet_raw in tweet_list:
            metrics = tweet_raw.get('metrics', {})
            author = tweet_raw.get('author', {})
            
            tweet = {
                'id': tweet_raw.get('id', ''),
                'author': author.get('screenName', author.get('name', '')),
                'author_name': author.get('name', ''),
                'text': tweet_raw.get('text', ''),
                'created_at': tweet_raw.get('createdAtISO', ''),
                'likes': metrics.get('likes', 0),
                'retweets': metrics.get('retweets', 0),
                'replies': metrics.get('replies', 0),
                'views': metrics.get('views', 0),
                'url': f"https://x.com/{author.get('screenName', '')}/status/{tweet_raw.get('id', '')}",
                'relevance_score': 0.0
            }
            
            tweet['relevance_score'] = calculate_relevance(
                tweet['text'],
                config['research']['topic']
            )
            
            tweets.append(tweet)
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse twitter output as JSON: {e}")
    except Exception as e:
        logger.error(f"Error parsing tweets: {e}")
    
    return tweets


def calculate_relevance(text: str, topic: str) -> float:
    """Calculate relevance score (0.0-1.0) based on keyword matching."""
    text_lower = text.lower()
    topic_lower = topic.lower()

    # Exact match
    if topic_lower in text_lower:
        return 1.0

    # Word-level matching
    topic_words = set(topic_lower.split())
    text_words = set(text_lower.split())

    overlap = len(topic_words & text_words)

    if overlap == len(topic_words):
        return 0.8
    elif overlap > 0:
        return 0.5 + (0.3 * overlap / len(topic_words))
    else:
        return 0.3


def try_keyword_variations(topic: str, config: dict) -> List[Dict[str, Any]]:
    """Fallback: try keyword variations if initial search returns nothing."""
    if not config['research']['keyword_variations']['enabled']:
        return []

    logger.info("Trying keyword variations...")

    variations = [
        f'"{topic}"',
        topic.replace('-', ' '),
        topic.replace('_', ' ')
    ]

    max_attempts = config['research']['keyword_variations']['max_attempts']

    for i, variant in enumerate(variations[:max_attempts]):
        logger.info(f"Attempt {i+1}: {variant}")

        cmd = [
            config['x_twitter']['search_tool'],
            "search",
            variant,
            "-n", str(config['research']['tweet_limit']),
            "--json"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=config['x_twitter']['timeout'],
                check=True
            )

            tweets = parse_xurl_output(result.stdout, config)

            if tweets:
                logger.info(f"Found {len(tweets)} tweets with variation: {variant}")
                return tweets

        except Exception as e:
            logger.warning(f"Variation {variant} failed: {e}")
            continue

    logger.warning("All keyword variations failed")
    return []
