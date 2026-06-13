# Phase 1.6 - Telegram Bot Commands

## ✅ Status: COMPLETE & OPERATIONAL

Telegram bot đã hoàn thành và tích hợp với hệ thống trading.

---

## 📱 Available Commands

### Basic Commands
- `/start` - Welcome message
- `/help` - Show all available commands

### Status Commands
- `/status` - Portfolio overview (balance, positions, PnL)
- `/positions` - Show all open positions with details
- `/trades` - Show last 10 closed trades
- `/pnl` - Detailed PnL breakdown

### Trading Commands
- `/close <trade_id>` - Close a specific position manually
- `/pause` - Pause trading (stop opening new positions)
- `/resume` - Resume trading

### Config Commands
- `/config` - Show current configuration

---

## 🎯 Features

### 1. Real-time Portfolio Monitoring
- View current balance (spot + futures)
- See open positions with entry price, SL, TP
- Track PnL in real-time
- Monitor system status (running/paused)

### 2. Trade Management
- View trade history (last 10 trades)
- Close positions manually via trade ID
- See detailed PnL per trade

### 3. System Control
- Pause trading without stopping the system
- Resume trading when ready
- Existing positions still monitored when paused

### 4. Configuration View
- View current trading parameters
- See risk management settings
- Check stop loss / take profit config

---

## 🚀 Usage Examples

### Check Portfolio Status
```
/status
```
Output:
```
📊 Portfolio Status

Balance:
  • Spot: $5,000.00
  • Futures: $5,007.87
  • Total: $10,007.87

Positions:
  • Open: 1
  • Total Trades: 0

Performance:
  🟢 Total PnL: $+7.87 (+0.08%)
  • Avg PnL/Trade: +0.00%

System:
  • Status: 🟢 Running
```

### View Open Positions
```
/positions
```
Output:
```
📈 Open Positions (1)

🔴 ETHUSDT ⚡
  • Side: SHORT
  • Entry: $1,765.78
  • Qty: 0.849000
  • Leverage: 10.0x
  • SL: $1,801.10
  • TP: $1,695.15
  • Trade ID: ETHUSDT_SHORT_1780576066163
```

### Close a Position
```
/close ETHUSDT_SHORT_1780576066163
```
Output:
```
✅ Position closed successfully
Trade ID: ETHUSDT_SHORT_1780576066163
```

### Pause Trading
```
/pause
```
Output:
```
🔴 Trading Paused

The system will stop opening new positions.
Existing positions will still be monitored.

Use /resume to continue trading.
```

### Resume Trading
```
/resume
```
Output:
```
🟢 Trading Resumed

The system will continue normal operations.
```

---

## 📋 Implementation Details

### Files Created
```
telegram_bot/
├── __init__.py
└── bot.py              # Main bot implementation
```

### Files Modified
```
scripts/run_paper_trading.py    # Integrated Telegram bot
```

### Bot Architecture
- **Framework**: python-telegram-bot v22.7
- **Pattern**: Async/await with polling
- **Integration**: Runs alongside trading loop
- **State**: Shared with OrderManager and PositionMonitor

### Command Handlers
1. `/start` - Welcome message
2. `/help` - Command list
3. `/status` - Portfolio stats from OrderManager
4. `/positions` - Open positions from database
5. `/trades` - Trade history from database
6. `/pnl` - PnL breakdown from stats
7. `/close` - Close position via OrderManager
8. `/pause` - Set is_paused flag
9. `/resume` - Clear is_paused flag
10. `/config` - Load from config system

### Pause/Resume Logic
- When paused: Trading loop still runs but skips analysis
- Position monitoring continues (SL/TP still active)
- Portfolio snapshots still saved
- Only new trade execution is skipped

---

## 🔧 Configuration

### Environment Variables
```env
TELEGRAM_BOT_TOKEN=8813276012:AAFDygfqcMvurKlxGYzFV9asxKcsSTgRBfA
TELEGRAM_CHAT_ID=1370258715
```

### Bot Settings
- **Polling**: Long polling (efficient)
- **Parse Mode**: HTML (for formatting)
- **Error Handling**: Try-catch with user feedback
- **Logging**: Integrated with system logger

---

## 📊 Test Results

### Startup Test
```
✓ Telegram bot started
✓ Test message sent
✓ Trading system initialized
✓ First cycle completed
```

### Command Tests
- `/status` - ✓ Working
- `/positions` - ✓ Working
- `/trades` - ✓ Working
- `/pnl` - ✓ Working
- `/pause` - ✓ Working
- `/resume` - ✓ Working
- `/config` - ✓ Working

### Integration Test
- Bot starts with trading system - ✓
- Commands work while trading - ✓
- Pause stops new trades - ✓
- Resume continues trading - ✓
- Positions monitored when paused - ✓

---

## 🎓 Next Steps

Phase 1.6 is complete. The system now has:
- ✅ Paper trading (Phase 1.5)
- ✅ Telegram bot control (Phase 1.6)

**Next: Phase 1.7 - Lite + Full Mode**
- Lite mode: Price monitoring every minute
- Full mode: Technical Analyst (already implemented)
- Cron scheduling: 07:00 Full, hourly Lite
- Daily report generation

---

## 📞 Support

### Common Issues

**Bot not responding:**
- Check if process is running: `ps aux | grep run_paper_trading`
- Check logs: `tail -f logs/paper_trading.log`
- Verify bot token and chat ID in .env

**Commands not working:**
- Ensure bot is started (check logs for "Telegram bot started")
- Check if chat ID is correct
- Verify bot has permission to send messages

**Can't close position:**
- Verify trade ID is correct (use /positions to see IDs)
- Check if position is still open
- Check logs for error messages

---

**System Status**: ✅ OPERATIONAL  
**Last Updated**: 2026-06-05  
**Version**: 1.6.0
