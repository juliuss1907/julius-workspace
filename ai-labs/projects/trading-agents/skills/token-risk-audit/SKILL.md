---
name: token-risk-audit
description: >
  Audit crypto token safety before treating a token as tradable: honeypot, tax, contract control, liquidity, ownership, fake token risk, and unsupported-chain limitations.
metadata:
  version: "1.0.0"
  author: "Hermes Agent, adapted for trading-agents"
  trigger: "Project-local trading-agents workflow"
  output: "Actionable review, plan, checklist, or artifact for the trading-agents project"
---
# Token Risk Audit

## Source Adaptation

Adapted for `ai-labs/projects/trading-agents` from:
- binance/binance-skills-hub: query-token-audit
- Starchild official-skills: birdeye, tokenomist concepts

This is a project-local agent skill. It is not trading advice, not an execution policy, and not a substitute for risk controls. Use it to structure analysis, design, review, and implementation work inside the repo.

## When to Use

Use before allowing a strategy to consider a small-cap/on-chain token, before adding a token to a universe, or when a replay uses token data from a risky market.

## Scope

This skill does not decide whether an asset is a good investment. It only asks whether the token is safe and liquid enough to be considered by the system.

## Risk Categories

- Contract risk: owner privileges, mintability, blacklist/whitelist, proxy upgrades.
- Trading risk: honeypot, buy/sell tax, transfer tax, cooldowns, max wallet/tx.
- Liquidity risk: shallow pool, locked/unlocked LP, large holder concentration.
- Identity risk: fake contract, symbol collision, unofficial social links.
- Data risk: unsupported chain, stale audit, missing result.
- Unlock/emission risk: cliffs, daily emissions, team/investor unlocks.

## Block Conditions

Block a token from tradable universe if:
- honeypot or cannot sell;
- critical ownership/mint/blacklist risk without mitigation;
- buy/sell tax is extreme or dynamic;
- liquidity too shallow for planned size;
- audit unavailable for a high-risk token;
- contract address cannot be verified.

## Output Template

```yaml
token: "..."
chain: "..."
contract: "..."
audit_status: supported | unsupported | missing | stale
risk_level: low | medium | high | critical
block_from_trading: true | false
risk_flags: []
liquidity_notes: []
identity_checks: []
required_followups: []
```

## Integration Note

This belongs upstream of strategy selection as a universe filter. It must not produce BUY/SELL recommendations.
