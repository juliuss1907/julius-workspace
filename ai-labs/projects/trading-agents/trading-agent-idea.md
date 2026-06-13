# Hệ thống Trading Crypto sử dụng Agent để phân tích

## Ý tưởng chính

- Sử dụng các **agent AI** (Hermes, OpenClaw) để theo dõi và phân tích các đồng coin.
- Kết hợp **Technical Analysis** (chỉ báo, chart patterns) với **News & Sentiment Analysis** để có góc nhìn toàn diện và đề xuất setup trading.
- Sử dụng **nhiều agent chuyên biệt** thay vì một agent đơn lẻ — mỗi agent làm một việc, phối hợp theo pipeline.
## Loại giao dịch
Spot + Futures/Perp
- Khi nào dùng spot: Mua và nắm giữ dài hạn, mua ngắn hạn (lướt sóng) với memecoin, coin biến động mạnh
- Khi nào dùng futures/perp: Trade ngắn hạn với các đồng coin lớn, ít biến động
---

## Data Sources

| Loại              | Nguồn đề xuất                                                     | Ghi chú                                              |
| **Giá real-time** | CEXs API (Binance, Bybit, OKX,...), DEXs API                                                     | OHLCV + order book depth                             |
| **On-chain**      | DefiLlama, CoinGecko, Token Terminal                              | TVL, volume, revenue                                 |
| **News**          | RSS (CryptoPanic, The Block), Telegram channels, Crypto news APIs | Lọc theo coin                                        |
| **Sentiment**     | X/Twitter (xurl), Telegram groups, Reddit                         | Dùng cho Quick & Flash mode                          |
| **Fundamentals**  | CoinGecko, CoinMarketCap, Token Terminal, Messari                 | Market cap, FDV, circulating supply, team, investors |

---

## Kiến trúc (5 tầng)

