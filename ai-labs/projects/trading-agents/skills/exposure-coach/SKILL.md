---
name: exposure-coach
description: >
  Synthesize regime, breadth, volatility, drawdown, correlation, and strategy quality into a trading-agents risk posture: exposure ceiling, new-entry permission, and risk-budget adjustments.
metadata:
  version: "1.0.0"
  author: "Hermes Agent, adapted for trading-agents"
  trigger: "Project-local trading-agents workflow"
  output: "Actionable review, plan, checklist, or artifact for the trading-agents project"
---
# Exposure Coach

## Source Adaptation

Adapted for `ai-labs/projects/trading-agents` from:
- tradermonty/claude-trading-skills: exposure-coach
- local skill: trading-system-design

This is a project-local agent skill. It is not trading advice, not an execution policy, and not a substitute for risk controls. Use it to structure analysis, design, review, and implementation work inside the repo.

## When to Use

Use before enabling new entries, after regime changes, during weekly review, or when multiple strategy signals conflict.

## Purpose

Answer: “How much risk should this system be allowed to express right now?” before asking “which symbol should it trade?”

## Inputs

- Market regime / technical state.
- Breadth or participation proxy if available.
- Volatility and drawdown state.
- Correlation among target assets.
- Strategy-level recent performance.
- Open exposure and risk budget.
- Event/catalyst risk.

## Posture Levels

- `risk_on`: normal or expanded exposure; new entries allowed if strategy passes.
- `selective`: reduced risk; only highest-quality setups.
- `defensive`: small size, fewer entries, quicker invalidation.
- `cash_priority`: no new entries except explicit hedge/exit/reduce logic.
- `halt`: no strategy action except risk reduction and diagnostics.

## Decision Rules

Increase exposure only when:
- regime matches active strategy families;
- volatility is within planned bounds;
- strategy attribution shows recent decisions are working;
- correlation does not concentrate risk;
- drawdown limits are respected.

Decrease exposure when:
- regime mismatch rises;
- strategy false positives cluster;
- volatility/liquidity deteriorates;
- open positions are highly correlated;
- drawdown or daily/weekly loss limits are near breach.

## Output Template

```yaml
posture: risk_on | selective | defensive | cash_priority | halt
net_exposure_ceiling: "..."
per_trade_risk_unit: "..."
new_entries_allowed: true | false
allowed_strategy_families: []
disabled_strategy_families: []
size_adjustments: []
reasons: []
recheck_triggers: []
```

## Integration Note

This skill informs `StrategyPolicy` and sizing constraints. It must not directly place orders or override strategy invalidation.
