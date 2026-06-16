---
name: trading-plan
description: >
  Create or review a disciplined trading plan for trading-agents covering objectives, markets, allowed strategy families, risk limits, entry/exit rules, daily loss limits, psychology/process, and performance review.
metadata:
  version: "1.0.0"
  author: "Hermes Agent, adapted for trading-agents"
  trigger: "Project-local trading-agents workflow"
  output: "Actionable review, plan, checklist, or artifact for the trading-agents project"
---
# Trading Plan

## Source Adaptation

Adapted for `ai-labs/projects/trading-agents` from:
- jamesrochabrun/skills: trading-plan-generator
- Starchild official-skills: trading-strategy
- local skill: trading-system-design

This is a project-local agent skill. It is not trading advice, not an execution policy, and not a substitute for risk controls. Use it to structure analysis, design, review, and implementation work inside the repo.

## When to Use

Use when setting system-level operating rules or reviewing whether the project has a coherent trading plan beyond individual strategies.

## Trading Plan Sections

1. **Objective**
   - What is optimized: learning, Sharpe, drawdown control, total return, consistency, or market research?
   - What is explicitly not optimized?

2. **Markets and universe**
   - Assets allowed.
   - Liquidity requirements.
   - Excluded assets.
   - Data requirements.

3. **Strategy families**
   - Trend following.
   - Mean reversion.
   - Breakout.
   - Volatility skip / risk-off.
   - Future families with acceptance criteria.

4. **Risk limits**
   - Max risk per trade.
   - Max daily/weekly drawdown.
   - Max correlated exposure.
   - Max leverage if any.
   - Halt conditions.

5. **Execution assumptions**
   - Paper/demo/live status.
   - Fees, slippage, spread, funding.
   - Order timing.

6. **Review cadence**
   - Per-trade/signal postmortem.
   - Weekly strategy attribution.
   - Monthly policy update.
   - Conditions for retiring a strategy.

## Output Template

```yaml
plan_name: "..."
objective: "..."
markets: []
allowed_strategy_families: []
risk_limits:
  per_trade: "..."
  daily_loss: "..."
  weekly_loss: "..."
  max_correlation: "..."
execution_assumptions: []
review_cadence: []
halt_conditions: []
```

## Common Pitfalls

- System has strategy modules but no portfolio-level risk plan.
- Strategy wins in isolation but violates global exposure cap.
- Daily loss limit exists in docs but not in decision flow.
- Plan cannot say “do nothing.”
