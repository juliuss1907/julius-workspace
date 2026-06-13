# Trading Agents Orchestration Refactor Plan

> **For OpenCode:** implement this plan in order. Keep commits small. Do not start with broad rewrites. First carve out shared orchestration, then reconnect demo/runtime and manual-report consumers.
> **Status note (2026-06):** The main shared-core / policy / readonly-cleanup milestones are implemented. Treat this as the historical implementation plan and source of architectural intent, not a request to recreate missing “proposed” files. Current canonical paths are `orchestration/contracts.py`, `orchestration/analysis_runner.py`, `policies/demo_execution.py`, `policies/manual_report.py`, `policies/reverse_planner.py`, `scripts/generate_manual_trade_report.py`, and `scripts/analyze_symbol_readonly.py`.

**Goal:** Re-center `trading-agents` around a shared analysis/synthesis orchestration layer that serves two products: demo auto-trading and manual real-money decision reports.

**Architecture:** Extract one explicit analysis pipeline from the current `scripts/run_paper_trading.py` and `scripts/analyze_symbol_readonly.py` flows. Standardize a shared `FinalAnalysis` contract. Make demo execution and manual reporting two downstream consumers of that contract.

**Tech Stack:** Python, existing agent classes in `agents/`, existing data layer in `dataflows/`, existing state/risk/execution modules in `state/` and `trading/`.

---

## 1. Non-goals for this refactor

Do **not** do these in the first orchestration pass:

- rewrite analyst internals
- redesign strategy logic
- remove paper-trading support
- add live-trading features
- redesign Telegram UX
- merge all config systems
- rename half the repo up front

This plan is about **control flow and responsibility placement**, not polishing every subsystem.

---

## 2. Current reality to preserve while refactoring

These existing flows are useful and should be treated as source material, not thrown away:

### Existing orchestration-heavy runtime
- `scripts/run_paper_trading.py`
  - historically initialized analysts, data manager, debate, risk, position manager, order manager, Telegram bot, reconciliation, locks, and runtime health
  - now should be read as the demo runtime consumer, not the architectural brain

### Existing read-only analysis path
- `scripts/analyze_symbol_readonly.py`
  - already proves there is demand for a non-execution path
  - now acts as a thin caller of the shared orchestration core
  - only loads demo/runtime managers behind explicit `--include-demo-decision`

### Existing shared reasoning pieces
- `agents/technical_analyst.py`
- `agents/news_analyst.py`
- `agents/sentiment_analyst.py`
- `agents/fundamentals_analyst.py`
- `agents/derivatives_analyst.py`
- `agents/trader_agent.py`
- `agents/research_debate.py`

### Existing demo-only policy/execution pieces
- `agents/risk_manager.py`
- `agents/position_manager.py`
- `state/entry_guard.py`
- `trading/`

---

## 3. Target orchestration model

The target control flow should be:

```text
Data Layer
  -> Analyst Layer
  -> Synthesis Layer
  -> FinalAnalysis
     -> DemoExecutionPolicy -> DemoExecutionDecision -> trading/
     -> ManualReportPolicy  -> ManualTradeReportItem -> markdown report
```

### Primary rule

`run_paper_trading.py` is no longer the only real orchestration entrypoint; keep it as a downstream demo consumer.

Instead:
- shared orchestration builds `FinalAnalysis`
- demo runtime consumes `FinalAnalysis`
- manual report generator consumes `FinalAnalysis`

---

## 4. Proposed file additions

These are the canonical paths after the first refactor pass, with two original-plan modules intentionally deferred unless complexity grows again.

### Shared orchestration/core files
- `orchestration/__init__.py`
- `orchestration/contracts.py`
- `orchestration/analysis_runner.py`
- `orchestration/bootstrap.py` — proposed in the original plan; not required unless shared dependency setup grows again
- `orchestration/final_analysis_builder.py` — proposed in the original plan; builder logic currently lives in `analysis_runner.py`

### New policy files
- `policies/__init__.py`
- `policies/demo_execution.py`
- `policies/manual_report.py`
- `policies/reverse_planner.py`

### New consumer script
- `scripts/generate_manual_trade_report.py`

### Test files
- `scripts/test_final_analysis_contract.py`
- `scripts/test_analysis_runner.py`
- `scripts/test_manual_report_policy.py`
- `scripts/test_demo_execution_policy.py`

