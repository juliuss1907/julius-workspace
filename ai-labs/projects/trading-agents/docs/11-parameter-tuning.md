# 11. Parameter Tuning — Per-Coin Adaptive

## Tổng quan

Hệ thống tự động tune parameters **mỗi coin riêng biệt** hàng tháng, dựa trên backtest performance.

**Scope tuning:**
- Indicator thresholds (RSI, MACD, BB...)
- Stop Loss / Take Profit rules
- Position sizing parameters

---

## Per-Coin Configuration

Mỗi coin có file config riêng, inherits từ `default_params.yaml`:

```
config/
├── default_params.yaml       # Global defaults
└── coin_params/
    ├── BTC.yaml
    ├── ETH.yaml
    ├── SOL.yaml
    └── ...
```

---

## Tunable Parameters

### 1. Technical Indicators

```yaml
# BTC.yaml
technical_indicators:
  rsi:
    oversold: 25      # Default: 30
    overbought: 75    # Default: 70
    period: 14
  
  macd:
    fast: 12
    slow: 26
    signal: 9
  
  bollinger_bands:
    period: 20
    std_dev: 2.0
  
  atr:
    period: 14
```

### 2. Stop Loss / Take Profit

```yaml
stop_loss:
  method: "atr"           # or "fixed", "support_resistance"
  atr_multiplier: 2.5     # Default: 2.0
  fixed_pct: 0.15
  
take_profit:
  risk_reward_ratio: 2.0
  trailing_stop:
    enabled: true
    activation_pct: 0.03  # Activate when profit >3%
    trail_pct: 0.015      # Trail 1.5%
```

### 3. Position Sizing

```yaml
position_sizing:
  risk_per_trade: 0.03      # 3% portfolio risk
  max_position_size: 0.30   # 30% max per coin
  
  confidence_multipliers:
    high: 1.0    # Confidence ≥0.8
    medium: 0.75 # Confidence 0.6-0.8
    low: 0.5     # Confidence 0.4-0.6
```

---

## Monthly Tuning Workflow

**Schedule:** Ngày 1 hàng tháng, 04:00

### Step 1: Backtest Parameter Grid

```python
def tune_coin_parameters(coin, last_month_data):
    """Backtest nhiều parameter combinations"""
    
    # Define parameter grid
    param_grid = {
        "rsi_oversold": [25, 30, 35],
        "rsi_overbought": [70, 75, 80],
        "macd_fast": [10, 12, 14],
        "sl_atr_multiplier": [1.5, 2.0, 2.5],
        "risk_per_trade": [0.02, 0.03, 0.04]
    }
    
    # Generate combinations (limit to ~30)
    combinations = generate_combinations(param_grid, max_combinations=30)
    
    results = []
    for params in combinations:
        # Run backtest with these params
        backtest_result = run_backtest(
            coin=coin,
            period=last_month_data,
            params=params
        )
        
        results.append({
            "params": params,
            "win_rate": backtest_result["win_rate"],
            "sharpe": backtest_result["sharpe_ratio"],
            "max_drawdown": backtest_result["max_drawdown"],
            "total_return": backtest_result["total_return"]
        })
    
    # Rank by composite score
    results = rank_by_composite_score(results)
    
    return results[:3]  # Top 3
```

### Step 2: Generate Proposal

```python
def generate_tuning_proposal(coin, current_params, top_3_results):
    """Tạo proposal file cho Julius"""
    
    proposal = f"""
---
type: inbox
inbox_type: param-tuning
coin: {coin}
created: {datetime.now().isoformat()}
---

# Parameter Tuning Proposal — {coin}

## Current Performance (Last 30 days)
- Trades: {current_stats['trades']}
- Win rate: {current_stats['win_rate']:.1%}
- Sharpe ratio: {current_stats['sharpe']:.2f}
- Max drawdown: {current_stats['max_dd']:.1%}

## Current Parameters
```yaml
{yaml.dump(current_params)}
```

## Backtest Results (30 combinations tested on 6-month data)

### Option 1: Conservative (Recommended)
Parameters:
```yaml
rsi_oversold: {top_3_results[0]['params']['rsi_oversold']}
rsi_overbought: {top_3_results[0]['params']['rsi_overbought']}
sl_atr_multiplier: {top_3_results[0]['params']['sl_atr_multiplier']}
risk_per_trade: {top_3_results[0]['params']['risk_per_trade']}
```

Backtest Performance:
- Win rate: {top_3_results[0]['win_rate']:.1%} (+{improvement}%)
- Sharpe: {top_3_results[0]['sharpe']:.2f}
- Max DD: {top_3_results[0]['max_drawdown']:.1%}
- Total return: {top_3_results[0]['total_return']:.1%}

### Option 2: Aggressive
[Similar format...]

### Option 3: Balanced
[Similar format...]

## Recommendation
Option 1 — Best risk-adjusted returns, lower drawdown.

## Decision
[ ] Approve Option 1
[ ] Approve Option 2
[ ] Approve Option 3
[ ] Keep current params
[ ] Custom adjustment (specify below)

Notes:
_______________________
"""
    
    # Save to tasks/inbox
    filename = f"tasks/inbox/param-tuning-{coin}-{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(filename, "w") as f:
        f.write(proposal)
    
    return filename
```

### Step 3: Telegram Notification

