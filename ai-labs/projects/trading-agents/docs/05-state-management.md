# 05. State Management — Tracking System State

## Tổng quan

State management sử dụng **hybrid storage**:
- **SQLite:** Paper portfolio, signals (cần query, aggregate)
- **JSON:** System state, cache (đơn giản, human-readable)

---

## Storage Structure

```
state/
├── trading_agents.db          # SQLite database
│   ├── paper_portfolio (table)
│   ├── open_positions (table)
│   ├── closed_positions (table)
│   └── signals (table)
├── system_state.json          # Current system state
├── cache/                     # Cached data
│   ├── BTC_ohlcv_1h.json
│   ├── BTC_fundamentals.json
│   └── ...
└── snapshots/                 # Backups mỗi 4h
    ├── 2026-06-02_00-00/
    │   ├── trading_agents.db
    │   └── system_state.json
    ├── 2026-06-02_04-00/
    └── ...
```

---

## 1. Paper Portfolio State (SQLite)

### Schema

```sql
-- Table: paper_portfolio
CREATE TABLE paper_portfolio (
    id INTEGER PRIMARY KEY,
    total_usdt REAL NOT NULL,
    available_usdt REAL NOT NULL,
    in_positions_usdt REAL NOT NULL,
    unrealized_pnl REAL DEFAULT 0,
    realized_pnl REAL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: open_positions
CREATE TABLE open_positions (
    id TEXT PRIMARY KEY,  -- pos_001, pos_002...
    coin TEXT NOT NULL,
    type TEXT NOT NULL,   -- 'spot' or 'futures'
    side TEXT NOT NULL,   -- 'long' or 'short'
    leverage INTEGER,
    entry_price REAL NOT NULL,
    size REAL NOT NULL,
    entry_time TIMESTAMP NOT NULL,
    stop_loss REAL,
    take_profit REAL,
    unrealized_pnl REAL DEFAULT 0,
    unrealized_pnl_pct REAL DEFAULT 0,
    last_price REAL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: closed_positions
CREATE TABLE closed_positions (
    id TEXT PRIMARY KEY,
    coin TEXT NOT NULL,
    type TEXT NOT NULL,
    side TEXT NOT NULL,
    leverage INTEGER,
    entry_price REAL NOT NULL,
    exit_price REAL NOT NULL,
    size REAL NOT NULL,
    entry_time TIMESTAMP NOT NULL,
    exit_time TIMESTAMP NOT NULL,
    realized_pnl REAL NOT NULL,
    realized_pnl_pct REAL NOT NULL,
    hold_duration_hours REAL,
    exit_reason TEXT,  -- 'tp_hit', 'sl_hit', 'manual'
    fees_paid REAL DEFAULT 0,
    slippage REAL DEFAULT 0
);

-- Table: signals
CREATE TABLE signals (
    id TEXT PRIMARY KEY,  -- sig_20260602_070015_BTC
    timestamp TIMESTAMP NOT NULL,
    mode TEXT NOT NULL,   -- 'full', 'quick', 'flash'
    coin TEXT NOT NULL,
    signal TEXT NOT NULL, -- 'BUY', 'SELL', 'HOLD'
    type TEXT NOT NULL,   -- 'spot', 'futures'
    entry REAL,
    stop_loss REAL,
    take_profit REAL,
    confidence REAL NOT NULL,
    position_size_suggested REAL,
    summary TEXT,
    
    -- Paper trade tracking
    paper_executed INTEGER DEFAULT 0,
    paper_position_id TEXT,
    paper_fill_price REAL,
    paper_fill_time TIMESTAMP,
    
    -- Julius action tracking
    julius_action TEXT,  -- 'executed', 'skipped', 'watching', NULL
    julius_action_time TIMESTAMP,
    julius_actual_price REAL,
    julius_actual_size REAL,
    julius_notes TEXT
);
```

### Example Queries

