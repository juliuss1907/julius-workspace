# 12. Fine-tuning — Agent Self-Learning

## Tổng quan

Hệ thống fine-tune agents định kỳ để cải thiện khả năng phân tích dựa trên:
- Trading knowledge base (PDFs, articles, books)
- Historical analysis results (đúng/sai)
- Julius feedback

**Model fine-tune:** DeepSeek V4 Flash

**Scope:** Tất cả analysts (Technical, Fundamentals, News, Sentiment, Derivatives)

**Frequency:** 1 tháng/lần

---

## Knowledge Base Structure

```
ai-labs/resource/trading-knowledge/
├── technical-analysis/
│   ├── japanese-candlestick-patterns.pdf
│   ├── elliott-wave-theory.pdf
│   ├── volume-spread-analysis.pdf
│   ├── wyckoff-method.pdf
│   ├── ichimoku-cloud.pdf
│   └── chart-patterns-encyclopedia.pdf
├── strategies/
│   ├── momentum-trading.pdf
│   ├── mean-reversion.pdf
│   ├── breakout-strategies.pdf
│   ├── trend-following.pdf
│   └── crypto-specific-patterns.md
├── risk-management/
│   ├── position-sizing-methods.pdf
│   ├── kelly-criterion.pdf
│   └── van-tharp-position-sizing.pdf
├── market-psychology/
│   ├── behavioral-finance.pdf
│   ├── trading-in-the-zone.pdf
│   └── market-cycles.pdf
├── derivatives/
│   ├── funding-rate-strategies.md
│   ├── open-interest-analysis.md
│   └── liquidation-heatmap-trading.md
└── crypto-specific/
    ├── on-chain-analysis.pdf
    ├── tokenomics-fundamentals.pdf
    └── defi-mechanics.pdf
```

**Note:** Julius sẽ tìm và bổ sung tài liệu sau (skill chưa có sẵn tài liệu).

---

## Fine-tuning Pipeline

### Step 1: Data Collection

Thu thập 3 loại training data:

#### A. Knowledge Base Documents

```python
def extract_knowledge_data():
    """Extract content từ PDFs, markdown files"""
    knowledge_data = []
    
    for category in ["technical-analysis", "strategies", "risk-management", ...]:
        files = glob.glob(f"ai-labs/resource/trading-knowledge/{category}/*")
        
        for file in files:
            if file.endswith(".pdf"):
                content = extract_pdf_text(file)
            elif file.endswith(".md"):
                content = read_markdown(file)
            else:
                continue
            
            # Chunk content (max 2000 tokens per chunk)
            chunks = chunk_text(content, max_tokens=2000)
            
            for chunk in chunks:
                knowledge_data.append({
                    "type": "knowledge",
                    "category": category,
                    "source": file,
                    "content": chunk
                })
    
    return knowledge_data
```

#### B. Historical Analysis Results

```python
def extract_historical_analysis():
    """Lấy reports + outcomes từ tháng qua"""
    training_examples = []
    
    # Get all signals từ tháng trước
    signals = get_signals_for_period(last_month_start, last_month_end)
    
    for signal in signals:
        # Get associated paper trade outcome
        position = get_paper_position(signal["paper_position_id"])
        if not position or position["exit_time"] is None:
            continue  # Trade chưa close
        
        # Get the analysis report
        report_file = f"reports/{signal['mode']}/{signal['date']}-{signal['coin']}.md"
        if not os.path.exists(report_file):
            continue
        
        with open(report_file) as f:
            report_content = f.read()
        
        # Outcome
        outcome = "correct" if position["realized_pnl"] > 0 else "incorrect"
        
        training_examples.append({
            "type": "historical",
            "input": format_analyst_input(signal),
            "output": format_analyst_output(signal, report_content),
            "outcome": outcome,
            "pnl_pct": position["realized_pnl_pct"]
        })
    
    return training_examples
```

#### C. Julius Feedback

```python
def extract_julius_feedback():
    """Lấy feedback từ Julius qua Telegram logs"""
    feedback_data = []
    
    # Parse Telegram logs cho feedback messages
    feedback_logs = parse_telegram_feedback_logs()
    
    for fb in feedback_logs:
        # Match feedback to signal
        signal = get_signal_by_id(fb["signal_id"])
        
        feedback_data.append({
            "type": "feedback",
            "signal": signal,
            "julius_action": fb["action"],  # 'executed', 'skipped'
            "julius_notes": fb["notes"],
            "outcome": fb.get("outcome", "unknown")
        })
    
    return feedback_data
```

