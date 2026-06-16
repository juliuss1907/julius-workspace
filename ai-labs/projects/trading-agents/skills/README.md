# Trading Agents Project Skills

Project-local skills adapted from selected public trading-skill repositories for `ai-labs/projects/trading-agents`.

These skills are **agent/operator workflows**, not runtime strategy code and not financial advice.

## Skill Index

- `thesis-builder` — turn a market worldview/hunch into evidence, counter-evidence, scenarios, and next step.
- `strategy-designer` — convert an edge idea into a strategy playbook contract.
- `strategy-review` — quality gate for strategy plausibility, overfitting, sizing, exits, and boundary purity.
- `market-structure` — price-action/structure lens with HTF context, levels, liquidity, trigger, stop, targets.
- `regime-review` — map market state into enabled/disabled strategy families and exposure posture.
- `exposure-coach` — synthesize regime/risk into exposure ceiling and new-entry permission.
- `position-sizing` — design/review sizing rules using edge/variance, volatility, drawdown, and correlation.
- `backtest-analysis` — robustness-first review of replay/backtest results and strategy attribution.
- `signal-postmortem` — classify closed/expired signals by process quality, not PnL alone.
- `smart-money-signal-audit` — treat whale/on-chain signals as noisy inputs, never direct orders.
- `token-risk-audit` — screen token safety/liquidity before adding to tradable universe.

## Sources Reviewed

- https://github.com/starchild-ai-agent/official-skills
- https://github.com/binance/binance-skills-hub
- https://github.com/jamesrochabrun/skills/tree/main/skills/trading-plan-generator
- https://github.com/tradermonty/claude-trading-skills

## Boundary Rule

`skills/` describes how agents should think and work. Runtime trading logic belongs in `strategies/`. Execution belongs downstream in policies/trading modules only after explicit approval.