Lấy ý tưởng từ [TradingAgents của Tauric Research](https://github.com/TauricResearch/TradingAgents), build bằng **LangGraph** — modular, hỗ trợ nhiều LLM provider (OpenAI, Anthropic, xAI, OpenRouter, Ollama...).

### Tầng 0 — Screening Agent *(bổ sung)*

- Chạy định kỳ (tuần 1 lần) hoặc on-demand.
- Quét thị trường tìm coin tiềm năng: volume spike, trend narrative, social buzz.
- Đề xuất coin mới vào **watchlist** — Julius quyết định thêm hay không.
- Nếu không cần automation, watchlist do Julius tự quản lý thủ công.

### Tầng 1 — Analyst Team

| Agent | Nhiệm vụ |
|---|---|
| **Fundamentals Analyst** | Market cap, FDV, P/E (nếu có), tokenomics, team, investors, vesting schedule |
| **Sentiment Analyst** | Social media, tâm lý thị trường ngắn hạn, fear & greed index |
| **News Analyst** | Macro events, tin tức liên quan coin, regulatory updates, partnerships |
| **Technical Analyst** | MACD, RSI, Bollinger Bands, OBV, Ichimoku, chart patterns (H&S, double top/bottom, wedge), khung 30m/1h/2h/4h/1d |

### Tầng 2 — Researcher Team

- **Bull Researcher** và **Bear Researcher** tranh luận có cấu trúc.
- Mỗi bên đưa ra luận điểm + dẫn chứng dựa trên dữ liệu từ Tầng 1.
- Kết quả: báo cáo cân bằng giữa cơ hội và rủi ro.

### Tầng 3 — Trader Agent

- Tổng hợp báo cáo từ Tầng 1 + Tầng 2 → ra đề xuất: **BUY / HOLD / SELL**.
- Kèm entry, stop loss, take profit (nếu có tín hiệu rõ ràng).

### Tầng 4 — Risk Management + Portfolio Manager

| Agent                      | Nhiệm vụ                                                                                                                                                      |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Risk Management**        | Đánh giá volatility (ATR, BB width), liquidity (spread, volume 24h, order book depth). **Threshold mẫu:** spread >0.5% hoặc volume <$1M → cảnh báo / từ chối. |
| **Portfolio Manager**      | Kiểm tra exposure, risk/reward ratio, approve hoặc reject lệnh.                                                                                               |
| **Gửi báo cáo cho Julius** | Sau khi Portfolio Manager đánh giá xong, toàn bộ báo cáo (từ Tầng 3 + Tầng 4) được gửi cho Julius kèm đề xuất. Julius là người quyết định cuối cùng.          |
|                            |                                                                                                                                                               |

---

## Directory Structure

```
trading-agents/
├── agents/
│   ├── analysts/          # 4 analyst agents
│   │   ├── fundamentals.py
│   │   ├── sentiment.py
│   │   ├── news.py
│   │   └── technical.py
│   ├── researchers/       # bull & bear
│   │   ├── bull.py
│   │   └── bear.py
│   ├── trader.py
│   ├── risk_mgmt.py
│   ├── managers/
│   │   └── portfolio.py
│   ├── screening.py       # Tầng 0
	│   └── utils/
├── dataflows/             # Data fetching & processing
├── graph/                 # LangGraph orchestration
├── llm_clients/           # Multi-provider LLM wrappers
├── config/
│   ├── default_config.py
│   └── thresholds.yaml    # Risk thresholds, triggers
├── watchlist.json         # Coins/tokens đang theo dõi
├── journal/               # Log các lệnh đã thực hiện
├── reports/               # Báo cáo .md output
│   ├── daily/             # YYYY-MM-DD-full.md
│   └── quick/             # YYYY-MM-DD-HH-quick.md
├── signals.log            # Tất cả tín hiệu đã gửi cho Julius
├── scripts/               # Utility scripts
└── README.md
```

---

## Chế độ hoạt động

### 1. Full Mode

Chạy toàn bộ quy trình: Tầng 1 → Tầng 2 → Tầng 3 → Tầng 4.
Dùng model lớn cho chất lượng phân tích tốt nhất.
**Khi nào chạy:**
- Automation: 7h sáng mỗi ngày
- On-demand: Khi Julius yêu cầu phân tích một coin cụ thể

### 2. Quick Mode

Chạy một phần quy trình: News Analyst + Technical Analyst + Trader Agent → bỏ qua Fundamentals, Researcher debate, Risk Manager.
Dùng model trung bình.
**Khi nào chạy:**
- Automation: Các khung giờ 11h, 15h, 19h, 23h — quét toàn bộ watchlist, chart khung 4h/2h/1h
- On-demand — **Routine Quick:** Y hệt automation quick, quét watchlist khi anh không yêu cầu coin cụ thể.
- On-demand — **Flash Quick:** Khi Julius hỏi "Sao coin ABC tăng/dump?" — Chỉ chạy cho 1 coin, thêm Sentiment Analyst để check social buzz.

### 3. Lite Mode

Chỉ fetch giá + volume, không gọi LLM. Dùng model nhỏ nhất (hoặc chỉ run script Python).
**Khi nào chạy:**
- Automation: Mỗi 1 giờ, quét watchlist chart khung 30m và 1h.
- On-demand: Khi Julius hỏi về giá ("Giá ABC bao nhiêu?") — trả lời nhanh.

---

## Automation Schedule

| Giờ                                                 | Mode                             | Mô tả                                              |
| --------------------------------------------------- | -------------------------------- | -------------------------------------------------- |
| **07:00**                                           | Full                             | Quét toàn bộ watchlist → báo cáo .md + noti Julius |
| **08:00 → 23:00** (mỗi 1h)                          | Lite                             | Scan giá watchlist khung 30m/1h                    |
| **→** Nếu biến động **>10%**                        | → **Flash Quick** (ngay lập tức) | Scan news cho coin đó + noti Julius                |
| **→** Nếu biến động **5-10%** trong khung giờ Quick | → Quick mode đã lên lịch xử lý   | Không trigger thêm                                 |
| **→** Nếu biến động **<5%**                         | → Bỏ qua                         | Không noti                                         |
| **11:00, 15:00, 19:00, 23:00**                      | Quick                            | Quét watchlist chart 4h/2h/1h + news               |

**Cơ chế trigger Lite → Quick:**
- Lite mode phát hiện biến động >10% → **lập tức chạy Flash Quick** cho coin đó (bất kể giờ).
- Flash Quick: News Analyst (check tin tức nóng) + Technical Analyst (check khung 1h/4h) → gửi noti cho Julius.
- Sau khi Flash Quick chạy xong, Lite mode tiếp tục chu kỳ bình thường.

---

## On-demand

| Yêu cầu của Julius | Mode | Scope |
|---|---|---|
| "Phân tích coin ABC" | Full | 1 coin, toàn bộ pipeline + setup cụ thể |
| "Sao coin ABC tăng/dump?" | Flash Quick | 1 coin, News + Sentiment + TA nhanh |
| "Giá ABC bao nhiêu?" | Lite | 1 coin, chỉ fetch giá + khung 30m/1h |

---

## Chi phí & Tối ưu

| Mode | Model gợi ý | Chi phí ước tính (lần) | Ghi chú |
|---|---|---|---|
| Full | Claude Sonnet 4 / GPT-4o | ~$0.50–$1.50 | Dùng model lớn, 10+ agent calls |
| Quick | DeepSeek / Llama 3.3 70B | ~$0.10–$0.30 | 2–4 agent calls |
| Flash Quick | DeepSeek / Llama 3.3 70B | ~$0.05–$0.15 | 2–3 agent calls |
| Lite | Python script (ko LLM) | $0 | Chỉ fetch API |

- Cache kết quả phân tích nếu chart chưa thay đổi (ví dụ: cùng khung 1h, cách nhau < 30 phút).
- Watchlist tối đa 5–10 coin để kiểm soát chi phí.

---

## signal.log Format

Ghi lại tất cả tín hiệu gửi cho Julius — kể cả anh không action. Cuối tháng review để cải thiện agent.

```json
{
  "timestamp": "2026-05-30T07:00:00+07:00",
  "mode": "full",
  "coin": "BTC",
  "signal": "BUY",
  "entry": 68000,
  "sl": 65000,
  "tp": 72000,
  "confidence": 0.75,
  "summary": "BTC broke resistance at 67.5k with volume, RSI bullish divergence on 4h",
  "julius_action": null,
  "julius_action_time": null
}
```

Cuối tháng run script: `scripts/review_signals.py` → tổng hợp hit rate, số tín hiệu đã action, số tín hiệu đúng/sai.

---

## Systems Thinking — Nền tảng triết lý

> *Hệ thống trading agent này được thiết kế dựa trên tư duy **Systems Thinking**, lấy cảm hứng từ mô hình **Journeys to Value (JVM)** của Ian Batterbee và các nguyên lý từ Donella Meadows, Peter Senge, và trường hợp LEGO.*

### Market là một System — Agent là người đọc system đó

```
System Conditions (thị trường)
  ├── Cấu trúc: trend/ranging/volatile
  ├── Liquidity: order book depth, spread, volume
  ├── Incentives: narratives, liquidity grabs, whale positioning
  ├── Constraints: regulatory, funding rate, market cap
        ↓ shapes
Journeys (price action + tin tức)
  ├── Giá di chuyển theo đường đi mà system cho phép
  ├── Tin tức không tự sinh ra — nó là output của system conditions
  ├── "Desire paths" = vùng giá được giao dịch nhiều nhất
        ↓ produces
Outcomes & Effects (tín hiệu giao dịch)
  ├── Agent phát hiện pattern → đề xuất BUY/HOLD/SELL
  └── Julius quyết định có follow hay không
        ↓ feedback loop
Hệ thống tự điều chỉnh:
  ├── Risk thresholds thay đổi dựa trên volatility mới
  ├── Watchlist cập nhật dựa trên screening agent
  └── signals.log → cuối tháng review → cải thiện agent
```

### Nguyên lý LEGO — Tương thích ngược

Technical Analyst + News Analyst là **core brick system**, giống viên gạch LEGO 1958. Mỗi phase mới (Researcher, Risk, Portfolio, Screening) phải đảm bảo:

- **Tương thích ngược:** Báo cáo hôm nay so sánh được với báo cáo tuần trước (cùng format). Lite mode chạy độc lập, không phụ thuộc Full mode.
- **Không over-diversify:** Nếu add quá nhiều tầng mà mất focus vào core analysis system → LEGO crisis 2003.

### "Desire Paths" trong phân tích

> *"Just because a path is heavily used doesn't mean it is the best path."*

- Volume cao + KOLs kêu réo → desire path — nhưng chưa chắc là best path.
- Agent không chỉ dựa vào volume hoặc social mentions, mà phải kết hợp **system conditions** (liquidity, market regime) để phân biệt demand thật vs wash trading / bots.

> *"Repeated behaviour does not always reveal what people truly want. Sometimes it reveals the conditions they have adapted to."*

- Giá reject liên tục ở một vùng — không phải vì thị trường "muốn ở đó" — mà vì system conditions (sell wall, funding rate) đang reinforce vùng đó.
- Agent cần đọc được cấu trúc, không chỉ đọc price action bề mặt.

### Market Regime Detection *(bổ sung vào Technical Analyst)*

Trước khi chạy technical indicators, Technical Analyst cần xác định **market regime** trước:

| Regime | Đặc điểm | Cách xử lý |
|---|---|---|
| **Trend up** | Higher highs, higher lows, EMA bull cross | Ưu tiên long setups, momentum indicators |
| **Trend down** | Lower highs, lower lows, EMA bear cross | Ưu tiên short setups, bollinger band bounces |
| **Ranging** | Sideways, low ADX, equal highs/lows | Mean reversion strategies, RSI extremes |
| **Volatile** | Wide spreads, low liquidity, sudden spikes | Skip trading, tăng risk thresholds |

Feedback từ market regime này sẽ điều chỉnh cách analyst các tầng dưới đọc dữ liệu.

### Feedback Loop — Agent thông minh dần theo thời gian

signals.log không chỉ để review — nó là **feedback loop** cho toàn bộ system:

```
Tháng này → scoring agent phân tích hit rate
         → pattern nào agent đoán đúng nhiều?
         → pattern nào sai nhiều?
         → điều chỉnh prompt, thresholds, weight của từng analyst
```

Càng chạy lâu, agent càng hiểu system conditions nào thực sự dẫn đến trade thành công — chứ không chỉ dựa vào lý thuyết TA sách vở.

---

## Implementation Roadmap

### Phase 1 — Technical Analyst MVP
- Data fetcher: Binance API (OHLCV) + CoinGecko (market data)
- Technical Analyst agent (MACD, RSI, BB, volume)
- Lite mode + Full mode (technical only)
- Output: báo cáo .md hàng ngày

### Phase 2 — Thêm News & Sentiment
- RSS news fetcher (CryptoPanic / The Block)
- News Analyst agent
- Sentiment Analyst agent (X/Twitter + Telegram)
- Quick mode hoàn chỉnh

### Phase 3 — Researcher Debate
- Bull/Bear researcher agents
- Trader Agent tổng hợp

### Phase 4 — Risk & Portfolio
- Risk Management metrics
- Portfolio Manager
- signals.log + review script

### Phase 5 — Screening Agent
- Tự động đề xuất coin mới cho watchlist

Mỗi phase đều cho ra output hữu dụng ngay, không phải đợi build xong mới có kết quả.
