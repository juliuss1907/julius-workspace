# 13. Implementation Roadmap

## Tổng quan

Hệ thống được build qua 8 phases. Mỗi phase có output usable ngay, không cần build hoàn chỉnh mới có kết quả.

```
Phase 1: Core MVP (4-6 tuần)
Phase 2: News & Sentiment (3-4 tuần)
Phase 3: Derivatives & Researchers (3-4 tuần)
Phase 4: Risk & Portfolio (2-3 tuần)
Phase 5: Backtesting (2-3 tuần)
Phase 6: Adaptive Tuning (2 tuần)
Phase 7: Fine-tuning (3-4 tuần)
Phase 8: Screening Agent (1-2 tuần)

Total: ~20-28 tuần (~5-7 tháng)
```

---

## Phase 1: Core MVP (4-6 tuần)

**Goal:** Có hệ thống chạy được với Technical Analyst + paper trading

### Phase 1.1: Project Setup (3-5 ngày)

- [ ] Initialize Python project structure
- [ ] Setup dependencies (LangGraph, ccxt, pandas, sqlite, telegram-bot)
- [ ] Configure logging
- [ ] Create `.env.example` với required keys
- [ ] Setup git repo

**Deliverable:** Project skeleton + dev environment ready

### Phase 1.2: Data Fetchers (1 tuần)

- [ ] Binance WebSocket client (real-time price stream)
- [ ] Binance REST client (historical OHLCV)
- [ ] CCXT integration (multi-exchange fallback)
- [ ] GeckoTerminal API client (DEX data)
- [ ] Parallel fetch architecture với error handling
- [ ] Cache layer với TTL

**Deliverable:** Có thể fetch data cho watchlist

### Phase 1.3: Storage Layer (3-5 ngày)

- [ ] SQLite schema (portfolio, positions, signals)
- [ ] JSON state files (system_state, cache)
- [ ] CSV writer cho OHLCV data
- [ ] Snapshot mechanism
- [ ] File locking (fcntl)

**Deliverable:** State persistence hoạt động

### Phase 1.4: Technical Analyst Agent (1 tuần)

- [ ] Indicator calculations (RSI, MACD, Bollinger Bands, OBV, ATR)
- [ ] Chart pattern detection (basic: H&S, double top/bottom)
- [ ] Market regime detection (trend/ranging/volatile)
- [ ] Multi-timeframe analysis
- [ ] Sub-score calculation
- [ ] LLM integration (OpenCode Go + Ollama fallback)

**Deliverable:** Technical Analyst chạy được standalone

### Phase 1.5: Paper Trading Engine (1 tuần)

- [ ] Paper portfolio state ($10k initial)
- [ ] Order simulation (market + limit)
- [ ] Real-time slippage calculation
- [ ] Fees calculation (Binance regular)
- [ ] Position monitoring (SL/TP triggers)
- [ ] P&L tracking

**Deliverable:** Paper trading auto-execute

### Phase 1.6: Telegram Bot (3-5 ngày)

- [ ] Bot setup với python-telegram-bot
- [ ] Send notifications (signals, alerts)
- [ ] Basic commands (/status, /pnl, /positions)
- [ ] Error logging

**Deliverable:** Notifications qua Telegram

### Phase 1.7: Lite + Full Mode (3-5 ngày)

- [ ] Lite mode (price monitoring + 10% trigger)
- [ ] Full mode (Technical Analyst only, no other agents)
- [ ] Cron scheduling (07:00 Full, hourly Lite)
- [ ] Daily report generation (markdown)

**Deliverable:** System tự chạy 7h sáng + giám sát giá

### Phase 1.8: Error Handling Foundation (1 tuần)

- [ ] Retry logic với exponential backoff
- [ ] Circuit breakers cho APIs
- [ ] LLM fallback chain (OpenCode Go → Ollama)
- [ ] Heartbeat monitoring
- [ ] Graceful degradation

**Deliverable:** System resilient với failures

**🎯 End of Phase 1:** Hệ thống core chạy ổn định, có thể paper trade tự động dựa trên Technical Analyst.

---

## Phase 2: News & Sentiment (3-4 tuần)

**Goal:** Thêm dimensions phân tích ngoài technical

### Phase 2.1: News Analyst (1 tuần)

- [ ] CryptoPanic RSS fetcher
- [ ] The Block RSS fetcher
- [ ] News filtering by coin
- [ ] Sentiment classification (positive/negative/neutral)
- [ ] Source quality scoring
- [ ] LLM-based summarization

**Deliverable:** News analysis cho mỗi coin

