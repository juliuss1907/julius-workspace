# 14. Rescue Architecture — Re-align `trading-agents` to the original 5-layer system

> **Status:** Accepted north-star document. The core orchestration/policy split has been implemented; this file remains the architecture intent source, with historical “should/proposed” language preserved where it describes the original rescue plan.
> **Why this exists:** The codebase drifted toward an execution-first paper-trading platform. The original product intent was broader and cleaner: **one shared trading brain** serving **two outputs** — **demo auto-trade** and **manual real-money decision reports**.

---

## 1. Original product intent

`trading-agents` should be treated as a **5-layer trading system** with **2 primary tracks**:

1. **Demo auto-trade track**
   - Purpose: validate signals in a safe environment using paper/demo accounts.
   - Success metric: stable execution, controlled risk, useful feedback loop, realistic performance diagnostics.

2. **Manual real-money report track**
   - Purpose: generate high-quality decision support so Julius can trade real capital manually.
   - Success metric: clear thesis, actionable setup summaries, invalidation/risk notes, concise review artifacts.

### Key rule

The system should share the **brain**, but not force both products through the same runtime path.

---

## 2. Root cause of the drift

The current repository appears to share not just data and analysts, but also too much orchestration around the paper-trading runtime.

That created three failure modes:

1. **Execution-first gravity**
   - Paper trading produces immediate feedback (orders, positions, PnL, alerts, incidents), so the code naturally grew around runtime stability.

2. **Manual-report path became secondary**
   - Reports exist, but most artifacts are operational or performance-oriented rather than decision-support-first.

3. **One runtime tried to serve two products**
   - Demo execution and manual decision support have different policies, outputs, and UX expectations.

---

## 3. Target system definition

**Current implemented seam (2026-06):**

- `orchestration.contracts.FinalAnalysis` — normalized shared contract
- `orchestration.analyze_symbol()` / `orchestration.analysis_runner.analyze_symbol()` — shared analysis/synthesis runner
- `policies.demo_execution` — demo runtime decision adapter
- `policies.manual_report` — manual report adapter
- `policies.reverse_planner` — stdlib-only guarded reverse planner
- `scripts/run_paper_trading.py` — demo runtime consumer
- `scripts/generate_manual_trade_report.py` — manual report consumer
- `scripts/analyze_symbol_readonly.py` — thin read-only orchestration client

The target architecture is:

- **One shared analysis core**
- **One shared synthesis / decision core**
- **Two distinct downstream consumers**
  - demo execution
  - manual report generation

This is the correct interpretation of the original intent.

---

## 4. The 5-layer architecture

## Layer 1 — Data Layer

**Responsibility**
- Gather raw inputs required for trading decisions.

**Includes**
- market / OHLCV / ticker data
- derivatives and funding context
- sentiment and macro context
- news and external feeds
- storage / caching / retrieval utilities

**Current code likely in this layer**
- `dataflows/`
- parts of `state/`
- data-loading helpers used by runtime and reports

**Design rule**
- No trade execution logic.
- No report rendering logic.
- Only fetch, normalize, store, and expose inputs.

---

## Layer 2 — Analysis Layer

**Responsibility**
- Convert raw data into analyst-specific interpretations.

**Includes**
- technical analysis
- sentiment analysis
- news analysis
- optional regime / derivatives / macro / screening analysts

**Current code likely in this layer**
- `agents/technical_analyst.py`
- `agents/news_analyst.py`
- `agents/sentiment_analyst.py`
- `agents/screening_agent.py`

**Design rule**
- Analysts should not place trades.
- Analysts should not know whether they are being used for demo trading or manual reporting.
- Output should be normalized into a common result shape.

---

## Layer 3 — Synthesis / Decision Layer

**Responsibility**
- Merge analyst outputs into one coherent market view.

**Includes**
- analyst aggregation
- confidence scoring
- conflict resolution
- research debate / thesis formation
- final directional view and rationale

