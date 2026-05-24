# config.py
import os

# ============================================================
# TOPICS CONFIGURATION
# ============================================================

TOPICS = {
    # Topic 1: Crypto
    'crypto': {
        'enabled': True,
        'display_name': 'Crypto',
        'icon': '🪙',
        'description': 'Cryptocurrency, DeFi, blockchain news',

        # Sources for this topic
        'sources': {
            'telegram': [
                # TODO: Add channels here
                # Example:
                # {
                #     'username': 'ahboyashreads',
                #     'name': 'The DeFi Edge',
                #     'priority': 'high',
                #     'type': 'research',
                #     'enabled': True
                # },
                {
                     'username': 'thedefiedge',
                     'name': 'Ahboyash Reads',
                     'priority': 'high',
                     'type': 'news',
                     'enabled': True
                 },
            ],

            'websites': [
                # TODO: Add websites here
                # Example:
                # {
                #     'name': 'thefeed.today',
                #     'url': 'https://thefeed.today/',
                #     'type': 'aggregator',
                #     'scraper': 'thefeed',
                #     'priority': 'medium',
                #     'enabled': True,
                #     'settings': {
                #         'use_browser': True,
                #         'filter': 'Crypto',
                #         'max_items': 25,
                #     }
                # },
                {
                     'name': 'thefeed.today',
                     'url': 'https://thefeed.today/',
                     'type': 'aggregator',
                     'scraper': 'thefeed',
                     'priority': 'medium',
                     'enabled': True,
                     'settings': {
                         'use_browser': False,  # Use requests instead of browser
                         'filter': 'Crypto',
                         'max_items': 25,
                     }
                },
            ],

            'rss': [
                # TODO: Add RSS feeds here
                # Example:
                # {
                #     'name': 'CoinDesk',
                #     'url': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
                #     'priority': 'high',
                #     'enabled': True
                # },
            ],
        },

        # Keywords for this topic
        'keywords': {
            'tier_1': {
                'keywords': [
                    # TODO: Add tier 1 keywords
                    # Example: 'ethereum', 'bitcoin', 'sec approval', 'etf'
                ],
                'weight': 100,
            },
            'tier_2': {
                'keywords': [
                    # TODO: Add tier 2 keywords
                    # Example: 'uniswap', 'aave', 'restaking'
                ],
                'weight': 70,
            },
            'tier_3': {
                'keywords': [
                    # TODO: Add tier 3 keywords
                    # Example: 'defi', 'dex', 'nft'
                ],
                'weight': 40,
            },
            'negative': {
                'keywords': [
                    # TODO: Add negative keywords
                    # Example: 'meme coin', 'pump and dump'
                ],
                'weight': -50,
            }
        },

        # Selection criteria for this topic
        'selection': {
            'worth_reading': {
                'min': 3,
                'max': 5,
                'min_score': 40,
            }
        }
    },

    # Topic 2: Tech
    'tech': {
        'enabled': True,
        'display_name': 'Tech',
        'icon': '💻',
        'description': 'AI, startups, developer tools',

        'sources': {
            'telegram': [
                # TODO: Add channels here
            ],

            'websites': [
                # TODO: Add websites here
            ],

            'rss': [
                # TODO: Add RSS feeds here
            ],
        },

        'keywords': {
            'tier_1': {
                'keywords': [
                    # TODO: Add tier 1 keywords
                    # Example: 'openai', 'anthropic', 'gpt-5', 'claude'
                ],
                'weight': 100,
            },
            'tier_2': {
                'keywords': [
                    # TODO: Add tier 2 keywords
                    # Example: 'chatgpt', 'copilot', 'vercel'
                ],
                'weight': 70,
            },
            'tier_3': {
                'keywords': [
                    # TODO: Add tier 3 keywords
                    # Example: 'artificial intelligence', 'machine learning'
                ],
                'weight': 40,
            },
            'negative': {
                'keywords': [
                    # TODO: Add negative keywords
                    # Example: 'clickbait', 'you won\'t believe'
                ],
                'weight': -50,
            }
        },

        'selection': {
            'worth_reading': {
                'min': 3,
                'max': 5,
                'min_score': 40,
            }
        }
    },

    # Topic 3: AI Safety (disabled by default)
    'ai_safety': {
        'enabled': False,
        'display_name': 'AI Safety',
        'icon': '🛡️',
        'description': 'AI alignment, safety research, governance',

        'sources': {
            'telegram': [],
            'websites': [],
            'rss': [
                # {
                #     'name': 'AI Alignment Forum',
                #     'url': 'https://www.alignmentforum.org/feed.xml',
                #     'priority': 'high',
                #     'enabled': True
                # },
            ],
        },

        'keywords': {
            'tier_1': {
                'keywords': [
                    'ai safety', 'alignment', 'agi risk',
                    'superintelligence', 'existential risk',
                ],
                'weight': 100,
            },
            'tier_2': {
                'keywords': [
                    'interpretability', 'mechanistic interpretability',
                    'ai governance', 'ai regulation',
                ],
                'weight': 70,
            },
            'tier_3': {
                'keywords': ['ai ethics', 'responsible ai'],
                'weight': 40,
            },
            'negative': {
                'keywords': [],
                'weight': -50,
            }
        },

        'selection': {
            'worth_reading': {
                'min': 2,
                'max': 4,
                'min_score': 40,
            }
        }
    },

    # Topic 4: Startup & VC (disabled by default)
    'startup': {
        'enabled': False,
        'display_name': 'Startup & VC',
        'icon': '🚀',
        'description': 'Startup funding, VC trends, entrepreneurship',

        'sources': {
            'telegram': [],
            'websites': [],
            'rss': [
                # {
                #     'name': 'TechCrunch Startups',
                #     'url': 'https://techcrunch.com/tag/startups/feed/',
                #     'priority': 'high',
                #     'enabled': True
                # },
            ],
        },

        'keywords': {
            'tier_1': {
                'keywords': [
                    'series a', 'series b', 'series c',
                    'unicorn', 'ipo', 'acquisition',
                ],
                'weight': 100,
            },
            'tier_2': {
                'keywords': [
                    'funding round', 'venture capital', 'seed round',
                    'yc', 'y combinator', 'a16z',
                ],
                'weight': 70,
            },
            'tier_3': {
                'keywords': ['startup', 'founder', 'entrepreneur'],
                'weight': 40,
            },
            'negative': {
                'keywords': [],
                'weight': -50,
            }
        },

        'selection': {
            'worth_reading': {
                'min': 2,
                'max': 4,
                'min_score': 40,
            }
        }
    },
}

