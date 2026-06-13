#!/usr/bin/env python3
"""
Telegram Authentication - Step 2: Verify Code
Run this after receiving the code in your Telegram app

Usage:
  ./venv/bin/python scripts/auth_telegram_step2.py CODE [2FA_PASSWORD]

Examples:
  ./venv/bin/python scripts/auth_telegram_step2.py 12345
  ./venv/bin/python scripts/auth_telegram_step2.py 12345 mypassword
"""
import asyncio
import os
import sys
import pickle
from pathlib import Path
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

# Load environment variables
load_dotenv()

API_ID = int(os.getenv('TELEGRAM_API_ID'))
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE = os.getenv('TELEGRAM_PHONE')

# Session file path
SESSION_FILE = Path(__file__).parent.parent / 'data' / 'telegram_session'
PHONE_HASH_FILE = Path(__file__).parent.parent / 'data' / 'phone_code_hash.pkl'

async def verify_code(code: str, password_2fa: str = None):
    """Verify the code received from Telegram"""
    
    # Check if phone_code_hash exists
    if not PHONE_HASH_FILE.exists():
        print("❌ Error: Phone code hash not found!")
        print("Please run Step 1 first:")
        print("  ./venv/bin/python scripts/auth_telegram_step1.py")
        return False
    
    # Load phone_code_hash
    with open(PHONE_HASH_FILE, 'rb') as f:
        phone_code_hash = pickle.load(f)
    
    print(f"🔐 Verifying code: {code}")
    
    # Create client
    client = TelegramClient(str(SESSION_FILE), API_ID, API_HASH)
    
    try:
        # Connect to Telegram
        await client.connect()
        
        # Sign in with code
        try:
            await client.sign_in(
                phone=PHONE,
                code=code,
                phone_code_hash=phone_code_hash
            )
            print("✅ Code verified successfully!")
            
        except SessionPasswordNeededError:
            # 2FA is enabled
            if not password_2fa:
                print("❌ Error: 2FA password required!")
                print("Usage: ./venv/bin/python scripts/auth_telegram_step2.py CODE 2FA_PASSWORD")
                return False
            
            print("🔑 Verifying 2FA password...")
            await client.sign_in(password=password_2fa)
            print("✅ 2FA verified successfully!")
        
        # Verify authentication
        if await client.is_user_authorized():
            me = await client.get_me()
            print()
            print("=" * 80)
            print("🎉 AUTHENTICATION SUCCESSFUL!")
            print("=" * 80)
            print(f"👤 Logged in as: {me.first_name} {me.last_name or ''} (@{me.username or 'N/A'})")
            print(f"💾 Session saved to: {SESSION_FILE}.session")
            print()
            print("Next step - Test the scraper:")
            print("  ./venv/bin/python scripts/test_telegram_scraper.py")
            print("=" * 80)
            
            # Clean up phone_code_hash file
            PHONE_HASH_FILE.unlink()
            
            return True
        else:
            print("❌ Authentication failed")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Troubleshooting:")
        print("1. Make sure the code is correct (5 digits)")
        print("2. Code expires quickly - run Step 1 again if needed")
        print("3. If you have 2FA enabled, provide password as second argument")
        return False
    finally:
        await client.disconnect()

async def main():
    if len(sys.argv) < 2:
        print("Usage: ./venv/bin/python scripts/auth_telegram_step2.py CODE [2FA_PASSWORD]")
        print()
        print("Examples:")
        print("  ./venv/bin/python scripts/auth_telegram_step2.py 12345")
        print("  ./venv/bin/python scripts/auth_telegram_step2.py 12345 mypassword")
        return False
    
    code = sys.argv[1]
    password_2fa = sys.argv[2] if len(sys.argv) > 2 else None
    
    return await verify_code(code, password_2fa)

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