**Current code likely in this layer**
- `agents/research_debate.py`
- `agents/trader_agent.py`
- confidence / scoring logic spread across agents and scripts

**Required output**
A shared object conceptually like:

```python
FinalAnalysis = {
    "symbol": "BTCUSDT",
    "direction": "bullish|bearish|neutral",
    "confidence": 0.0,
    "thesis": "...",
    "supporting_signals": [...],
    "conflicts": [...],
    "invalidation": "...",
    "risk_notes": [...],
    "market_regime": "trend|range|high_vol|risk_off|...",
}
```

**Design rule**
- This layer is the true product core.
- Both downstream tracks must consume this layer rather than rebuilding logic locally.

---

## Layer 4 — Policy Layer

**Responsibility**
- Translate `FinalAnalysis` into track-specific decisions.

This is where the system must split.

### 4A. Demo auto-trade policy

**Purpose**
- Determine whether the demo runtime should act automatically.

**Output concept**

```python
DemoExecutionDecision = {
    "approved": True,
    "action": "open|hold|reduce|close|reverse|skip",
    "size_multiplier": 0.0,
    "max_leverage": 0,
    "risk_reason": "...",
    "execution_notes": [...],
}
```

**Current code likely in this policy**
- `agents/risk_manager.py`
- `agents/position_manager.py`
- `state/entry_guard.py`

### 4B. Manual real-money report policy

**Purpose**
- Convert analysis into high-quality human decision support.

**Output concept**

```python
ManualTradeReportItem = {
    "symbol": "BTCUSDT",
    "bias": "bullish|bearish|neutral",
    "setup_quality": "A|B|C|avoid",
    "entry_idea": "...",
    "trigger": "...",
    "invalidation": "...",
    "risk_notes": [...],
    "why_it_matters": "...",
}
```

**Design rule**
- Manual-report policy must not reuse execution approval semantics as its primary abstraction.
- `approved / blocked / reverse / reduce` are not sufficient user-facing outputs for manual trading.

---

## Layer 5 — Output Layer

This layer is where the two tracks fully diverge.

### 5A. Demo auto-trade output

**Responsibility**
- execute paper trades
- manage positions
- notify status
- schedule runtime
- maintain operational safety

**Current code likely in this layer**
- `scripts/run_paper_trading.py`
- `trading/`
- `scripts/runtime_control.py`
- `scripts/trading_scheduler.py`
- `telegram_bot/` (for ops/control usage)

### 5B. Manual report output

**Responsibility**
- generate concise decision-support artifacts for Julius
- produce watchlists, setup summaries, and reviewable markdown

**Current code likely in this layer**
- `scripts/generate_manual_trade_report.py`
- `policies/manual_report.py`
- `scripts/run_screening.py`
- `scripts/update_dynamic_watchlist.py`
- parts of `scripts/generate_daily_report.py`

**Design rule**
- Manual-report output must remain a first-class path, not a side effect of the auto-trade runtime.

---

## 5. Current codebase mapping

The repo already contains many pieces needed for the intended architecture. The problem is mostly **responsibility placement**, not total absence of components.

### Shared core that should remain shared
- `dataflows/`
- `agents/base_agent.py`
- `agents/technical_analyst.py`
- `agents/news_analyst.py`
- `agents/sentiment_analyst.py`
- `agents/research_debate.py`
- `agents/trader_agent.py`
- confidence / signal-combination logic

### Demo-only path
- `scripts/run_paper_trading.py`
- `trading/`
- `agents/risk_manager.py`
- `agents/position_manager.py`
- `state/entry_guard.py`
- `scripts/runtime_control.py`
- `scripts/trading_scheduler.py`

### Manual-report path
- `scripts/generate_manual_trade_report.py`
- `policies/manual_report.py`
- `scripts/run_screening.py`
- `scripts/update_dynamic_watchlist.py`
- report-rendering code that should be reoriented toward actionable manual decisions