# ============================================================
# GLOBAL SETTINGS (apply to all topics)
# ============================================================

GLOBAL_SETTINGS = {
    # Telegram API
    'telegram_api': {
        'api_id': os.getenv('TELEGRAM_API_ID', 'YOUR_API_ID'),
        'api_hash': os.getenv('TELEGRAM_API_HASH', 'YOUR_API_HASH'),
        'phone': os.getenv('TELEGRAM_PHONE', '+84...'),
        'max_messages_per_channel': 50,
        'time_window_hours': 24,
        'skip_spam': True,
        'skip_media_only': True,
    },

    # RSS settings
    'rss': {
        'max_items_per_feed': 20,
        'time_window_hours': 24,
    },

    # Keyword matching
    'keywords': {
        'case_sensitive': False,
        'match_whole_word': False,
        'search_in': ['title', 'summary'],
        'min_keyword_score': 0,
    },

    # Engagement weights
    'engagement': {
        'telegram': {
            'views': {
                'weight': 1.0,
                'normalization': {
                    'min': 1_000,
                    'max': 100_000,
                    'max_points': 50,
                }
            },
        },
        'thefeed': {
            'views': {
                'weight': 1.0,
                'normalization': {
                    'min': 5_000,
                    'max': 5_000_000,
                    'max_points': 50,
                }
            },
            'engagement_rate': {
                'weight': 10.0,
                'threshold': 2.0,
                'bonus_points': 10,
            }
        },
        'website': {
            'default_score': 20,
        },
        'rss': {
            'high_priority': 30,
            'medium_priority': 20,
            'low_priority': 10,
        }
    },

    # Source authority
    'source_authority': {
        'priority_multiplier': {
            'high': 1.5,
            'medium': 1.0,
            'low': 0.7,
        },
        'type_multiplier': {
            'research': 1.3,
            'news': 1.0,
            'alpha': 1.1,
            'community': 0.8,
            'aggregator': 0.9,
        },
        'max_bonus': 15,
    },

    # Recency bonus
    'recency': {
        'last_3h': 10,
        'last_6h': 7,
        'last_12h': 3,
        'older': 0,
    },

    # Quality filters
    'quality': {
        'min_text_length': 50,
        'min_views': 100,
        'max_age_hours': 24,
        'require_link': True,
    },

    # Spam detection
    'spam_keywords': [
        'buy now', 'limited time', 'click here', 'join our',
        'pump', 'moon', 'wagmi', 'lfg', 'free money',
        'airdrop', 'giveaway', '\U0001f680\U0001f680\U0001f680', 'join channel',
        'subscribe', 'follow us', 'don\'t miss',
    ],
}

# ============================================================
# TOP STORIES SELECTION (cross-topic)
# ============================================================

TOP_STORIES_SETTINGS = {
    'min': 2,
    'max': 5,
    'min_score': 80,
    'require_keyword_match': True,
    'breaking_override': True,
}

# ============================================================
# OUTPUT SETTINGS
# ============================================================

