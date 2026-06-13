# 10. Monitoring & Dashboard — Telegram

## Tổng quan

Dashboard hoàn toàn qua **Telegram bot** — không cần web interface.

**Hai loại monitoring:**
- **On-demand:** Julius hỏi bất cứ lúc nào
- **Periodic summaries:** Daily (23h), Weekly (Chủ nhật 23h)

---

## On-Demand Commands

Julius gửi tin nhắn tự nhiên, bot parse intent:

| Yêu cầu Julius | Bot Response |
|---|---|
| "Status" / "Hệ thống thế nào?" | System health summary |
| "P&L" / "Lời lỗ?" | Paper P&L + Julius P&L (nếu có) |
| "Positions" / "Đang hold gì?" | Open positions với current P&L |
| "Cost" / "Tốn bao nhiêu?" | LLM cost today/week/month |
| "Signals hôm nay" | Tổng hợp signals đã gửi |
| "Win rate" | Rolling 7d + 30d win rate |

### Example Responses

**Status:**
```
✅ System Status — OK

Last runs:
  Full: 07:00 (4 coins analyzed)
  Quick: 15:00 (watchlist scan)
  Lite: 15:00 (price monitoring)

Heartbeat: 5 minutes ago
Errors today: 0
API health: All sources OK
```

**P&L:**
```
📊 Performance Summary

Paper Portfolio:
  Balance: $10,245 (+$245 / +2.5%)
  Open: 2 positions
    - BTC long: +2.1% (+$63)
    - SOL short: -0.8% (-$18)
  Realized P&L (7d): +$180 (+1.8%)

Julius Portfolio:
  (Manual tracking via your logs)
  Trades this week: 3
  Last logged: BTC buy at $68,100
```

**Positions:**
```
📈 Open Positions (2)

1. BTC Long (Spot)
   Entry: $68,000
   Current: $69,428 (+2.1%)
   Size: 0.044 BTC ($3,055 value)
   P&L: +$63
   SL: $65,000 | TP: $72,000
   Age: 8h 30m

2. SOL Short (Futures x5)
   Entry: $142.50
   Current: $143.64 (-0.8%)
   Size: 21 SOL (margin: $602)
   P&L: -$18
   SL: $148.00 | TP: $135.00
   Age: 2h 15m

Total exposure: 36% portfolio
Available: $6,420 (64%)
```

**Cost:**
```
💰 Cost Tracking

Today: $2.80
  OpenCode Go: $2.10 (18 calls)
  Ollama: $0.70 (5 calls)

This week: $18.50
This month: $38.20

Budget:
  Monthly limit: $60
  Remaining: $21.80 (36%)
  Projected: ~$52 (on track)
```

**Signals:**
```
🔔 Signals Today (3)

1. BTC BUY (07:00) — Conf: 0.82
   Entry: $68,000 | SL: $65,000 | TP: $72,000
   Paper: Executed ✅
   Julius: Executed at $68,100 ✅

2. ETH HOLD (11:00) — Conf: 0.55
   Paper: Skipped (low confidence)
   Julius: Skipped

3. SOL SHORT (15:00) — Conf: 0.71
   Entry: $142.50 | SL: $148 | TP: $135
   Paper: Executed ✅
   Julius: Pending
```

**Win Rate:**
```
📊 Win Rate

Last 7 days:
  Trades: 8 (5 win, 3 loss)
  Win rate: 62.5%
  Avg win: +4.2%
  Avg loss: -2.8%

Last 30 days:
  Trades: 28 (18 win, 10 loss)
  Win rate: 64.3%
  Avg win: +4.8%
  Avg loss: -3.1%
  Best trade: SOL +12.5%
  Worst trade: DOGE -5.2%
```

---

## Daily Summary (23h)

```
📊 Daily Summary — 2026-06-02

System Health: OK (0 errors)
Runs: Full ×1, Quick ×4, Lite ×15, Flash ×1

Paper Portfolio:
  Balance: $10,245 (+$85 today / +0.8%)
  Open: BTC long +2.1%, SOL short -0.8%
  Trades today: 2 (1 win, 1 open)

Signals: 3
  ✅ BTC BUY (conf 0.82) — Julius: executed
  ⏭ ETH HOLD (conf 0.55) — Julius: skipped
  ⏳ SOL SHORT (conf 0.71) — Julius: pending

Win rate: 62% (7d) | 64% (30d)
Cost today: $2.80
Monthly budget: $38/$60 (63%)
```

---

## Weekly Summary (Chủ nhật 23h)

```
📈 Weekly Summary — Week 22/2026

Paper Portfolio:
  Start: $10,160
  End: $10,580
  Return: +$420 (+4.1%)

Julius Portfolio:
  Trades: 5 (3 win, 2 loss)
  Estimated return: ~+3.2%

Best trade: SOL long +8.5%
Worst trade: ETH short -3.2%

Signals: 21 total
  Paper executed: 15 (10 win, 5 loss)
  Julius executed: 12
  Skipped: 6

Win rate: 66.7% (paper) | 58.3% (Julius)

Top analyst accuracy:
  Technical: 74%
  Derivatives: 68%
  News: 61%
  Fundamentals: 58%
  Sentiment: 52%

System uptime: 99.8%
Errors: 1 (Binance timeout, auto-recovered)
Total cost: $18.50
```

---

## Alert Levels

