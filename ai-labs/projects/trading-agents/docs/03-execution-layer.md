# 03. Execution Layer — Live Advisory + Paper Trading

## Tổng quan

Hệ thống có **dual mode** execution:

- **Live Trading:** Pure Advisory — Agent chỉ đưa ra đề xuất, Julius tự trade thủ công
- **Paper Trading:** Full Auto — Agent tự đặt lệnh trên paper portfolio để benchmark chất lượng

```
                Trader Agent ra signal
                         │
            ┌────────────┴────────────┐
            ↓                         ↓
    ┌──────────────┐          ┌──────────────┐
    │  LIVE MODE   │          │  PAPER MODE  │
    │ (Advisory)   │          │  (Full Auto) │
    └──────┬───────┘          └──────┬───────┘
           ↓                         ↓
    Telegram báo cáo            Tự đặt lệnh paper
    Julius tự trade             Track P&L ảo
    Julius log action           Track performance
```

---

## Live Mode (Pure Advisory)

### Workflow

1. Trader Agent ra signal → Risk/Portfolio Manager approve
2. System gửi báo cáo qua Telegram cho Julius
3. Julius đọc, tự quyết định trade hay không
4. Julius vào sàn (Binance, Hyperliquid...) tự đặt lệnh
5. Julius reply Telegram bot: "Đã mua BTC ở 68100" hoặc "Skip"
6. Bot update `signals.log` với Julius action

### Lý do chọn Pure Advisory cho Live

✅ **An toàn:** Không có risk auto-execute sai
✅ **Julius giữ control:** 100% quyết định cuối cùng
✅ **Đơn giản:** Không cần API keys với quyền trade
✅ **Linh hoạt:** Julius có thể adjust entry/SL/TP theo gut feel

### Format báo cáo gửi Julius

```
🔔 SIGNAL — BTC BUY

Mode: Full
Confidence: 0.78 (Moderate)

Setup:
  Entry: $68,000 (limit) hoặc market nếu giá <$68,200
  Stop Loss: $65,000 (-4.4%)
  Take Profit: $72,000 (+5.9%)
  R:R: 1:1.34

Position Size đề xuất:
  Spot: $4,533 (~6.7% portfolio)
  Hoặc Futures x5: $907 margin

Tóm tắt:
- BTC break resistance $67.5k với volume tăng 45%
- RSI bullish divergence trên 4h
- Funding rate neutral (-0.01%)
- News: ETF inflow $250M tuần qua
- Sentiment: Polymarket "BTC $70k by month-end" odds tăng từ 35% → 52%

Researchers debate:
- Bull: Strong technical breakout + ETF momentum
- Bear: Resistance lớn ở $70k, có thể reject

Báo cáo đầy đủ: reports/daily/2026-06-02-full.md

Reply để log action:
  /executed [price] — đã trade
  /skip — không trade
  /watching — đang theo dõi
```

---

## Paper Mode (Full Auto)

### Cấu hình

| Parameter           | Value                               |
| ------------------- | ----------------------------------- |
| **Initial Balance** | $10,000 USDT                        |
| **Trading Types**   | Spot + Futures                      |
| **Max Leverage**    | x10                                 |
| **Margin Type**     | Isolated                            |
| **Auto-execute**    | Tất cả signals từ Quick + Full mode |

### Workflow

```
Trader Agent ra signal
  ↓
Paper Executor:
  ├── Calculate position size (theo confidence)
  ├── Apply slippage (real-time order book)
  ├── Apply fees (Binance regular: 0.1% spot, 0.05% futures taker)
  ├── Update paper portfolio state
  └── Set monitoring task (track SL/TP)
  ↓
Position Monitor (real-time):
  ├── Check current price vs SL/TP
  ├── Auto-close khi hit
  └── Update P&L mỗi khi giá thay đổi
  ↓
Notification:
  └── Gửi report cho Julius khi position close
```

### Position Sizing Logic

```python
def calculate_paper_position_size(signal, portfolio):
    base_risk = portfolio.total * 0.03  # 3% risk per trade
    
    # Confidence multiplier
    if signal.confidence >= 0.8:
        risk_amount = base_risk * 1.0       # 100% size
    elif signal.confidence >= 0.6:
        risk_amount = base_risk * 0.75      # 75% size
    elif signal.confidence >= 0.4:
        risk_amount = base_risk * 0.5       # 50% size
    else:
        return None  # Skip
    
    # Position size based on SL distance
    sl_distance = abs(signal.entry - signal.stop_loss)
    position_value = risk_amount / (sl_distance / signal.entry)
    
    # Apply max position size constraint
    max_position = portfolio.total * 0.30  # 30% max per coin
    position_value = min(position_value, max_position)
    
    return position_value
```

### Slippage Model (Real-time)

Cho paper trade, dùng real-time order book để estimate slippage chính xác:

```python
def calculate_realtime_slippage(coin, side, size_usd):
    orderbook = fetch_binance_orderbook(coin)
    
    if side == "buy":
        levels = orderbook["asks"]
    else:
        levels = orderbook["bids"]
    
    filled = 0
    total_cost = 0
    
    for price, qty in levels:
        level_value = price * qty
        if filled + level_value >= size_usd:
            # Partial fill at this level
            remaining = size_usd - filled
            total_cost += remaining
            filled = size_usd
            break
        else:
            filled += level_value
            total_cost += level_value
    
    effective_price = total_cost / (size_usd / orderbook["mid_price"])
    slippage = (effective_price - orderbook["mid_price"]) / orderbook["mid_price"]
    
    return slippage
```

