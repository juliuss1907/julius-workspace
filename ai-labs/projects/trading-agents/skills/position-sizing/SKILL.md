---
name: position-sizing
description: >
  Review and design position sizing rules for trading-agents using fixed-fractional, volatility-adjusted, drawdown-aware, correlation-aware, and fractional-Kelly concepts.
metadata:
  version: "1.0.0"
  author: "Hermes Agent, adapted for trading-agents"
  trigger: "Project-local trading-agents workflow"
  output: "Actionable review, plan, checklist, or artifact for the trading-agents project"
---
# Position Sizing

## Source Adaptation

Adapted for `ai-labs/projects/trading-agents` from:
- tradermonty/claude-trading-skills: position-sizer
- jamesrochabrun/skills: trading-plan-generator
- local skill: trading-system-design

This is a project-local agent skill. It is not trading advice, not an execution policy, and not a substitute for risk controls. Use it to structure analysis, design, review, and implementation work inside the repo.

## When to Use

Use when implementing or reviewing the `Sizing` part of a strategy contract.

## Core Formula

```text
size ∝ edge / variance
```

Sizing is part of the decision, not an afterthought.

## Sizing Inputs

- Account or simulated equity.
- Max risk per trade.
- Stop/invalidation distance.
- Volatility / ATR / realized variance.
- Strategy confidence and historical expectancy.
- Correlation with existing exposure.
- Current drawdown and loss limits.
- Liquidity and slippage constraints.

## Methods

1. **Fixed fractional**
   - Risk a fixed fraction of equity per trade.
   - Good default when strategy history is limited.

2. **Volatility adjusted**
   - Reduce size when ATR/realized vol rises.
   - Prevents “same dollars, wildly different risk.”

3. **Drawdown aware**
   - Reduce risk unit during drawdown.
   - Hard halt if max drawdown or daily loss reached.

4. **Correlation aware**
   - Penalize new positions that duplicate existing risk.
   - Crypto majors often correlate heavily during stress.

5. **Fractional Kelly**
   - Only if robust expectancy/win-loss estimates exist.
   - Use fractional Kelly, never full Kelly.

## Output Template

```yaml
strategy_id: "..."
base_risk_unit: "..."
stop_distance: "..."
volatility_adjustment: "..."
correlation_adjustment: "..."
drawdown_adjustment: "..."
final_size: "..."
max_loss_if_stopped: "..."
reasons: []
reject_if: []
```

## Red Flags

- Same size across all regimes and volatility states.
- No cap for correlated positions.
- Stop distance changes but position size does not.
- Kelly used with tiny sample size or non-stationary returns.
- Sizing ignores funding/slippage/liquidity.
