# 02. Data Sources — Nguồn Dữ liệu

## Tổng quan

Hệ thống sử dụng **parallel fetch model** — tất cả sources chạy đồng thời, aggregate kết quả, không phải fallback chain.

## 1. Giá Real-time & Historical

### Binance WebSocket (Primary)

**Dùng cho:** Coin lớn (BTC, ETH, SOL...) trên CEX

**Data:**
- Real-time price stream
- OHLCV (Open, High, Low, Close, Volume)
- Order book depth

**Endpoint:** `wss://stream.binance.com:9443/ws`

**Rate limit:** Không giới hạn cho WebSocket subscriptions

---

### CCXT (Multi-exchange)

**Dùng cho:** 
- Fallback khi Binance fail
- Historical OHLCV data
- Multi-exchange price comparison

**Library:** `ccxt` (free version, REST API only)

**Exchanges:** Binance, OKX, Bybit

**Note:** Không có WebSocket (cần `ccxt.pro` với phí). Chỉ dùng REST cho historical data.

---

### GeckoTerminal API

**Dùng cho:** DEX prices, memecoin, token chưa list CEX

**Endpoint:** `https://api.geckoterminal.com/api/v2/`

**Data:**
- DEX pools trên 100+ chains
- OHLCV cho DEX pairs
- Trending tokens
- Pool info (liquidity, volume, 24h change)

**Rate limit:** Free tier, generous limits

**Docs:** https://apiguide.geckoterminal.com/

---

### DEX Screener API

**Dùng cho:** Thêm source cho memecoin/DEX data

**Endpoint:** `https://api.dexscreener.com/latest/dex/`

**Data:**
- Multi-chain DEX aggregation
- Real-time prices
- Social links, audit info

**Rate limit:** 300 requests/minute (free)

---

### Birdeye API

**Dùng cho:** Solana ecosystem, memecoin

**Endpoint:** `https://public-api.birdeye.so/`

**Data:**
- Solana DEX prices
- Token security check
- Holder analysis

**Rate limit:** Free tier available

---

## 2. Derivatives Data (Futures/Perp)

### Hyperliquid API

**Endpoint:** `https://api.hyperliquid.xyz/info`

**Data:**
- Funding rate
- Open Interest (OI)
- Liquidation levels
- Order book depth

**Rate limit:** Không khắt khe

**Docs:** https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api

---

### Binance Futures API

**Endpoint:** `https://fapi.binance.com/`

**Data:**
- Funding rate (USDT-M futures)
- Open Interest
- Long/Short ratio
- Top trader positions

**Rate limit:** 2400 requests/minute (weighted)

---

### Lighter API

**Endpoint:** `https://api.lighter.xyz/`

**Data:**
- Perp DEX (Arbitrum)
- Order book-based
- Funding rate
- Open Interest

**Rate limit:** Rõ ràng trong docs

**Docs:** https://apidocs.lighter.xyz/docs/rate-limits

---

## 3. On-chain & Fundamentals

### DefiLlama API

**Endpoint:** `https://api.llama.fi/`

**Data:**
- TVL (Total Value Locked) per protocol
- Protocol revenue
- Chain TVL breakdown

**Rate limit:** Free, không cần API key

---

### Token Terminal API

**Endpoint:** `https://api.tokenterminal.com/v2/`

**Data:**
- Protocol revenue
- P/F ratio (Price to Fees)
- Active users
- Transaction count

**Rate limit:** Free tier + paid plans

---

### Messari API

**Endpoint:** `https://data.messari.io/api/v1/`

**Data:**
- Tokenomics (supply schedule, inflation)
- Vesting calendar
- Market metrics
- Fundamental reports

**Rate limit:** Free tier available

---

### CoinGecko Demo API

**Endpoint:** `https://api.coingecko.com/api/v3/`

**Data:**
- Market cap, FDV
- Circulating supply
- Price (fallback only)

**Rate limit:** 10-30 calls/minute (free tier, cần API key)

**Note:** Chỉ dùng làm **fallback cuối cùng** cho fundamentals. Không dùng cho price feed chính.

---

## 4. News & Sentiment

### CryptoPanic RSS

**Endpoint:** `https://cryptopanic.com/api/v1/`

**Data:**
- Aggregated crypto news
- Filter theo coin
- Sentiment score (positive/negative/neutral)

**Rate limit:** Free tier 100 requests/day

---

### The Block RSS

**Endpoint:** `https://www.theblock.co/rss.xml`

**Data:**
- High-quality crypto journalism
- Institutional news
- Regulatory updates

**Format:** RSS feed

---

### X/Twitter (agent-reach skill)

**Access:** Qua `agent-reach` skill đã có sẵn

**Data:**
- Mentions, hashtags
- Influencer tweets
- Social sentiment