```sql
-- Get current portfolio state
SELECT * FROM paper_portfolio ORDER BY last_updated DESC LIMIT 1;

-- Get all open positions
SELECT * FROM open_positions ORDER BY entry_time DESC;

-- Get closed positions this month
SELECT * FROM closed_positions 
WHERE strftime('%Y-%m', exit_time) = strftime('%Y-%m', 'now')
ORDER BY exit_time DESC;

-- Calculate win rate (30 days)
SELECT 
    COUNT(*) as total_trades,
    SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
    ROUND(100.0 * SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate
FROM closed_positions
WHERE exit_time >= datetime('now', '-30 days');

-- Get signals Julius executed vs skipped
SELECT 
    julius_action,
    COUNT(*) as count,
    AVG(confidence) as avg_confidence
FROM signals
WHERE julius_action IS NOT NULL
GROUP BY julius_action;
```

---

## 2. System State (JSON)

### Format

```json
{
  "last_run": {
    "full": "2026-06-02T07:00:00+07:00",
    "quick": "2026-06-02T15:00:00+07:00",
    "lite": "2026-06-02T15:00:00+07:00",
    "screening": "2026-06-01T22:00:00+07:00"
  },
  "errors_today": 2,
  "api_calls_today": {
    "binance": 145,
    "geckoterminal": 23,
    "opencode_go": 87,
    "ollama": 12
  },
  "cost_today": 2.45,
  "cost_week": 18.30,
  "cost_month": 38.50,
  "heartbeat": "2026-06-02T15:05:00+07:00",
  "watchlist": ["BTC", "ETH", "SOL", "ARB", "DOGE"],
  "active_circuit_breakers": []
}
```

### Updates

```python
def update_system_state(updates):
    with open("state/system_state.json", "r+") as f:
        state = json.load(f)
        state.update(updates)
        state["heartbeat"] = datetime.now().isoformat()
        f.seek(0)
        json.dump(state, f, indent=2)
        f.truncate()
```

---

## 3. Cache State (JSON files)

### Structure

```json
// cache/BTC_ohlcv_1h.json
{
  "coin": "BTC",
  "timeframe": "1h",
  "data": [
    {
      "timestamp": 1717308000,
      "open": 68000,
      "high": 68500,
      "low": 67800,
      "close": 68200,
      "volume": 1250.5
    }
  ],
  "fetched_at": "2026-06-02T15:00:00+07:00",
  "expires_at": "2026-06-02T15:30:00+07:00"
}
```

### TTL (Time To Live)

| Data type | TTL |
|---|---|
| OHLCV (≥1h) | 30 phút |
| OHLCV (30m) | 5 phút |
| Fundamentals | 24 giờ |
| News | 1 giờ |
| Sentiment | 30 phút |
| Polymarket | 6 giờ |
| Derivatives | 1 giờ |

```python
def is_cache_valid(cache_file):
    if not os.path.exists(cache_file):
        return False
    
    with open(cache_file) as f:
        data = json.load(f)
    
    expires_at = datetime.fromisoformat(data["expires_at"])
    return datetime.now() < expires_at
```

---

## 4. Snapshots (Disaster Recovery)

### Schedule

**Frequency:** Mỗi 4 giờ (00:00, 04:00, 08:00, 12:00, 16:00, 20:00)

**Retention:** 32 ngày

### Structure

```
snapshots/
├── 2026-06-02_00-00/
│   ├── trading_agents.db
│   ├── system_state.json
│   └── metadata.json
├── 2026-06-02_04-00/
└── ...
```

### Metadata

```json
{
  "snapshot_time": "2026-06-02T04:00:00+07:00",
  "portfolio_balance": 10245.30,
  "open_positions_count": 2,
  "system_health": "ok"
}
```

### Snapshot Script

