---
name: regime-review
description: >
  Review or design market regime classification for trading-agents, mapping crypto market state into enabled/disabled strategy families and exposure posture.
metadata:
  version: "1.0.0"
  author: "Hermes Agent, adapted for trading-agents"
  trigger: "Project-local trading-agents workflow"
  output: "Actionable review, plan, checklist, or artifact for the trading-agents project"
---
# Regime Review

## Source Adaptation

Adapted for `ai-labs/projects/trading-agents` from:
- tradermonty/claude-trading-skills: macro-regime-detector, market-breadth-analyzer, uptrend-analyzer
- local skill: trading-system-design

This is a project-local agent skill. It is not trading advice, not an execution policy, and not a substitute for risk controls. Use it to structure analysis, design, review, and implementation work inside the repo.

## When to Use

Use when adding/refactoring `MarketState`, `TechnicalState`, `market_regime.py`, or strategy registry mappings.

## Crypto-Oriented Regime Dimensions

- Trend: up, down, range, transition.
- Volatility: compressed, normal, expanded, disorderly.
- Liquidity: deep, thin, fragmented, liquidation cascade risk.
- Participation: majors only, broad alt participation, meme rotation, risk-off concentration.
- Derivatives: funding, OI expansion/contraction, liquidation clusters.
- Macro/risk: dollar, rates, equities correlation, event risk.
- Catalyst: ETF flow, unlocks, protocol events, news shock.

## Regime Output

```yaml
market_state:
  primary_regime: trend_up | trend_down | ranging | volatile | risk_off | transition
  confidence: low | medium | high
  supporting_evidence: []
  contradicting_evidence: []
  enabled_strategy_families: []
  disabled_strategy_families: []
  exposure_posture: risk_on | selective | defensive | cash_priority | halt
  reclassification_triggers: []
```

## Mapping Guidelines

- `trend_up`: trend-following, breakout, pullback continuation may be enabled.
- `trend_down`: short continuation or cash/hedge; disable naive dip-buying unless mean-reversion has strong rules.
- `ranging`: mean reversion/range fade; disable late breakouts until confirmed.
- `volatile`: reduce size; prefer skip or explicit volatility strategy.
- `risk_off`: exposure reduction and no-trade dominate.
- `transition`: lower confidence; require stronger confirmation.

## Review Checklist

- Does the regime classifier use canonical config names?
- Are thresholds documented and testable?
- Is confidence exposed, not hidden?
- Can strategies query state without importing runtime modules?
- Are strategy mappings explicit rather than string labels in config only?