### Step 2: Format Training Data

Format theo OpenAI fine-tuning format:

```python
def format_training_examples(knowledge_data, historical_data, feedback_data):
    """Format thành conversational format"""
    examples = []
    
    # Knowledge examples
    for knowledge in knowledge_data:
        examples.append({
            "messages": [
                {"role": "system", "content": "You are an expert crypto trading analyst."},
                {"role": "user", "content": f"Explain the concept from {knowledge['category']}: [section topic]"},
                {"role": "assistant", "content": knowledge["content"]}
            ]
        })
    
    # Historical examples (positive examples — agent đúng)
    for hist in [h for h in historical_data if h["outcome"] == "correct"]:
        examples.append({
            "messages": [
                {"role": "system", "content": "You are a Technical Analyst..."},
                {"role": "user", "content": hist["input"]},
                {"role": "assistant", "content": hist["output"]}
            ]
        })
    
    # Negative examples (agent sai — học để tránh)
    for hist in [h for h in historical_data if h["outcome"] == "incorrect"]:
        # Generate corrected example
        corrected_output = generate_corrected_analysis(hist)
        examples.append({
            "messages": [
                {"role": "system", "content": "You are a Technical Analyst..."},
                {"role": "user", "content": hist["input"]},
                {"role": "assistant", "content": corrected_output}
            ]
        })
    
    # Julius feedback
    for fb in feedback_data:
        if fb["julius_action"] == "skipped" and fb["julius_notes"]:
            examples.append({
                "messages": [
                    {"role": "system", "content": "..."},
                    {"role": "user", "content": format_signal_input(fb["signal"])},
                    {"role": "assistant", "content": f"Note: This signal should be flagged for caution. Reason: {fb['julius_notes']}"}
                ]
            })
    
    return examples
```

### Step 3: Train per Analyst

```python
def fine_tune_analyst(analyst_name, training_data):
    """Fine-tune từng analyst riêng biệt"""
    
    # Filter training data cho analyst này
    analyst_data = filter_data_for_analyst(training_data, analyst_name)
    
    # Split train/validation
    train_data, val_data = train_test_split(analyst_data, test_size=0.1)
    
    # Save in JSONL format
    train_file = f"fine-tuning/{analyst_name}_train.jsonl"
    val_file = f"fine-tuning/{analyst_name}_val.jsonl"
    
    save_jsonl(train_data, train_file)
    save_jsonl(val_data, val_file)
    
    # Submit fine-tuning job
    job = openai_client.fine_tuning.jobs.create(
        training_file=upload_file(train_file),
        validation_file=upload_file(val_file),
        model="deepseek-v4-flash",
        suffix=f"trading-{analyst_name}-{datetime.now().strftime('%Y%m')}"
    )
    
    logger.info(f"Fine-tuning job submitted for {analyst_name}: {job.id}")
    return job
```

### Step 4: A/B Testing

Trước khi deploy, A/B test model mới vs base model:

```python
def ab_test_models(new_model_id, base_model_id, test_signals):
    """Run cả 2 models trên cùng test set"""
    results = {"new": [], "base": []}
    
    for signal_input in test_signals:
        # Run new model
        new_output = run_analyst(new_model_id, signal_input)
        results["new"].append(evaluate_output(new_output, signal_input["expected"]))
        
        # Run base model
        base_output = run_analyst(base_model_id, signal_input)
        results["base"].append(evaluate_output(base_output, signal_input["expected"]))
    
    # Calculate metrics
    metrics = {
        "new_accuracy": sum(results["new"]) / len(results["new"]),
        "base_accuracy": sum(results["base"]) / len(results["base"])
    }
    
    return metrics
```

### Step 5: Deploy or Rollback

