# 08. Confidence Scoring — Weighted Analyst Scores

## Tổng quan

Confidence score (0.0 → 1.0) quyết định mức độ tin tưởng vào signal, ảnh hưởng trực tiếp đến position size.

**Cách tính:** Weighted average từ sub-scores của các analysts trong Tầng 1.

---

## Analyst Weights (Per Mode)

### Full Mode

| Analyst | Weight | Lý do |
|---|---|---|
| **Technical** | **60%** | Core analysis, đo trực tiếp price action |
| News | 10% | Bổ trợ, không phải driver chính |
| Fundamentals | 10% | Long-term, ít ảnh hưởng short-term trades |
| Sentiment | 5% | Noisy, dễ bị manipulate |
| Derivatives | 15% | Predictive value cao (funding, OI) |
| **Total** | **100%** | |

### Quick Mode

| Analyst | Weight |
|---|---|
| **Technical** | **60%** |
| News | 15% |
| Derivatives | 25% |
| **Total** | **100%** |

### Flash Quick Mode

| Analyst | Weight |
|---|---|
| **Technical** | **60%** |
| News | 15% |
| Sentiment | 15% |
| Derivatives | 10% |
| **Total** | **100%** |

---

## Sub-score Calculation (Per Analyst)

### Technical Analyst (0.0 → 1.0)

```python
def calculate_technical_score(data):
    score = 0.0
    
    # Factor 1: Multi-timeframe alignment (30%)
    alignments = 0
    for tf in ["1h", "4h", "1d"]:
        if data[tf]["trend"] == data["signal_direction"]:
            alignments += 1
    score += (alignments / 3) * 0.30
    
    # Factor 2: Indicator confirmation (25%)
    confirmations = 0
    indicators = ["rsi", "macd", "bb", "obv"]
    for ind in indicators:
        if data[ind]["signal"] == data["signal_direction"]:
            confirmations += 1
    score += (confirmations / len(indicators)) * 0.25
    
    # Factor 3: Chart pattern quality (20%)
    if data["pattern"]:
        pattern_quality = data["pattern"]["quality"]  # 'strong', 'medium', 'weak'
        score += {"strong": 0.20, "medium": 0.10, "weak": 0.05}.get(pattern_quality, 0)
    
    # Factor 4: Market regime fit (15%)
    if data["regime"] in ["trend_up", "trend_down"]:
        score += 0.15  # Trend strategies work well in trending
    elif data["regime"] == "ranging":
        score += 0.08  # Mean reversion OK in ranging
    else:  # volatile
        score += 0.02  # Skip trading = low confidence
    
    # Factor 5: Volume confirmation (10%)
    if data["volume"]["spike"]:
        score += 0.10
    elif data["volume"]["above_average"]:
        score += 0.05
    
    return min(score, 1.0)
```

### News Analyst (0.0 → 1.0)

```python
def calculate_news_score(data, signal_direction):
    score = 0.0
    
    # Factor 1: Relevant news count (40%)
    news_count = data["relevant_news_count"]
    score += min(news_count / 5, 1.0) * 0.40
    
    # Factor 2: Sentiment alignment (40%)
    if signal_direction == "BUY" and data["overall_sentiment"] == "positive":
        score += 0.40
    elif signal_direction == "SELL" and data["overall_sentiment"] == "negative":
        score += 0.40
    elif data["overall_sentiment"] == "neutral":
        score += 0.20
    # Else: 0 (misalignment)
    
    # Factor 3: Source quality (20%)
    high_quality_sources = sum(1 for s in data["sources"] if s in ["The Block", "CoinDesk", "Bloomberg"])
    score += min(high_quality_sources / 3, 1.0) * 0.20
    
    return score
```

### Fundamentals Analyst (0.0 → 1.0)

```python
def calculate_fundamentals_score(data):
    score = 0.0
    
    # Factor 1: Valuation (30%)
    if data["valuation"] == "undervalued":
        score += 0.30
    elif data["valuation"] == "fair":
        score += 0.15
    
    # Factor 2: Tokenomics (25%)
    if data["inflation_rate"] < 0.05:  # <5% annual
        score += 0.15
    if not data["major_unlocks_soon"]:
        score += 0.10
    
    # Factor 3: Protocol metrics trend (25%)
    if data["tvl_trend"] == "growing":
        score += 0.10
    if data["revenue_trend"] == "growing":
        score += 0.15
    
    # Factor 4: Team & investors (20%)
    if data["team_quality"] == "strong":
        score += 0.10
    if data["top_tier_vcs"]:
        score += 0.10
    
    return score
```