| Level | Format | Khi nào | Example |
|---|---|---|---|
| **🔴 CRITICAL** | Immediate | System down, auth fail, không recover | "System heartbeat dead" |
| **🟠 ERROR** | Immediate | 1 coin skip, agent fail sau retry | "BTC analysis failed: all LLM exhausted" |
| **🟡 WARNING** | Batch (daily summary) | Degraded, fallback model | "Using fallback model (3 times today)" |
| **🟢 INFO** | Không send | Normal operations | Chỉ log vào system.log |

---

## Real-time Alerts

### Price Alerts (Lite Mode Triggers)

```
⚠️ Price Alert — BTC

Price: $68,000 → $75,200 (+10.6% in 1h)

Flash Quick analysis triggered...
(News Analyst checking for catalysts)
```

### Position Alerts

```
🎯 Take Profit Hit — BTC

Position: BTC long (spot)
Entry: $68,000
Exit: $72,000 (+5.9%)
P&L: +$263 (paper)

Realized P&L: +2.6% portfolio
```

```
🛑 Stop Loss Hit — SOL

Position: SOL short (futures x5)
Entry: $142.50
Exit: $148.00 (-3.9% before leverage)
P&L: -$115 (paper)

Realized loss: -1.1% portfolio
```

### System Alerts

```
🔴 CRITICAL: Heartbeat Dead

Last update: 18 minutes ago
Attempting auto-restart...
```

```
🟠 ERROR: BTC Analysis Skipped

Reason: All LLM providers exhausted
  - OpenCode Go: timeout (3/3)
  - Ollama: 503 error (3/3)

Manual review may be needed.
```

---

## Monitoring Metrics

### System Health

```python
def check_system_health():
    health = {
        "heartbeat": check_heartbeat_age() < 900,  # <15 min
        "disk_usage": psutil.disk_usage('/').percent < 80,
        "memory_usage": psutil.virtual_memory().percent < 80,
        "api_status": check_all_apis_status(),
        "llm_status": check_llm_providers(),
        "errors_24h": count_errors_24h()
    }
    
    if all(health.values()):
        return "OK", health
    elif health["heartbeat"] and health["api_status"]:
        return "DEGRADED", health
    else:
        return "CRITICAL", health
```

### Trading Performance

```python
def calculate_performance_summary(period="7d"):
    positions = get_closed_positions(period)
    
    return {
        "total_trades": len(positions),
        "winning_trades": sum(1 for p in positions if p["realized_pnl"] > 0),
        "losing_trades": sum(1 for p in positions if p["realized_pnl"] <= 0),
        "win_rate": calculate_win_rate(positions),
        "avg_win_pct": calculate_avg_win(positions),
        "avg_loss_pct": calculate_avg_loss(positions),
        "best_trade": max(positions, key=lambda p: p["realized_pnl_pct"]),
        "worst_trade": min(positions, key=lambda p: p["realized_pnl_pct"]),
        "total_pnl": sum(p["realized_pnl"] for p in positions),
        "total_pnl_pct": sum(p["realized_pnl"] for p in positions) / 10000  # Assuming $10k base
    }
```

### Cost Tracking

```python
def track_llm_costs():
    """Parse api_calls.log để tính cost"""
    costs = {"opencode_go": 0, "ollama": 0}
    
    with open("logs/api_calls.log") as f:
        for line in f:
            entry = json.loads(line)
            if "cost" in entry:
                provider = entry["api"]
                costs[provider] += entry["cost"]
    
    return costs

def project_monthly_cost(current_day, current_cost):
    """Estimate cost cuối tháng"""
    days_in_month = 30
    daily_avg = current_cost / current_day
    projected = daily_avg * days_in_month
    return projected
```

---

## Custom Queries

Julius có thể hỏi bất cứ thứ gì, bot parse với LLM:

```
Julius: "Coin nào win rate cao nhất tháng này?"

Bot: 
📊 Top Performers (June 2026)

By win rate:
1. SOL: 80% (4/5 trades)
2. BTC: 70% (7/10 trades)
3. ETH: 60% (6/10 trades)
4. ARB: 50% (2/4 trades)
5. DOGE: 33% (1/3 trades)

By P&L:
1. SOL: +$185
2. BTC: +$142
3. ETH: +$78
4. ARB: -$22
5. DOGE: -$45
```

```
Julius: "Hôm nào có nhiều signal nhất?"

Bot:
📅 Signal Frequency

Top 5 days:
1. 2026-06-15: 8 signals (volatile day)
2. 2026-06-22: 7 signals
3. 2026-06-08: 6 signals
4. 2026-06-12: 6 signals
5. 2026-06-01: 5 signals

Average: 3.2 signals/day
```

---

## Bot Implementation

```python
@bot.message_handler(func=lambda m: True)
async def handle_message(message):
    # Parse intent
    intent = await parse_query(
        message.text,
        model="deepseek-v4-flash",
        context={"user": "julius", "role": "trading_query"}
    )
    
    # Route to handler
    if intent["type"] == "status":
        response = generate_status_summary()
    elif intent["type"] == "pnl":
        response = generate_pnl_summary(intent.get("period", "all"))
    elif intent["type"] == "positions":
        response = generate_positions_summary()
    elif intent["type"] == "cost":
        response = generate_cost_summary()
    elif intent["type"] == "custom":
        response = handle_custom_query(intent["query"])
    else:
        response = "Mình chưa hiểu câu hỏi này. Bạn có thể hỏi:\n- Status\n- P&L\n- Positions\n- Cost\n- Win rate"
    
    await bot.reply_to(message, response)
```

---

## Next

- [11. Parameter Tuning](11-parameter-tuning.md) — Per-coin adaptive tuning