### Phase 2.2: Sentiment Analyst (1-1.5 tuần)

- [ ] X/Twitter integration (qua agent-reach skill)
- [ ] Reddit scraping (r/cryptocurrency)
- [ ] Fear & Greed Index API
- [ ] Polymarket CLOB API integration
- [ ] Smart money vs retail detection
- [ ] Sentiment score calculation

**Deliverable:** Sentiment Analyst hoạt động

### Phase 2.3: Quick Mode (3-5 ngày)

- [ ] Quick mode pipeline (Technical + News + Derivatives)
- [ ] Flash Quick mode (thêm Sentiment)
- [ ] Lite → Flash trigger (>10% biến động)
- [ ] Schedule: 11h, 15h, 19h, 23h
- [ ] Quick reports generation

**Deliverable:** Quick + Flash Quick chạy được

### Phase 2.4: Confidence Scoring v1 (3-5 ngày)

- [ ] Weighted score calculation
- [ ] Per-mode weights (Full/Quick/Flash)
- [ ] Confidence thresholds → position size adjustment
- [ ] Sub-score storage trong signals.log

**Deliverable:** Confidence scoring system

**🎯 End of Phase 2:** Multi-dimensional analysis với confidence scoring.

---

## Phase 3: Derivatives & Researchers (3-4 tuần)

**Goal:** Thêm derivatives data + Bull/Bear debate

### Phase 3.1: Derivatives Data (1 tuần)

- [ ] Hyperliquid API integration
- [ ] Binance Futures API integration
- [ ] Lighter API integration
- [ ] Funding rate aggregation
- [ ] Open Interest tracking
- [ ] Liquidation heatmap analysis

**Deliverable:** Derivatives data đầy đủ

### Phase 3.2: Derivatives Analyst (3-5 ngày)

- [ ] Funding rate analysis (contrarian signals)
- [ ] OI + price correlation
- [ ] Liquidation magnet detection
- [ ] Cross-source validation
- [ ] Sub-score calculation

**Deliverable:** Derivatives Analyst integrated

### Phase 3.3: Researcher Team (1 tuần)

- [ ] Bull Researcher agent (luận điểm long)
- [ ] Bear Researcher agent (luận điểm short)
- [ ] Structured debate (2-3 rounds)
- [ ] Consensus detection
- [ ] Confidence adjustment (+0.05 / -0.10)

**Deliverable:** Bull/Bear debate hoạt động

### Phase 3.4: Trader Agent (3-5 ngày)

- [ ] Aggregate inputs từ Tầng 1 + Tầng 2
- [ ] Final BUY/SELL/HOLD decision
- [ ] Entry/SL/TP calculation
- [ ] Confidence finalization
- [ ] Output formatting

**Deliverable:** Trader Agent ra final signals

**🎯 End of Phase 3:** Pipeline phân tích hoàn chỉnh với 5 analysts + 2 researchers + trader.

---

## Phase 4: Risk & Portfolio Management (2-3 tuần)

**Goal:** Position sizing thông minh + portfolio constraints

### Phase 4.1: Risk Manager Agent (1 tuần)

- [ ] Volatility analysis (ATR, BB width)
- [ ] Liquidity check (spread, volume, orderbook depth)
- [ ] Risk thresholds enforcement
- [ ] Position size adjustment
- [ ] Approval/rejection logic

**Deliverable:** Risk Manager validates signals

### Phase 4.2: Portfolio Manager (3-5 ngày)

- [ ] Current exposure tracking
- [ ] Constraints enforcement (max 30%/coin, 80% total, 5 positions)
- [ ] Correlated exposure check
- [ ] Final approve/reject

**Deliverable:** Portfolio Manager control

### Phase 4.3: Position Sizing Logic (3-5 ngày)

- [ ] Risk-based sizing (3% per trade)
- [ ] Confidence multiplier
- [ ] Coin type allocation (memecoin 5%, large cap 30%...)
- [ ] Futures leverage by confidence
- [ ] Margin safety checks

**Deliverable:** Sophisticated position sizing

### Phase 4.4: SL/TP Strategies (3-5 ngày)

- [ ] ATR-based SL (default)
- [ ] Fixed % SL (fallback)
- [ ] Support/Resistance SL
- [ ] R:R-based TP
- [ ] Trailing stop

**Deliverable:** Multiple SL/TP strategies

### Phase 4.5: Daily/Weekly Summaries (3 ngày)

- [ ] Daily summary template (23h)
- [ ] Weekly summary template (Chủ nhật 23h)
- [ ] Performance analytics
- [ ] Cost tracking

**Deliverable:** Periodic summaries qua Telegram