```python
def create_snapshot():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    snapshot_dir = f"state/snapshots/{timestamp}"
    os.makedirs(snapshot_dir, exist_ok=True)
    
    # Copy database
    shutil.copy("state/trading_agents.db", f"{snapshot_dir}/trading_agents.db")
    
    # Copy system state
    shutil.copy("state/system_state.json", f"{snapshot_dir}/system_state.json")
    
    # Generate metadata
    portfolio = get_current_portfolio()
    metadata = {
        "snapshot_time": datetime.now().isoformat(),
        "portfolio_balance": portfolio["total_usdt"],
        "open_positions_count": len(get_open_positions()),
        "system_health": check_system_health()
    }
    
    with open(f"{snapshot_dir}/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Snapshot created: {snapshot_dir}")
```

### Cleanup Old Snapshots

```python
def cleanup_old_snapshots(retention_days=32):
    snapshot_base = "state/snapshots"
    cutoff = datetime.now() - timedelta(days=retention_days)
    
    for snapshot_name in os.listdir(snapshot_base):
        # Parse timestamp từ folder name
        try:
            snapshot_time = datetime.strptime(snapshot_name, "%Y-%m-%d_%H-%M")
            if snapshot_time < cutoff:
                shutil.rmtree(f"{snapshot_base}/{snapshot_name}")
                logger.info(f"Deleted old snapshot: {snapshot_name}")
        except ValueError:
            continue
```

Chạy hàng ngày lúc 02:00.

---

## 5. File Locking (Concurrent Access)

Sử dụng **fcntl** (Linux) để tránh race conditions:

```python
import fcntl

def write_state_safe(filepath, data):
    """Thread-safe file write với exclusive lock"""
    with open(filepath, 'w') as f:
        # Acquire exclusive lock
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        
        try:
            json.dump(data, f, indent=2)
        finally:
            # Release lock
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def read_state_safe(filepath):
    """Thread-safe file read với shared lock"""
    with open(filepath, 'r') as f:
        # Acquire shared lock
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        
        try:
            data = json.load(f)
            return data
        finally:
            # Release lock
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

**Note:** Lock tự động release khi process crash.

---

## 6. State Validation & Corruption Handling

### Validation Checks

```python
def validate_portfolio_state(portfolio):
    """Kiểm tra tính toàn vẹn của portfolio state"""
    errors = []
    
    # Balance không âm
    if portfolio["available_usdt"] < 0:
        errors.append("Negative available balance")
    
    # Tổng balance đúng
    positions_value = sum(p["size"] * p["last_price"] for p in get_open_positions())
    expected_total = portfolio["available_usdt"] + positions_value
    
    if abs(expected_total - portfolio["total_usdt"]) > 1.0:  # Tolerance $1
        errors.append(f"Balance mismatch: expected {expected_total}, got {portfolio['total_usdt']}")
    
    # Open positions không duplicate
    position_ids = [p["id"] for p in get_open_positions()]
    if len(position_ids) != len(set(position_ids)):
        errors.append("Duplicate position IDs")
    
    return errors

def check_state_health():
    """Chạy validation checks định kỳ"""
    errors = validate_portfolio_state(get_current_portfolio())
    
    if errors:
        logger.error(f"State corruption detected: {errors}")
        notify_julius(f"🔴 CRITICAL: Portfolio state corruption detected\n" + "\n".join(errors))
        return False
    
    return True
```

### Corruption Recovery

```python
def recover_from_corruption():
    """Rollback về snapshot gần nhất"""
    snapshots = sorted(os.listdir("state/snapshots"), reverse=True)
    
    if not snapshots:
        logger.critical("No snapshots available for recovery")
        notify_julius("🔴 CRITICAL: Cannot recover, no snapshots available")
        return False
    
    latest_snapshot = snapshots[0]
    logger.info(f"Rolling back to snapshot: {latest_snapshot}")
    
    # Backup current (corrupt) state
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.move("state/trading_agents.db", f"state/trading_agents.db.corrupt.{timestamp}")
    shutil.move("state/system_state.json", f"state/system_state.json.corrupt.{timestamp}")
    
    # Restore from snapshot
    snapshot_path = f"state/snapshots/{latest_snapshot}"
    shutil.copy(f"{snapshot_path}/trading_agents.db", "state/trading_agents.db")
    shutil.copy(f"{snapshot_path}/system_state.json", "state/system_state.json")
    
    notify_julius(f"✅ Rolled back to snapshot: {latest_snapshot}")
    return True
