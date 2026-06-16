---
name: signal-postmortem
description: >
  Review closed trades or expired signals by separating market outcome from decision quality, execution quality, policy error, sizing error, regime mismatch, and data/context error.
metadata:
  version: "1.0.0"
  author: "Hermes Agent, adapted for trading-agents"
  trigger: "Project-local trading-agents workflow"
  output: "Actionable review, plan, checklist, or artifact for the trading-agents project"
---
# Signal Postmortem

## Source Adaptation

Adapted for `ai-labs/projects/trading-agents` from:
- tradermonty/claude-trading-skills: signal-postmortem, trade-performance-coach
- local skill: trading-system-design

This is a project-local agent skill. It is not trading advice, not an execution policy, and not a substitute for risk controls. Use it to structure analysis, design, review, and implementation work inside the repo.

## When to Use

Use after a simulated/live/paper trade closes, after a signal's holding window expires, or during weekly/monthly strategy review.

## Core Rule

Do not grade by PnL alone. A profitable trade can be a bad decision; a losing trade can be a good decision.

## Postmortem Dimensions

- **Market outcome:** what happened after the signal.
- **Decision quality:** did the strategy follow its stated policy?
- **Execution quality:** entry, stop, exit, slippage, order assumption.
- **Sizing quality:** risk unit, volatility adjustment, exposure cap, correlation.
- **Regime match:** did the chosen playbook match the actual market state?
- **Data/context quality:** missing data, stale data, wrong candle alignment, news/event blind spot.
- **Policy update:** keep, revise, split by regime, retire, or collect more data.

## Classification Tags

- `true_positive`: strategy thesis worked and decision process was valid.
- `false_positive`: signal triggered but expected move did not occur.
- `good_loss`: loss occurred but process was valid and risk contained.
- `bad_win`: PnL positive but process violated rules.
- `missed_opportunity`: setup appeared but trigger/action missed due to policy gap.
- `regime_mismatch`: strategy acted in state where it should be disabled.
- `sizing_error`: action direction acceptable, position sizing wrong.
- `execution_error`: policy signal okay, execution assumption or order handling bad.

## Output Template

```yaml
signal_id: "..."
strategy_id: "..."
symbol: "..."
entry_time: "..."
exit_or_review_time: "..."
outcome:
  pnl_or_return: "..."
  max_favorable_excursion: "..."
  max_adverse_excursion: "..."
classification: []
decision_quality: good | mixed | poor
execution_quality: good | mixed | poor
sizing_quality: good | mixed | poor
regime_match: yes | no | uncertain
root_causes: []
policy_update:
  action: keep | revise | split | retire | collect_more
  notes: []
```

## Review Questions

- Was the setup valid according to the strategy, or did the agent invent a discretionary exception?
- Did the trigger fire using only data available at that time?
- Did invalidation occur before exit?
- Did size reflect variance and confidence?
- Would the same decision be acceptable if this trade lost money?
