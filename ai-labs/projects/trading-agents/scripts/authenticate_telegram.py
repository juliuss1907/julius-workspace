#!/usr/bin/env python3
"""
First-time Telegram Authentication Script
Run this once to authenticate and save session file
"""
import asyncio
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
    """Authenticate with Telegram and save session"""
    import os
    
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone = os.getenv('TELEGRAM_PHONE')
    
    if not all([api_id, api_hash, phone]):
        logger.error("Missing credentials in .env file")
        logger.error("Required: TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE")
        return False
    
    session_path = Path(__file__).parent.parent / "data" / "telegram_session"
    session_path.parent.mkdir(exist_ok=True)
    
    logger.info("=" * 80)
    logger.info("Telegram Authentication")
    logger.info("=" * 80)
    logger.info(f"\nPhone: {phone}")
    logger.info(f"Session file: {session_path}\n")
    
    client = TelegramClient(str(session_path), int(api_id), api_hash)
    
    try:
        await client.connect()
        
        if await client.is_user_authorized():
            logger.info("✓ Already authenticated!")
            logger.info("Session file exists and is valid.")
            return True
        
        logger.info("Sending authentication code...")
        await client.send_code_request(phone)
        logger.info("✓ Code sent to your Telegram app")
        
        code = input("\nEnter the code you received: ")
        
        try:
            await client.sign_in(phone, code)
        except Exception as e:
            if "Two-steps verification" in str(e):
                logger.info("\nTwo-step verification enabled")
                password = input("Enter your 2FA password: ")
                await client.sign_in(password=password)
            else:
                raise
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ Authentication successful!")
        logger.info("=" * 80)
        logger.info(f"\nSession saved to: {session_path}")
        logger.info("\nYou can now run the trading system without re-authenticating.")
        
        return True
        
    except Exception as e:
        logger.error(f"\n✗ Authentication failed: {e}")
        return False
    
    finally:
        await client.disconnect()


async def main():
    """Main entry point"""
    success = await authenticate()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