**Note:** Không cần Twitter API trực tiếp, dùng agent-reach skill.

---

### Telegram Channels

**Access:** Manual scraping hoặc Telegram API

**Data:**
- Alpha leaks
- Community sentiment
- Announcement channels

**Note:** Phase 2-3 mới implement scraping.

---

### Reddit

**Endpoint:** `https://www.reddit.com/r/cryptocurrency/.json`

**Data:**
- Retail sentiment
- Discussion threads
- Trending topics

**Rate limit:** 60 requests/minute (unauthenticated)

---

### Polymarket API

**Endpoint:** `https://clob.polymarket.com/`

**Data:**
- Prediction market odds
- Crypto-related markets (ETH ETF, Fed rate, protocol launches...)
- Probability changes over time

**Rate limit:** Generous cho read-only

**Docs:** https://docs.polymarket.com

**Use case:**
- Track odds của "Will ETH reach $5k by Q2?"
- Sudden odds change (>10% in 1h) → trigger News Analyst
- Macro events (Fed rate decision) → ảnh hưởng toàn thị trường

---

## 5. Market Structure

### Binance Order Book (REST/WebSocket)

**Data:**
- Bid/ask spread
- Order book depth
- Liquidity analysis

**Use:** Risk Manager đánh giá liquidity trước khi approve signal.

---

### Fear & Greed Index

**Endpoint:** `https://api.alternative.me/fng/`

**Data:**
- Market sentiment macro (0-100)
- Historical values

**Use:** Sentiment Analyst đánh giá crowd psychology.

---

## Parallel Fetch Model

### Cách hoạt động

```python
# Ví dụ: Fetch derivatives data
async def fetch_derivatives_data(coin):
    tasks = [
        fetch_hyperliquid(coin),      # Task 1
        fetch_binance_futures(coin),  # Task 2
        fetch_lighter(coin)           # Task 3
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Aggregate results
    derivatives_data = {
        "hyperliquid": results[0] if not isinstance(results[0], Exception) else None,
        "binance": results[1] if not isinstance(results[1], Exception) else None,
        "lighter": results[2] if not isinstance(results[2], Exception) else None
    }
    
    return derivatives_data
```

**Key points:**
- Tất cả sources chạy đồng thời
- Nếu 1 source fail → các source khác vẫn chạy
- Hiển thị **tất cả data** cho analyst (không aggregate/average)
- Threshold: chỉ cần ≥1 source thành công

---

## Cross-validation & Anomaly Detection

Khi có data từ nhiều sources, system tự động cross-check:

| Scenario | Action |
|---|---|
| Funding rate Hyperliquid ≠ Binance (>0.5%) | Flag anomaly, hiển thị cả 2 |
| Giá Binance vs OKX lệch >1% | Flag, có thể arbitrage opportunity |
| Volume spike chỉ 1 exchange | Flag wash trading risk |

Không tự chọn source nào "đúng" — analyst tự đánh giá với full context.

---

## Data Freshness Requirements

| Data type | Max staleness |
|---|---|
| Price (real-time modes) | 5 phút |
| OHLCV (1h candle) | 30 phút |
| Derivatives (funding, OI) | 1 giờ |
| Fundamentals (TVL, market cap) | 24 giờ |
| News | 1 giờ |
| Sentiment (social) | 30 phút |
| Polymarket odds | 6 giờ |

Nếu data cũ hơn threshold → warning flag cho analyst.

---

## API Keys Management

**Lưu trữ:** `.env` file (gitignored)

**Required keys:**
```bash
# LLM Providers
OPENCODE_GO_API_KEY=xxx
OLLAMA_CLOUD_API_KEY=xxx

# Exchange APIs
BINANCE_API_KEY=xxx
BINANCE_API_SECRET=xxx

# Data providers (optional, free tiers)
COINGECKO_API_KEY=xxx
MESSARI_API_KEY=xxx
TOKEN_TERMINAL_API_KEY=xxx

# Telegram
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx
```

**Security:**
- Binance API: **Read-only permissions** (không cho trade, withdraw)
- Rotate keys mỗi 3 tháng
- Monitor API usage trong logs

---

## Rate Limit Management

```python
# Rate limiter wrapper
class RateLimitedAPI:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
    
    async def call(self, func, *args, **kwargs):
        # Clean old calls
        now = time.time()
        self.calls = [t for t in self.calls if now - t < self.period]
        
        # Check limit
        if len(self.calls) >= self.max_calls:
            wait_time = self.period - (now - self.calls[0])
            await asyncio.sleep(wait_time)
        
        # Make call
        result = await func(*args, **kwargs)
        self.calls.append(time.time())
        return result
```

---

## Next

- [03. Execution Layer](03-execution-layer.md) — Pure advisory + paper trading
