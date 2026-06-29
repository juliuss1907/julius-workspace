# Batch 4B — Evaluation Metrics Implementation Plan

> **For Hermes / OpenCode:** This batch turns the Batch 4A evaluation framework into repeatable offline evaluation tooling. It is code, but only evaluation/reporting code. It must not touch execution, live trading, strategy-to-order mapping, threshold tuning, or runtime trading behavior.

**Goal:** Implement a deterministic offline evaluator that reads replay JSONL artifacts with top-level `strategy_signal`, computes the Batch 4A Strategy-vs-TraderAgent metrics, and writes flat Markdown + JSON evaluation reports for review and future calibration comparisons.

**North Star:** Evidence-driven trading intelligence, not autonomous gambling.

```text
Observe → Attribute → Replay → Compare → Review → Evaluate → Then maybe execute
```

Batch 4B should answer: **Can we compute Strategy-vs-TraderAgent evaluation metrics repeatably from replay artifacts, using Batch 3G as the baseline, without changing trading behavior?**

---

## Current Context

Repo:

```text
/home/julius/julius-workspace/ai-labs/projects/trading-agents
```

Relevant completed batches:

```text
97dcea3 feat(trading-agents): record strategy attribution in replay
9186e6a feat(trading-agents): add replay attribution analyzer
09ab91f docs(trading-agents): add replay attribution review
3e4c52c docs(trading-agents): add bounded replay attribution review
1ba2215 docs(trading-agents): expand replay attribution coverage
cc9267e docs(trading-agents): add strategy evaluation proposal
```

Key Batch 4A artifact:

```text
strategy-vs-traderagent-evaluation-proposal-2026-06-29.md
```

Batch 3G baseline input:

```text
logs/replay_signals-batch3g-2026-06-28.jsonl
```

Batch 3G baseline metrics:

```text
total_records: 140
records_with_strategy_signal: 140
records_missing_strategy_signal: 0
strategy_ids: volatility-skip 126, trend-following 10, breakout 4
strategy_actions: skip 80, hold 46, short 9, long 5
market_regimes: volatile 80, trend_down 45, trend_up 15
action_alignment: aligned 35, neutral_or_observational 105, conflicted 0, missing 0
BUY|skip + SELL|skip: 49/140 = 35.0%
volatility_skip_blocks: 80/140 = 57.1%
directional_strategy_coverage: 14/140 = 10.0%
```

Existing analyzer:

```text
scripts/analyze_replay_attribution.py
scripts/test_replay_attribution_analyzer.py
```

Design preference for Batch 4B:

```text
Create a new evaluator script instead of overloading the analyzer.
```

Rationale:

- `analyze_replay_attribution.py` summarizes replay attribution.
- `evaluate_strategy_vs_trader.py` should evaluate against Batch 4A metrics and gates.
- Keeping them separate avoids mixing descriptive analysis with evaluation policy.

---

## Hard Constraints

- Do **not** run live trading.
- Do **not** place, submit, simulate-live, or execute orders.
- Do **not** map strategy `long/short/hold/skip` into execution `BUY/SELL/HOLD`.
- Do **not** change `FinalAnalysis.action` or TraderAgent action semantics.
- Do **not** change `strategies/registry.py` behavior.
- Do **not** tune thresholds.
- Do **not** alter runtime config.
- Do **not** implement PnL/backtest/equity metrics.
- Do **not** implement `mean_reversion`.
- Do **not** add dependencies; keep evaluator stdlib-only.
- Do **not** move code into `src/`.
- Do **not** overwrite existing replay artifacts.
- Do **not** touch `.agent/**` staged docs/renames.
- Do **not** touch unrelated untracked files: `ai-agent-trading-report.md`, `outputs/`, `researchs.md`.
- Use scoped staging/commit only. Never use `git add -A`.

---

## Deliverables

### Code

Create:

```text
scripts/evaluate_strategy_vs_trader.py
```

Expected CLI:

