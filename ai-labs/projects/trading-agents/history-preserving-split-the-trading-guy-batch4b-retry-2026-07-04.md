# Batch 4B Retry — History-Preserving Split for the-trading-guy

Status: blocked
Repo created: false
Push executed: false

## Summary

- Forbidden files remain after filtering in HEAD or history; do not push.
- Source working-tree .agent/outputs/report noise remains excluded; split/filter used committed history only.

## Target

- SSH URL: git@github.com:juliuss1907/the-trading-guy.git
- Accessible by ls-remote: true
- Target ref count: 0

## Extraction

- Method: git subtree split
- Subtree available: true
- Split branch: split/the-trading-guy-batch4b-retry-20260704-0952
- Split hash: 27b88319703cef2a5bee9d0aad0370f672db0e13
- Temp repo: /tmp/batch4b-retry-584200/the-trading-guy-filtered
- Filter method: git-filter-branch-tree-filter-temp-repo
- Filter rc: 0
- Filtered HEAD: 711c2d545746bb32b3da365f9751beba7ef1f145

## Content Audit

- Pre-filter HEAD file count: 345
- Post-filter HEAD file count: 342
- Post-filter history path count: 10092
- Forbidden HEAD file count: 0
- Forbidden history path count: 39
- Raw replay logs included: false
- Env/secret files included: true
- Project-local skills path count: 13

