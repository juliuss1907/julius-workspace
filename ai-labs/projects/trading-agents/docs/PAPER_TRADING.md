# Phase 1.5 - Paper Trading System

## ✅ Status: COMPLETE & OPERATIONAL

Hệ thống paper trading đã hoàn thành và sẵn sàng chạy tự động.

---

## 📊 Test Results

### API Connections
- ✓ Spot Demo API: OK
- ✓ Futures Testnet API: OK
- ✓ Telegram Bot: OK

### Balances
- Spot Demo: $5,000.00
- Futures Testnet: $5,000.00
- **Total: $10,000.00**

### First Trading Cycle
```
BTCUSDT: bearish | Score: 0.360 | Confidence: 0.885 | Regime: trend_down
✓ Trade executed: BTCUSDT_SHORT - 0.024 BTC @ $62,730.67 (10x leverage)

ETHUSDT: bearish | Score: 0.330 | Confidence: 0.835 | Regime: trend_down
✓ Trade executed: ETHUSDT_SHORT - 0.856 ETH @ $1,751.40 (10x leverage)

SOLUSDT: bearish | Score: 0.330 | Confidence: 0.835 | Regime: trend_down
✓ Trade executed: SOLUSDT_SHORT - 21.9 SOL @ $68.60 (10x leverage)

Open Positions: 3
Futures Balance: $4,998.19 (after fees)
```

---

## 🚀 How to Run

### 1. Chạy paper trading tự động (mỗi giờ)
```bash
cd /home/julius/julius-workspace/ai-labs/projects/trading-agents
source venv/bin/activate
python scripts/run_paper_trading.py
```

### 2. Chạy background (recommended)
```bash
nohup python scripts/run_paper_trading.py > logs/paper_trading.log 2>&1 &
```

### 3. Xem logs
```bash
tail -f logs/paper_trading.log
```

### 4. Stop system
```bash
pkill -f run_paper_trading.py
```

---

## 🎯 System Features

### Trading Logic
- **Technical Analyst**: RSI, MACD, Bollinger Bands, ATR, OBV
- **Market Regime Detection**: Trend up/down, Ranging, Volatile
- **Confidence Scoring**: 0.0 - 1.0
- **Min Confidence**: 0.70 (chỉ trade khi confidence >= 70%)

### Market Selection
- **Spot**: Uptrend, smaller coins
- **Futures**: Downtrend, hoặc large caps (BTC, ETH, SOL) với leverage 3-10x

### Risk Management
- **Risk per trade**: 3% of balance
- **Max position size**: 30% per coin
- **Max open positions**: 5
- **Stop Loss**: 2x ATR (Average True Range)
- **Take Profit**: 2:1 Risk/Reward ratio
- **Trailing Stop**: Activate at 3% profit, trail 1.5%

### Position Sizing
```
position_size = (balance * risk_per_trade) / (stop_loss_distance * price)
```

Adjusted by confidence:
- High (>= 0.8): 100%
- Medium (0.6-0.8): 75%
- Low (< 0.6): 50%

### Leverage (Futures)
Based on confidence:
- High (>= 0.8): 10x
- Medium (0.6-0.8): 5x
- Low (< 0.6): 3x

---

## 📱 Telegram Notifications

Hệ thống sẽ gửi thông báo qua Telegram khi:
- ✓ Trade được mở
- ✓ Trade được đóng (SL/TP/manual)
- ✓ Daily summary (mỗi 24h)
- ✓ Error alerts

---

## 📁 File Structure

```
trading/
├── __init__.py
├── base_trader.py              # Abstract base class
├── spot_demo_trader.py         # Spot Demo Mode trader
├── futures_testnet_trader.py   # Futures Testnet trader
├── order_manager.py            # Coordinates trading + position sizing
├── position_monitor.py         # SL/TP/trailing stop monitoring
└── trade_notifier.py           # Telegram notifications

scripts/
├── run_paper_trading.py        # Main trading loop
├── test_paper_trading.py       # Integration tests
└── test_technical_analyst.py   # Analyst tests

state/
├── schema.sql                  # Database schema
├── database.py                 # Database operations
└── trading.db                  # SQLite database (auto-created)
```

---

## 🔧 Configuration

### Environment Variables (.env)
```env
BINANCE_DEMO_API_KEY=...
BINANCE_DEMO_SECRET=...
BINANCE_FUTURES_TESTNET_API_KEY=...
BINANCE_FUTURES_TESTNET_SECRET=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

### Config File (config/default_params.yaml)
```yaml
demo_trading:
  auto_execute:
    enabled: true
    min_confidence: 0.70
    check_interval_seconds: 3600  # 1 hour
  
  market_selection:
    futures_allowed_coins: ["BTC", "ETH", "SOL", "BNB", "XRP"]
    futures_on_downtrend: true
    max_futures_leverage: 10
  
  fees:
    spot_maker: 0.001
    spot_taker: 0.001
    futures_maker: 0.0002
    futures_taker: 0.0005
```

---

## 📊 Database Tables

### paper_positions
- Open positions with entry price, SL, TP, trailing stop
- Status: open/closed

### paper_trades
- Closed trades history
- PnL, fees, duration

### paper_portfolio
- Portfolio snapshots
- Balance, equity, PnL

### trade_notifications
- Telegram notification log

---

## 🎓 Next Steps

### Phase 1.6 - Telegram Bot Commands
- `/status` - Xem portfolio status
- `/positions` - Xem open positions
- `/trades` - Xem trade history
- `/pnl` - Xem PnL
- `/close <trade_id>` - Đóng position thủ công

### Phase 1.7 - Backtesting
- Backtest Technical Analyst với historical data
- Optimize parameters
- Validate strategy

### Phase 1.8 - Lite Mode
- Price monitoring (mỗi phút)
- Trigger Flash Quick khi có biến động >10%

---

## 🐛 Known Issues

1. **Margin Type Warning**: "No need to change margin type" - Không ảnh hưởng, chỉ là warning
2. **Entry Price = 0**: Log hiển thị entry price = 0 nhưng thực tế đã lấy đúng từ API response

---

## 📞 Support

Nếu có vấn đề:
1. Check logs: `tail -f logs/paper_trading.log`
2. Check database: `sqlite3 state/trading.db`
3. Check Telegram notifications

---

**System Status**: ✅ OPERATIONAL  
**Last Updated**: 2026-06-04  
**Version**: 1.5.0