```python
def deploy_or_rollback(metrics, analyst_name):
    """Deploy nếu performance cải thiện"""
    improvement = metrics["new_accuracy"] - metrics["base_accuracy"]
    
    if improvement >= 0.05:  # ≥5% improvement
        # Deploy
        update_active_model(analyst_name, new_model_id)
        notify_julius(f"""
✅ {analyst_name} model upgraded

Old accuracy: {metrics['base_accuracy']:.1%}
New accuracy: {metrics['new_accuracy']:.1%}
Improvement: +{improvement:.1%}

New model active for next analyses.
        """)
        return "deployed"
    
    elif improvement < -0.02:  # Performance giảm >2%
        # Rollback
        notify_julius(f"""
⚠️ {analyst_name} fine-tuning failed

New model performed worse:
  Base: {metrics['base_accuracy']:.1%}
  New: {metrics['new_accuracy']:.1%}

Sticking with base model.
        """)
        return "rejected"
    
    else:
        # Marginal change — stay với base
        return "no_change"
```

---

## Monthly Schedule

```
Day 1, 04:00 — Data Collection (1 hour)
Day 1, 05:00 — Data Formatting (30 min)
Day 1, 05:30 — Submit Fine-tuning Jobs (parallel cho 5 analysts)
Day 2-3 — Wait for jobs to complete
Day 3, 09:00 — A/B Testing (2 hours)
Day 3, 11:00 — Deploy Decision + Notification

Total: ~2 days
```

### Cron Setup

```bash
# crontab entry
0 4 1 * * cd /path/to/trading-agents && python scripts/run_monthly_finetuning.py
```

---

## Cost Estimation

DeepSeek V4 Flash fine-tuning costs (estimate):

| Phase | Cost |
|---|---|
| Training data preparation | $0 (compute only) |
| Fine-tuning job (per analyst) | ~$5-10 |
| 5 analysts | ~$25-50 |
| A/B testing | ~$5 |
| **Total monthly** | **~$30-55** |

---

## Rollback History

Track tất cả model versions để rollback nếu cần:

```
fine-tuning/
├── models/
│   ├── technical-2026-06.json    # Model metadata
│   ├── technical-2026-07.json
│   ├── technical-2026-08.json
│   └── ...
└── active_models.yaml            # Current active models per analyst
```

```yaml
# active_models.yaml
analysts:
  technical: "ft:deepseek-v4-flash:trading-technical-202606"
  fundamentals: "ft:deepseek-v4-flash:trading-fundamentals-202606"
  news: "ft:deepseek-v4-flash:trading-news-202606"
  sentiment: "ft:deepseek-v4-flash:trading-sentiment-202606"
  derivatives: "ft:deepseek-v4-flash:trading-derivatives-202606"

last_updated: "2026-06-03T11:00:00+07:00"
```

### Manual Rollback

Julius có thể rollback bất cứ lúc nào:

```
Julius: "Rollback technical analyst"

Bot:
🔄 Available Versions — Technical Analyst

1. trading-technical-202606 (current)
   Deployed: 2026-06-03
   Accuracy: 74%

2. trading-technical-202605
   Deployed: 2026-05-03
   Accuracy: 71%

3. base (DeepSeek V4 Flash)
   No fine-tuning
   Accuracy: 65%

Reply: "rollback to 2" to use May version
```

---

## Adding New Knowledge

Khi Julius có tài liệu mới:

```bash
# 1. Add document to knowledge base
cp ~/Downloads/wyckoff-method.pdf ai-labs/resource/trading-knowledge/technical-analysis/

# 2. Trigger immediate re-training (optional, không cần đợi tháng)
python scripts/run_finetuning.py --analyst technical --force
```

Hoặc đợi tháng sau, system tự pickup.

---

## Quality Metrics

Track để evaluate fine-tuning quality:

```python
def evaluate_finetuning_quality(analyst_name, period="30d"):
    """Đo chất lượng analyst sau fine-tune"""
    
    # Get all analyses từ analyst trong period
    analyses = get_analyses_by_analyst(analyst_name, period)
    
    metrics = {
        "total_analyses": len(analyses),
        "agreed_with_outcome": 0,
        "confidence_calibration": 0,  # High confidence → đúng nhiều?
        "consistency": 0  # Cùng input → cùng output?
    }
    
    for analysis in analyses:
        outcome = get_outcome_for_analysis(analysis)
        
        if (analysis["signal"] == "BUY" and outcome["pnl"] > 0) or \
           (analysis["signal"] == "SELL" and outcome["pnl"] < 0):
            metrics["agreed_with_outcome"] += 1
    
    metrics["accuracy"] = metrics["agreed_with_outcome"] / metrics["total_analyses"]
    
    return metrics
```

---

## Next

- [13. Implementation Roadmap](13-implementation-roadmap.md) — Phases với breakdown chi tiết