**🎯 End of Phase 4:** Full risk/portfolio management hoạt động.

---

## Phase 5: Backtesting (2-3 tuần)

**Goal:** Validate strategy + benchmark performance

### Phase 5.1: Backtest Engine (1-1.5 tuần)

- [ ] DataLoader (load 6 months historical)
- [ ] Rule-based strategy simulator
- [ ] Trade execution simulation
- [ ] Slippage model (fixed for backtest)
- [ ] Fees calculation
- [ ] Position monitoring

**Deliverable:** Backtest engine hoạt động

### Phase 5.2: Performance Analytics (3-5 ngày)

- [ ] Win rate, Sharpe, Max DD calculations
- [ ] Buy-and-hold BTC baseline
- [ ] Buy-and-hold watchlist baseline
- [ ] Alpha calculation
- [ ] Trade-by-trade breakdown

**Deliverable:** Comprehensive metrics

### Phase 5.3: Monthly Automation (3-5 ngày)

- [ ] Cron job (ngày 1 hàng tháng, 03:00)
- [ ] Auto-generate reports
- [ ] Telegram summary notification
- [ ] Comparison với previous months

**Deliverable:** Monthly backtest tự chạy

**🎯 End of Phase 5:** Có data để evaluate strategy quality.

---

## Phase 6: Adaptive Parameter Tuning (2 tuần)

**Goal:** System tự đề xuất parameter improvements

### Phase 6.1: Parameter Tuning Engine (1 tuần)

- [ ] Per-coin config files
- [ ] Parameter grid generation
- [ ] Backtest 30 combinations
- [ ] Composite score ranking
- [ ] Top 3 selection

**Deliverable:** Engine tìm best parameters

### Phase 6.2: Approval Workflow (3-5 ngày)

- [ ] Proposal generation (markdown)
- [ ] Telegram notification
- [ ] Natural language approval parsing
- [ ] Apply changes mechanism
- [ ] Backup previous configs

**Deliverable:** Julius approve qua Telegram

### Phase 6.3: Auto-rollback (3 ngày)

- [ ] Performance degradation detection (2 tuần after change)
- [ ] Auto-rollback nếu win rate giảm >10%
- [ ] Rollback history tracking

**Deliverable:** Safety mechanism

### Phase 6.4: Self-adjusting Confidence Weights (3 ngày)

- [ ] Monthly accuracy analysis per analyst
- [ ] Weight adjustment algorithm
- [ ] Approval workflow
- [ ] Constraints (Technical ≥50%)

**Deliverable:** Confidence weights adapt

**🎯 End of Phase 6:** System tự cải thiện qua thời gian.

---

## Phase 7: Fine-tuning (3-4 tuần)

**Goal:** Agents học từ knowledge base + historical performance

### Phase 7.1: Knowledge Base Setup (3-5 ngày)

- [ ] Tạo folder structure
- [ ] PDF text extraction
- [ ] Markdown processing
- [ ] Content chunking
- [ ] Categorization

**Deliverable:** Knowledge base ready (chờ Julius bổ sung tài liệu)

### Phase 7.2: Training Data Pipeline (1 tuần)

- [ ] Knowledge data extraction
- [ ] Historical analysis collection
- [ ] Julius feedback parsing
- [ ] Data formatting (JSONL)
- [ ] Train/val split

**Deliverable:** Training data ready

### Phase 7.3: Fine-tuning Pipeline (1 tuần)

- [ ] Fine-tuning job submission (DeepSeek V4 Flash)
- [ ] Job monitoring
- [ ] Model versioning
- [ ] Cost tracking

**Deliverable:** Fine-tuning workflow

### Phase 7.4: A/B Testing & Deployment (3-5 ngày)

- [ ] A/B test framework
- [ ] Performance comparison
- [ ] Auto-deploy nếu improvement ≥5%
- [ ] Auto-reject nếu degradation >2%
- [ ] Manual rollback option

**Deliverable:** Safe deployment workflow

**🎯 End of Phase 7:** Agents tự học và cải thiện.

---

## Phase 8: Screening Agent (1-2 tuần)

**Goal:** Tự động đề xuất coin mới cho watchlist

### Phase 8.1: Market Screening (1 tuần)

- [ ] Volume spike detection (>200% 7d avg)
- [ ] Trending narratives detection
- [ ] Social buzz scoring
- [ ] New listings tracking
- [ ] Filtering logic

**Deliverable:** Engine tìm coin tiềm năng

### Phase 8.2: Watchlist Proposals (3-5 ngày)

