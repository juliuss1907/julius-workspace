# 07. Backtesting Framework

## Tổng quan

Backtesting = chạy strategy trên historical data để đánh giá hiệu quả trước khi deploy.

**Approach:** Rule-based backtest (không dùng LLM trong backtest để đảm bảo nhanh, rẻ, reproducible).

**Period:** 6 tháng

**Schedule:** Ngày 1 hàng tháng lúc 03:00

---

## Mục đích

1. **Validate strategy quality** — Strategy có hiệu quả trên historical data không?
2. **So sánh strategies** — v1 vs v2, parameters khác nhau
3. **Tune parameters** — RSI 30 hay 25 tốt hơn? SL 3% hay 5%?
4. **Đánh giá trước khi deploy** — Mỗi thay đổi major → backtest trước

---

## Architecture

```
BacktestEngine
  ├── DataLoader
  │   ├── load_ohlcv(coins, period="6m", timeframes)
  │   ├── load_derivatives(coins, period="6m")
  │   └── validate_data_completeness()
  │
  ├── StrategySimulator (Rule-based)
  │   ├── calculate_indicators(RSI, MACD, BB, OBV, Ichimoku)
  │   ├── detect_patterns(H&S, double_top, wedge...)
  │   └── generate_signals(BUY/SELL/HOLD)
  │
  ├── TradeExecutor (simulated)
  │   ├── apply_slippage (fixed for backtest)
  │   ├── apply_fees (Binance regular)
  │   ├── track_portfolio (balance, positions)
  │   └── calculate_pnl()
  │
  └── PerformanceAnalyzer
      ├── calculate_metrics
      ├── baseline_buy_hold_btc
      ├── baseline_buy_hold_watchlist
      └── generate_report
```

---

## Configuration

```python
backtest_config = {
    "strategy": "rule-based-v1",
    "period_months": 6,
    "coins": ["BTC", "ETH", "SOL", "ARB", "DOGE"],
    "initial_balance": 10000,
    "timeframes": ["1h", "4h", "1d"],
    
    "fees": {
        "spot": 0.001,           # 0.1% (Binance regular)
        "futures_maker": 0.0002, # 0.02%
        "futures_taker": 0.0005  # 0.05%
    },
    
    "slippage_fixed": {
        "spot": 0.0005,    # 0.05%
        "futures": 0.0002  # 0.02%
    },
    
    "execution": {
        "fill_type": "instant",  # Instant fill at signal price
        "max_open_positions": 5
    }
}
```

---

## Slippage Model (Hybrid)

### Paper Trading (Real-time)

Sử dụng real-time order book của Binance để tính slippage chính xác:

```python
def calculate_realtime_slippage(coin, side, size_usd):
    orderbook = fetch_binance_orderbook(coin)
    
    levels = orderbook["asks"] if side == "buy" else orderbook["bids"]
    
    filled = 0
    total_cost = 0
    
    for price, qty in levels:
        level_value = price * qty
        if filled + level_value >= size_usd:
            remaining = size_usd - filled
            total_cost += remaining
            filled = size_usd
            break
        else:
            filled += level_value
            total_cost += level_value
    
    effective_price = total_cost / (size_usd / orderbook["mid_price"])
    return (effective_price - orderbook["mid_price"]) / orderbook["mid_price"]
```