```bash
./venv/bin/python scripts/evaluate_strategy_vs_trader.py \
  --input logs/replay_signals-batch3g-2026-06-28.jsonl \
  --output strategy-vs-traderagent-evaluation-batch4b-2026-06-29.md \
  --json-output strategy-vs-traderagent-evaluation-batch4b-2026-06-29.json
```

### Tests

Create:

```text
scripts/test_strategy_vs_trader_evaluator.py
```

Extend if needed:

```text
scripts/test_boundary_guardrails.py
```

### Artifacts

Generate from Batch 3G baseline:

```text
strategy-vs-traderagent-evaluation-batch4b-2026-06-29.md
strategy-vs-traderagent-evaluation-batch4b-2026-06-29.json
```

### Commit

Commit locally only, with scoped files:

```text
feat(trading-agents): add strategy evaluation metrics
```

Do not push unless Julius explicitly approves.

---

## Required Metrics

The evaluator must compute the Batch 4A metrics exactly and repeatably.

### 1. Attribution coverage

```text
records_with_strategy_signal / total_records
```

Fields:

```json
{
  "total_records": 140,
  "records_with_strategy_signal": 140,
  "records_missing_strategy_signal": 0,
  "attribution_coverage_rate": 1.0
}
```

### 2. Alignment rate

Aligned pairs:

```text
BUY + long
SELL + short
HOLD + hold
```

Field:

```json
"alignment_rate": 0.25
```

### 3. Conflict rate

Conflicted pairs:

```text
BUY + short
SELL + long
```

Field:

```json
"conflict_rate": 0.0
```

### 4. Neutral / observational rate

Everything known but not aligned/conflicted.

Field:

```json
"neutral_or_observational_rate": 0.75
```

### 5. Directional strategy coverage

```text
(strategy_action == long or short) / total_records
```

Batch 3G expected:

```text
14/140 = 0.10
```

### 6. Skip-during-TraderAgent-action rate

```text
(BUY|skip + SELL|skip) / total_records
```

Batch 3G expected:

```text
49/140 = 0.35
```

### 7. Volatility-skip direct block rate

```text
volatility_skip_blocks / total_records
```

Batch 3G expected:

```text
80/140 = 0.571428...
```

### 8. Strategy-family diversity

Counts and shares by strategy family:

```text
volatility_skip
trend_following
breakout
unknown
```

### 9. Action matrix

Count all TraderAgent action + StrategySignal action pairs:

```text
BUY|long
BUY|hold
BUY|skip
SELL|short
SELL|hold
SELL|skip
HOLD|hold
HOLD|skip
HOLD|short
...
```

### 10. Gate statuses

Report human-readable gate statuses, not automatic execution approvals.

Suggested gates:

```text
attribution_ready
conflict_review_ready
directional_sample_insufficient
skip_calibration_needed
execution_not_authorized
```

Example interpretations for Batch 3G:

```text
attribution_ready: pass
conflict_review_ready: pass
directional_sample_insufficient: warn
skip_calibration_needed: warn
execution_not_authorized: blocked
```

---

## Proposed Implementation Shape

Keep the evaluator stdlib-only and import-light.

Suggested functions:

```python
def load_replay_records(path: Path) -> List[Dict]: ...
def extract_trader_action(record: Dict) -> str: ...
def extract_strategy_signal(record: Dict) -> Dict: ...
def extract_strategy_action(record: Dict) -> str: ...
def extract_strategy_family(strategy_signal: Dict) -> str: ...
def extract_market_regime(strategy_signal: Dict) -> str: ...
def is_volatility_skip_block(strategy_signal: Dict) -> bool: ...
def classify_alignment(trader_action: str, strategy_action: str) -> str: ...
def safe_rate(numerator: int, denominator: int) -> float: ...
def evaluate_strategy_vs_trader(records: List[Dict]) -> Dict: ...
def render_markdown_evaluation(evaluation: Dict) -> str: ...
def write_json(path: Path, evaluation: Dict) -> None: ...
def parse_args(argv=None): ...
def main(argv=None) -> int: ...
```

