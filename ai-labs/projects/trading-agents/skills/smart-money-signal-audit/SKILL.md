---
name: smart-money-signal-audit
description: >
  Treat on-chain or whale smart-money signals as noisy inputs, not copy-trade commands; audit recency, exit rate, concentration, liquidity, regime fit, and strategy compatibility.
metadata:
  version: "1.0.0"
  author: "Hermes Agent, adapted for trading-agents"
  trigger: "Project-local trading-agents workflow"
  output: "Actionable review, plan, checklist, or artifact for the trading-agents project"
---
# Smart Money Signal Audit

## Source Adaptation

Adapted for `ai-labs/projects/trading-agents` from:
- binance/binance-skills-hub: trading-signal
- Starchild official-skills: birdeye, debank, coinglass concepts

This is a project-local agent skill. It is not trading advice, not an execution policy, and not a substitute for risk controls. Use it to structure analysis, design, review, and implementation work inside the repo.

## When to Use

Use when a data source surfaces whale/smart-money buys/sells, wallet flows, inflows, or copy-trade-looking signals.

## Core Rule

Smart-money activity is **context**, not a strategy. Never convert it directly into an order. It must pass through state, setup, trigger, risk, and invalidation.

## Audit Questions

- Recency: is the signal still active or stale?
- Exit rate: has the tracked cohort already exited?
- Concentration: one wallet or many independent wallets?
- Liquidity: can the system enter/exit without moving the market?
- Token risk: honeypot/tax/contract risk checked if on-chain token.
- Regime fit: does this signal align with current market state?
- Strategy fit: which strategy family can validly consume this signal?
- Invalidation: what would prove the smart-money read wrong?

## Output Template

```yaml
signal_source: "..."
symbol_or_token: "..."
signal_type: buy | sell | inflow | outflow | accumulation | distribution
status: active | stale | completed | unknown
quality:
  recency: low | medium | high
  cohort_strength: low | medium | high
  exit_risk: low | medium | high
  liquidity_fit: low | medium | high
strategy_compatibility:
  valid_input_for: []
  not_valid_for: []
trade_decision: never_direct
required_followups: []
```

## Red Flags

- High exit rate: opportunity likely already harvested.
- Thin liquidity: signal is not executable at expected price.
- Wallet cluster may be coordinated or sybil-like.
- Signal conflicts with market regime.
- No independent trigger beyond “wallet bought.”
