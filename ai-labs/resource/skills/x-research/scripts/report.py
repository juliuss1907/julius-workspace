#!/usr/bin/env python3
"""
Stage 4: Report Generation
Single .md file output with all sections inline.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


def generate_report(
    topic: str,
    synthesis_result: Dict[str, Any],
    tweets_data: List[Dict[str, Any]],
    web_data: List[Dict[str, Any]],
    config: dict,
    output_path: Path
) -> str:
    """
    Generate a single Markdown report file.
    Returns the output file path.
    """
    logger.info("Generating report...")

    context = prepare_context(
        topic=topic,
        synthesis_result=synthesis_result,
        tweets_data=tweets_data,
        web_data=web_data,
        config=config
    )

    render_markdown_report(context, output_path, config)
    logger.info(f"Report: {output_path}")

    return str(output_path)


def prepare_context(
    topic: str,
    synthesis_result: Dict[str, Any],
    tweets_data: List[Dict[str, Any]],
    web_data: List[Dict[str, Any]],
    config: dict
) -> Dict[str, Any]:
    """Prepare template context."""
    deep_analysis = synthesis_result.get('deep_analysis', {})

    context = {
        'topic': topic,
        'date': datetime.now().strftime('%B %d, %Y'),
        'executive_summary': deep_analysis.get('executive_summary', '') if isinstance(deep_analysis, dict) else '',
        'deep_analysis': deep_analysis.get('deep_analysis', '') if isinstance(deep_analysis, dict) else str(deep_analysis),
        'emerging_trends': deep_analysis.get('emerging_trends', []) if isinstance(deep_analysis, dict) else [],
        'contrarian_views': deep_analysis.get('contrarian_views', []) if isinstance(deep_analysis, dict) else [],
        'market_landscape': synthesis_result.get('market_landscape', {}),
        'key_metrics': synthesis_result.get('key_metrics', {}),
        'information_gaps': synthesis_result.get('information_gaps', []),
        'alpha_signals': synthesis_result.get('alpha_signals', []),
        'tweet_claims': [],
        'sentiment': {},
        'notable_voices': [],
        'tweets': tweets_data,
        'web_sources': web_data,
        'metadata': synthesis_result.get('metadata', {}),
        'sections': config['output']['sections']
    }

    # Extract tweet summary data
    tweet_summary = synthesis_result.get('tweet_summary', {})
    if isinstance(tweet_summary, dict):
        context['tweet_claims'] = tweet_summary.get('claims', [])
        context['sentiment'] = tweet_summary.get('sentiment', {})
        context['notable_voices'] = tweet_summary.get('notable_voices', [])

    return context


def render_markdown_report(context: Dict[str, Any], output_path: Path, config: dict):
    """Render single Markdown report using Jinja2 template."""
    template_dir = Path(__file__).parent.parent / 'templates'
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template('report.j2')

    markdown = template.render(**context)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