Reuse logic from `scripts/analyze_replay_attribution.py` only by copying small pure helpers if importing would create coupling. Prefer no runtime imports.

---

## Test Plan: RED First, Then GREEN

### RED tests before implementation

Create `scripts/test_strategy_vs_trader_evaluator.py` with fixture records and tests for:

1. Loading JSONL with blank lines.
2. Invalid JSON reports line number.
3. Alignment classification.
4. Safe division when total records is zero.
5. Evaluation computes expected rates from fixture:
   - attribution coverage
   - alignment rate
   - conflict rate
   - neutral rate
   - directional coverage
   - skip-during-action rate
   - volatility-skip block rate
   - strategy family shares
   - action matrix
6. Markdown output contains required sections.
7. CLI writes Markdown and JSON outputs.

Expected first RED:

```text
ModuleNotFoundError: No module named 'scripts.evaluate_strategy_vs_trader'
```

### GREEN implementation

Implement `scripts/evaluate_strategy_vs_trader.py` until tests pass.

### Boundary guardrails

Extend `scripts/test_boundary_guardrails.py` with:

1. Evaluator `--help` exits zero.
2. Evaluator import does not load forbidden runtime/execution modules.

Forbidden module substrings should remain consistent with existing guardrails:

```text
dotenv
dataflows
state
trading
telegram_bot
risk_manager
position_manager
order_manager
entry_guard
runtime_health
reconciliation
```

---

## Validation Commands

Run targeted tests:

```bash
./venv/bin/python scripts/test_strategy_vs_trader_evaluator.py
./venv/bin/python scripts/test_replay_attribution_analyzer.py
./venv/bin/python scripts/test_boundary_guardrails.py
```

Run evaluator on Batch 3G:

```bash
./venv/bin/python scripts/evaluate_strategy_vs_trader.py \
  --input logs/replay_signals-batch3g-2026-06-28.jsonl \
  --output strategy-vs-traderagent-evaluation-batch4b-2026-06-29.md \
  --json-output strategy-vs-traderagent-evaluation-batch4b-2026-06-29.json
```

Validate expected baseline in JSON:

```text
total_records == 140
records_with_strategy_signal == 140
records_missing_strategy_signal == 0
attribution_coverage_rate == 1.0
alignment_rate == 0.25
conflict_rate == 0.0
neutral_or_observational_rate == 0.75
directional_strategy_coverage_rate == 0.10
skip_during_trader_action_rate == 0.35
volatility_skip_direct_block_rate == 80/140
```

Whitespace check:

```bash
git diff --check -- \
  scripts/evaluate_strategy_vs_trader.py \
  scripts/test_strategy_vs_trader_evaluator.py \
  scripts/test_boundary_guardrails.py \
  strategy-vs-traderagent-evaluation-batch4b-2026-06-29.md \
  strategy-vs-traderagent-evaluation-batch4b-2026-06-29.json
```

Optional dry-run smoke:

```bash
timeout 120s ./venv/bin/python scripts/run_paper_trading.py --single-cycle --dry-run
```

Dry-run is optional because Batch 4B is offline evaluation tooling. If run, verify exit code 0 and no live order messages.

---

## Expected Output Structure

Markdown report should include:

```text
# Strategy vs TraderAgent Evaluation
## Dataset
## Core Metrics
## Strategy Distribution
## Action Matrix
## Gate Status
## Interpretation
## Next Recommendation
```

JSON report should include machine-readable sections:

```json
{
  "dataset": {},
  "metrics": {},
  "counts": {},
  "rates": {},
  "action_matrix": {},
  "gate_status": {},
  "recommendation": {}
}
```

---

## Scope Boundary

Batch 4B succeeds if it makes evaluation repeatable.

Batch 4B does **not** decide whether thresholds should change. It creates the measurement tool that future calibration batches must use.

Recommended next step after Batch 4B:

```text
Batch 3H — Volatility-Skip Calibration Review
```

Only after metrics are implemented should calibration variants be run and compared against Batch 3G baseline.
