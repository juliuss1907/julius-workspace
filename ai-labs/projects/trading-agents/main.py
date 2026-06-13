#!/usr/bin/env python3
"""
Trading Agents - Main Entry Point
"""
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from utils import setup_logging, get_logger, config, watchlist


# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging(os.getenv("LOG_LEVEL", "INFO"))


async def main():
    """Main function"""
    logger = get_logger(__name__)
    logger.info("=" * 80)
    logger.info("Trading Agents v0.1.0-dev - Starting")
    logger.info("=" * 80)
    
    # Load configuration
    logger.info("Loading configuration...")
    default_params = config.load_default_params()
    thresholds = config.load_thresholds()
    logger.info("Configuration loaded successfully")
    
    # Load watchlist
    logger.info("Loading watchlist...")
    coins = watchlist.get_all()
    logger.info(f"Watchlist: {coins}")
    
    # TODO: Initialize components
    logger.info("System initialization complete")
    logger.info("Ready to start trading analysis")
    
    # For now, just print status
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 1.1 COMPLETE: Project Setup")
    logger.info("=" * 80)
    logger.info("\nNext steps:")
    logger.info("1. Install dependencies: pip install -r requirements.txt")
    logger.info("2. Copy .env.example to .env and fill in API keys")
    logger.info("3. Continue with Phase 1.2: Data Fetchers")


if __name__ == "__main__":
    asyncio.run(main())
