# 04. Error Handling — Fallback & Recovery

## Tổng quan

Hệ thống có nhiều failure points. Error handling được thiết kế theo nguyên tắc:

1. **Retry trước khi fallback**
2. **Graceful degradation** — hệ thống vẫn chạy dù một phần fail
3. **Parallel fetch** cho data sources (không phải serial fallback chain)
4. **Never skip agents** — luôn retry đủ cả 2 LLM providers trước

---

## 1. Data Fetching Failures

### Parallel Fetch Model

**Không phải fallback chain** — tất cả sources chạy đồng thời:

```python
async def fetch_derivatives_data(coin):
    # Fetch song song
    hyperliquid_task = fetch_hyperliquid(coin)
    binance_task = fetch_binance_futures(coin)
    lighter_task = fetch_lighter(coin)
    
    results = await asyncio.gather(
        hyperliquid_task,
        binance_task,
        lighter_task,
        return_exceptions=True
    )
    
    # Aggregate
    data = {}
    if not isinstance(results[0], Exception):
        data["hyperliquid"] = results[0]
    if not isinstance(results[1], Exception):
        data["binance"] = results[1]
    if not isinstance(results[2], Exception):
        data["lighter"] = results[2]
    
    # Chỉ cần ≥1 source thành công
    if not data:
        raise AllSourcesFailedError("All derivatives sources failed")
    
    return data
```

### Retry Logic per Source

Mỗi source retry **3 lần** với exponential backoff:

```python
async def fetch_with_retry(func, *args, retries=3, backoff_base=2):
    for attempt in range(retries):
        try:
            return await func(*args)
        except Exception as e:
            if attempt == retries - 1:
                # Last attempt failed
                logger.error(f"{func.__name__} failed after {retries} attempts: {e}")
                raise
            
            # Exponential backoff
            wait_time = backoff_base ** attempt  # 2s, 4s, 8s
            logger.warning(f"{func.__name__} failed attempt {attempt + 1}, retry in {wait_time}s")
            await asyncio.sleep(wait_time)
```

**Timeout:**
- REST API: 10s per request
- WebSocket: 5s reconnect timeout

### Required vs Optional Data

Khi nhóm data fail, xử lý khác nhau:

| Data nhóm | Mức độ | Nếu toàn bộ nhóm fail |
|---|---|---|
| **OHLCV (giá)** | REQUIRED | Skip coin này, log error, notify Julius |
| **Derivatives** | OPTIONAL | Chạy tiếp, analyst nhận warning flag |
| **On-chain / Fundamentals** | OPTIONAL | Dùng cached data hoặc skip, chạy tiếp |
| **News** (Full/Quick) | OPTIONAL | Chạy tiếp |
| **News** (Flash Quick) | REQUIRED | Retry aggressive (5 lần) — biến động >10% cần nguyên nhân |
| **Sentiment** | OPTIONAL | Chạy tiếp |
| **Polymarket** | OPTIONAL | Chạy tiếp |

**Example:**

```python
# Full mode execution
data = {
    "ohlcv": None,
    "derivatives": None,
    "fundamentals": None,
    "news": None,
    "sentiment": None
}

# Fetch OHLCV (REQUIRED)
try:
    data["ohlcv"] = await fetch_ohlcv(coin)
except AllSourcesFailedError:
    logger.critical(f"Cannot fetch OHLCV for {coin}, skipping")
    notify_julius(f"⚠️ {coin} skipped: no price data")
    return None  # Skip coin

# Fetch Derivatives (OPTIONAL)
try:
    data["derivatives"] = await fetch_derivatives(coin)
except AllSourcesFailedError:
    logger.warning(f"No derivatives data for {coin}")
    data["derivatives_flag"] = "unavailable"
    # Continue anyway

# Continue với other data sources...
```

### Circuit Breaker

