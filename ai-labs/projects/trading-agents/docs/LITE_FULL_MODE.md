# Phase 1.7 - Lite + Full Mode

## ✅ Status: COMPLETE & OPERATIONAL

Hệ thống đã hoàn thành với 2 chế độ trading và scheduler tự động.

---

## 🎯 Overview

Phase 1.7 thêm 2 chế độ trading:

1. **Lite Mode**: Price monitoring mỗi phút, trigger Flash Quick khi biến động >10%
2. **Full Mode**: Technical Analyst đầy đủ (đã có từ Phase 1.4)
3. **Scheduler**: Tự động chạy Full mode lúc 07:00, Lite mode liên tục, Daily report lúc 23:00

---

## 📊 Trading Modes

### Lite Mode (Price Monitoring)

**Mục đích:** Giám sát giá liên tục, phát hiện biến động mạnh

**Hoạt động:**
- Check giá mỗi **60 giây**
- Theo dõi price change cho mỗi coin
- Trigger **Flash Quick** khi biến động >10%
- Cooldown 1 giờ giữa các flash cho cùng 1 coin
- Vẫn monitor SL/TP cho open positions

**Flash Quick Trigger:**
- Khi price change > ±10%
- Chạy Technical Analyst nhanh
- Execute trade nếu confidence >= 70%
- Gửi Telegram notification

**Files:**
```
scripts/lite_mode_monitor.py    # 280 lines
```

### Full Mode (Technical Analyst)

**Mục đích:** Phân tích kỹ thuật đầy đủ

**Hoạt động:**
- Chạy lúc **07:00 hàng ngày**
- Fetch OHLCV data (200 candles)
- Fetch fundamentals từ CoinGecko
- Run Technical Analyst
- Execute trades nếu confidence >= 70%
- Monitor SL/TP

**Files:**
```
scripts/run_paper_trading.py    # Updated with --single-cycle flag
```

### Daily Report

**Mục đích:** Tổng kết hoạt động trading trong ngày

**Hoạt động:**
- Chạy lúc **23:00 hàng ngày**
- Generate markdown report
- Gửi Telegram summary
- Lưu report vào `reports/` folder

**Report Content:**
- Portfolio summary (balance, PnL)
- Today's performance (trades, win rate, PnL)
- List of trades executed
- Open positions
- Performance metrics

**Files:**
```
scripts/generate_daily_report.py    # 250 lines
reports/daily_report_YYYY-MM-DD.md
```

---

## ⏰ Scheduler

**File:** `scripts/trading_scheduler.py`

**Schedule:**
```
07:00 - Full Mode (Technical Analyst)
Every minute - Lite Mode (price monitoring)
23:00 - Daily Report
```

**Features:**
- Auto-start Lite Mode khi scheduler chạy
- Auto-restart Lite Mode nếu process chết
- Check schedule mỗi 30 giây
- Run Full Mode tại thời điểm chỉ định
- Generate daily report tại thời điểm chỉ định
- Track last execution để tránh duplicate

**Usage:**
```bash
# Start scheduler (recommended)
python scripts/trading_scheduler.py

# Or run in background
setsid python scripts/trading_scheduler.py > logs/scheduler.log 2>&1 < /dev/null &
```

---

## 📁 Files Created

```
scripts/
├── lite_mode_monitor.py        # Lite mode price monitor
├── trading_scheduler.py        # Cron scheduler
├── generate_daily_report.py    # Daily report generator
└── run_paper_trading.py        # Updated with --single-cycle

config/
└── default_params.yaml         # Added lite_mode, scheduler, watchlist

reports/
└── daily_report_2026-06-05.md  # Sample report

logs/
├── lite_mode.log               # Lite mode logs
├── full_mode.log               # Full mode logs
├── daily_report.log            # Report generation logs
└── scheduler.log               # Scheduler logs
```

---

## ⚙️ Configuration

### Lite Mode Settings

```yaml
lite_mode:
  check_interval_seconds: 60      # Check every minute
  flash_threshold_pct: 10.0       # Trigger at 10% movement
  flash_cooldown_hours: 1         # Wait 1 hour between flashes
```

### Scheduler Settings

```yaml
scheduler:
  full_mode_time: "07:00"         # Daily at 07:00
  lite_mode_enabled: true         # Enable lite mode
  report_time: "23:00"            # Daily report at 23:00
```

### Watchlist

```yaml
watchlist:
  - BTCUSDT
  - ETHUSDT
  - SOLUSDT
```

---

## 🚀 Usage

### Start Complete System

```bash
cd /home/julius/julius-workspace/ai-labs/projects/trading-agents
source venv/bin/activate

# Start scheduler (manages all modes)
setsid python scripts/trading_scheduler.py > logs/scheduler.log 2>&1 < /dev/null &

# Check status
ps aux | grep -E "(trading_scheduler|lite_mode|run_paper)" | grep -v grep
```

### Manual Commands

```bash
# Run Full Mode manually as a dry-run smoke test (safe)
python scripts/run_paper_trading.py --single-cycle --dry-run

# Operational single-cycle run (not a smoke test; may mutate positions/state)
# python scripts/run_paper_trading.py --single-cycle

# Run Lite Mode manually
python scripts/lite_mode_monitor.py

# Generate daily report manually
python scripts/generate_daily_report.py
```

### Stop System

```bash
# Find and kill all trading processes
pkill -f "trading_scheduler\|lite_mode_monitor\|run_paper_trading"
```

