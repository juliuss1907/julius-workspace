---
name: market-structure
description: >
  Analyze price action and market structure for trading-agents without vague indicator commentary: HTF context, structure, liquidity, key levels, trigger, stop, target, invalidation, and no-trade condition.
metadata:
  version: "1.0.0"
  author: "Hermes Agent, adapted for trading-agents"
  trigger: "Project-local trading-agents workflow"
  output: "Actionable review, plan, checklist, or artifact for the trading-agents project"
---
# Market Structure

## Source Adaptation

Adapted for `ai-labs/projects/trading-agents` from:
- Starchild official-skills: market-structure-ta
- tradermonty/claude-trading-skills: technical-analyst

This is a project-local agent skill. It is not trading advice, not an execution policy, and not a substitute for risk controls. Use it to structure analysis, design, review, and implementation work inside the repo.

## When to Use

Use when a strategy or report needs a price-action lens instead of another indicator summary. Useful for BTC/ETH/crypto charts, replay annotations, and validating whether indicator signals align with real structure.

## Principles

- Read auction structure first; indicators are secondary features.
- Always work top-down: higher timeframe context before lower timeframe trigger.
- No forced trades. If levels/structure are messy, output `skip`.
- Every actionable thesis needs levels, trigger, stop, target, invalidation, and R:R.

## Workflow

1. **HTF context**
   - Weekly/daily or equivalent higher timeframe.
   - Trend: HH/HL, LH/LL, range, compression, expansion.
   - Major BOS/CHoCH, distribution/accumulation/markup/markdown if identifiable.

2. **Structure map**
   - Key swing highs/lows.
   - Support/resistance and supply/demand zones.
   - Current channel/range if present.
   - Clean vs messy structure.

3. **Liquidity map**
   - Buy-side liquidity above equal highs / prior highs.
   - Sell-side liquidity below equal lows / prior lows.
   - Stop clusters, liquidation magnets, obvious breakout traps.

4. **Setup identification**
   - Continuation, reversal, sweep-and-reclaim, range fade, breakout, failed breakout.
   - State which regime this setup belongs to.

5. **Trigger and invalidation**
   - Trigger must be observable and non-hindsight.
   - Invalidation must be specific: level, close condition, or volatility-adjusted threshold.

6. **Action plan**
   - Entry idea.
   - Stop/invalidation.
   - Targets.
   - R:R.
   - No-trade condition.

## Output Template

```yaml
symbol: "..."
timeframes: []
htf_context: "..."
structure:
  trend: "..."
  key_levels: []
  liquidity: []
setup:
  type: "..."
  quality: low | medium | high
trigger: "..."
action_plan:
  action: long | short | wait | skip
  entry: "..."
  stop: "..."
  targets: []
  invalidation: "..."
  rr_estimate: "..."
no_trade_condition: []
```

## Forbidden Output

- “RSI overbought, MACD bullish, mixed signals” with no thesis.
- Vague zones without levels.
- Entry without invalidation.
- Lower-timeframe scalp plan that contradicts higher-timeframe context without explaining why.