If OpenCode prefers `tests/` instead of `scripts/test_*.py`, that is fine, but follow the repo’s dominant test convention unless changing it is part of a broader cleanup.

---

## 5. Target contracts

These do **not** need to be over-engineered. Start with dataclasses or typed dicts.

## 5.1 `FinalAnalysis`

This is the most important contract in the refactor.

```python
FinalAnalysis = {
    "symbol": str,
    "timeframe": str,
    "price": float | None,
    "timestamp": str,
    "analyst_signals": dict,
    "draft_signal": dict,
    "research_debate": dict | None,
    "final_signal": dict,
    "market_snapshot": dict,
    "thesis": str,
    "direction": "bullish|bearish|neutral",
    "confidence": float,
    "action": "BUY|SELL|HOLD",
    "hold_reason": str | None,
    "risk_notes": list,
    "metadata": dict,
}
```

### Important note

Do not expose raw `AgentResult` objects directly as the only outward API.

Inside the orchestration layer, using `AgentResult` is fine. But external consumers should receive a normalized, serialization-friendly object.

---

## 5.2 `DemoExecutionDecision`

```python
DemoExecutionDecision = {
    "approved": bool,
    "action": "open|hold|reduce|close|reverse|skip",
    "position_action": dict,
    "risk_decision": dict,
    "reason": str,
    "execution_mode": str,
}
```

This wraps current `PositionManager` and `RiskManager` outcomes into one consumer-facing decision.

---

## 5.3 `ManualTradeReportItem`

```python
ManualTradeReportItem = {
    "symbol": str,
    "direction": str,
    "confidence": float,
    "setup_quality": str,
    "thesis": str,
    "entry_idea": str | None,
    "trigger": str | None,
    "invalidation": str | None,
    "risk_notes": list,
    "supporting_factors": list,
    "conflicts": list,
}
```

This should be optimized for human review, not execution semantics.

---

## 6. Refactor phases

## Phase 1 — Define contracts and bootstrap shared dependencies

**Objective:** Create the minimum shared foundation without changing product behavior yet.

**Files:**
- Create: `orchestration/contracts.py`
- Create: `orchestration/bootstrap.py`
- Modify: `scripts/analyze_symbol_readonly.py`
- Test: `scripts/test_final_analysis_contract.py`

### Deliverables

1. `contracts.py`
   - dataclasses or typed dicts for:
     - `AnalystSignalSummary`
     - `FinalAnalysis`
     - `DemoExecutionDecision`
     - `ManualTradeReportItem`

2. `bootstrap.py`
   - one place to initialize shared dependencies:
     - `data_manager`
     - analysts
     - `TraderAgent`
     - `ResearchDebate`
   - optional helper class like `AnalysisServices`

3. Update `analyze_symbol_readonly.py`
   - do not change behavior yet
   - but start importing shared bootstrap helpers where practical

### Verification

- A contract unit test can serialize and validate `FinalAnalysis`
- `analyze_symbol_readonly.py` still runs after minimal bootstrap extraction

### Suggested commit

```bash
git add orchestration/contracts.py orchestration/bootstrap.py scripts/analyze_symbol_readonly.py scripts/test_final_analysis_contract.py
git commit -m "refactor: add shared orchestration contracts and bootstrap"
```

---

## Phase 2 — Extract analysis runner from current runtime logic

**Objective:** Make analysis runnable without paper-trading side effects.

**Files:**
- Create: `orchestration/analysis_runner.py`
- Create: `orchestration/final_analysis_builder.py`
- Modify: `scripts/analyze_symbol_readonly.py`
- Reference: `scripts/run_paper_trading.py:171+` (current `analyze_and_trade` flow)
- Test: `scripts/test_analysis_runner.py`

### Required behavior

Implement a function conceptually like:

```python
async def analyze_symbol(symbol: str, timeframe: str = "1h", mode: str = "full") -> FinalAnalysis:
    ...
```

### Responsibilities of `analyze_symbol()`

1. fetch market data
2. fetch optional fundamentals/ticker context
3. run all analysts in parallel
4. build `draft_signal`
5. run `ResearchDebate`
6. build final signal
7. derive normalized `FinalAnalysis`
8. return it without touching order execution

### Source extraction guidance

