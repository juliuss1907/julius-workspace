"""
Utility Functions
Common helpers for X-Research
"""

import re
import logging
import os
from pathlib import Path
from typing import Optional
import requests


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Setup logging configuration."""
    log_level = getattr(logging, level.upper(), logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    text = text.strip('-')
    return text


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists, create if needed."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def send_telegram_brief(report_path: Path, config: dict):
    """Send Telegram notification with research brief extracted from report."""
    logger = logging.getLogger(__name__)

    if not config['telegram']['enabled']:
        return

    bot_token = os.getenv(config['telegram']['bot_token_env'])
    chat_id = os.getenv(config['telegram']['chat_id_env'])

    if not bot_token or not chat_id:
        logger.warning("Telegram credentials not found")
        return

    # Extract brief from report
    content = ""
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Get first paragraph after "Executive Summary" heading
        exec_match = re.search(r'## Executive Summary\n\n(.+?)(?=\n\n---)', content, re.DOTALL)
        brief_text = exec_match.group(1).strip() if exec_match else "Research report generated."
    except Exception:
        brief_text = "Research report generated."

    max_points = config['telegram']['brief_max_points']

    # Find emerging trends
    trends_match = re.search(r'## Emerging Trends\n\n((?:\d+\. .+\n)+)', content)
    if trends_match:
        trends = trends_match.group(1).strip().split('\n')[:max_points]
        brief_text += "\n\n📈 Trends:\n" + '\n'.join(trends)

    brief_text += f"\n\n📄 {report_path}"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': brief_text[:4000],  # Telegram limit
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Telegram sent")
    except requests.exceptions.RequestException as e:
        logger.error(f"Telegram failed: {e}")