**Note:** Logic lấy từ repo [binanceslippagecalculator](https://github.com/cfnetworks/binanceslippagecalculator) port sang Python.

### Backtest (Fixed)

Cho historical backtest (không có order book history), dùng fixed estimates:

```python
def calculate_backtest_slippage(order_type):
    if order_type == "spot":
        return 0.0005  # 0.05%
    else:  # futures
        return 0.0002  # 0.02%
```

**Lý do dùng fixed:** Historical order book không có sẵn → không thể simulate chính xác. Fixed estimates là pragmatic choice.

---

## Fees (Binance Regular User)

```python
FEES = {
    "spot": {
        "maker": 0.0010,
        "taker": 0.0010
    },
    "futures_usdt_m": {
        "maker": 0.0002,
        "taker": 0.0005
    }
}

def calculate_fees(trade):
    if trade.type == "spot":
        return trade.value * FEES["spot"]["taker"]  # Assume taker
    else:
        return trade.value * FEES["futures_usdt_m"]["taker"]

def calculate_total_trade_cost(trade):
    """Entry + Exit fees + Slippage"""
    entry_fee = calculate_fees(trade)
    exit_fee = calculate_fees(trade.exit)
    slippage_cost = trade.value * calculate_backtest_slippage(trade.type)
    
    return entry_fee + exit_fee + slippage_cost
```

---

## Rule-based Strategy

### Indicator Logic

```python
def generate_signal_rule_based(coin_data, params):
    """Rule-based signal generation"""
    df = coin_data["ohlcv_1h"]
    
    # Calculate indicators
    df['rsi'] = calculate_rsi(df['close'], period=14)
    df['macd'], df['signal'] = calculate_macd(df['close'])
    df['bb_upper'], df['bb_middle'], df['bb_lower'] = calculate_bollinger(df['close'])
    df['atr'] = calculate_atr(df, period=14)
    
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Rule 1: RSI oversold + MACD bullish cross → BUY
    if (last['rsi'] < params['rsi_oversold'] 
        and last['macd'] > last['signal']
        and prev['macd'] <= prev['signal']):
        return {
            "signal": "BUY",
            "entry": last['close'],
            "stop_loss": last['close'] - 2 * last['atr'],
            "take_profit": last['close'] + 4 * last['atr']  # R:R 1:2
        }
    
    # Rule 2: RSI overbought + MACD bearish cross → SELL
    if (last['rsi'] > params['rsi_overbought']
        and last['macd'] < last['signal']
        and prev['macd'] >= prev['signal']):
        return {
            "signal": "SELL",
            "entry": last['close'],
            "stop_loss": last['close'] + 2 * last['atr'],
            "take_profit": last['close'] - 4 * last['atr']
        }
    
    return {"signal": "HOLD"}
```

---

## Trade Execution Simulation

```python
def execute_simulated_trade(signal, portfolio, current_candle):
    """Simulate trade execution with fees and slippage"""
    
    # Position sizing (3% risk per trade)
    risk_amount = portfolio.total * 0.03
    sl_distance = abs(signal["entry"] - signal["stop_loss"])
    position_value = risk_amount / (sl_distance / signal["entry"])
    
    # Apply max position size
    position_value = min(position_value, portfolio.total * 0.30)
    
    # Apply slippage
    slippage = calculate_backtest_slippage(signal.get("type", "spot"))
    fill_price = signal["entry"] * (1 + slippage if signal["signal"] == "BUY" else 1 - slippage)
    
    # Calculate fees
    entry_fee = position_value * FEES["spot"]["taker"]
    
    # Open position
    position = {
        "id": f"pos_{len(portfolio.closed_positions) + 1}",
        "coin": signal["coin"],
        "side": "long" if signal["signal"] == "BUY" else "short",
        "entry_price": fill_price,
        "entry_time": current_candle["timestamp"],
        "size": position_value / fill_price,
        "stop_loss": signal["stop_loss"],
        "take_profit": signal["take_profit"],
        "fees_paid": entry_fee,
        "slippage_cost": position_value * slippage
    }
    
    portfolio.open_positions.append(position)
    portfolio.available -= position_value + entry_fee
    
    return position
```

---

## Position Monitoring

Mỗi candle, check open positions:

```python
def monitor_positions(portfolio, current_candle):
    """Check if any position hits SL/TP"""
    for position in portfolio.open_positions[:]:
        high = current_candle["high"]
        low = current_candle["low"]
        
        if position["side"] == "long":
            # Check SL
            if low <= position["stop_loss"]:
                close_position(portfolio, position, position["stop_loss"], "sl_hit", current_candle)
            # Check TP
            elif high >= position["take_profit"]:
                close_position(portfolio, position, position["take_profit"], "tp_hit", current_candle)
        
        else:  # short
            if high >= position["stop_loss"]:
                close_position(portfolio, position, position["stop_loss"], "sl_hit", current_candle)
            elif low <= position["take_profit"]:
                close_position(portfolio, position, position["take_profit"], "tp_hit", current_candle)

def close_position(portfolio, position, exit_price, reason, candle):
    """Close position and record P&L"""
    # Apply exit slippage
    slippage = calculate_backtest_slippage(position.get("type", "spot"))
    if position["side"] == "long":
        actual_exit = exit_price * (1 - slippage)
    else:
        actual_exit = exit_price * (1 + slippage)
    
    # Calculate P&L
    if position["side"] == "long":
        pnl = (actual_exit - position["entry_price"]) * position["size"]
    else:
        pnl = (position["entry_price"] - actual_exit) * position["size"]
    
    # Subtract exit fee
    exit_fee = (position["size"] * actual_exit) * FEES["spot"]["taker"]
    pnl -= exit_fee
    
    # Update portfolio
    portfolio.available += position["size"] * actual_exit - exit_fee
    portfolio.realized_pnl += pnl
    
    # Move to closed
    position["exit_price"] = actual_exit
    position["exit_time"] = candle["timestamp"]
    position["realized_pnl"] = pnl
    position["realized_pnl_pct"] = pnl / (position["entry_price"] * position["size"])
    position["exit_reason"] = reason
    position["fees_paid"] += exit_fee
    
    portfolio.closed_positions.append(position)
    portfolio.open_positions.remove(position)
```

---

## Performance Metrics

```python
def calculate_performance_metrics(portfolio, period_days):
    """Calculate all performance metrics"""
    closed = portfolio.closed_positions
    
    if not closed:
        return None
    
    # Basic stats
    total_trades = len(closed)
    winning = [p for p in closed if p["realized_pnl"] > 0]
    losing = [p for p in closed if p["realized_pnl"] <= 0]
    
    win_rate = len(winning) / total_trades if total_trades > 0 else 0
    avg_win = sum(p["realized_pnl_pct"] for p in winning) / len(winning) if winning else 0
    avg_loss = sum(p["realized_pnl_pct"] for p in losing) / len(losing) if losing else 0
    
    # Returns
    total_return = (portfolio.total - portfolio.initial) / portfolio.initial
    
    # Sharpe Ratio (annualized)
    daily_returns = calculate_daily_returns(portfolio)
    sharpe = (np.mean(daily_returns) / np.std(daily_returns)) * np.sqrt(365) if np.std(daily_returns) > 0 else 0
    
    # Max Drawdown
    equity_curve = calculate_equity_curve(portfolio)
    rolling_max = np.maximum.accumulate(equity_curve)
    drawdown = (equity_curve - rolling_max) / rolling_max
    max_drawdown = abs(np.min(drawdown))
    
    # Profit factor
    total_wins = sum(p["realized_pnl"] for p in winning)
    total_losses = abs(sum(p["realized_pnl"] for p in losing))
    profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
    
    return {
        "total_trades": total_trades,
        "winning_trades": len(winning),
        "losing_trades": len(losing),
        "win_rate": win_rate,
        "avg_win_pct": avg_win,
        "avg_loss_pct": avg_loss,
        "total_return": total_return,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_drawdown,
        "profit_factor": profit_factor
    }
```

---

## Baseline Comparisons

### Buy-and-Hold BTC

```python
def calculate_btc_baseline(period_start, period_end, initial_balance):
    btc_data = load_ohlcv("BTC", "1d", period_start, period_end)
    
    initial_price = btc_data.iloc[0]["close"]
    final_price = btc_data.iloc[-1]["close"]
    
    btc_holding = initial_balance / initial_price
    final_value = btc_holding * final_price
    
    return {
        "return": (final_value - initial_balance) / initial_balance,
        "max_drawdown": calculate_max_drawdown(btc_data["close"])
    }
```

### Buy-and-Hold Watchlist (Equal Weight)

```python
def calculate_watchlist_baseline(coins, period_start, period_end, initial_balance):
    allocation_per_coin = initial_balance / len(coins)
    
    final_value = 0
    for coin in coins:
        coin_data = load_ohlcv(coin, "1d", period_start, period_end)
        initial_price = coin_data.iloc[0]["close"]
        final_price = coin_data.iloc[-1]["close"]
        
        holding = allocation_per_coin / initial_price
        final_value += holding * final_price
    
    return {
        "return": (final_value - initial_balance) / initial_balance,
        "allocation": {coin: 1.0/len(coins) for coin in coins}
    }
```

---

## Output Report Format

```json
{
  "backtest_id": "bt_2026-07-01_rule-v1_6m",
  "strategy": "rule-based-v1",
  "period": "2025-12-01 to 2026-06-01",
  "period_days": 183,
  "coins": ["BTC", "ETH", "SOL", "ARB", "DOGE"],
  "config": {
    "initial_balance": 10000,
    "risk_per_trade": 0.03,
    "max_positions": 5,
    "fees": {"spot": 0.001, "futures_taker": 0.0005},
    "slippage": {"spot": 0.0005, "futures": 0.0002}
  },
  
  "performance": {
    "initial_balance": 10000,
    "final_balance": 12800,
    "total_return": 0.28,
    "annualized_return": 0.61,
    "total_trades": 87,
    "winning_trades": 54,
    "losing_trades": 33,
    "win_rate": 0.621,
    "avg_win_pct": 0.048,
    "avg_loss_pct": -0.031,
    "max_drawdown": 0.16,
    "sharpe_ratio": 1.72,
    "sortino_ratio": 2.15,
    "profit_factor": 2.1
  },
  
  "baselines": {
    "buy_hold_btc": {
      "return": 0.22,
      "max_drawdown": 0.25
    },
    "buy_hold_watchlist": {
      "return": 0.19,
      "max_drawdown": 0.30,
      "allocation": {"BTC": 0.2, "ETH": 0.2, "SOL": 0.2, "ARB": 0.2, "DOGE": 0.2}
    }
  },
  
  "alpha": {
    "vs_btc": 0.06,
    "vs_watchlist": 0.09
  },
  
  "costs": {
    "total_fees_paid": 85.6,
    "total_slippage": 42.3,
    "total_costs": 127.9,
    "cost_pct": 0.013
  },
  
  "trades": [...]
}
```

---

## Monthly Backtest Automation

**Schedule:** Ngày 1 hàng tháng, 03:00

```bash
# crontab entry
0 3 1 * * cd /path/to/trading-agents && python scripts/run_monthly_backtest.py
```

```python
# scripts/run_monthly_backtest.py
def run_monthly_backtest():
    # Period: 6 tháng gần nhất
    period_end = datetime.now()
    period_start = period_end - timedelta(days=180)
    
    # Load current strategy
    strategy_config = load_yaml("config/active_strategy.yaml")
    
    # Run backtest
    result = run_backtest(
        strategy=strategy_config,
        period_start=period_start,
        period_end=period_end,
        coins=load_watchlist()
    )
    
    # Save result
    output_file = f"backtests/{datetime.now().strftime('%Y-%m-%d')}_{strategy_config['name']}.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    
    # Generate summary
    summary = generate_telegram_summary(result)
    notify_julius(summary)
```

### Telegram Summary

```
📊 Monthly Backtest — June 2026

Strategy: rule-based-v1
Period: 2025-12-01 to 2026-06-01

Performance:
  Return: +28.0%
  Win rate: 62.1% (54/87 trades)
  Sharpe: 1.72
  Max DD: 16%

Baselines:
  BTC HODL: +22% (alpha: +6%)
  Watchlist HODL: +19% (alpha: +9%)

Costs:
  Fees: $85.60
  Slippage: $42.30
  Total: $127.90 (1.3% of returns)

Full report: backtests/2026-07-01_rule-based-v1.json
```

---

## Comparison Reports

So sánh kết quả backtest qua các tháng để track strategy evolution:

```
📊 Strategy Performance Trend (6 months)

Jun 2026: +28% (Sharpe 1.72) ← latest
May 2026: +24% (Sharpe 1.65)
Apr 2026: +18% (Sharpe 1.42)
Mar 2026: +21% (Sharpe 1.58)
Feb 2026: +15% (Sharpe 1.31)
Jan 2026: +12% (Sharpe 1.20)

Trend: Improving ↗
Best parameter set: BTC RSI 25/75 (locked in May)
```

---

## Next

- [08. Confidence Scoring](08-confidence-scoring.md) — Weighted scoring, self-adjusting weights
