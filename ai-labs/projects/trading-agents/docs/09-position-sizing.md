# 09. Position Sizing & Strategy

## Tổng quan

Position sizing quyết định **mỗi trade đặt bao nhiêu tiền**, dựa trên:
- **Risk-based:** 3% portfolio risk per trade
- **Confidence multiplier:** Adjust theo confidence score
- **Constraints:** Max position size, leverage, exposure

---

## Base Position Sizing (Risk-Based)

```python
def calculate_position_size(signal, portfolio, confidence):
    # Base risk: 3% of portfolio
    base_risk = portfolio.total * 0.03
    
    # Adjust by confidence
    confidence_multiplier = get_position_size_multiplier(confidence)
    adjusted_risk = base_risk * confidence_multiplier
    
    # Calculate size based on SL distance
    sl_distance = abs(signal.entry - signal.stop_loss)
    sl_percentage = sl_distance / signal.entry
    
    position_value = adjusted_risk / sl_percentage
    
    # Apply max position size constraint (30% per coin)
    max_position = portfolio.total * 0.30
    position_value = min(position_value, max_position)
    
    # Check available balance
    if position_value > portfolio.available:
        position_value = portfolio.available * 0.95  # Leave 5% buffer
    
    return position_value
```

**Example:**

```
Portfolio: $10,000
Signal: BTC BUY at $68,000, SL $65,000
Confidence: 0.82 (strong)

Base risk = $10,000 × 3% = $300
Confidence multiplier = 1.0 (≥0.8)
Adjusted risk = $300 × 1.0 = $300

SL distance = $68,000 - $65,000 = $3,000
SL percentage = $3,000 / $68,000 = 4.4%

Position value = $300 / 0.044 = $6,818
Max position (30%) = $3,000
→ Final position value = $3,000
```

---

## Constraints

| Rule | Value |
|---|---|
| **Risk per trade** | 3% portfolio |
| **Max position size per coin** | 30% portfolio |
| **Max total exposure** | 80% portfolio (luôn giữ 20% cash) |
| **Max correlated exposure** | 50% portfolio |
| **Max open positions** | 5 đồng thời |
| **Max leverage (futures)** | x10 |
| **Margin type** | Isolated |

### Enforcement

```python
def check_constraints(signal, portfolio):
    errors = []
    
    # Check total exposure
    current_exposure = sum(p["value"] for p in portfolio.open_positions)
    if current_exposure + signal.position_value > portfolio.total * 0.80:
        errors.append("Max total exposure reached (80%)")
    
    # Check max positions
    if len(portfolio.open_positions) >= 5:
        errors.append("Max open positions reached (5)")
    
    # Check correlated exposure (BTC + ETH cùng long)
    correlated_coins = get_correlated_coins(signal.coin)
    correlated_exposure = sum(
        p["value"] for p in portfolio.open_positions
        if p["coin"] in correlated_coins and p["side"] == signal.side
    )
    if correlated_exposure + signal.position_value > portfolio.total * 0.50:
        errors.append("Max correlated exposure reached (50%)")
    
    return errors
```

---

## Stop Loss Strategies

### Default: ATR-based

```python
def calculate_atr_stop_loss(data, entry_price, side, atr_multiplier=2.0):
    """ATR-based SL — adaptive theo volatility"""
    atr = calculate_atr(data, period=14)
    
    if side == "long":
        stop_loss = entry_price - (atr * atr_multiplier)
    else:  # short
        stop_loss = entry_price + (atr * atr_multiplier)
    
    return stop_loss
```

**Ưu điểm:** Adaptive — coin volatile có SL rộng hơn, coin ít volatile có SL hẹp hơn.

### Fallback: Fixed Percentage

```python
def calculate_fixed_stop_loss(entry_price, side, fixed_pct=0.15):
    """Fixed 15% SL"""
    if side == "long":
        stop_loss = entry_price * (1 - fixed_pct)
    else:
        stop_loss = entry_price * (1 + fixed_pct)
    
    return stop_loss
```