### Calibration / research support path
- `scripts/generate_backtest_dashboard.py`
- `scripts/generate_parameter_recommendations.py`
- `scripts/run_calibration_workflow.py`
- `scripts/parameter_sweep.py`
- `scripts/replay_parameter_sweep.py`

These are useful, but they should support the shared core and demo policy — not dictate the whole product identity.

---

## 6. What changed / what must remain true

The first rescue pass has already created the shared orchestration seam and downstream policy consumers. The guardrail now is to keep future work from drifting back into execution-first design.

## A. Make the shared brain explicit

Maintain the shared orchestration path that does this for any symbol/set of symbols:

1. fetch normalized data
2. run analysts
3. synthesize final analysis
4. return `FinalAnalysis`

This should work **without** needing to enter paper-trading runtime flow.

### Current functions / modules
- `orchestration.analyze_symbol()`
- `orchestration.analysis_runner.analyze_symbol()`
- `orchestration.contracts.FinalAnalysis`

---

## B. Make demo execution a consumer, not the center

`run_paper_trading.py` should become a downstream consumer of shared analysis outputs.

Instead of being the architectural center, it should do:

1. call shared analysis core
2. apply demo policy
3. execute approved paper actions
4. persist logs and metrics

This keeps auto-trade intact without letting it define the entire system.

---

## C. Keep the true manual-report pipeline first-class

The manual path has a dedicated consumer and must stay independent from demo runtime execution.

### Current artifact
- `scripts/generate_manual_trade_report.py`

### Responsibilities
- call the same shared analysis core
- apply manual-report policy
- rank best setups
- generate one markdown report that Julius can read and act on

### Required report sections
- market regime summary
- top symbols to watch
- bullish setups
- bearish setups
- invalidation / risk notes
- high-uncertainty zones
- optional “do not trade” section

This output should optimize for **clarity and discretion**, not execution automation.

---

## D. Separate analysis modes from execution modes

At the moment, mode concepts appear mixed.

They should be split into two independent dimensions:

### Analysis mode
- `quick`
- `full`

### Execution mode
- `dry_run`
- `execute_close_only`
- `execute_reduce_and_close`
- `execute_all`

This avoids conflating “how deeply we analyze” with “how aggressively we act.”

---

## E. Stop using operational reports as the manual-trading product

Current reporting artifacts are valuable but serve different jobs:

- daily trading report → ops/performance
- backtest dashboard → calibration
- parameter recommendations → tuning
- watchlist proposal → support tool

None of these should be mistaken for the main manual real-money report product.

The manual product needs a dedicated format optimized for:
- trade review
- market bias
- setup selection
- invalidation planning

---

## 7. Minimal refactor strategy (least painful)

Do **not** rewrite everything.

Use a carve-out strategy.

### Phase 1 — Freeze and define boundaries

**Goal**
Stop further drift.

**Actions**
- Freeze new execution features unless they are bug fixes.
- Accept this document as the north-star architecture.
- Define which modules are shared core vs demo-only vs manual-report-only.

**Exit condition**
- The team can answer for any file: shared core, demo path, manual path, or support tooling.

---

### Phase 2 — Extract shared analysis orchestration

**Goal**
Make analysis runnable without paper-trading runtime.

**Actions**
- Introduce one explicit orchestration module for analysis.
- Normalize outputs from analysts.
- Standardize a `FinalAnalysis` object.
- Move synthesis concerns out of `run_paper_trading.py` where practical.

**Exit condition**
- A script can run analysis and produce final symbol-level conclusions without touching order execution.

---

### Phase 3 — Build manual-report pipeline as a first-class product

**Goal**
Restore the second main track.

**Actions**
- Create `generate_manual_trade_report.py`.
- Add report policy that transforms `FinalAnalysis` into trader-facing setups.
- Output one flat markdown artifact.
- Reuse screening/watchlist if helpful, but do not let them define the whole report UX.