Nếu 1 API fail liên tục **5 lần**, tạm ngừng 15 phút:

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=900):
        self.failure_count = 0
        self.threshold = failure_threshold
        self.timeout = timeout
        self.opened_at = None
    
    def is_open(self):
        if self.opened_at:
            if time.time() - self.opened_at > self.timeout:
                # Reset after timeout
                self.opened_at = None
                self.failure_count = 0
                return False
            return True
        return False
    
    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.threshold:
            self.opened_at = time.time()
            logger.error(f"Circuit breaker opened for {self.timeout}s")
    
    def record_success(self):
        self.failure_count = 0
```

### Cache Fallback

Nếu không fetch được data mới, dùng cached data **<5 phút**:

```python
async def fetch_with_cache_fallback(func, coin, max_age=300):
    # Try fetch fresh
    try:
        data = await fetch_with_retry(func, coin)
        await cache.set(f"{func.__name__}:{coin}", data)
        return data
    except Exception as e:
        # Fallback to cache
        cached = await cache.get(f"{func.__name__}:{coin}")
        if cached and cached.age < max_age:
            logger.warning(f"Using cached data for {coin} (age: {cached.age}s)")
            return {"data": cached.value, "flag": "stale"}
        else:
            raise e
```

---

## 2. LLM Failures

### Fallback: OpenCode Go → Ollama Cloud Pro

```python
async def call_llm_with_fallback(prompt, mode="full"):
    # Determine models
    if mode == "full":
        primary_model = "opencode-go/qwen3.7-max"
        fallback_model = "ollama/qwen3.7-max"
    elif mode == "quick":
        primary_model = "opencode-go/deepseek-v4-pro"
        fallback_model = "ollama/deepseek-v4-pro"
    else:  # flash
        primary_model = "opencode-go/deepseek-v4-flash"
        fallback_model = "ollama/mimo-v2.5"
    
    # Try primary (3 retries)
    for attempt in range(3):
        try:
            return await call_llm(prompt, model=primary_model, timeout=60)
        except Exception as e:
            logger.warning(f"Primary LLM failed attempt {attempt + 1}: {e}")
            await asyncio.sleep(2 ** attempt)
    
    # Primary failed, try fallback (3 retries)
    logger.error(f"Primary LLM exhausted, switching to fallback")
    for attempt in range(3):
        try:
            return await call_llm(prompt, model=fallback_model, timeout=60)
        except Exception as e:
            logger.warning(f"Fallback LLM failed attempt {attempt + 1}: {e}")
            await asyncio.sleep(2 ** attempt)
    
    # Both failed
    raise LLMExhaustedError("Both primary and fallback LLM failed")
```

### Error Types Handling

| Error | Action |
|---|---|
| **Timeout (>60s)** | Retry với timeout ngắn hơn (45s), nếu fail → fallback model |
| **Rate limit (429)** | Wait theo `retry-after` header, nếu >30s → fallback |
| **503 Overload** | Retry 3 lần, nếu fail → fallback |
| **Malformed response** | Retry 3 lần same model (có thể random glitch), nếu fail → fallback |
| **Context exceeded** | Truncate input (bỏ data ít quan trọng nhất), retry same model |
| **Auth/Billing error** | CRITICAL — stop toàn bộ, notify Julius ngay (không retry) |

### Graceful Degradation (Pipeline Level)

**Full mode pipeline:** 4 Analysts → 2 Researchers → Trader → Risk/Portfolio

```python
async def run_full_mode(coin):
    # Tầng 1: Analysts
    analyst_results = {}
    
    for analyst_name in ["technical", "fundamentals", "news", "sentiment"]:
        try:
            result = await run_analyst_with_fallback(analyst_name, coin)
            analyst_results[analyst_name] = result
        except LLMExhaustedError:
            # KHÔNG skip — retry trước
            logger.error(f"{analyst_name} analyst failed, retrying...")
            try:
                result = await run_analyst_with_fallback(analyst_name, coin, force_retry=True)
                analyst_results[analyst_name] = result
            except:
                # Still failed → notify Julius
                notify_julius(f"⚠️ {analyst_name} analyst failed for {coin}, manual review needed")
                # Chạy tiếp với missing analyst
                analyst_results[analyst_name] = None
    
    # Check if có đủ data
    if sum(1 for v in analyst_results.values() if v) < 2:
        # <2 analysts thành công → skip coin
        logger.error(f"Too few analysts succeeded for {coin}, skipping")
        return None
    
    # Tầng 2: Researchers (nếu có ≥3 analysts data)
    researcher_results = None
    if sum(1 for v in analyst_results.values() if v) >= 3:
        try:
            researcher_results = await run_researchers(analyst_results)
        except LLMExhaustedError:
            logger.warning("Researchers failed, proceeding without debate")
            # Chạy tiếp không có debate
    
    # Tầng 3: Trader
    try:
        signal = await run_trader(analyst_results, researcher_results)
        return signal
    except LLMExhaustedError:
        # Trader Agent fail = CRITICAL
        logger.critical(f"Trader agent failed for {coin}")
        notify_julius(f"🔴 CRITICAL: Trader agent failed for {coin}")
        return None