**Khi dùng:** Khi không đủ data để tính ATR.

### Support/Resistance-based

```python
def calculate_sr_stop_loss(data, entry_price, side):
    """SL dưới nearest support (long) hoặc trên resistance (short)"""
    if side == "long":
        support_levels = detect_support_levels(data)
        nearest_support = max([s for s in support_levels if s < entry_price], default=None)
        if nearest_support:
            return nearest_support * 0.99  # Chừa buffer 1%
    else:
        resistance_levels = detect_resistance_levels(data)
        nearest_resistance = min([r for r in resistance_levels if r > entry_price], default=None)
        if nearest_resistance:
            return nearest_resistance * 1.01
    
    return None  # Fallback to ATR
```

---

## Take Profit Strategies

### Default: Risk/Reward Ratio

```python
def calculate_rr_take_profit(entry_price, stop_loss, side, rr_ratio=2.0):
    """TP dựa trên R:R ratio (min 1:2)"""
    sl_distance = abs(entry_price - stop_loss)
    tp_distance = sl_distance * rr_ratio
    
    if side == "long":
        take_profit = entry_price + tp_distance
    else:
        take_profit = entry_price - tp_distance
    
    return take_profit
```

### Resistance/Support Target

```python
def calculate_sr_take_profit(data, entry_price, side):
    """TP tại next resistance (long) hoặc support (short)"""
    if side == "long":
        resistance_levels = detect_resistance_levels(data)
        targets = [r for r in resistance_levels if r > entry_price]
        if targets:
            return min(targets)  # Nearest resistance
    else:
        support_levels = detect_support_levels(data)
        targets = [s for s in support_levels if s < entry_price]
        if targets:
            return max(targets)
    
    return None  # Fallback to R:R
```

### Trailing Stop

```python
def check_trailing_stop(position, current_price, activation_pct=0.03, trail_pct=0.015):
    """Activate trailing stop khi profit >3%, trail 1.5%"""
    if position["side"] == "long":
        profit_pct = (current_price - position["entry_price"]) / position["entry_price"]
        
        if profit_pct >= activation_pct:
            # Update SL to current_price - trail_pct
            new_sl = current_price * (1 - trail_pct)
            if new_sl > position["stop_loss"]:
                position["stop_loss"] = new_sl
                position["trailing_active"] = True
```

---

## Futures-Specific Rules

### Leverage by Confidence

```python
def calculate_futures_leverage(confidence):
    if confidence >= 0.8:
        return 10  # Max x10
    elif confidence >= 0.6:
        return 5   # x5
    elif confidence >= 0.4:
        return 3   # x3
    else:
        return 1   # No leverage
```

### Margin Requirements

```python
def calculate_margin_required(position_value, leverage):
    return position_value / leverage

def check_margin_safety(portfolio, margin_required):
    """Đảm bảo margin level >150% (buffer cho volatility)"""
    if portfolio.available < margin_required * 1.5:
        return False, "Insufficient margin buffer"
    return True, None
```

### Funding Rate Check

```python
def check_funding_rate_risk(coin, side, max_acceptable=0.001):
    """Cảnh báo nếu funding rate quá cao"""
    funding = get_current_funding_rate(coin)
    
    # Long pay positive funding, short pay negative funding
    if side == "long" and funding > max_acceptable:
        return False, f"High funding rate: {funding:.4%} (longs paying)"
    elif side == "short" and funding < -max_acceptable:
        return False, f"High funding rate: {funding:.4%} (shorts paying)"
    
    return True, None
```

---

## Spot-Specific Rules

### Coin Type Allocation

