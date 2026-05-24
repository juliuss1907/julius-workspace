# Plan: AI Agent trong Trading (AI Agents in Trading)

**Slug:** `ai-agent-trading`
**Date:** 2026-05-22
**Language:** Vietnamese (output)
**Sources:** English + Vietnamese

---

## Scale Decision

**Type:** Broad survey / Landscape analysis
**Approach:** Multi-agent research using researcher subagents
**Rationale:** Topic spans multiple domains (AI/ML architectures, financial trading systems, regulation, production deployments). Direct search alone would miss systematic coverage. Subagents enable parallel evidence gathering across separate angles.

---

## Key Questions

1. **What are AI agents in trading?** — Definitions, architectures, how they differ from traditional algorithmic trading.
2. **What architectures and frameworks are used?** — RL-based agents, LLM-based agents, multi-agent systems, tool-use paradigms.
3. **Who are the key players?** — Companies, open-source projects, academic labs building AI trading agents.
4. **What is the empirical evidence?** — Benchmark results, backtest performance, live trading outcomes. What works vs what's hype?
5. **What are the risks and limitations?** — Overfitting, market regime change, regulatory concerns, explainability.
6. **What is the current landscape (mid-2026)?** — Latest products, papers, regulatory developments.

---

## Evidence Needed

| Evidence | Sources | Priority |
|---|---|---|
| Definitions and taxonomy of AI trading agents | Academic papers, survey papers | High |
| RL and deep RL for trading | arXiv papers, IJCAI/NeurIPS/ICML proceedings | High |
| LLM-based trading agents (e.g., FinAgent, TradingGPT) | arXiv, GitHub, official docs | High |
| Multi-agent trading systems | Papers, industry reports | Medium |
| Production platforms (e.g., Trade Ideas, Tickeron, Kavout, AlphaSense) | Company websites, news, product docs | High |
| Regulatory landscape (SEC, ESMA, MAS) | Official regulatory docs, news | Medium |
| Benchmark datasets and evaluation protocols | Papers, Kaggle, GitHub | High |
| Vietnamese context (AI trading tại Việt Nam, regulations by SSC) | Vietnamese news, government sites | Medium |

---

## Task Ledger

| # | Task | Owner | Status | Notes |
|---|---|---|---|---|
| T1 | Write researcher brief: AI trading agent taxonomy & architectures | Plan → brief file | ⬜ | |
| T2 | Write researcher brief: Industry players & production systems | Plan → brief file | ⬜ | |
| T3 | Write researcher brief: Academic papers & empirical results | Plan → brief file | ⬜ | |
| T4 | Write researcher brief: Risks, regulations & Vietnamese context | Plan → brief file | ⬜ | |
| R1 | Execute research: taxonomy & architectures | Researcher subagent | ⬜ | |
| R2 | Execute research: industry & production systems | Researcher subagent | ⬜ | |
| R3 | Execute research: academic papers & benchmarks | Researcher subagent | ⬜ | |
| R4 | Execute research: risks, regulations & VN context | Researcher subagent | ⬜ | |
| D1 | Synthesize draft (Vietnamese) | Lead | ⬜ | |
| V1 | Verify citations & sources | Verifier subagent | ⬜ | |
| V2 | Review & quality check | Reviewer subagent | ⬜ | |
| DEL | Deliver final files | Lead | ⬜ | |

---

## Verification Log

| Check | Status | Evidence |
|---|---|---|
| All 4 researcher briefs written | ⬜ | |
| All 4 research outputs received | ⬜ | |
| Directories exist | ✅ | outputs/.plans, outputs/.drafts, papers |
| Plan written | ✅ | This file |
| User approval | ⬜ | Waiting |

---

## Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-05-22 | Scale = multi-agent research | Topic is broad, multi-faceted, spans academia + industry + regulation |
| 2026-05-22 | Output language = Vietnamese | User requested "trình bày bằng tiếng Việt" |
| 2026-05-22 | 4 researcher roles | Covers: architectures, industry, academia, risks/regs/VN |