Use these blocks as starting material:
- `scripts/run_paper_trading.py` — the current analysis chain inside `analyze_and_trade()`
- `scripts/analyze_symbol_readonly.py` — existing non-executing end-to-end flow

Avoid duplicating the logic in both places after extraction.

### Verification

- `scripts/analyze_symbol_readonly.py BTCUSDT` works by calling the shared runner
- no order execution imports are required in `analysis_runner.py`
- `test_analysis_runner.py` checks normalized output shape and failure handling

### Suggested commit

```bash
git add orchestration/analysis_runner.py orchestration/final_analysis_builder.py scripts/analyze_symbol_readonly.py scripts/test_analysis_runner.py
git commit -m "refactor: extract shared analysis runner"
```

---

## Phase 3 — Create demo execution policy adapter

**Objective:** Convert shared analysis into demo-path decisions without letting demo runtime own the core orchestration.

**Files:**
- Create: `policies/demo_execution.py`
- Modify: `scripts/run_paper_trading.py`
- Reference: `agents/risk_manager.py`
- Reference: `agents/position_manager.py`
- Test: `scripts/test_demo_execution_policy.py`

### Required behavior

Implement a function conceptually like:

```python
async def build_demo_execution_decision(final_analysis, open_positions, portfolio_stats, portfolio_context, execution_mode) -> DemoExecutionDecision:
    ...
```

### Responsibilities

1. take `FinalAnalysis`
2. reconstruct or pass through what `RiskManager` needs
3. reconstruct or pass through what `PositionManager` needs
4. combine their outputs into one normalized `DemoExecutionDecision`
5. leave actual execution to existing `trading/` components

### `run_paper_trading.py` change target

Refactor so its main symbol loop becomes roughly:

```python
final_analysis = await analyze_symbol(...)
demo_decision = await build_demo_execution_decision(...)
await maybe_execute_demo_decision(demo_decision)
```

### Important constraint

Do not fully rewrite `run_paper_trading.py` in one shot. First route one narrow path through the adapter, then expand.

### Verification

- existing paper-trading runtime still works in single-cycle mode
- decision logic is clearer and more testable
- policy adapter can be unit-tested without placing trades

### Suggested commit

```bash
git add policies/demo_execution.py scripts/run_paper_trading.py scripts/test_demo_execution_policy.py
git commit -m "refactor: add demo execution policy adapter"
```

---

## Phase 4 — Create first-class manual report policy

**Objective:** Restore the second product track as a real output path.

**Files:**
- Create: `policies/manual_report.py`
- Create: `scripts/generate_manual_trade_report.py`
- Modify: optional reuse from `scripts/run_screening.py` or `scripts/update_dynamic_watchlist.py`
- Test: `scripts/test_manual_report_policy.py`

### Required behavior

Implement functions conceptually like:

```python
def final_analysis_to_report_item(final_analysis: FinalAnalysis) -> ManualTradeReportItem:
    ...

async def generate_manual_trade_report(symbols: list[str], mode: str = "full") -> str:
    ...
```

### Manual report requirements

The first version should output one flat markdown file with sections like:

1. Market regime / session summary
2. Top bullish setups
3. Top bearish setups
4. Neutral / avoid / conflict-heavy setups
5. Risk notes
6. Optional watchlist appendix

### Content rule

This report is for Julius to trade manually with real money. Therefore it must prioritize:
- thesis clarity
- what to watch
- what invalidates the setup
- why the setup matters
- confidence and caveats

It should **not** read like an ops log.

### Verification

- report can be generated without paper-trading runtime
- report uses shared analysis orchestration
- output is one flat markdown artifact

### Suggested commit

```bash
git add policies/manual_report.py scripts/generate_manual_trade_report.py scripts/test_manual_report_policy.py
git commit -m "feat: add manual report orchestration path"
```

---

## Phase 5 — Thin out `analyze_symbol_readonly.py`

**Objective:** Turn the readonly script into a thin CLI over shared orchestration and policies.

**Files:**
- Modify: `scripts/analyze_symbol_readonly.py`

### Required behavior

After previous phases, this script should mostly:
1. parse args
2. call `analyze_symbol()`
3. optionally call demo/manual policy adapters for inspection
4. print JSON

It should stop duplicating orchestration internals.

### Verification

- file length and complexity shrink materially
- output remains useful for debugging