### Sentiment Analyst (0.0 → 1.0)

```python
def calculate_sentiment_score(data, signal_direction):
    score = 0.0
    
    # Factor 1: Social buzz alignment (35%)
    if data["social_sentiment"] == signal_direction:
        score += 0.35
    elif data["social_sentiment"] == "neutral":
        score += 0.15
    
    # Factor 2: Fear & Greed (contrarian, 25%)
    fg_index = data["fear_greed_index"]
    if signal_direction == "BUY" and fg_index < 25:  # Extreme fear
        score += 0.25
    elif signal_direction == "SELL" and fg_index > 75:  # Extreme greed
        score += 0.25
    elif 40 <= fg_index <= 60:  # Neutral
        score += 0.10
    
    # Factor 3: Polymarket odds (25%)
    if data["polymarket_trending"] == signal_direction:
        score += 0.25
    
    # Factor 4: Smart money vs retail (15%)
    if data["smart_money_aligned"]:
        score += 0.15
    
    return score
```

### Derivatives Analyst (0.0 → 1.0)

```python
def calculate_derivatives_score(data, signal_direction):
    score = 0.0
    
    # Factor 1: Funding rate (contrarian, 35%)
    funding = data["funding_rate_avg"]  # From multiple sources
    if signal_direction == "BUY" and funding < -0.0005:  # Negative funding
        score += 0.35
    elif signal_direction == "SELL" and funding > 0.0010:  # High positive
        score += 0.35
    elif abs(funding) < 0.0002:  # Neutral
        score += 0.15
    
    # Factor 2: OI + price correlation (35%)
    if data["oi_trend"] == "increasing" and data["price_trend"] == signal_direction:
        score += 0.35  # Strong trend confirmation
    elif data["oi_trend"] == "decreasing":
        score += 0.10  # Weak trend
    
    # Factor 3: Liquidation levels (30%)
    if data["liquidation_magnet"] == signal_direction:
        score += 0.30
    
    return score
```

---

## Final Confidence Calculation

```python
def calculate_final_confidence(analyst_scores, mode="full", researcher_debate=None):
    # Get weights for mode
    weights = get_mode_weights(mode)
    
    # Weighted average
    raw_confidence = sum(
        analyst_scores[analyst] * weights[analyst]
        for analyst in weights.keys()
        if analyst in analyst_scores
    )
    
    # Researcher debate adjustment (Full mode only)
    if researcher_debate and mode == "full":
        if researcher_debate["consensus"] == "aligned":
            raw_confidence += 0.05
        elif researcher_debate["consensus"] == "opposite":
            raw_confidence -= 0.10
    
    # Clamp to [0, 1]
    return max(0.0, min(raw_confidence, 1.0))
```

---

## Confidence Thresholds

| Confidence | Action | Position Size |
|---|---|---|
| **0.8 - 1.0** | Trade (strong) | 100% of base size |
| **0.6 - 0.8** | Trade (moderate) | 75% of base size |
| **0.4 - 0.6** | Trade (weak) | 50% of base size |
| **< 0.4** | Skip | 0% |

```python
def get_position_size_multiplier(confidence):
    if confidence >= 0.8:
        return 1.0
    elif confidence >= 0.6:
        return 0.75
    elif confidence >= 0.4:
        return 0.5
    else:
        return 0.0
```

---

## Self-Adjusting Weights (Monthly)

**Mục đích:** Analyst nào đúng nhiều hơn → tăng weight.

### Accuracy Tracking

Sau mỗi tháng, phân tích `signals.log` + `closed_positions`:

