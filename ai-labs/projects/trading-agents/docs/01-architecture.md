# 01. Architecture — Kiến trúc Hệ thống

> **Context note (2026-06):** Tài liệu này mô tả product vision 5 tầng gốc. Kiến trúc thực tế đã được refactor qua orchestration refactor (Milestones A–C) — hệ thống hiện dùng custom async orchestration (`orchestration.analyze_symbol()`), không dùng LangGraph. Để hiểu boundary hiện tại của repo, đọc [14-rescue-architecture.md](14-rescue-architecture.md) và [15-orchestration-implementation-plan.md](15-orchestration-implementation-plan.md).

## Tổng quan

Hệ thống trading agents được thiết kế theo kiến trúc **5 tầng** (layers), lấy cảm hứng từ [TradingAgents của Tauric Research](https://github.com/TauricResearch/TradingAgents). Orchestration hiện dùng custom async pipeline qua `orchestration.analysis_runner.analyze_symbol()` — không dùng LangGraph.

## Tech Stack

| Component         | Technology                                                    |
| ----------------- | ------------------------------------------------------------- |
| **Orchestration** | Custom async pipeline (`orchestration.analyze_symbol()`)      |
| **LLM Providers** | OpenCode Go ($10/tháng) + Ollama Cloud Pro (20$/tháng)        |
| **Models**        | Qwen3.7 Max, GLM-5.1, Kimi K2.6, DeepSeek V4 Pro/Flash...    |
| **Data Storage**  | SQLite (state + positions + signals) + JSON (cache)           |
| **Notifications** | Telegram Bot API                                              |
| **Language**      | Python 3.10+                                                  |

---

## Kiến trúc 5 Tầng

```
┌─────────────────────────────────────────────────────────────┐
│  Tầng 0: Screening Agent (tuần 1 lần)                      │
│  Quét thị trường → đề xuất coin mới cho watchlist          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Tầng 1: Analyst Team (song song)                          │
│  ┌──────────────┬──────────────┬──────────────┬─────────┐  │
│  │ Technical    │ Fundamentals │ News         │Sentiment│  │
│  │ Analyst      │ Analyst      │ Analyst      │Analyst  │  │
│  └──────────────┴──────────────┴──────────────┴─────────┘  │
│  + Derivatives Analyst (funding, OI, liquidations)         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Tầng 2: Researcher Team (tranh luận)                      │
│  ┌───────────────────┐    ┌───────────────────┐           │
│  │ Bull Researcher   │ vs │ Bear Researcher   │           │
│  │ (luận điểm long)  │    │ (luận điểm short) │           │
│  └───────────────────┘    └───────────────────┘           │
│  → Báo cáo cân bằng giữa cơ hội và rủi ro                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Tầng 3: Trader Agent                                      │
│  Tổng hợp tất cả data → BUY / HOLD / SELL                  │
│  + Entry, SL, TP, Confidence score                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Tầng 4: Risk & Portfolio Management                       │
│  ┌─────────────────┐    ┌──────────────────┐              │
│  │ Risk Manager    │    │ Portfolio Manager│              │
│  │ (volatility,    │ →  │ (exposure,       │              │
│  │  liquidity)     │    │  approve/reject) │              │
│  └─────────────────┘    └──────────────────┘              │
│  → Gửi báo cáo + đề xuất cho Julius                        │
└─────────────────────────────────────────────────────────────┘
```

### Tầng 0 — Screening Agent

**Mục đích:** Tìm coin tiềm năng mới cho watchlist

**Chạy khi:**
- Automation: Tuần 1 lần (Chủ nhật 22h)
- On-demand: Khi Julius yêu cầu

**Tiêu chí screening:**
- Volume spike (>200% so với 7d average)
- Trending narratives (DeFi, AI, RWA...)
- Social buzz (X/Twitter mentions tăng đột biến)
- New listings trên top exchanges

**Output:** Đề xuất 3-5 coins → Julius quyết định thêm vào watchlist

---

### Tầng 1 — Analyst Team

Các analysts chạy **song song** (parallel), mỗi analyst tập trung 1 khía cạnh:

#### Technical Analyst

**Input:**
- OHLCV data (30m, 1h, 2h, 4h, 1d)
- Order book depth
- Volume profile
 
**Phân tích:** 
- **Indicators:** RSI, MACD, Bollinger Bands, OBV, Ichimoku
- **Chart patterns:** Head & Shoulders, Double top/bottom, Wedge, Triangle
- **Market regime detection:** Trend up/down, Ranging, Volatile
- **Multi-timeframe confirmation:** 1h + 4h + 1d alignment

**Output:**
- Signal direction (bullish/bearish/neutral)
- Entry zones
- Support/Resistance levels
- Sub-score (0.0 → 1.0)

#### Fundamentals Analyst

**Input:**
- Market cap, FDV, circulating supply
- Tokenomics (inflation rate, vesting schedule)
- Protocol metrics (TVL, revenue, active users)
- Team & investors info

**Phân tích:**
- Valuation (FDV/TVL ratio, P/E nếu có)
- Token unlock schedule
- Protocol health (growing/declining metrics)
- Competitive positioning

**Output:**
- Fundamental strength (strong/neutral/weak)
- Major risks
- Sub-score (0.0 → 1.0)

#### News Analyst

**Input:**
- RSS feeds (CryptoPanic, The Block)
- Aggregated news từ APIs

**Phân tích:**
- Relevant news trong 24h-7d
- Sentiment (positive/negative/neutral)
- Impact level (high/medium/low)
- Source credibility

**Output:**
- News summary
- Sentiment alignment với signal
- Sub-score (0.0 → 1.0)

#### Sentiment Analyst

**Input:**
- X/Twitter mentions (qua agent-reach skill)
- Reddit discussions
- Telegram group sentiment
- Fear & Greed Index
- Polymarket prediction odds

**Phân tích:**
- Social buzz intensity
- Retail vs smart money sentiment
- Contrarian indicators (extreme fear/greed)
- Prediction market odds trend

**Output:**
- Overall sentiment (bullish/bearish/neutral)
- Crowd positioning
- Sub-score (0.0 → 1.0)

#### Derivatives Analyst (bonus)

**Input:**
- Funding rates (Hyperliquid, Binance Futures, Lighter)
- Open Interest trend
- Liquidation heatmap

**Phân tích:**
- Funding rate alignment (positive → long crowded, negative → short crowded)
- OI + price correlation (OI↑ + price↑ = strong trend)
- Liquidation magnet zones

**Output:**
- Derivatives outlook
- Contrarian signals
- Sub-score (0.0 → 1.0)

---

### Tầng 2 — Researcher Team

**Bull Researcher** và **Bear Researcher** tranh luận có cấu trúc dựa trên data từ Tầng 1.

**Cách hoạt động:**
1. Bull Researcher đưa ra luận điểm bullish + dẫn chứng
2. Bear Researcher phản biện + đưa luận điểm bearish
3. Mỗi bên 2-3 rounds
4. Kết quả: Báo cáo cân bằng risk vs reward

**Impact:**
- Nếu cả 2 đồng thuận hướng signal → Confidence +0.05
- Nếu debate cân bằng → Confidence giữ nguyên
- Nếu debate nghiêng ngược signal → Confidence -0.10

---

### Tầng 3 — Trader Agent

**Input:** Tất cả output từ Tầng 1 + Tầng 2

**Quyết định:**
- **Signal:** BUY / SELL / HOLD
- **Entry price:** Giá vào lệnh đề xuất
- **Stop Loss:** Dựa trên ATR hoặc support/resistance
- **Take Profit:** R:R tối thiểu 1:2
- **Confidence score:** Weighted average từ analysts (0.0 → 1.0)

**Output format:**
```json
{
  "signal": "BUY",
  "coin": "BTC",
  "type": "spot",
  "entry": 68000,
  "stop_loss": 65000,
  "take_profit": 72000,
  "confidence": 0.78,
  "summary": "BTC broke resistance at 67.5k with volume..."
}
```

---

### Tầng 4 — Risk Management + Portfolio Manager

#### Risk Manager

**Kiểm tra:**
- Volatility (ATR, Bollinger Band width)
- Liquidity (spread, volume 24h, order book depth)
- Market conditions (extreme volatility → tăng risk threshold)

**Thresholds:**
- Spread >0.5% → warning
- Volume 24h <$1M → reject
- ATR >10% daily average → reduce position size

#### Portfolio Manager

**Kiểm tra:**
- Current exposure (max 80% portfolio)
- Max position size per coin (30%)
- Max correlated exposure (50% — ví dụ: BTC + ETH cùng long)
- Max open positions (5)

**Quyết định:** Approve hoặc Reject signal

**Final output:** Báo cáo đầy đủ gửi cho Julius qua Telegram.

---

## 3 Chế độ Hoạt động

### Full Mode

**Pipeline:** Tầng 1 → Tầng 2 → Tầng 3 → Tầng 4 (toàn bộ)

**Model:** Qwen3.7 Max / GLM-5.1 / Kimi K2.6 (lớn nhất)

**Khi chạy:**
- **Automation:** 7h sáng hàng ngày
- **On-demand:** Julius yêu cầu phân tích 1 coin cụ thể

**Output:** Báo cáo markdown chi tiết `reports/daily/YYYY-MM-DD-full.md`

**Chi phí:** ~$0.50-$1.50 / lần (10+ agent calls)

---

### Quick Mode

**Pipeline:** Technical + News + Derivatives → Trader (bỏ qua Fundamentals, Researchers, Risk/Portfolio)

**Model:** DeepSeek V4 Pro / Kimi K2.5

**Khi chạy:**
- **Automation:** 11h, 15h, 19h, 23h — quét toàn watchlist
- **On-demand (Routine Quick):** Julius yêu cầu "quick scan" toàn watchlist
- **On-demand (Flash Quick):** Julius hỏi "Sao BTC tăng/dump?" → chỉ scan 1 coin + thêm Sentiment Analyst

**Output:** `reports/quick/YYYY-MM-DD-HH-quick.md`

**Chi phí:** ~$0.10-$0.30 / lần

---

### Lite Mode

**Pipeline:** Không gọi LLM, chỉ fetch giá + volume

**Khi chạy:**
- **Automation:** Mỗi 1 giờ (08h-23h)
- **On-demand:** Julius hỏi "Giá BTC bao nhiêu?"

**Trigger mechanism:**
```
Lite mode phát hiện biến động >10% trong 1h
  → Lập tức trigger Flash Quick cho coin đó
  → Gửi alert cho Julius
```

**Output:** Log vào `logs/system.log`, không tạo report

**Chi phí:** $0 (chỉ API calls)

---

## Automation Schedule

| Giờ                      | Mode      | Mô tả                                          |
| ------------------------ | --------- | ---------------------------------------------- |
| **07:00**                | Full      | Quét toàn watchlist → báo cáo hàng ngày        |
| **08:00-23:00 (mỗi 1h)** | Lite      | Giám sát giá → trigger Flash Quick nếu >10%    |
| **11:00, 15h, 19h, 23h** | Quick     | Phân tích nhanh technical + news + derivatives |
| **Chủ nhật 22h**         | Screening | Tìm coin mới cho watchlist                     |


---

## Systems Thinking — Nền tảng Triết lý

> Hệ thống này được thiết kế dựa trên **Systems Thinking**, lấy cảm hứng từ **Journeys to Value (JVM)** của Ian Batterbee, Donella Meadows, Peter Senge, và case study LEGO.

### Market là một System

```
System Conditions (thị trường)
  ├── Cấu trúc: trend/ranging/volatile
  ├── Liquidity: orderbook depth, spread, volume
  ├── Incentives: narratives, liquidity grabs, whale positioning
  ├── Constraints: regulatory, funding rate, market cap
        ↓ shapes
Journeys (price action + news)
  ├── Giá di chuyển theo đường đi mà system cho phép
  ├── Tin tức là output của system conditions, không tự sinh ra
  ├── "Desire paths" = vùng giá traded nhiều nhất
        ↓ produces
Outcomes (signals)
  ├── Agent phát hiện pattern → BUY/SELL/HOLD
  └── Julius quyết định follow hay không
        ↓ feedback loop
System tự điều chỉnh:
  ├── Risk thresholds thay đổi theo volatility
  ├── Confidence weights tự adjust dựa trên accuracy
  └── Parameters tự tune dựa trên backtest
```

### Market Regime Detection

Trước khi chạy indicators, Technical Analyst phải xác định **market regime**:

| Regime         | Đặc điểm                                  | Strategy                           |
| -------------- | ----------------------------------------- | ---------------------------------- |
| **Trend Up**   | Higher highs, higher lows, EMA bull cross | Momentum strategies, long bias     |
| **Trend Down** | Lower highs, lower lows, EMA bear cross   | Short bias, BB bounces             |
| **Ranging**    | Sideways, low ADX, equal highs/lows       | Mean reversion, RSI extremes       |
| **Volatile**   | Wide spreads, low liquidity, spikes       | Skip trading, tăng risk thresholds |

### "Desire Paths" trong Phân tích

> *"Just because a path is heavily used doesn't mean it is the best path."*

- Volume cao + KOLs shilling → desire path, nhưng chưa chắc là best path
- Agent phải phân biệt **real demand** vs **wash trading / bots**
- Kết hợp system conditions (liquidity, funding rate) để validate

### Nguyên lý LEGO — Tương thích ngược

Technical + News Analyst = **core brick system** (giống LEGO 1958).

Mỗi phase mới phải đảm bảo:
- **Backward compatibility:** Báo cáo hôm nay compare được với tuần trước
- **Không over-diversify:** Focus vào core analysis, không thêm quá nhiều tầng mà mất direction

### Feedback Loop

```
signals.log + paper trades
  → Monthly review: analyst nào đúng nhiều?
  → Adjust confidence weights
  → Tune parameters per-coin
  → Fine-tune agents
  → Improve system
```

Càng chạy lâu, agent càng hiểu **system conditions nào** thực sự dẫn đến successful trades.

---

## Next

- [02. Data Sources](02-data-sources.md) — Chi tiết các nguồn dữ liệu
