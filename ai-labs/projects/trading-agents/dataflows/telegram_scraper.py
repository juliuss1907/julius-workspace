"""
Telegram Channels Scraper
Fetches messages from public Telegram channels for news analysis
"""
import os
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat
from utils import get_logger
from .base import DataSource


logger = get_logger(__name__)


class TelegramScraper(DataSource):
    """Scrape messages from public Telegram channels"""
    
    # 9 channels đã chọn
    CHANNELS = [
        'the_block_crypto',
        'onecryptofeed',
        'ahboyashreads',
        'wublockchainenglish',
        'WatcherGuru',
        'cointelegraph',
        'AshCryptoTG',
        'DegenerateNews',
        'sosovaluenewsbot'
    ]
    
    def __init__(self):
        super().__init__("telegram_scraper")
        
        # Load credentials from environment
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone = os.getenv('TELEGRAM_PHONE')  # Optional, for first-time auth
        
        if not self.api_id or not self.api_hash:
            raise ValueError("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in .env")
        
        # Session file path
        self.session_path = Path(__file__).parent.parent / "data" / "telegram_session"
        self.session_path.parent.mkdir(exist_ok=True)
        
        # Telegram client
        self.client: Optional[TelegramClient] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize Telegram client and authenticate"""
        if self._initialized:
            return
        
        try:
            # Create client
            self.client = TelegramClient(
                str(self.session_path),
                int(self.api_id),
                self.api_hash
            )
            
            # Connect and authenticate
            await self.client.connect()
            
            # Check if already authorized
            if not await self.client.is_user_authorized():
                logger.info("Telegram client not authorized. Starting authentication...")
                
                if self.phone:
                    # Send code
                    await self.client.send_code_request(self.phone)
                    logger.info(f"Authentication code sent to {self.phone}")
                    
                    # Get code from user (for first-time setup)
                    code = input("Enter the code you received: ")
                    await self.client.sign_in(self.phone, code)
                    logger.info("✓ Telegram authentication successful")
                else:
                    raise ValueError(
                        "TELEGRAM_PHONE not set in .env. "
                        "Please add your phone number for first-time authentication."
                    )
            else:
                logger.info("✓ Telegram client already authenticated")
            
            self._initialized = True
            self.record_success()
            
        except Exception as e:
            logger.error(f"Failed to initialize Telegram client: {e}")
            self.record_error()
            raise
    
    async def fetch_messages(
        self,
        channel: str,
        hours: int = 24,
        limit: int = 50
    ) -> List[Dict]:
        """
        Fetch recent messages from a channel
        
        Args:
            channel: Channel username (without @)
            hours: Fetch messages from last N hours
            limit: Maximum number of messages to fetch
        
        Returns:
            List of message dicts with: text, date, views, forwards, channel
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Calculate time threshold
            time_threshold = datetime.now() - timedelta(hours=hours)
            
            # Get channel entity
            try:
                entity = await self.client.get_entity(channel)
            except Exception as e:
                logger.warning(f"Could not get entity for channel {channel}: {e}")
                return []
            
            # Fetch messages
            messages = []
            async for message in self.client.iter_messages(
                entity,
                limit=limit,
                offset_date=datetime.now()
            ):
                # Filter by date
                if message.date.replace(tzinfo=None) < time_threshold:
                    break
                
                # Skip empty messages
                if not message.text or not message.text.strip():
                    continue
                
                # Extract message data
                msg_data = {
                    'text': message.text,
                    'date': message.date.isoformat(),
                    'views': message.views or 0,
                    'forwards': message.forwards or 0,
                    'channel': channel,
                    'source': 'telegram',
                    'message_id': message.id
                }
                
                messages.append(msg_data)
            
            logger.info(f"Fetched {len(messages)} messages from @{channel} (last {hours}h)")
            self.record_success()
            return messages
            
        except Exception as e:
            logger.error(f"Error fetching messages from @{channel}: {e}")
            self.record_error()
            return []
    
    async def fetch_all_channels(
        self,
        hours: int = 24,
        limit: int = 50
    ) -> List[Dict]:
        """
        Fetch messages from all channels in parallel
        
        Args:
            hours: Fetch messages from last N hours
            limit: Maximum number of messages per channel
        
        Returns:
            Aggregated list of messages from all channels
        """
        if not self._initialized:
            await self.initialize()
        
        logger.info(f"Fetching messages from {len(self.CHANNELS)} channels (last {hours}h)...")
        
        # Create tasks for all channels
        tasks = [
            self.fetch_messages(channel, hours, limit)
            for channel in self.CHANNELS
        ]
        
        # Run in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        all_messages = []
        for channel, result in zip(self.CHANNELS, results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching from @{channel}: {result}")
                continue
            
            all_messages.extend(result)
        
        # Sort by date (newest first)
        all_messages.sort(key=lambda x: x['date'], reverse=True)
        
        logger.info(f"✓ Fetched {len(all_messages)} total messages from all channels")
        return all_messages
    
    async def health_check(self) -> bool:
        """Check if Telegram client is connected"""
        if not self.client:
            return False
        
        try:
            return await self.client.is_user_authorized()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def close(self):
        """Disconnect Telegram client"""
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram client disconnected")
    
    async def fetch(self, hours: int = 24, limit: int = 50, **kwargs) -> List[Dict]:
        """
        Fetch messages from all channels (implements DataSource.fetch)
        
        Args:
            hours: Fetch messages from last N hours
            limit: Maximum number of messages per channel
            **kwargs: Additional arguments (ignored)
        
        Returns:
            List of message dicts
        """
        return await self.fetch_all_channels(hours=hours, limit=limit)
    
    def filter_by_keywords(
        self,
        messages: List[Dict],
        keywords: List[str]
    ) -> List[Dict]:
        """
        Filter messages by keywords (coin symbols, etc.)
        
        Args:
            messages: List of message dicts
            keywords: List of keywords to search for (case-insensitive)
        
        Returns:
            Filtered list of messages containing keywords
        """
        keywords_lower = [kw.lower() for kw in keywords]
        
        filtered = []
        for msg in messages:
            text_lower = msg['text'].lower()
            
            # Check if any keyword is in the message
            if any(kw in text_lower for kw in keywords_lower):
                # Add matched keywords to message data
                msg['matched_keywords'] = [
                    kw for kw in keywords_lower if kw in text_lower
                ]
                filtered.append(msg)
        
        logger.info(f"Filtered {len(filtered)}/{len(messages)} messages by keywords: {keywords}")
        return filtered
    
    def remove_duplicates(
        self,
        messages: List[Dict],
        similarity_threshold: float = 0.8
    ) -> List[Dict]:
        """
        Remove duplicate messages based on text similarity
        
        Args:
            messages: List of message dicts
            similarity_threshold: Minimum similarity to consider as duplicate (0-1)
        
        Returns:
            Deduplicated list of messages
        """
        if not messages:
            return []
        
        unique_messages = []
        seen_texts = []
        
        for msg in messages:
            text = msg['text']
            
            # Check if similar text already seen
            is_duplicate = False
            for seen_text in seen_texts:
                similarity = self._calculate_similarity(text, seen_text)
                if similarity >= similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_messages.append(msg)
                seen_texts.append(text)
        
        logger.info(f"Removed {len(messages) - len(unique_messages)} duplicate messages")
        return unique_messages
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity using Jaccard index
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity score (0-1)
        """
        # Tokenize
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Jaccard similarity
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
