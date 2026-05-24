# setup_telegram.py
from telethon import TelegramClient
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE
import asyncio


async def setup():
    """One-time setup to authenticate Telegram"""
    print("=" * 60)
    print("Telegram Authentication Setup")
    print("=" * 60)

    if TELEGRAM_API_ID == 'YOUR_API_ID' or TELEGRAM_API_HASH == 'YOUR_API_HASH':
        print("\nError: TELEGRAM_API_ID and TELEGRAM_API_HASH not configured")
        print("\nPlease:")
        print("1. Go to https://my.telegram.org/apps")
        print("2. Create a new application")
        print("3. Copy api_id and api_hash")
        print("4. Set them in config.py or environment variables")
        return

    if TELEGRAM_PHONE == '+84...':
        print("\nError: TELEGRAM_PHONE not configured")
        print("\nPlease set your phone number in config.py")
        return

    print(f"\nPhone: {TELEGRAM_PHONE}")
    print("\nConnecting to Telegram...")

    client = TelegramClient('hermes_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)

    try:
        await client.start(phone=TELEGRAM_PHONE)

        print("\nAuthenticated successfully!")
        print("\nSession saved to: hermes_session.session")
        print("\nYou can now run:")
        print("  python3 scrape.py")
        print("  python3 synthesize.py")

    except Exception as e:
        print(f"\nAuthentication failed: {e}")

    finally:
        await client.disconnect()


if __name__ == '__main__':
    asyncio.run(setup())
