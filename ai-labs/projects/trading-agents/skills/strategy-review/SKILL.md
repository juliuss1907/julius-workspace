---
name: strategy-review
description: >
  Critically review a trading-agents strategy draft for edge plausibility, overfitting risk, sample size adequacy, execution realism, sizing, exits, invalidation, and repo boundary safety.
metadata:
  version: "1.0.0"
  author: "Hermes Agent, adapted for trading-agents"
  trigger: "Project-local trading-agents workflow"
  output: "Actionable review, plan, checklist, or artifact for the trading-agents project"
---
# Strategy Review

## Source Adaptation

Adapted for `ai-labs/projects/trading-agents` from:
- tradermonty/claude-trading-skills: edge-strategy-reviewer
- jamesrochabrun/skills: trading-plan-generator
- local skill: trading-system-design

This is a project-local agent skill. It is not trading advice, not an execution policy, and not a substitute for risk controls. Use it to structure analysis, design, review, and implementation work inside the repo.

## When to Use

Use before implementing a strategy, after OpenCode writes a strategy module, or when reviewing a replay/backtest result that claims a strategy has edge.

## Review Criteria

Score each criterion 0-2:

- **C1 Edge thesis:** clear causal reason for edge, not just pattern matching.
- **C2 State specificity:** strategy only acts in states where thesis should work.
- **C3 Setup/trigger separation:** trigger is actionable and not hindsight-dependent.
- **C4 Invalidation:** thesis and trade invalidation are explicit.
- **C5 Sizing realism:** risk scales with edge/variance and has hard caps.
- **C6 No-trade logic:** strategy can refuse bad conditions.
- **C7 Data quality:** required features are available without lookahead.
- **C8 Execution realism:** slippage, fees, latency, liquidity, and order type assumptions are acknowledged.
- **C9 Robustness:** not overfit to one symbol, regime, or parameter island.
- **C10 Boundary purity:** no imports from Telegram, runtime execution, broker/order modules, or mutable paper-position state.

## Verdict

- `PASS`: total >= 16 and no critical failure.
- `REVISE`: total 10-15 or one fixable critical gap.
- `REJECT`: total < 10, no edge thesis, no invalidation, lookahead bias, or execution leakage.

## Review Output

```yaml
strategy_id: "..."
verdict: PASS | REVISE | REJECT
score: 0-20
critical_failures: []
strengths: []
required_revisions: []
overfitting_risks: []
execution_risks: []
boundary_risks: []
recommended_tests: []
```

## Boundary Checklist

A strategy module should be pure:
- accepts state/context objects;
- returns `StrategySignal` / `StrategyDecision`;
- does not place orders;
- does not send Telegram messages;
- does not mutate runtime state;
- does not read private `.env`, databases, or session logs.

## Common Failure Modes

- Indicator stack masquerading as strategy.
- Strategy only works because of hindsight parameter selection.
- Entry exists but no exit/invalidation.
- Stop exists but sizing ignores stop distance.
- Replay report has global metrics but no strategy-level attribution.
