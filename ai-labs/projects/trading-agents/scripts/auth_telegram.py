#!/usr/bin/env python3
"""
Telegram Authentication - Single Script
Usage: TELEGRAM_CODE=12345 ./venv/bin/python scripts/auth_telegram.py
Or with 2FA: TELEGRAM_CODE=12345 TELEGRAM_2FA=mypassword ./venv/bin/python scripts/auth_telegram.py
"""
import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from telethon import TelegramClient
from utils import setup_logging, get_logger


setup_logging("INFO")
logger = get_logger(__name__)


async def authenticate():
    """Authenticate with Telegram"""
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone = os.getenv('TELEGRAM_PHONE')
    code = os.getenv('TELEGRAM_CODE')
    password_2fa = os.getenv('TELEGRAM_2FA')
    
    if not all([api_id, api_hash, phone]):
        logger.error("Missing credentials in .env file")
        logger.error("Required: TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE")
        return False
    
    if not code:
        logger.error("Missing TELEGRAM_CODE environment variable")
        logger.error("Usage: TELEGRAM_CODE=12345 ./venv/bin/python scripts/auth_telegram.py")
        return False
    
    session_path = Path(__file__).parent.parent / "data" / "telegram_session"
    session_path.parent.mkdir(exist_ok=True)
    
    logger.info("=" * 80)
    logger.info("Telegram Authentication")
    logger.info("=" * 80)
    logger.info(f"\nPhone: {phone}")
    logger.info(f"Code: {code}")
    if password_2fa:
        logger.info("2FA Password: ***")
    logger.info("")
    
    client = TelegramClient(str(session_path), int(api_id), api_hash)
    
    try:
        await client.connect()
        
        # Check if already authorized
        if await client.is_user_authorized():
            logger.info("✓ Already authenticated!")
            me = await client.get_me()
            logger.info(f"Logged in as: {me.first_name} {me.last_name or ''}")
            return True
        
        # Send code request
        logger.info("Sending authentication code request...")
        result = await client.send_code_request(phone)
        phone_code_hash = result.phone_code_hash
        logger.info(f"✓ Code request sent (hash: {phone_code_hash[:10]}...)")
        
        # Sign in with code and phone_code_hash
        logger.info("Verifying code...")
        try:
            await client.sign_in(
                phone=phone,
                code=code,
                phone_code_hash=phone_code_hash
            )
            logger.info("✓ Code verified!")
        
        except Exception as e:
            error_msg = str(e).lower()
            if "two-steps" in error_msg or "password" in error_msg:
                if not password_2fa:
                    logger.error("✗ Two-step verification enabled but no password provided")
                    logger.error("Usage: TELEGRAM_CODE=12345 TELEGRAM_2FA=mypassword ./venv/bin/python scripts/auth_telegram.py")
                    return False
                
                logger.info("Two-step verification detected, signing in with password...")
                await client.sign_in(password=password_2fa)
                logger.info("✓ 2FA verified!")
            else:
                raise
        
        # Verify authentication
        if await client.is_user_authorized():
            me = await client.get_me()
            logger.info(f"\n✓ Logged in as: {me.first_name} {me.last_name or ''} (@{me.username or 'N/A'})")
            logger.info(f"✓ Session saved to: {session_path}")
            logger.info("\n" + "=" * 80)
            logger.info("SUCCESS! You can now run:")
            logger.info("  ./venv/bin/python scripts/test_telegram_scraper.py")
            logger.info("=" * 80)
            return True
        else:
            logger.error("✗ Authentication failed: not authorized")
            return False
        
    except Exception as e:
        logger.error(f"\n✗ Authentication failed: {e}")
        logger.error("\nTroubleshooting:")
        logger.error("1. Make sure the code is correct (5 digits)")
        logger.error("2. Code expires quickly - request a new one if needed")
        logger.error("3. If you have 2FA enabled, provide TELEGRAM_2FA env var")
        return False
    
    finally:
        await client.disconnect()


async def main():
    success = await authenticate()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
