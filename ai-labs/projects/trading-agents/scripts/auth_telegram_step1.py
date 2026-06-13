#!/usr/bin/env python3
"""
Telegram Authentication - Step 1: Send Code Request
Run this first to receive a code in your Telegram app
"""
import asyncio
import os
import pickle
from pathlib import Path
from dotenv import load_dotenv
from telethon import TelegramClient

# Load environment variables
load_dotenv()

API_ID = int(os.getenv('TELEGRAM_API_ID'))
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE = os.getenv('TELEGRAM_PHONE')

# Session file path
SESSION_FILE = Path(__file__).parent.parent / 'data' / 'telegram_session'
PHONE_HASH_FILE = Path(__file__).parent.parent / 'data' / 'phone_code_hash.pkl'

async def send_code_request():
    """Send code request to Telegram"""
    print(f"📱 Sending code request to {PHONE}...")
    
    # Create client
    client = TelegramClient(str(SESSION_FILE), API_ID, API_HASH)
    
    try:
        # Connect to Telegram
        await client.connect()
        
        # Send code request
        result = await client.send_code_request(PHONE)
        phone_code_hash = result.phone_code_hash
        
        # Save phone_code_hash for step 2
        PHONE_HASH_FILE.parent.mkdir(exist_ok=True)
        with open(PHONE_HASH_FILE, 'wb') as f:
            pickle.dump(phone_code_hash, f)
        
        print("✅ Code request sent successfully!")
        print(f"📲 Check your Telegram app for the verification code")
        print(f"💾 Phone code hash saved to: {PHONE_HASH_FILE}")
        print()
        print("Next step:")
        print(f"  ./venv/bin/python scripts/auth_telegram_step2.py YOUR_CODE YOUR_2FA_PASSWORD")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(send_code_request())