```python
def analyze_analyst_accuracy(month):
    # Get all closed positions from month
    positions = get_closed_positions_for_month(month)
    
    analyst_performance = {
        "technical": {"correct": 0, "total": 0},
        "fundamentals": {"correct": 0, "total": 0},
        "news": {"correct": 0, "total": 0},
        "sentiment": {"correct": 0, "total": 0},
        "derivatives": {"correct": 0, "total": 0}
    }
    
    for position in positions:
        signal = get_signal_for_position(position["id"])
        outcome = "win" if position["realized_pnl"] > 0 else "loss"
        
        # Check each analyst's sub-signal
        for analyst, sub_data in signal["analyst_details"].items():
            analyst_performance[analyst]["total"] += 1
            
            # Analyst's individual signal matched outcome?
            if (sub_data["signal"] == signal["signal"] and outcome == "win") or \
               (sub_data["signal"] != signal["signal"] and outcome == "loss"):
                analyst_performance[analyst]["correct"] += 1
    
    # Calculate accuracy
    for analyst in analyst_performance:
        total = analyst_performance[analyst]["total"]
        if total > 0:
            accuracy = analyst_performance[analyst]["correct"] / total
            analyst_performance[analyst]["accuracy"] = accuracy
    
    return analyst_performance
```

### Weight Adjustment

```python
def adjust_weights(current_weights, analyst_performance):
    """Adjust weights dựa trên accuracy"""
    new_weights = current_weights.copy()
    
    # Calculate overall average accuracy
    avg_accuracy = sum(p["accuracy"] for p in analyst_performance.values() if p["total"] > 0) / len(analyst_performance)
    
    for analyst, perf in analyst_performance.items():
        if perf["total"] < 10:  # Chưa đủ sample size
            continue
        
        accuracy = perf["accuracy"]
        
        # Adjust ±5%
        if accuracy > avg_accuracy + 0.05:
            new_weights[analyst] += 0.05
        elif accuracy < avg_accuracy - 0.05:
            new_weights[analyst] -= 0.05
    
    # Normalize to sum = 1.0
    total = sum(new_weights.values())
    new_weights = {k: v / total for k, v in new_weights.items()}
    
    # Constraint: Technical luôn ≥ 50%
    if new_weights["technical"] < 0.50:
        diff = 0.50 - new_weights["technical"]
        new_weights["technical"] = 0.50
        # Distribute diff across others
        for k in new_weights:
            if k != "technical":
                new_weights[k] -= diff / (len(new_weights) - 1)
    
    return new_weights
```

### Approval Workflow

```python
def generate_weight_adjustment_proposal():
    """Tạo proposal gửi Julius"""
    performance = analyze_analyst_accuracy(last_month)
    current_weights = load_weights("config/confidence_weights.yaml")
    proposed_weights = adjust_weights(current_weights, performance)
    
    proposal = f"""
📊 Monthly Weight Adjustment — {last_month}

Analyst Performance:
  Technical: {performance['technical']['accuracy']:.1%} ({performance['technical']['correct']}/{performance['technical']['total']})
  Fundamentals: {performance['fundamentals']['accuracy']:.1%}
  News: {performance['news']['accuracy']:.1%}
  Sentiment: {performance['sentiment']['accuracy']:.1%}
  Derivatives: {performance['derivatives']['accuracy']:.1%}

Current Weights:
{format_weights(current_weights)}

Proposed Weights:
{format_weights(proposed_weights)}

Changes:
{format_weight_changes(current_weights, proposed_weights)}

Approve? (Yes/No)
"""
    
    # Save to tasks/inbox
    save_proposal(proposal)
    notify_julius(proposal)
```

Julius reply "Yes" → apply changes. "No" → giữ nguyên weights.

---

## Example Calculation

**Scenario:** Full mode, BTC BUY signal

```
Analyst Scores:
  Technical:     0.82 × 0.60 = 0.492
  News:          0.70 × 0.10 = 0.070
  Fundamentals:  0.65 × 0.10 = 0.065
  Sentiment:     0.55 × 0.05 = 0.028
  Derivatives:   0.78 × 0.15 = 0.117
                              ------
Raw confidence:                0.772

Researcher Debate: Bull thắng rõ → +0.05
                                   ------
Final confidence:                  0.822 → Strong signal
```

**Action:** Trade với 100% base position size.

---

## Next

- [09. Position Sizing](09-position-sizing.md) — Risk-based sizing, SL/TP strategies
