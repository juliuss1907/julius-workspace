---
name: backtest-analysis
description: >
  Analyze trading-agents replay/backtest outputs with robustness-first methodology: bias checks, sample size, costs, regime attribution, strategy attribution, drawdown, expectancy, and failure modes.
metadata:
  version: "1.0.0"
  author: "Hermes Agent, adapted for trading-agents"
  trigger: "Project-local trading-agents workflow"
  output: "Actionable review, plan, checklist, or artifact for the trading-agents project"
---
# Backtest Analysis

## Source Adaptation

Adapted for `ai-labs/projects/trading-agents` from:
- tradermonty/claude-trading-skills: backtest-expert
- Starchild official-skills: backtest

This is a project-local agent skill. It is not trading advice, not an execution policy, and not a substitute for risk controls. Use it to structure analysis, design, review, and implementation work inside the repo.

## When to Use

Use when reviewing any replay/backtest/calibration result before trusting it, changing parameters, or promoting a strategy.

## Philosophy

The goal is not to find the prettiest equity curve. The goal is to find what breaks the least after friction, bad regimes, parameter perturbation, and realistic execution assumptions.

## Required Checks

1. **Bias checks**
   - No lookahead data.
   - No survivorship-only universe unless declared.
   - No future candle in trigger/exit.
   - No parameter choice made after looking at final results without walk-forward validation.

2. **Friction checks**
   - Fees, spread, slippage.
   - Funding if perps.
   - Liquidity and order-size feasibility.
   - Latency / close confirmation assumptions.

3. **Sample checks**
   - Number of trades per strategy.
   - Symbol diversity.
   - Regime diversity.
   - Side diversity long/short.
   - Outlier dependence: performance with top 1-5 trades removed.

4. **Attribution checks**
   - Metrics by strategy, not only global BUY/SELL/HOLD.
   - Metrics by regime.
   - Metrics by symbol and side.
   - Metrics by volatility bucket.

5. **Robustness checks**
   - Parameter sensitivity.
   - Walk-forward or train/test split.
   - Stress slippage/costs.
   - Alternative start/end dates.

## Minimum Metrics

- Total trades.
- Win rate.
- Average win / average loss.
- Expectancy per trade.
- Profit factor.
- Max drawdown.
- Sharpe / Sortino if applicable.
- Exposure time.
- Average and median hold time.
- Worst trade / best trade dependence.
- Performance by strategy/regime/symbol/side.

## Verdict Output

```yaml
backtest_id: "..."
trust_level: low | medium | high
main_result: "..."
fragility_flags: []
robustness_evidence: []
strategy_attribution:
  missing: true | false
  notes: []
required_next_tests: []
do_not_promote_until: []
```

## Red Flags

- Great global performance but one strategy/symbol created all returns.
- High win rate with fat-tail losses.
- No slippage/funding/fee modeling.
- Parameter cliff: one value works, neighbors fail.
- Backtest uses signal close and entry close on same candle without realistic execution rule.