**Exit condition**
- Julius can use the system without running auto-trade and still get a high-quality daily/adhoc decision report.

---

### Phase 4 — Demote paper runtime to downstream consumer

**Goal**
Keep demo auto-trading, but remove its architectural monopoly.

**Actions**
- Refactor `run_paper_trading.py` to call shared analysis core.
- Keep `RiskManager`, `PositionManager`, and `EntryGuard` as policy/execution concerns.
- Ensure execution uses `FinalAnalysis -> DemoExecutionDecision -> order execution`.

**Exit condition**
- Demo trading still works, but no longer acts as the de facto definition of the entire system.

---

### Phase 5 — Clean docs and naming

**Goal**
Make the repo reflect the actual product model.

**Actions**
- Update `README.md` and `docs/README.md`.
- Reframe docs around the 5 layers and 2 tracks.
- Clarify that calibration/backtesting support the core rather than define it.

**Exit condition**
- A new reader understands the intended system in under 5 minutes.

---

## 8. Concrete file direction

## Keep as shared core (but gradually reorganize)
- `agents/base_agent.py`
- `agents/technical_analyst.py`
- `agents/news_analyst.py`
- `agents/sentiment_analyst.py`
- `agents/research_debate.py`
- `agents/trader_agent.py`
- `dataflows/`

## Keep as demo-path-specific
- `scripts/run_paper_trading.py`
- `trading/`
- `agents/risk_manager.py`
- `agents/position_manager.py`
- `state/entry_guard.py`
- runtime supervision / control scripts

## Upgrade into manual-report-first assets
- `scripts/run_screening.py`
- `scripts/update_dynamic_watchlist.py`
- report rendering utilities that currently focus mostly on operational summaries

## Created by orchestration refactor
- `orchestration/analysis_runner.py`
- `orchestration/contracts.py`
- `policies/demo_execution.py`
- `policies/manual_report.py`
- `policies/reverse_planner.py`
- `scripts/generate_manual_trade_report.py`

These paths are now the canonical import locations. Avoid reintroducing shared analysis logic into `scripts/run_paper_trading.py`.

---

## 9. Architecture guardrails

Use these rules to prevent future drift.

### Guardrail 1
No analyst module may directly depend on order execution.

### Guardrail 2
No manual-report artifact should require paper-trading runtime to be running.

### Guardrail 3
Execution decisions must consume normalized shared analysis outputs.

### Guardrail 4
Analysis modes and execution modes must remain separate configuration axes.

### Guardrail 5
Operational reports are not a substitute for trader decision-support reports.

### Guardrail 6
If a new feature only helps demo execution, classify it explicitly as demo-path-only.

### Guardrail 7
If a new feature only helps manual trade review, classify it explicitly as manual-path-only.

---

## 10. Recommended next actions after the orchestration split

The initial rescue/refactor milestones are implemented. The next concrete tasks are:

1. **Repo inventory / tracking plan**
   - classify remaining untracked source, docs, generated artifacts, and private/runtime paths
   - propose `.gitignore` updates before any broad staging

2. **Runtime integration smoke**
   - run safe manual-report and demo-runtime smoke checks
   - verify no execution side effects unless an explicit execution mode is used

3. **Continue boundary hardening only where it protects the seam**
   - keep shared analysis importable without execution/runtime modules
   - keep manual-report defaults flat and execution-free

---

## 11. Final summary

The repo does **not** need to be thrown away.

The historical core issue was that:
- the **shared trading brain existed in pieces**, but
- the **paper-trading runtime became the dominant orchestration path**, and
- the **manual report product was not yet first-class**.

The rescue strategy remains:

1. keep the shared analysis pieces,
2. formalize synthesis as the true core,
3. split policy by use case,
4. keep demo auto-trade as one consumer,
5. keep manual decision reports as the second first-class consumer.

That gets the project back to its original idea without wasting the execution work already built.