### Top-level entries
- .gitignore
- .hermes
- README.md
- __init__.py
- agents
- candidate-level-attribution-instrumentation-batch3w-2026-07-03.json
- candidate-level-attribution-instrumentation-batch3w-2026-07-03.md
- candidate-level-fresh-replay-review-batch3x-2026-07-03.json
- candidate-level-fresh-replay-review-batch3x-2026-07-03.md
- config
- dataflows
- docs
- history-preserving-split-the-trading-guy-batch4b-2026-07-04.json
- history-preserving-split-the-trading-guy-batch4b-2026-07-04.md
- main.py
- manual-readonly-monitoring-cadence-run-2-batch3u-2026-07-03.json
- manual-readonly-monitoring-cadence-run-2-batch3u-2026-07-03.md
- manual-readonly-monitoring-cadence-run-3-scheduler-review-batch3v-2026-07-03.json
- manual-readonly-monitoring-cadence-run-3-scheduler-review-batch3v-2026-07-03.md
- manual-readonly-monitoring-cadence-runbook-batch3t-2026-07-02.json
- manual-readonly-monitoring-cadence-runbook-batch3t-2026-07-02.md
- ops
- orchestration
- policies
- push-release-readiness-audit-batch3z-2026-07-04.json
- push-release-readiness-audit-batch3z-2026-07-04.md
- readonly-monitoring-cadence-batch3r-2026-07-02.json
- readonly-monitoring-cadence-batch3r-2026-07-02.md
- readonly-monitoring-cadence-execution-batch3s-2026-07-02.json
- readonly-monitoring-cadence-execution-batch3s-2026-07-02.md
- readonly-monitoring-readiness-consolidation-batch3y-2026-07-03.json
- readonly-monitoring-readiness-consolidation-batch3y-2026-07-03.md
- replay-attribution-review-2026-06-28.md
- replay-attribution-review-batch3f-2026-06-28.md
- replay-attribution-review-batch3g-2026-06-28.md
- replay-attribution-summary-2026-06-28.json
- replay-attribution-summary-2026-06-28.md
- replay-attribution-summary-batch3f-2026-06-28.json
- replay-attribution-summary-batch3f-2026-06-28.md
- replay-attribution-summary-batch3g-2026-06-28.json
- replay-attribution-summary-batch3g-2026-06-28.md
- replay-import-safety-readiness-batch3q-a-2026-07-02.json
- replay-import-safety-readiness-batch3q-a-2026-07-02.md
- replay-runtime-dependency-readiness-batch3q-b-2026-07-02.json
- replay-runtime-dependency-readiness-batch3q-b-2026-07-02.md
- requirements.txt
- scripts
- separate-repo-the-trading-guy-audit-batch4a-2026-07-04.json
- separate-repo-the-trading-guy-audit-batch4a-2026-07-04.md
- skills
- state
- strategies
- strategy-vs-traderagent-evaluation-batch3h-variant-a-2026-06-29.json
- strategy-vs-traderagent-evaluation-batch3h-variant-a-2026-06-29.md
- strategy-vs-traderagent-evaluation-batch3h-variant-b-2026-06-29.json
- strategy-vs-traderagent-evaluation-batch3h-variant-b-2026-06-29.md
- strategy-vs-traderagent-evaluation-batch3h-variant-c-2026-06-29.json
- strategy-vs-traderagent-evaluation-batch3h-variant-c-2026-06-29.md
- strategy-vs-traderagent-evaluation-batch3h-variant-d-2026-06-29.json
- strategy-vs-traderagent-evaluation-batch3h-variant-d-2026-06-29.md
- strategy-vs-traderagent-evaluation-batch4b-2026-06-29.json
- strategy-vs-traderagent-evaluation-batch4b-2026-06-29.md
- strategy-vs-traderagent-evaluation-proposal-2026-06-29.md
- telegram_bot
- trading
- trading-agent-idea.md
- utils
- volatility-skip-broader-validation-batch3j-2026-06-29.json
- volatility-skip-broader-validation-batch3j-2026-06-29.md
- volatility-skip-calibration-implementation-proposal-batch3i-2026-06-29.json
- volatility-skip-calibration-implementation-proposal-batch3i-2026-06-29.md
- volatility-skip-calibration-review-batch3h-2026-06-29.json
- volatility-skip-calibration-review-batch3h-2026-06-29.md
- volatility-skip-config-seam-confirmation-batch3m-b-2026-06-30.json
- volatility-skip-config-seam-confirmation-batch3m-b-2026-06-30.md
- volatility-skip-fresh-replay-cadence-plan-batch3q-2026-07-02.json
- volatility-skip-fresh-replay-cadence-plan-batch3q-2026-07-02.md
- volatility-skip-implementation-design-batch3l-2026-06-30.json
- volatility-skip-implementation-design-batch3l-2026-06-30.md
- volatility-skip-monitoring-baseline-expansion-batch3p-2026-07-01.json
- volatility-skip-monitoring-baseline-expansion-batch3p-2026-07-01.md
- volatility-skip-monitoring-batch3o-2026-07-01.json
- volatility-skip-monitoring-batch3o-2026-07-01.md
- volatility-skip-monitoring-cadence-batch3q-retry-2026-07-02.json
- volatility-skip-monitoring-cadence-batch3q-retry-2026-07-02.md
- volatility-skip-monitoring-cadence-batch3r-2026-07-02-batch3s.json
- volatility-skip-monitoring-cadence-batch3r-2026-07-02-batch3s.md
- volatility-skip-monitoring-cadence-batch3r-manual-2026-07-03-0917-batch3u.json
- volatility-skip-monitoring-cadence-batch3r-manual-2026-07-03-0917-batch3u.md
- volatility-skip-monitoring-cadence-batch3r-manual-2026-07-03-0958-batch3v.json
- volatility-skip-monitoring-cadence-batch3r-manual-2026-07-03-0958-batch3v.md
- volatility-skip-monitoring-candidate-batch3x-2026-07-03.json
- volatility-skip-monitoring-candidate-batch3x-2026-07-03.md
- volatility-skip-monitoring-combined-batch3q-retry-2026-07-02.json
- volatility-skip-monitoring-combined-batch3q-retry-2026-07-02.md
- volatility-skip-monitoring-combined-batch3r-2026-07-02-batch3s.json
- volatility-skip-monitoring-combined-batch3r-2026-07-02-batch3s.md
- volatility-skip-monitoring-combined-batch3r-manual-2026-07-03-0917-batch3u.json
- volatility-skip-monitoring-combined-batch3r-manual-2026-07-03-0917-batch3u.md
- volatility-skip-monitoring-combined-batch3r-manual-2026-07-03-0958-batch3v.json
- volatility-skip-monitoring-combined-batch3r-manual-2026-07-03-0958-batch3v.md
- volatility-skip-monitoring-combined-candidate-batch3x-2026-07-03.json
- volatility-skip-monitoring-combined-candidate-batch3x-2026-07-03.md
- volatility-skip-post-implementation-review-batch3n-2026-07-01.json
- volatility-skip-post-implementation-review-batch3n-2026-07-01.md
- volatility-skip-runtime-config-loader-probe-batch3m-c-2026-06-30.json
- volatility-skip-runtime-config-loader-probe-batch3m-c-2026-06-30.md
- volatility-skip-runtime-implementation-batch3m-2026-07-01.json
- volatility-skip-runtime-implementation-batch3m-2026-07-01.md
- volatility-skip-runtime-readiness-batch3m-a-2026-06-30.json
- volatility-skip-runtime-readiness-batch3m-a-2026-06-30.md
- volatility-skip-zero-block-diagnostic-batch3v-alt-2026-07-03.json
- volatility-skip-zero-block-diagnostic-batch3v-alt-2026-07-03.md
- volatility-skip-zero-block-review-batch3k-2026-06-30.json
- volatility-skip-zero-block-review-batch3k-2026-06-30.md
- watchlist

## Source Working Tree Exclusions

