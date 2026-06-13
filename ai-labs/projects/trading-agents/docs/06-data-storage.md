# 06. Data Storage — Historical Data & Logs

## Tổng quan

Hệ thống lưu trữ nhiều loại data với retention policies khác nhau:

```
trading-agents/
├── data/                       # Historical data
│   ├── ohlcv/                  # 3 tháng rolling
│   ├── derivatives/            # 90 ngày rolling
│   └── cache/                  # Auto-expire theo TTL
├── state/                      # Current state (covered in 05)
├── reports/                    # Analysis reports
│   ├── daily/                  # Giữ mãi (~3.5MB/năm)
│   ├── quick/                  # Giữ mãi (~5MB/năm)
│   └── flash/                  # Giữ mãi (~0.3MB/năm)
├── logs/                       # System logs
│   ├── signals.log             # Giữ mãi
│   ├── paper_trades.log        # Giữ mãi
│   ├── errors.log              # 90 ngày
│   ├── system.log              # 30 ngày
│   └── api_calls.log           # 90 ngày
├── backtests/                  # Backtest results
└── backups/                    # Gitignored, local staging
```

---

## 1. Historical OHLCV Data

### Storage: CSV files

**Watchlist:** 5-7 coins

**Timeframes:** 30m, 1h, 2h, 4h, 1d

**Retention:** 3 tháng rolling

**Ước tính:** ~50MB total (5-7 coins × 5 timeframes × 3 tháng)

### Structure

```
data/ohlcv/
├── BTC_30m.csv
├── BTC_1h.csv
├── BTC_2h.csv
├── BTC_4h.csv
├── BTC_1d.csv
├── ETH_30m.csv
└── ...
```

### CSV Format

```csv
timestamp,open,high,low,close,volume
1717308000,68000,68500,67800,68200,1250.5
1717311600,68200,68800,68100,68600,1380.2
...
```

### Fetching & Updating

```python
def update_ohlcv_csv(coin, timeframe):
    """Fetch mới nhất, append vào CSV"""
    csv_file = f"data/ohlcv/{coin}_{timeframe}.csv"
    
    # Get last timestamp from CSV
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        last_ts = df['timestamp'].max()
    else:
        last_ts = datetime.now() - timedelta(days=90)  # 3 tháng
    
    # Fetch new data
    new_data = fetch_binance_ohlcv(coin, timeframe, since=last_ts)
    
    # Append to CSV
    new_df = pd.DataFrame(new_data)
    if os.path.exists(csv_file):
        new_df.to_csv(csv_file, mode='a', header=False, index=False)
    else:
        new_df.to_csv(csv_file, index=False)
    
    # Cleanup old data (>3 tháng)
    df = pd.read_csv(csv_file)
    cutoff = datetime.now().timestamp() - (90 * 86400)
    df = df[df['timestamp'] > cutoff]
    df.to_csv(csv_file, index=False)
```

### Cleanup Schedule

Chạy hàng ngày lúc 03:00:

```python
def cleanup_old_ohlcv():
    """Xóa data >3 tháng"""
    cutoff = datetime.now() - timedelta(days=90)
    
    for csv_file in glob.glob("data/ohlcv/*.csv"):
        df = pd.read_csv(csv_file)
        original_count = len(df)
        
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        df = df[df['datetime'] > cutoff]
        
        removed = original_count - len(df)
        if removed > 0:
            df.to_csv(csv_file, index=False)
            logger.info(f"Removed {removed} old candles from {csv_file}")
```

---

## 2. Derivatives Data

### Storage: SQLite

**Retention:** 90 ngày rolling

**Data:** Funding rates, Open Interest, Liquidations từ Hyperliquid, Binance Futures, Lighter

### Schema

```sql
CREATE TABLE funding_rates (
    id INTEGER PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    coin TEXT NOT NULL,
    source TEXT NOT NULL,  -- 'hyperliquid', 'binance', 'lighter'
    rate REAL NOT NULL,
    next_funding_time TIMESTAMP
);

CREATE TABLE open_interest (
    id INTEGER PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    coin TEXT NOT NULL,
    source TEXT NOT NULL,
    oi_usd REAL NOT NULL,
    oi_change_24h REAL
);

CREATE TABLE liquidations (
    id INTEGER PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    coin TEXT NOT NULL,
    source TEXT NOT NULL,
    side TEXT NOT NULL,  -- 'long' or 'short'
    price REAL NOT NULL,
    amount_usd REAL NOT NULL
);

-- Indexes for fast queries
CREATE INDEX idx_funding_coin_time ON funding_rates(coin, timestamp);
CREATE INDEX idx_oi_coin_time ON open_interest(coin, timestamp);
CREATE INDEX idx_liq_coin_time ON liquidations(coin, timestamp);
```

### Cleanup

