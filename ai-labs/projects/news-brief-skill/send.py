# send.py
import requests
from config import OUTPUT_SETTINGS


def send_to_telegram(brief, parse_mode=None):
    """
    Send brief to Telegram chat

    Args:
        brief: Formatted brief text
        parse_mode: Override parse mode (default from config)

    Returns:
        bool: Success status
    """
    telegram_config = OUTPUT_SETTINGS['telegram']
    bot_token = telegram_config['bot_token']
    chat_id = telegram_config['chat_id']

    if parse_mode is None:
        parse_mode = telegram_config.get('parse_mode', 'Markdown')

    if not bot_token or bot_token == 'YOUR_BOT_TOKEN':
        print("TELEGRAM_BOT_TOKEN not configured")
        return False

    if not chat_id or chat_id == 'YOUR_CHAT_ID':
        print("TELEGRAM_CHAT_ID not configured")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # Telegram has 4096 char limit per message
    MAX_LENGTH = 4000

    if len(brief) <= MAX_LENGTH:
        return _send_single(url, chat_id, brief, parse_mode)
    else:
        # Split into multiple messages
        return _send_multipart(url, chat_id, brief, parse_mode, MAX_LENGTH)


def _send_single(url, chat_id, text, parse_mode):
    """Send single message"""
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode,
        'disable_web_page_preview': True
    }

    try:
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            print("Brief sent to Telegram")
            return True
        else:
            print(f"Failed to send: {response.text}")
            return False

    except Exception as e:
        print(f"Error sending: {e}")
        return False


def _send_multipart(url, chat_id, text, parse_mode, max_length):
    """Split and send multiple messages"""
    # Split by sections
    parts = text.split('━━━━━━━━━━━━━━')

    messages = []
    current = ''

    for part in parts:
        if len(current) + len(part) + 50 < max_length:
            current += '━━━━━━━━━━━━━━' + part if current else part
        else:
            if current:
                messages.append(current)
            current = part

    if current:
        messages.append(current)

    # Send each message
    success = True
    for i, msg in enumerate(messages):
        if not msg.strip():
            continue

        prefix = f"_(Part {i + 1}/{len(messages)})_\n\n" if len(messages) > 1 else ""
        result = _send_single(url, chat_id, prefix + msg, parse_mode)
        success = success and result

    return success


def send_error_notification(error_message):
    """Send error notification to Telegram"""
    telegram_config = OUTPUT_SETTINGS['telegram']
    bot_token = telegram_config['bot_token']
    chat_id = telegram_config['chat_id']

    if not bot_token or bot_token == 'YOUR_BOT_TOKEN':
        return False
    if not chat_id or chat_id == 'YOUR_CHAT_ID':
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    text = f"*News Brief Error*\n\n```\n{error_message[:500]}\n```"

    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }

    try:
        requests.post(url, json=payload, timeout=10)
        return True
    except:
        return False