```

**Rule:** Luôn retry đủ primary + fallback trước khi skip agent.

---

## 3. Paper Trade Execution Failures

| Scenario | Handling |
|---|---|
| **Không fetch được giá fill** | Dùng last known price + slippage estimate + warning flag |
| **Portfolio state corrupt** | Rollback về hourly snapshot gần nhất |
| **Position size > balance** | Reject trade, log error, notify Julius |
| **Duplicate order** | Idempotency check (same coin + side + <1min) |
| **Leverage liquidation risk** | Pre-check margin level, reject nếu <150% |

```python
def execute_paper_trade(signal, portfolio):
    # Idempotency
    if is_duplicate_order(signal, window_minutes=1):
        logger.warning(f"Duplicate order detected: {signal}")
        return None
    
    # Balance check
    if portfolio.available < signal.position_value:
        logger.error(f"Insufficient balance for {signal.coin}")
        notify_julius(f"⚠️ Paper portfolio insufficient balance")
        return None
    
    # Leverage check (futures only)
    if signal.type == "futures":
        margin_required = signal.position_value / signal.leverage
        if margin_required > portfolio.available:
            logger.error(f"Insufficient margin for leverage x{signal.leverage}")
            return None
    
    # Execute
    try:
        trade = place_paper_order(signal)
        update_portfolio_state(portfolio, trade)
        snapshot_portfolio(portfolio)  # For rollback
        return trade
    except Exception as e:
        logger.error(f"Paper trade execution failed: {e}")
        rollback_portfolio(portfolio)
        return None
```

---

## 4. System-Level Failures

### Heartbeat Monitoring

```python
# Update heartbeat mỗi khi run xong
def update_heartbeat():
    with open(".heartbeat", "w") as f:
        f.write(str(time.time()))

# Watchdog check mỗi 5 phút
async def heartbeat_watchdog():
    while True:
        await asyncio.sleep(300)  # 5 phút
        
        try:
            with open(".heartbeat", "r") as f:
                last_heartbeat = float(f.read())
            
            age = time.time() - last_heartbeat
            if age > 900:  # 15 phút
                notify_julius("🔴 CRITICAL: System heartbeat dead")
                # Attempt restart
                os.system("systemctl restart trading-agents")
        except FileNotFoundError:
            notify_julius("🔴 CRITICAL: Heartbeat file missing")