```

---

## 7. Telegram Bot — Natural Language Logging

### Workflow

```python
async def handle_telegram_logging(message, signal_id):
    # Parse intent với LLM
    intent = await parse_trading_action(
        message,
        model="deepseek-v4-flash",
        context={"signal_id": signal_id}
    )
    
    if intent["confidence"] < 0.7:
        # Không chắc → confirm
        await bot.send_message(
            f"Mình hiểu là: {intent['summary']}\n"
            f"Đúng không? (Yes/No)"
        )
        # Wait for confirmation...
        return
    
    # Update database
    if intent["action"] == "executed":
        conn = sqlite3.connect("state/trading_agents.db")
        conn.execute("""
            UPDATE signals SET
                julius_action = 'executed',
                julius_action_time = ?,
                julius_actual_price = ?,
                julius_actual_size = ?,
                julius_notes = ?
            WHERE id = ?
        """, (
            datetime.now().isoformat(),
            intent["price"],
            intent["size"],
            intent["notes"],
            signal_id
        ))
        conn.commit()
        
        await bot.send_message(f"✅ Logged: {intent['summary']}")
    
    elif intent["action"] == "skipped":
        conn.execute("""
            UPDATE signals SET
                julius_action = 'skipped',
                julius_action_time = ?,
                julius_notes = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), intent["reason"], signal_id))
        conn.commit()
        
        await bot.send_message(f"✅ Marked as skipped")
```

### Example Messages

| Julius input | Parsed intent |
|---|---|
| "Đã mua BTC ở 68100" | `{action: "executed", coin: "BTC", side: "buy", price: 68100, type: "spot"}` |
| "Vào short ETH 3200, x5" | `{action: "executed", coin: "ETH", side: "short", price: 3200, leverage: 5, type: "futures"}` |
| "Skip, không tin setup này" | `{action: "skipped", reason: "không tin setup"}` |
| "Chốt lời BTC ở 72k" | `{action: "closed", coin: "BTC", exit_price: 72000}` |

---

## 8. State Backup (Google Drive)

**Schedule:** Mỗi ngày lúc 02:00

**Files backup:**
- `trading_agents.db`
- `signals.log`
- `paper_trades.log`
- `reports/daily/` (7 ngày gần nhất)
- `snapshots/` (snapshot gần nhất)

```bash
#!/bin/bash
# scripts/backup_to_drive.sh

DATE=$(date +%Y-%m-%d)
BACKUP_DIR="/tmp/trading-agents-backup-$DATE"

mkdir -p $BACKUP_DIR

# Copy files
cp state/trading_agents.db $BACKUP_DIR/
cp logs/signals.log $BACKUP_DIR/
cp logs/paper_trades.log $BACKUP_DIR/
cp -r reports/daily $(ls -t reports/daily | head -7) $BACKUP_DIR/reports/
cp -r state/snapshots/$(ls -t state/snapshots | head -1) $BACKUP_DIR/snapshot/

# Compress
tar -czf trading-agents-backup-$DATE.tar.gz -C /tmp trading-agents-backup-$DATE

# Upload via rclone
rclone copy trading-agents-backup-$DATE.tar.gz gdrive:trading-agents-backups/

# Cleanup local
rm -rf $BACKUP_DIR trading-agents-backup-$DATE.tar.gz

# Delete backups >90 days on Drive
rclone delete --min-age 90d gdrive:trading-agents-backups/
```

---

## Next

- [06. Data Storage](06-data-storage.md) — OHLCV, logs, reports retention