### Suggested commit

```bash
git add scripts/analyze_symbol_readonly.py
git commit -m "refactor: make readonly analyzer a thin orchestration client"
```

---

## Phase 6 — Docs alignment

**Objective:** Ensure future contributors don’t reintroduce the same drift.

**Files:**
- Modify: `README.md`
- Modify: `docs/README.md`
- Reference: `docs/14-rescue-architecture.md`
- Reference: this file

### Required updates

Add a short architecture summary:
- shared analysis core
- demo execution consumer
- manual report consumer
- calibration/support tooling as supporting paths

### Verification

- a new contributor can identify where orchestration belongs
- runtime script is no longer described as the system’s only brain

### Suggested commit

```bash
git add README.md docs/README.md docs/14-rescue-architecture.md docs/15-orchestration-implementation-plan.md
git commit -m "docs: align architecture docs with orchestration split"
```

---

## Phase 7 — Policy cleanup (Milestone E)

**Completed:** 2026-06-12

Extracted the guarded-reverse decision logic from `_execute_guarded_reverse()` into a pure `plan_guarded_reverse()` function in `policies/reverse_planner.py`.  The runtime still performs all side effects (close, risk rerun, ticker fetch, execute, notify), but the *decision* about whether to close/re-run/open now lives in a stdlib-only planner that can be imported without loading runtime/data dependencies.

- `policies/reverse_planner.py`: added `GuardedReversePlan` dataclass + `plan_guarded_reverse()` (zero side effects, stdlib-only imports)
- `policies/demo_execution.py`: re-exports the reverse planner for compatibility but is no longer the pure import path
- `scripts/run_paper_trading.py::_execute_guarded_reverse()`: delegates policy to the planner while retaining all side effects
- `scripts/test_demo_execution_policy.py`: covers guarded-reverse decision paths, including fail-safe missing-`trade_id` behavior
- Boundary guardrails verify both `orchestration.analyze_symbol` and `policies.reverse_planner` stay free of execution/runtime imports

---

---

## 7. Practical guardrails for OpenCode during implementation

### Guardrail 1
If a new module needs `OrderManager`, it is not part of shared analysis orchestration.

### Guardrail 2
If a new module cannot run without Telegram bot startup, it is not part of shared analysis orchestration.

### Guardrail 3
If logic can be used by both demo and manual paths, it belongs in `orchestration/` or a shared helper, not in `scripts/run_paper_trading.py`.

### Guardrail 4
Do not let `FinalAnalysis` become a dump of every internal object. Normalize aggressively enough that it is stable and testable.

### Guardrail 5
Do not try to solve naming, config cleanup, and runtime ops at the same time as orchestration extraction.

---

## 8. Recommended implementation order for OpenCode

If OpenCode is going to work autonomously, the safest order is:

1. contracts + bootstrap
2. analysis runner
3. readonly script migration
4. demo execution policy adapter
5. manual report policy + report script
6. docs cleanup

This order minimizes breakage because it first creates parallel paths, then migrates existing entrypoints onto them.

---

## 9. Acceptance criteria

The orchestration refactor is successful when all of the following are true:

1. There is one shared function/class that produces `FinalAnalysis`
2. `scripts/analyze_symbol_readonly.py` uses that shared path
3. `scripts/run_paper_trading.py` consumes that shared path instead of owning all analysis logic itself
4. A new manual-report script can generate a trader-facing markdown report without starting trading runtime
5. Demo execution policy and manual report policy are separate modules
6. Runtime ops components remain functional, but are no longer the architectural center

---

## 10. First coding milestone to aim for

If OpenCode only does one milestone first, it should be this:

### Milestone A
- add `orchestration/contracts.py`
- add `orchestration/analysis_runner.py`
- refactor `scripts/analyze_symbol_readonly.py` to use the shared runner

Why this milestone first:
- lowest risk
- highest leverage
- proves the shared brain exists independently of execution
- creates the seam needed for all later work

---

## 11. Final note for implementation style

Prefer **carve-out refactoring** over **in-place mutation**.

That means:
- create shared modules first
- move one slice of logic at a time
- keep the old runtime working while new seams are introduced
- only delete duplicated code after the new path is proven

This project drifted because orchestration boundaries were implicit. The fix is to make them explicit in code structure, contracts, and entrypoints.