```

### Process Timeout

Mỗi mode có max runtime:

| Mode | Max runtime |
|---|---|
| Full | 10 phút |
| Quick | 5 phút |
| Flash Quick | 2 phút |
| Lite | 1 phút |

Nếu vượt quá → kill process, notify Julius.

```python
async def run_with_timeout(func, timeout_seconds):
    try:
        return await asyncio.wait_for(func(), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        logger.error(f"{func.__name__} exceeded timeout {timeout_seconds}s")
        notify_julius(f"⚠️ {func.__name__} timeout, killed")
        return None
```

### Disk/Memory Checks

```python
def check_system_resources():
    # Disk
    disk = psutil.disk_usage('/')
    if disk.percent > 80:
        logger.warning(f"Disk usage: {disk.percent}%")
        notify_julius(f"⚠️ Disk usage high: {disk.percent}%")
    
    # Memory
    mem = psutil.virtual_memory()
    if mem.percent > 80:
        logger.warning(f"Memory usage: {mem.percent}%")
        # Force garbage collection
        gc.collect()
```

Chạy trước mỗi mode execution.

---

## 5. Telegram Notification Failures

| Scenario | Handling |
|---|---|
| **API down** | Queue messages, retry sau 1 phút, max 10 retries |
| **Rate limit (30 msg/s)** | Batch messages thành 1 summary |
| **Message >4096 chars** | Split thành nhiều messages hoặc gửi file attachment |
| **Bot token expired** | Log CRITICAL, system vẫn chạy nhưng mute |

```python
async def send_telegram_with_retry(message, retries=10):
    for attempt in range(retries):
        try:
            await bot.send_message(chat_id=CHAT_ID, text=message)
            return
        except TelegramError as e:
            if "too many requests" in str(e):
                # Rate limit
                await asyncio.sleep(1)
            elif "message is too long" in str(e):
                # Split message
                chunks = split_message(message, max_length=4000)
                for chunk in chunks:
                    await bot.send_message(chat_id=CHAT_ID, text=chunk)
                return
            else:
                logger.error(f"Telegram send failed: {e}")
                await asyncio.sleep(60)  # 1 phút
    
    # Failed after retries
    logger.critical(f"Failed to send Telegram after {retries} attempts")
    # Log to file instead
    with open("logs/telegram_failed.log", "a") as f:
        f.write(f"{time.time()}: {message}\n")
```

---

## 6. Data Quality Validation

Trước khi đưa data vào agent, validate:

| Check | Rule | Action |
|---|---|---|
| **Price spike >50%** | Non-memecoin, 1 phút | Giữ data + thêm `anomaly: true` flag |
| **Price spike >200%** | Memecoin | Giữ data + flag |
| **Zero volume** | Volume = 0 | Reject candle |
| **Data gap** | Missing >3 candles liên tục | Warning flag |
| **Stale data** | >5 phút (real-time) | Warning flag |
| **Negative values** | Price/volume < 0 | Reject, log error |

```python
def validate_ohlcv(candle, prev_candle=None, coin_type="normal"):
    # Negative check
    if any(v < 0 for v in [candle.open, candle.high, candle.low, candle.close, candle.volume]):
        raise InvalidDataError("Negative values detected")
    
    # Zero volume
    if candle.volume == 0:
        raise InvalidDataError("Zero volume")
    
    # Price spike
    if prev_candle:
        change = abs(candle.close - prev_candle.close) / prev_candle.close
        threshold = 2.0 if coin_type == "memecoin" else 0.5
        
        if change > threshold:
            candle.flags.append("anomaly_price_spike")
            logger.warning(f"Price spike detected: {change:.1%}")
    
    return candle
```

---

## 7. Error Logging

Tất cả errors ghi vào `logs/errors.log`:

```json
{
  "timestamp": "2026-06-02T07:05:23+07:00",
  "mode": "full",
  "coin": "BTC",
  "error_type": "data_fetch_failure",
  "source": "binance_websocket",
  "message": "Connection timeout after 3 retries",
  "fallback_used": "binance_rest",
  "impact": "5min delay, analysis completed",
  "stack_trace": "..."
}
```

Review `errors.log` hàng tuần để identify patterns.

---

## 8. Telegram Alert Levels

| Level | Format | Khi nào |
|---|---|---|
| **CRITICAL** | `🔴 CRITICAL: [msg]` | System down, auth error, không recover được |
| **ERROR** | `🟠 ERROR: [msg]` | 1 coin bị skip, 1 agent fail sau retry |
| **WARNING** | `🟡 WARNING: [msg]` | Degraded performance, dùng fallback |
| **INFO** | `🟢 INFO: [msg]` | Run completed bình thường |

---

## Next

- [05. State Management](05-state-management.md) — SQLite + JSON, snapshots