---

## 📊 Test Results

### Lite Mode Monitor
```
✓ Initialized successfully
✓ Checking prices every 60s
✓ Monitoring 3 coins (BTC, ETH, SOL)
✓ Flash Quick trigger logic working
✓ Position monitoring active
```

### Full Mode (Single Cycle)
```
✓ --single-cycle flag working
✓ Technical Analyst executed
✓ Trades evaluated
✓ Positions monitored
```

### Daily Report Generator
```
✓ Markdown report generated
✓ Telegram summary sent
✓ Report saved to reports/ folder
✓ All metrics calculated correctly
```

### Trading Scheduler
```
✓ Scheduler started
✓ Lite Mode auto-started
✓ Schedule checking every 30s
✓ Process monitoring active
```

---

## 📈 Sample Daily Report

```markdown
# 📊 Daily Trading Report - 2026-06-05

## 📈 Portfolio Summary

| Metric | Value |
|--------|-------|
| **Spot Balance** | $5,000.00 |
| **Futures Balance** | $5,007.87 |
| **Total Balance** | $10,007.87 |
| **Total PnL** | $+0.00 (+0.00%) |

## 🎯 Today's Performance

| Metric | Value |
|--------|-------|
| **Total Trades** | 0 |
| **Winning Trades** | 0 ✅ |
| **Losing Trades** | 0 ❌ |
| **Win Rate** | 0.0% |
| **Daily PnL** | $+0.00 |

## 📊 Open Positions (3)

| Symbol | Side | Entry | Qty | Leverage | SL | TP |
|--------|------|-------|-----|----------|----|----|
| SOLUSDT | SHORT | $69.17 | 21.7 | 10.0x | $71.77 | $63.97 |
| ETHUSDT | SHORT | $1,765.78 | 0.849 | 10.0x | $1,820.07 | $1,657.21 |
| BTCUSDT | SHORT | $63,199.04 | 0.024 | 10.0x | $64,782.02 | $60,033.09 |
```

---

## 🎓 How It Works

### Lite Mode Flow

```
Every 60 seconds:
  1. Fetch current prices for all coins
  2. Calculate price change from last check
  3. Update price history (keep last 60 entries)
  4. Check if change > ±10%
  5. If yes and cooldown expired:
     - Trigger Flash Quick
     - Run Technical Analyst
     - Execute trade if confidence >= 70%
     - Send Telegram notification
  6. Monitor existing positions (SL/TP)
```

### Full Mode Flow

```
At 07:00 daily:
  1. Fetch OHLCV data (200 candles, 1h)
  2. Fetch fundamentals from CoinGecko
  3. Run Technical Analyst
  4. Evaluate signals
  5. Execute trades if confidence >= 70%
  6. Monitor positions
  7. Send Telegram notifications
  8. Exit after single cycle
```

### Daily Report Flow

```
At 23:00 daily:
  1. Query all trades from today
  2. Query open positions
  3. Calculate statistics:
     - Total trades
     - Win/loss count
     - Win rate
     - Total PnL
     - Avg PnL per trade
     - Best/worst trade
  4. Generate markdown report
  5. Save to reports/ folder
  6. Generate Telegram summary
  7. Send via Telegram
```

---

## 🔧 Troubleshooting

### Lite Mode not triggering Flash Quick

**Check:**
- Price change threshold (default 10%)
- Cooldown period (default 1 hour)
- Logs for errors

**Solution:**
```bash
# Check lite mode logs
tail -f logs/lite_mode.log

# Adjust threshold in config
# config/default_params.yaml -> lite_mode.flash_threshold_pct
```

### Scheduler not starting Full Mode

**Check:**
- Current time vs full_mode_time
- Last execution date
- Scheduler logs

**Solution:**
```bash
# Check scheduler logs
tail -f logs/scheduler.log

# Verify time
date

# Run Full Mode manually as a dry-run smoke test
python scripts/run_paper_trading.py --single-cycle --dry-run
```

### Daily report not generating

**Check:**
- Current time vs report_time
- Last report date
- Report generation logs

**Solution:**
```bash
# Check report logs
tail -f logs/daily_report.log

# Generate manually
python scripts/generate_daily_report.py

# Check reports folder
ls -lh reports/
```

---

## 📞 Support

### Common Issues

**Lite Mode process keeps dying:**
- Check logs for errors
- Verify API keys in .env
- Check network connectivity
- Scheduler will auto-restart

**Full Mode not executing trades:**
- Check confidence threshold (default 70%)
- Verify market conditions
- Check if already have open position for coin
- Review Technical Analyst logs

**Daily report empty:**
- Check if trades were executed today
- Verify database connection
- Check report generation logs

---

## 🎯 Next Steps

Phase 1.7 is complete! The system now has:

✅ **Phase 1.1-1.4**: Core trading system
✅ **Phase 1.5**: Paper trading engine
✅ **Phase 1.6**: Telegram bot control
✅ **Phase 1.7**: Lite + Full mode with scheduler

**Possible next phases:**
- Phase 2: News & Sentiment Analyst
- Phase 3: Derivatives & Researchers
- Phase 4: Risk & Portfolio Management
- Phase 5: Backtesting
- Phase 6: Adaptive Tuning
- Phase 7: Fine-tuning
- Phase 8: Screening Agent

---

**System Status**: ✅ FULLY OPERATIONAL  
**Last Updated**: 2026-06-05  
**Version**: 1.7.0