```python
def cleanup_old_derivatives():
    """Xóa data >90 ngày"""
    cutoff = datetime.now() - timedelta(days=90)
    
    conn = sqlite3.connect("data/derivatives/derivatives.db")
    
    for table in ['funding_rates', 'open_interest', 'liquidations']:
        result = conn.execute(f"""
            DELETE FROM {table}
            WHERE timestamp < ?
        """, (cutoff.isoformat(),))
        
        logger.info(f"Deleted {result.rowcount} old rows from {table}")
    
    conn.commit()
    conn.execute("VACUUM")  # Reclaim space
```

Chạy hàng ngày lúc 03:00.

---

## 3. Cache (Temporary)

### Storage: JSON files trong `data/cache/`

**TTL:** Auto-expire (xem [05. State Management](05-state-management.md))

**Cleanup:** Hàng ngày lúc 04:00

```python
def cleanup_expired_cache():
    """Xóa cache files đã expired"""
    cache_dir = "data/cache"
    
    for cache_file in glob.glob(f"{cache_dir}/*.json"):
        try:
            with open(cache_file) as f:
                data = json.load(f)
            
            expires_at = datetime.fromisoformat(data["expires_at"])
            if datetime.now() > expires_at:
                os.remove(cache_file)
                logger.info(f"Removed expired cache: {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to check cache {cache_file}: {e}")
```

---

## 4. Reports (Markdown)

### Daily Reports

**Path:** `reports/daily/YYYY-MM-DD-full.md`

**Retention:** Giữ mãi

**Ước tính:** ~5-10KB/file × 365 ngày = **~3.5MB/năm**

**Format:**

```markdown
# Full Analysis Report — BTC — 2026-06-02

## Summary
Signal: BUY
Confidence: 0.78 (Moderate)
Entry: $68,000
Stop Loss: $65,000 (-4.4%)
Take Profit: $72,000 (+5.9%)

## Technical Analysis
- RSI: 45 (neutral)
- MACD: Bullish cross on 4h
- Bollinger Bands: Price near lower band
- OBV: Increasing
- Chart pattern: Inverse H&S forming

## Fundamentals
- Market cap: $1.2T
- FDV: $1.35T
- Inflation rate: 1.8% annual
- Protocol revenue: N/A (Bitcoin)

## News & Sentiment
- ETF inflow: $250M past week
- Fear & Greed Index: 52 (Neutral)
- X/Twitter sentiment: Bullish (70% positive mentions)
- Polymarket "BTC $70k by month-end": 52% odds

## Derivatives
- Funding rate: -0.01% (neutral)
- Open Interest: $12.5B (+5% 24h)
- Liquidation levels: $70k resistance, $65k support

## Researcher Debate
**Bull:** Strong technical breakout + ETF momentum
**Bear:** Resistance at $70k may reject, funding neutral

## Risk Assessment
- Volatility: Moderate (ATR: $2,500)
- Liquidity: Excellent (spread: 0.01%)
- Market regime: Trend up

## Recommendation
BUY with 6.7% portfolio allocation
R:R ratio: 1:1.34
```

---

### Quick Reports

**Path:** `reports/quick/YYYY-MM-DD-HH-quick.md`

**Retention:** Giữ mãi

**Ước tính:** ~2-5KB × 4/ngày × 365 = **~5MB/năm**

---

### Flash Reports

**Path:** `reports/flash/YYYY-MM-DD-HHmm-{COIN}-flash.md`

**Retention:** Giữ mãi

**Ước tính:** ~1-2KB × 2-3/tuần × 52 = **~0.3MB/năm**

---

**Total reports:** ~9MB/năm → Giữ mãi hoàn toàn không vấn đề.

---

## 5. Logs

### signals.log (JSON Lines)

**Retention:** Giữ mãi (cần cho monthly review)

**Format:**

```jsonl
{"timestamp": "2026-06-02T07:00:15+07:00", "mode": "full", "coin": "BTC", "signal": "BUY", "entry": 68000, "sl": 65000, "tp": 72000, "confidence": 0.78, "summary": "BTC broke resistance...", "paper_executed": true, "paper_position_id": "pos_001", "julius_action": "executed", "julius_actual_price": 68100}
{"timestamp": "2026-06-02T11:00:22+07:00", "mode": "quick", "coin": "ETH", "signal": "HOLD", "confidence": 0.55, "summary": "ETH ranging...", "paper_executed": false, "julius_action": "skipped"}
```

**Usage:** Monthly review script phân tích file này.

---

### paper_trades.log (JSON Lines)

**Retention:** Giữ mãi

**Format:**

```jsonl
{"timestamp": "2026-06-02T07:00:30+07:00", "position_id": "pos_001", "action": "open", "coin": "BTC", "type": "spot", "side": "long", "entry_price": 68050, "size": 0.0667, "fees": 4.54, "slippage": 0.07}
{"timestamp": "2026-06-02T10:30:15+07:00", "position_id": "pos_001", "action": "close", "exit_price": 72000, "realized_pnl": 263.33, "realized_pnl_pct": 5.8, "hold_duration_hours": 3.5, "exit_reason": "tp_hit"}
```

---

### errors.log (JSON Lines)

**Retention:** 90 ngày

**Format:** (xem [04. Error Handling](04-error-handling.md))