```python
ALLOCATION_LIMITS = {
    "memecoin": 0.05,    # Max 5% per memecoin
    "large_cap": 0.30,   # Max 30% per large cap (BTC, ETH)
    "mid_cap": 0.15,     # Max 15% per mid cap
    "small_cap": 0.10    # Max 10% per small cap
}

def get_coin_type(coin):
    market_cap = get_market_cap(coin)
    
    if coin in ["BTC", "ETH"]:
        return "large_cap"
    elif market_cap > 10_000_000_000:  # >$10B
        return "large_cap"
    elif market_cap > 1_000_000_000:   # >$1B
        return "mid_cap"
    elif market_cap > 100_000_000:     # >$100M
        return "small_cap"
    else:
        return "memecoin"

def apply_coin_type_limit(position_value, coin, portfolio):
    coin_type = get_coin_type(coin)
    max_allocation = ALLOCATION_LIMITS[coin_type] * portfolio.total
    
    return min(position_value, max_allocation)
```

---

## Entry Types

### Market vs Limit

```python
def determine_entry_type(signal, current_price):
    """
    Nếu current price gần entry (<0.5%) → market
    Nếu xa entry (>0.5%) → limit order
    """
    diff_pct = abs(current_price - signal.entry) / signal.entry
    
    if diff_pct < 0.005:  # <0.5%
        return {
            "type": "market",
            "price": current_price
        }
    else:
        return {
            "type": "limit",
            "price": signal.entry,
            "expire_minutes": 60  # Limit order expire sau 1h
        }
```

### Scale-in (Optional)

```python
def create_scale_in_orders(signal, total_size, num_entries=3):
    """Chia entry thành 3 phần để giảm slippage"""
    entry_prices = [
        signal.entry * 0.998,  # -0.2%
        signal.entry,
        signal.entry * 1.002   # +0.2%
    ]
    
    size_per_entry = total_size / num_entries
    
    return [
        {"price": p, "size": size_per_entry}
        for p in entry_prices
    ]
```

**Khi dùng:** Position lớn (>$5,000), để giảm market impact.

---

## Risk/Reward Validation

```python
def validate_risk_reward(signal):
    """Minimum R:R = 1:2"""
    entry = signal.entry
    sl = signal.stop_loss
    tp = signal.take_profit
    
    risk = abs(entry - sl)
    reward = abs(tp - entry)
    rr_ratio = reward / risk if risk > 0 else 0
    
    if rr_ratio < 2.0:
        return False, f"R:R too low: 1:{rr_ratio:.2f} (min 1:2)"
    
    return True, None
```

---

## Full Position Sizing Workflow

```python
def calculate_full_position_setup(signal, portfolio, confidence):
    # 1. Calculate base position size
    position_value = calculate_position_size(signal, portfolio, confidence)
    
    # 2. Apply coin type limit (spot only)
    if signal.type == "spot":
        position_value = apply_coin_type_limit(position_value, signal.coin, portfolio)
    
    # 3. Check constraints
    errors = check_constraints(signal, portfolio)
    if errors:
        return None, errors
    
    # 4. Calculate leverage (futures only)
    if signal.type == "futures":
        leverage = calculate_futures_leverage(confidence)
        margin_required = calculate_margin_required(position_value, leverage)
        
        ok, err = check_margin_safety(portfolio, margin_required)
        if not ok:
            return None, [err]
        
        ok, err = check_funding_rate_risk(signal.coin, signal.side)
        if not ok:
            return None, [err]
    else:
        leverage = 1
        margin_required = position_value
    
    # 5. Determine entry type
    current_price = get_current_price(signal.coin)
    entry_details = determine_entry_type(signal, current_price)
    
    # 6. Validate R:R
    ok, err = validate_risk_reward(signal)
    if not ok:
        return None, [err]
    
    # 7. Final setup
    return {
        "position_value": position_value,
        "leverage": leverage,
        "margin_required": margin_required,
        "entry_type": entry_details["type"],
        "entry_price": entry_details["price"],
        "stop_loss": signal.stop_loss,
        "take_profit": signal.take_profit,
        "risk_amount": position_value * abs(signal.entry - signal.stop_loss) / signal.entry,
        "reward_amount": position_value * abs(signal.take_profit - signal.entry) / signal.entry,
        "rr_ratio": abs(signal.take_profit - signal.entry) / abs(signal.entry - signal.stop_loss)
    }, None
```

---

## Next

- [10. Monitoring](10-monitoring.md) — Telegram dashboard, alerts
