---
name: strategy-designer
description: >
  Convert an edge idea into a concrete strategy playbook for trading-agents: state, setup, trigger, action, sizing, exit, invalidation, no-trade conditions, and review metrics.
metadata:
  version: "1.0.0"
  author: "Hermes Agent, adapted for trading-agents"
  trigger: "Project-local trading-agents workflow"
  output: "Actionable review, plan, checklist, or artifact for the trading-agents project"
---
# Strategy Designer

## Source Adaptation

Adapted for `ai-labs/projects/trading-agents` from:
- tradermonty/claude-trading-skills: edge-concept-synthesizer, edge-strategy-designer
- Starchild official-skills: trading-strategy
- local skill: trading-system-design

This is a project-local agent skill. It is not trading advice, not an execution policy, and not a substitute for risk controls. Use it to structure analysis, design, review, and implementation work inside the repo.

## When to Use

Use when Julius or an agent has an observation, thesis, indicator cluster, replay anomaly, or market intuition and needs to turn it into a concrete strategy candidate.

Do **not** use this to create generic BUY/SELL/HOLD rules. A valid output must explain what edge is being expressed, in what state, through what action, and with what invalidation.

## Required Inputs

- Edge idea or observation.
- Target market / symbol universe.
- Intended timeframe.
- Available data features.
- Constraints: max risk, allowed direction, execution mode, slippage/cost assumptions.
- Existing related code paths if implementation is planned.

## Design Workflow

1. **Name the edge**
   - One sentence: why should this state-action pair have positive expectancy?
   - State whether the edge is trend continuation, mean reversion, breakout, volatility avoidance, liquidity sweep, catalyst drift, or another family.

2. **Define market state**
   - Regime: `trend_up`, `trend_down`, `ranging`, `volatile`, `risk_off`, or project-specific state.
   - Technical state: trend, momentum, volatility, volume, liquidity, funding/OI if available.
   - Context: market-wide risk, correlation, news/catalyst, sentiment, unlocks if relevant.

3. **Separate setup from trigger**
   - Setup = condition that earns attention.
   - Trigger = condition that authorizes action.
   - A setup without a trigger is a watchlist item, not a trade.

4. **Define action contract**
   - Allowed actions: `long`, `short`, `reduce`, `exit`, `hold`, `skip`.
   - Entry style: breakout, pullback, reclaim, breakdown, fade, confirmation close, staged entry.
   - Time horizon and expected hold window.

5. **Define sizing logic**
   - Start from `size ∝ edge / variance`.
   - Reduce size for volatility, drawdown, correlation, weak data quality, regime mismatch, and high execution cost.
   - Include hard caps and no-trade conditions.

6. **Define exit and invalidation**
   - Stop / invalidation level or condition.
   - Profit-taking logic.
   - Time stop.
   - Thesis invalidation distinct from execution stop.

7. **Define review metrics**
   - Expectancy, win rate, average win/loss, max drawdown, hold time, side bias.
   - Regime-conditioned performance.
   - False positive / missed opportunity tags.

## Output Template

```yaml
strategy_id: kebab-case-name
family: trend_following | mean_reversion | breakout | volatility_skip | other
edge_thesis: "..."
timeframe: "..."
market_universe: ["BTC", "ETH", "..."]
state:
  required_regime: "..."
  technical_conditions: []
  context_filters: []
setup:
  description: "..."
  required_features: []
trigger:
  description: "..."
  confirmation_rules: []
action:
  primary: long | short | skip | reduce | exit
  entry_logic: "..."
sizing:
  base_risk_unit: "..."
  scale_up_when: []
  scale_down_when: []
  hard_caps: []
exit:
  stop_or_invalidation: "..."
  take_profit: "..."
  time_stop: "..."
no_trade_conditions: []
review:
  metrics: []
  attribution_tags: []
implementation_notes:
  pure_strategy_module: "strategies/<name>.py"
  tests: []
```

## Quality Gate

A strategy draft is incomplete if it lacks any of:
- explicit state/regime;
- trigger separate from setup;
- invalidation;
- sizing constraints;
- no-trade condition;
- review metrics.