- [ ] Weekly schedule (Chủ nhật 22h)
- [ ] Proposal generation (3-5 coins)
- [ ] Telegram notification
- [ ] Julius approval workflow
- [ ] Watchlist update mechanism

**Deliverable:** Screening tự động

**🎯 End of Phase 8:** Hệ thống hoàn chỉnh.

---

## Dependencies & Critical Path

```
Phase 1 (foundation)
  ├── Phase 2 (depends on Phase 1)
  │   └── Phase 3 (depends on Phase 2)
  │       └── Phase 4 (depends on Phase 3)
  │           ├── Phase 5 (Backtesting — uses all analysts)
  │           ├── Phase 6 (Tuning — uses Phase 5 backtest)
  │           └── Phase 7 (Fine-tuning — uses historical data)
  │
  └── Phase 8 (Screening — independent, can be parallel)
```

**Critical path:** 1 → 2 → 3 → 4 → 5 → 6 → 7

**Parallel opportunities:**
- Phase 8 có thể làm song song với Phase 6-7
- Trong mỗi phase, một số tasks có thể parallel (ví dụ: nhiều analysts cùng implement)

---

## Milestones & Releases

| Version | After Phase | Capabilities |
|---|---|---|
| **v0.1 (MVP)** | Phase 1 | Technical analysis + paper trading + Telegram |
| **v0.2** | Phase 2 | Multi-dimensional analysis (Tech + News + Sentiment) |
| **v0.3** | Phase 3 | Full agent pipeline với Researchers |
| **v0.4** | Phase 4 | Risk & portfolio management |
| **v0.5** | Phase 5 | Backtesting validation |
| **v0.6** | Phase 6 | Self-tuning system |
| **v0.7** | Phase 7 | Fine-tuned agents |
| **v1.0** | Phase 8 | Complete autonomous system |

---

## Risk Mitigation

### Technical Risks

| Risk | Mitigation |
|---|---|
| **LLM API instability** | Dual provider (OpenCode Go + Ollama), fallback chain |
| **Data source outages** | Parallel fetch, multiple sources per data type |
| **Paper trade bugs** | Extensive testing, idempotency, snapshots |
| **Cost overrun** | Strict budget monitoring, auto-pause if exceeded |

### Project Risks

| Risk | Mitigation |
|---|---|
| **Scope creep** | Strict phase boundaries, defer features to next phase |
| **Integration issues** | Test mỗi phase trước khi move next |
| **Performance issues** | Profile early, optimize hotpaths |

---

## Success Metrics per Phase

### Phase 1 Success
- ✅ System chạy 7 ngày liên tục không crash
- ✅ Paper trading executes signals đúng
- ✅ Telegram notifications work
- ✅ Cost <$50/tháng

### Phase 2 Success
- ✅ Confidence scoring giải thích được win/loss
- ✅ News + Sentiment data flow ổn

### Phase 3 Success
- ✅ Bull/Bear debate generate insights hữu ích
- ✅ Derivatives data integrated

### Phase 4 Success
- ✅ Position sizing đúng theo rules
- ✅ Risk constraints enforced

### Phase 5 Success
- ✅ Backtest results match paper trading
- ✅ Alpha vs BTC HODL >0%

### Phase 6 Success
- ✅ Win rate cải thiện sau tuning ≥5%

### Phase 7 Success
- ✅ Fine-tuned models cải thiện accuracy ≥5%

### Phase 8 Success
- ✅ Screening đề xuất coins thực sự perform tốt

---

## Maintenance & Operations

Sau khi system hoàn chỉnh:

| Task | Frequency |
|---|---|
| **Code reviews** | Per major change |
| **Dependency updates** | Hàng tháng |
| **Backtest review** | Hàng tháng |
| **Cost optimization** | Hàng quý |
| **Strategy rebalancing** | Khi performance giảm |

---

## End State

Sau khi hoàn thành tất cả phases:

✅ **Multi-mode analysis** — Full / Quick / Flash / Lite
✅ **Comprehensive data** — Spot + Derivatives + News + Sentiment + On-chain
✅ **Adaptive learning** — Self-tuning + Fine-tuning monthly
✅ **Risk management** — Sophisticated position sizing + constraints
✅ **Reliable execution** — Robust error handling + recovery
✅ **Continuous improvement** — Monthly review + adjustments

**Total LOC estimate:** ~15,000-20,000 lines of Python code

**Total monthly cost (after deployment):** ~$80-120/month
- LLM costs: $50-80
- Fine-tuning: $30-55
- Storage/backup: ~$5

---

*This roadmap is a living document. Adjust based on learnings during implementation.*