### Fees (Binance Regular User)

| Type | Maker | Taker |
|---|---|---|
| **Spot** | 0.1000% | 0.1000% |
| **USDT-M Futures** | 0.0200% | 0.0500% |

Mỗi trade tính fees 2 lần (entry + exit).

---

## Telegram Bot — Natural Language Logging

### Cách hoạt động

Julius reply tự nhiên, bot dùng DeepSeek V4 Flash parse intent:

**Examples:**

```
Julius: "Đã mua BTC ở 68100"
Bot: "✅ Confirmed: BTC spot BUY at $68,100. Logged."

Julius: "Vào short ETH 3200, x5"
Bot: "✅ Confirmed: ETH futures SHORT at $3,200, leverage x5. Logged."

Julius: "Skip signal này"
Bot: "✅ Marked as skipped. Reason recorded."

Julius: "Chốt lời BTC ở 72k"
Bot: "✅ Confirmed: BTC spot SELL at $72,000. P&L: +$300 (+5.9%). Logged."
```

### Bot Workflow

```python
async def handle_telegram_message(message, signal_id):
    # Parse với LLM
    intent = await parse_intent(message, model="deepseek-v4-flash")
    
    if intent.confidence < 0.7:
        # Không chắc → hỏi lại
        await bot.send_message(
            f"Mình hiểu là: {intent.summary}\n"
            f"Đúng không? (Yes/No)"
        )
        return
    
    # Confirm
    if intent.action == "executed":
        await update_signal_log(signal_id, {
            "julius_action": "executed",
            "julius_action_time": now(),
            "actual_price": intent.price,
            "actual_size": intent.size,
            "leverage": intent.leverage
        })
        await update_state(intent)
        await bot.send_message(f"✅ Logged: {intent.summary}")
    
    elif intent.action == "skipped":
        await update_signal_log(signal_id, {
            "julius_action": "skipped",
            "julius_action_time": now(),
            "skip_reason": intent.reason
        })
```

### Supported Actions

| Intent | Examples |
|---|---|
| **Executed** | "Đã mua...", "Vào lệnh...", "Buy at...", "Long BTC..." |
| **Skipped** | "Skip", "Bỏ qua", "Không trade" |
| **Watching** | "Đang theo dõi", "Wait", "Chờ thêm signal" |
| **Closed** | "Chốt lời...", "Cắt lỗ...", "Close position", "Exit at..." |
| **Modified** | "Move SL to...", "Update TP..." |

---

## So sánh Performance: Paper vs Live

### Mục đích

Đánh giá quality của agent system bằng cách:
- Paper trading đại diện cho **strategy quality**
- Live trading đại diện cho **Julius execution + quality combined**

### Monthly Comparison Report

```
📊 Monthly Performance — June 2026

Paper Portfolio (Agent Auto):
  Initial: $10,000
  Final: $11,420
  Return: +14.2%
  Trades: 28 (18 win, 10 loss)
  Win rate: 64%
  Sharpe: 1.85
  Max DD: 12%

Julius Live Portfolio:
  Return: +8.7%
  Trades: 15 (Julius selected từ signals)
  Followed signals: 15/28 (54%)
  Skipped signals: 13

Analysis:
✅ Paper outperformed Live by 5.5%
  → Agent đề xuất tốt nhưng Julius skip nhiều winners

⚠️ Top missed opportunities (Julius skipped, paper executed, won):
  1. SOL long +12% (Julius: "Quá rủi ro")
  2. ETH short +8% (Julius: "Không tin TA")
  3. DOGE long +25% (Julius: "Memecoin sợ")

💡 Recommendation: Tin tưởng signals confidence >0.8 hơn
```

### Insights cho System Improvement

```
Patterns:
  ✅ Signals confidence >0.8: Win rate 78% (paper), 73% (Julius)
  ⚠️ Signals confidence 0.6-0.8: Win rate 62% (paper), 55% (Julius)
  ❌ Signals confidence <0.6: Win rate 48% (paper) → Maybe skip threshold

Actions:
  → Tăng skip threshold lên 0.55
  → Add more weight to derivatives data (đúng nhiều nhất)
  → Reduce technical weight cho memecoin (volatile, indicators không reliable)
```

---

## Risk Mitigation

### Paper Trading Risks

| Risk | Mitigation |
|---|---|
| **Bug auto-execute sai** | Extensive testing, idempotency checks, manual override |
| **Portfolio state corrupt** | Snapshots mỗi 4h, rollback mechanism |
| **Slippage estimate sai** | Sử dụng real-time order book, conservative estimates |
| **Leverage liquidation** | Isolated margin, max x10, monitor margin level |

### Edge Cases

```python
# Idempotency check
def execute_paper_trade(signal):
    # Check duplicate
    recent = get_recent_paper_trades(coin=signal.coin, minutes=5)
    if recent:
        for trade in recent:
            if trade.side == signal.side:
                logger.warning(f"Duplicate trade detected, skipping")
                return None
    
    # Check available balance
    if portfolio.available < signal.position_value:
        logger.error(f"Insufficient balance")
        notify_julius("⚠️ Paper portfolio low balance")
        return None
    
    # Check max positions
    if len(portfolio.open_positions) >= 5:
        logger.warning(f"Max positions reached, skipping")
        return None
    
    # Execute
    return execute(signal)
```

---

## Next

- [04. Error Handling](04-error-handling.md) — Fallback chains, retry logic