- A  ai-labs/projects/trading-agents/.agent/README.md
- A  ai-labs/projects/trading-agents/.agent/indicators/atr.md
- A  ai-labs/projects/trading-agents/.agent/indicators/bollinger-bands.md
- A  ai-labs/projects/trading-agents/.agent/indicators/donchian.md
- A  ai-labs/projects/trading-agents/.agent/indicators/ema.md
- A  ai-labs/projects/trading-agents/.agent/indicators/funding-rate.md
- A  ai-labs/projects/trading-agents/.agent/indicators/macd.md
- A  ai-labs/projects/trading-agents/.agent/indicators/obv.md
- A  ai-labs/projects/trading-agents/.agent/indicators/open-interest.md
- A  ai-labs/projects/trading-agents/.agent/indicators/rsi.md
- A  ai-labs/projects/trading-agents/.agent/roles/layer-0-screening-agent.md
- A  ai-labs/projects/trading-agents/.agent/roles/layer-1-derivatives-analyst.md
- A  ai-labs/projects/trading-agents/.agent/roles/layer-1-fundamentals-analyst.md
- A  ai-labs/projects/trading-agents/.agent/roles/layer-1-news-analyst.md
- A  ai-labs/projects/trading-agents/.agent/roles/layer-1-sentiment-analyst.md
- A  ai-labs/projects/trading-agents/.agent/roles/layer-1-technical-analyst.md
- A  ai-labs/projects/trading-agents/.agent/roles/layer-2-bear-researcher.md
- A  ai-labs/projects/trading-agents/.agent/roles/layer-2-bull-researcher.md
- A  ai-labs/projects/trading-agents/.agent/roles/layer-3-trader-agent.md
- A  ai-labs/projects/trading-agents/.agent/roles/layer-4-portfolio-manager.md
- A  ai-labs/projects/trading-agents/.agent/roles/layer-4-risk-manager.md
- R  ai-labs/projects/trading-agents/skills/README.md -> ai-labs/projects/trading-agents/.agent/skills/README.md
- R  ai-labs/projects/trading-agents/skills/backtest-analysis/SKILL.md -> ai-labs/projects/trading-agents/.agent/skills/backtest-analysis/SKILL.md
- R  ai-labs/projects/trading-agents/skills/exposure-coach/SKILL.md -> ai-labs/projects/trading-agents/.agent/skills/exposure-coach/SKILL.md
- R  ai-labs/projects/trading-agents/skills/market-structure/SKILL.md -> ai-labs/projects/trading-agents/.agent/skills/market-structure/SKILL.md
- R  ai-labs/projects/trading-agents/skills/position-sizing/SKILL.md -> ai-labs/projects/trading-agents/.agent/skills/position-sizing/SKILL.md
- R  ai-labs/projects/trading-agents/skills/regime-review/SKILL.md -> ai-labs/projects/trading-agents/.agent/skills/regime-review/SKILL.md
- R  ai-labs/projects/trading-agents/skills/signal-postmortem/SKILL.md -> ai-labs/projects/trading-agents/.agent/skills/signal-postmortem/SKILL.md
- R  ai-labs/projects/trading-agents/skills/smart-money-signal-audit/SKILL.md -> ai-labs/projects/trading-agents/.agent/skills/smart-money-signal-audit/SKILL.md
- R  ai-labs/projects/trading-agents/skills/strategy-designer/SKILL.md -> ai-labs/projects/trading-agents/.agent/skills/strategy-designer/SKILL.md
- R  ai-labs/projects/trading-agents/skills/strategy-review/SKILL.md -> ai-labs/projects/trading-agents/.agent/skills/strategy-review/SKILL.md
- R  ai-labs/projects/trading-agents/skills/thesis-builder/SKILL.md -> ai-labs/projects/trading-agents/.agent/skills/thesis-builder/SKILL.md
- R  ai-labs/projects/trading-agents/skills/token-risk-audit/SKILL.md -> ai-labs/projects/trading-agents/.agent/skills/token-risk-audit/SKILL.md
- R  ai-labs/projects/trading-agents/skills/trading-plan/SKILL.md -> ai-labs/projects/trading-agents/.agent/skills/trading-plan/SKILL.md
- ?? ai-labs/projects/trading-agents/.agent/skills/handoff/
- ?? ai-labs/projects/trading-agents/ai-agent-trading-report.md
- ?? ai-labs/projects/trading-agents/outputs/
- ?? ai-labs/projects/trading-agents/researchs.md

## Push Proposal

No push proposal is ready because audit is blocked.

## Safety Confirmation

- repo_created: false
- push_executed: false
- force_push_used: false
- source_repo_history_rewritten: false
- runtime_default_config_change_performed: false
- scheduler_enabled: false
- live_trading_authorized: false
- order_placement_authorized: false
- raw_replay_logs_included: false
- env_or_secret_files_included: true
