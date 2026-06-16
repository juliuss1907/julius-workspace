---
name: thesis-builder
description: >
  Develop a market thesis into evidence, counter-evidence, conviction, scenarios, and possible strategy expressions without prematurely forcing an entry rule.
metadata:
  version: "1.0.0"
  author: "Hermes Agent, adapted for trading-agents"
  trigger: "Project-local trading-agents workflow"
  output: "Actionable review, plan, checklist, or artifact for the trading-agents project"
---
# Thesis Builder

## Source Adaptation

Adapted for `ai-labs/projects/trading-agents` from:
- Starchild official-skills: trading-strategy
- tradermonty/claude-trading-skills: trade-hypothesis-ideator, edge-concept-synthesizer

This is a project-local agent skill. It is not trading advice, not an execution policy, and not a substitute for risk controls. Use it to structure analysis, design, review, and implementation work inside the repo.

## When to Use

Use before `strategy-designer` when the idea is still a worldview, worry, narrative, or hunch rather than a concrete strategy.

## Workflow

1. **State the thesis**
   - What does the user/system believe?
   - What horizon is implied?
   - Which assets should be affected?

2. **Collect evidence**
   - Price structure.
   - On-chain/derivatives data.
   - Macro/liquidity context.
   - News/catalyst.
   - Sentiment/positioning.

3. **Collect counter-evidence**
   - What would make the thesis wrong?
   - What data conflicts with it?
   - What alternative explanation exists?

4. **Scenario map**
   - Bull/base/bear paths.
   - Key signposts.
   - What strategy family fits each path, if any.

5. **Decide next step**
   - `research_more` if evidence is weak.
   - `watchlist` if thesis is plausible but trigger absent.
   - `strategy_draft` if it can be turned into explicit state/setup/trigger/action.
   - `reject` if thesis is vague or non-falsifiable.

## Output Template

```yaml
thesis: "..."
horizon: "..."
assets: []
evidence: []
counter_evidence: []
scenarios:
  bull: "..."
  base: "..."
  bear: "..."
signposts: []
possible_strategy_expressions: []
next_step: research_more | watchlist | strategy_draft | reject
```

## Guardrails

- Do not confuse a good story with a trade.
- Do not force entry/exit before the thesis is falsifiable.
- Do not ignore counter-evidence.