OUTPUT_SETTINGS = {
    # Telegram delivery
    'telegram': {
        'enabled': True,
        'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN'),
        'chat_id': os.getenv('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID'),
        'parse_mode': 'Markdown',
    },

    # Markdown file output
    'markdown': {
        'enabled': True,
        'path': '~/Documents/news-briefs',
        'filename_format': '{date}/{time}.md',
        # Available variables:
        # - {date}: YYYY-MM-DD
        # - {time}: HHmm (e.g., 0700, 1430)
        # - {timestamp}: YYYYMMDDHHmm
        # - {datetime}: YYYY-MM-DD_HHmm
        # - {year}, {month}, {day}, {hour}, {minute}
        #
        # Examples:
        # - '{date}/{time}.md' -> 2026-05-23/0700.md
        # - '{timestamp}.md' -> 20260523_0700.md
        # - '{date}/brief-{time}.md' -> 2026-05-23/brief-0700.md
        # - '{year}/{month}/{day}-{time}.md' -> 2026/05/23-0700.md
        'keep_days': 30,  # Delete files older than N days (0 = keep forever)
        'create_index': True,  # Create index.md listing all briefs
    },

    # Brief formatting
    'brief': {
        'language': 'vi',
        'icon': '📰',  # Single icon for all briefs
    }
}

# ============================================================
# SYSTEM SETTINGS
# ============================================================

STATE_DIR = '.state'
LOGS_DIR = 'logs'

SCRAPE_TIMEOUT_SECONDS = 300
JSON_FRESHNESS_MINUTES = 15
TIME_WINDOW_HOURS = 24

MAX_RETRIES = 1
RETRY_DELAY_SECONDS = 30

LOG_LEVEL = 'INFO'

# ============================================================
# BACKWARD COMPATIBILITY
# Auto-generated from TOPICS and GLOBAL_SETTINGS
# ============================================================


def _generate_legacy_config():
    """Generate legacy config structure from TOPICS"""
    news_sources = {
        'telegram': {
            'enabled': any(t['enabled'] for t in TOPICS.values()),
            'channels': {},
            'settings': {
                'max_messages_per_channel': GLOBAL_SETTINGS['telegram_api']['max_messages_per_channel'],
                'time_window_hours': GLOBAL_SETTINGS['telegram_api']['time_window_hours'],
                'skip_spam': GLOBAL_SETTINGS['telegram_api']['skip_spam'],
                'skip_media_only': GLOBAL_SETTINGS['telegram_api']['skip_media_only'],
            }
        },
        'websites': {
            'enabled': any(t['enabled'] for t in TOPICS.values()),
            'sources': []
        },
        'rss': {
            'enabled': any(
                t['enabled'] and len(t['sources'].get('rss', [])) > 0
                for t in TOPICS.values()
            ),
            'feeds': {},
            'settings': GLOBAL_SETTINGS['rss']
        },
    }

    keyword_filters = {}

    for topic_id, topic in TOPICS.items():
        if not topic['enabled']:
            continue

        # Aggregate telegram channels
        news_sources['telegram']['channels'][topic_id] = \
            topic['sources'].get('telegram', [])

        # Aggregate websites
        news_sources['websites']['sources'].extend(
            topic['sources'].get('websites', [])
        )

        # Aggregate RSS feeds
        news_sources['rss']['feeds'][topic_id] = \
            topic['sources'].get('rss', [])

        # Aggregate keywords
        keyword_filters[topic_id] = topic['keywords']

    keyword_filters['settings'] = GLOBAL_SETTINGS['keywords']

    return news_sources, keyword_filters


NEWS_SOURCES, KEYWORD_FILTERS = _generate_legacy_config()

# Top-level credential aliases
TELEGRAM_API_ID = GLOBAL_SETTINGS['telegram_api']['api_id']
TELEGRAM_API_HASH = GLOBAL_SETTINGS['telegram_api']['api_hash']
TELEGRAM_PHONE = GLOBAL_SETTINGS['telegram_api']['phone']
TELEGRAM_BOT_TOKEN = OUTPUT_SETTINGS['telegram']['bot_token']
TELEGRAM_CHAT_ID = OUTPUT_SETTINGS['telegram']['chat_id']

# Top-level settings aliases
ENGAGEMENT_WEIGHTS = GLOBAL_SETTINGS['engagement']
SOURCE_AUTHORITY = GLOBAL_SETTINGS['source_authority']
RECENCY_BONUS = GLOBAL_SETTINGS['recency']
SPAM_KEYWORDS = GLOBAL_SETTINGS['spam_keywords']
QUALITY_FILTERS = GLOBAL_SETTINGS['quality']

SELECTION_CRITERIA = {
    'top_stories': TOP_STORIES_SETTINGS,
    'worth_reading': {
        topic_id: topic['selection']['worth_reading']
        for topic_id, topic in TOPICS.items()
        if topic['enabled']
    },
    'require_keyword_match': False,
    'breaking_override': TOP_STORIES_SETTINGS['breaking_override'],
}

BRIEF_SETTINGS = OUTPUT_SETTINGS['brief']