```
📊 Parameter Tuning Proposal — BTC

Last month performance: 62% win rate, Sharpe 1.65

Tested 30 combinations on 6-month data.

Top option: RSI 25/75, ATR SL 2.5x
→ Win rate: 68% (+6%), Sharpe: 1.85

Full proposal: tasks/inbox/param-tuning-BTC-2026-07-01.md

Reply to approve:
  "Approve option 1" / "Keep current" / "Skip"
```

### Step 4: Apply Changes

```python
async def handle_tuning_approval(message, proposal_file):
    """Apply changes khi Julius approve"""
    
    # Parse Julius response
    if "approve option 1" in message.text.lower():
        selected = load_option_1_from_proposal(proposal_file)
    elif "approve option 2" in message.text.lower():
        selected = load_option_2_from_proposal(proposal_file)
    elif "keep current" in message.text.lower():
        await bot.send_message("✅ Keeping current parameters")
        return
    else:
        await bot.send_message("❓ Not understood. Reply: 'approve option 1/2/3' or 'keep current'")
        return
    
    # Update config file
    coin = extract_coin_from_proposal(proposal_file)
    config_file = f"config/coin_params/{coin}.yaml"
    
    with open(config_file, "w") as f:
        yaml.dump(selected, f)
    
    # Confirm
    await bot.send_message(f"""
✅ {coin} parameters updated

Changes applied:
{format_changes(old_params, selected)}

Effective immediately in next analysis.
Rollback available if needed.
    """)
    
    # Log change
    log_parameter_change(coin, old_params, selected, approved_by="julius")
```

---

## Constraints & Safety

### 1. Minimum Sample Size

```python
def check_tuning_eligibility(coin, period="30d"):
    """Chỉ tune nếu đủ data"""
    trades = get_trades_for_coin(coin, period)
    
    if len(trades) < 10:
        logger.info(f"Skipping {coin} tuning: only {len(trades)} trades (<10 minimum)")
        return False
    
    return True
```

### 2. Maximum Parameter Change

```python
def validate_param_change(old_value, new_value, max_change_pct=0.30):
    """Không cho thay đổi quá 30% một lần"""
    change_pct = abs(new_value - old_value) / old_value
    
    if change_pct > max_change_pct:
        return False, f"Change too large: {change_pct:.1%} (max {max_change_pct:.1%})"
    
    return True, None
```

### 3. Tuning Frequency

```python
def check_last_tuning(coin):
    """Tối đa 1 lần/tháng per coin"""
    last_tuning = get_last_tuning_date(coin)
    
    if last_tuning and (datetime.now() - last_tuning).days < 30:
        return False, f"Last tuned {(datetime.now() - last_tuning).days} days ago (min 30 days)"
    
    return True, None
```

### 4. Rollback Mechanism

```python
def rollback_parameters(coin, reason="performance_degraded"):
    """Rollback về parameters trước đó"""
    
    # Load previous version
    backup_file = f"config/coin_params/backups/{coin}_{last_change_date}.yaml"
    if not os.path.exists(backup_file):
        logger.error(f"No backup found for {coin}")
        return False
    
    # Restore
    shutil.copy(backup_file, f"config/coin_params/{coin}.yaml")
    
    notify_julius(f"""
🔄 {coin} Parameters Rolled Back

Reason: {reason}
Restored: {last_change_date} version

Current parameters reverted.
    """)
    
    return True
```

**Auto-rollback trigger:** Nếu win rate giảm >10% sau 2 tuần với params mới.

```python
def check_performance_degradation(coin, new_params_date):
    """Check nếu cần auto-rollback"""
    if (datetime.now() - new_params_date).days < 14:
        return  # Chưa đủ 2 tuần
    
    trades_before = get_trades_before(new_params_date, days=30)
    trades_after = get_trades_after(new_params_date, days=14)
    
    win_rate_before = calculate_win_rate(trades_before)
    win_rate_after = calculate_win_rate(trades_after)
    
    if win_rate_after < win_rate_before - 0.10:  # Giảm >10%
        rollback_parameters(coin, "win_rate_degraded")
        notify_julius(f"⚠️ Auto-rollback triggered for {coin}: win rate dropped from {win_rate_before:.1%} to {win_rate_after:.1%}")
```

---

## Tuning History

Track tất cả changes để review sau:

```
config/coin_params/history/
├── BTC_changes.log
└── ...
```

```json
// BTC_changes.log
{"date": "2026-07-01", "approved_by": "julius", "option": 1, "changes": {"rsi_oversold": {"old": 30, "new": 25}, "sl_atr_multiplier": {"old": 2.0, "new": 2.5}}, "backtest_win_rate": 0.68}
{"date": "2026-08-01", "approved_by": "julius", "option": 2, "changes": {...}}
```

---

## Rollback Command

Julius có thể rollback bất cứ lúc nào qua Telegram:

```
Julius: "Rollback BTC params"

Bot:
🔄 Rollback Options — BTC

1. 2026-06-01 (current)
   RSI 25/75, ATR 2.5x
   Win rate: 68%

2. 2026-05-01
   RSI 30/70, ATR 2.0x
   Win rate: 62%

3. 2026-04-01
   RSI 30/70, ATR 2.2x
   Win rate: 58%

Reply: "rollback to 2" to restore May version
```

---

## Next

- [12. Fine-tuning](12-fine-tuning.md) — Agent self-learning via model fine-tuning