**Cleanup:**

```python
def cleanup_errors_log():
    cutoff = datetime.now() - timedelta(days=90)
    
    with open("logs/errors.log") as f:
        lines = f.readlines()
    
    kept_lines = []
    for line in lines:
        try:
            entry = json.loads(line)
            ts = datetime.fromisoformat(entry["timestamp"])
            if ts > cutoff:
                kept_lines.append(line)
        except:
            continue
    
    with open("logs/errors.log", "w") as f:
        f.writelines(kept_lines)
```

---

### system.log

**Retention:** 30 ngày

**Format:** Standard Python logging

```
2026-06-02 07:00:00,123 INFO Starting full mode for BTC
2026-06-02 07:00:15,456 INFO Technical analyst completed (0.78 score)
2026-06-02 07:00:30,789 INFO Paper trade executed: pos_001
```

**Rotation:** Dùng `RotatingFileHandler`, max 100MB per file, giữ 3 backup files.

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    "logs/system.log",
    maxBytes=100*1024*1024,  # 100MB
    backupCount=3
)
logger.addHandler(handler)
```

---

### api_calls.log (JSON Lines)

**Retention:** 90 ngày

**Format:**

```jsonl
{"timestamp": "2026-06-02T07:00:05+07:00", "api": "binance", "endpoint": "/api/v3/klines", "coin": "BTC", "response_time_ms": 123, "success": true}
{"timestamp": "2026-06-02T07:00:10+07:00", "api": "opencode_go", "model": "qwen3.7-max", "prompt_tokens": 1200, "completion_tokens": 350, "cost": 0.045, "success": true}
```

**Usage:** Cost monitoring, rate limit tracking.

---

## 6. Backtests

**Path:** `backtests/YYYY-MM-DD-{strategy}.json`

**Retention:** Giữ mãi

**Format:**

```json
{
  "backtest_id": "bt_2026-07-01_rule-based_6m",
  "strategy": "rule-based-v1",
  "period": "2025-12-01 to 2026-06-01",
  "coins": ["BTC", "ETH", "SOL"],
  "initial_balance": 10000,
  "final_balance": 12800,
  "total_return": 0.28,
  "win_rate": 0.621,
  "sharpe_ratio": 1.72,
  "max_drawdown": 0.16,
  "baseline_btc_return": 0.22,
  "baseline_watchlist_return": 0.19,
  "alpha_vs_btc": 0.06,
  "trades": [...]
}
```

---

## 7. Backup Strategy

### Local Backups

**Snapshots:** Mỗi 4h, giữ 32 ngày (xem [05. State Management](05-state-management.md))

### Remote Backup (Google Drive)

**Schedule:** Mỗi ngày lúc 02:00

**Files:**
- `trading_agents.db` (state)
- `signals.log`
- `paper_trades.log`
- `reports/daily/` (7 ngày gần nhất)
- Snapshot gần nhất

**Retention trên Drive:** 90 ngày

**Script:** `scripts/backup_to_drive.sh` (xem [05. State Management](05-state-management.md))

---

## 8. Storage Estimates

| Category | Size | Retention | Annual growth |
|---|---|---|---|
| OHLCV (3 tháng) | ~50MB | Rolling | 0MB (constant) |
| Derivatives (90 ngày) | ~20MB | Rolling | 0MB (constant) |
| Reports | ~9MB | Forever | ~9MB/năm |
| signals.log | ~5MB | Forever | ~5MB/năm |
| paper_trades.log | ~2MB | Forever | ~2MB/năm |
| errors.log | ~10MB | 90 days | 0MB (rolling) |
| system.log | ~100MB | 30 days | 0MB (rotating) |
| api_calls.log | ~20MB | 90 days | 0MB (rolling) |
| Backtests | ~50MB | Forever | ~50MB/năm |
| **Total** | **~266MB** | | **~66MB/năm** |

**Sau 5 năm:** ~600MB → Hoàn toàn acceptable.

---

## 9. Maintenance Scripts

### Daily Cleanup (03:00)

```bash
#!/bin/bash
# scripts/daily_cleanup.sh

echo "Starting daily cleanup..."

# Cleanup old OHLCV
python -c "from storage import cleanup_old_ohlcv; cleanup_old_ohlcv()"

# Cleanup old derivatives
python -c "from storage import cleanup_old_derivatives; cleanup_old_derivatives()"

# Cleanup expired cache
python -c "from storage import cleanup_expired_cache; cleanup_expired_cache()"

# Cleanup old snapshots
python -c "from state import cleanup_old_snapshots; cleanup_old_snapshots()"

# Cleanup old logs
python -c "from storage import cleanup_errors_log; cleanup_errors_log()"
python -c "from storage import cleanup_api_calls_log; cleanup_api_calls_log()"

echo "Daily cleanup completed."
```

### Backup Script (02:00)

Xem `scripts/backup_to_drive.sh` trong [05. State Management](05-state-management.md).

---

## Next

- [07. Backtesting](07-backtesting.md) — Framework, slippage, fees, baselines
