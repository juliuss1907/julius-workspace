# Trading Agents Repo — Inventory Review & Staging Recommendations

**Reviewed:** 2026-06-13  
**Scope:** `ai-labs/projects/trading-agents/` in parent repo `/home/julius/julius-workspace`  
**Inventory source:** generated working inventory; final reviewed classifications are captured in this report.  
**Status:** `.gitignore` patched; `reports/phase10a/` analysis notes moved to `docs/phase10a/`; no files staged at review creation time.

---

## 1. Summary

- **Total untracked paths in scope:** 136 entries (per inventory).
- **Git state after `.gitignore` patch:** 98 source/config/doc paths remain visible for staging; generated/runtime/private paths are now ignored.
- **No live trading or mutating scripts were executed.**
- **No secrets were read or printed.** Inspection relied on file paths, directory listings, and a sample of source/config files.
- **Julius decision applied:** track `watchlist/watchlist.json` as base source config; move and track phase10a analysis notes under `docs/phase10a/`.

### High-level classification counts

| Category | Count | Notes |
|---|---|---|
| Safe to track (source / ops / tests) | ~71 | agents, dataflows, main.py, scripts, state source modules, telegram_bot, trading, utils, ops/systemd examples |
| Safe docs to track | ~29 | docs/*.md, docs/phase10a/*.md, ops/README.md, trading-agent-idea.md |
| Safe config examples to track | 4 | .env.example, config/default_params.yaml, config/thresholds.yaml, config/coin_params/BTC.yaml.example |
| Should ignore / never track | ~50+ | .env, .hermes/, logs/, data/cache+session+db, state/*.db/cache/snapshots, reports/generated, venv/, dynamic watchlist output, __pycache__ |
| Needs sanitization | 0 | No hardcoded secrets found in inspected source |
| Needs human decision | 0 | Julius approved tracking base watchlist and moving phase10a notes to docs/ |

---

## 2. Safe to track now

These are source modules, operational helpers, tests, and templates with no observed secrets and no side-effect-on-import behavior.

### Core source

- `__init__.py`
- `main.py`
- `requirements.txt`
- `agents/` — all `*.py` source files
- `dataflows/` — all `*.py` source files
- `state/` — source modules only (see §5 for ignored runtime artifacts inside this dir)
  - `state/__init__.py`
  - `state/database.py`
  - `state/entry_guard.py`
  - `state/portfolio_context.py`
  - `state/reconciliation.py`
  - `state/runtime_health.py`
  - `state/schema.sql`
  - `state/signal_recorder.py`
- `telegram_bot/` — `__init__.py`, `bot.py`
- `trading/` — all `*.py` source files
- `utils/` — all `*.py` source files
- `ops/systemd/*.example` service templates
- `ops/README.md`

### Scripts (all `scripts/*.py` and `scripts/setup.sh`)

Reviewed the five Telegram auth scripts specifically (see §7). They read credentials from environment variables and write sessions to ignored `data/telegram_session`. No hardcoded secrets observed. Classification: **a) safe helper source to track after review**.

- `scripts/auth_telegram.py`
- `scripts/auth_telegram_cli.py`
- `scripts/auth_telegram_step1.py`
- `scripts/auth_telegram_step2.py`
- `scripts/authenticate_telegram.py`
- All other `scripts/*.py` (analysis, backtest, test, runtime control, etc.)

### Other safe files

- `trading-agent-idea.md` — concept doc, no secrets.

---

## 3. Safe docs to track

All docs inspected are safe, no secrets.

- `docs/01-architecture.md`
- `docs/02-data-sources.md`
- `docs/03-execution-layer.md`
- `docs/04-error-handling.md`
- `docs/05-state-management.md`
- `docs/06-data-storage.md`
- `docs/07-backtesting.md`
- `docs/08-confidence-scoring.md`
- `docs/09-position-sizing.md`
- `docs/10-monitoring.md`
- `docs/11-parameter-tuning.md`
- `docs/12-fine-tuning.md`
- `docs/13-implementation-roadmap.md`
- `docs/BACKTESTING.md`
- `docs/LITE_FULL_MODE.md`
- `docs/PAPER_TRADING.md`
- `docs/SESSION_HANDOFF_2026-06-06.md`
- `docs/TELEGRAM_BOT.md`
- `docs/alerting-policy.md`
- `docs/config-promotion-checklist.md`
- `docs/daily-ops-checklist.md`
- `docs/reconciliation.md`
- `docs/runtime-runbook.md`
- `docs/service-setup.md`
- `ops/README.md`
- `docs/phase10a/*.md` — analysis notes moved from `reports/phase10a/`

---

## 4. Safe config examples to track

- `.env.example` — verified placeholders only; safe.
- `config/default_params.yaml` — safe source config with default parameters.
- `config/thresholds.yaml` — safe source config with risk thresholds.
- `config/coin_params/BTC.yaml.example` — safe example override file.

**Caveat:** No `BTC.yaml` (non-example) exists yet. If created later, it should be ignored or treated as local runtime config unless Julius decides coin-specific params are source.

---

## 5. Should ignore / never track

### Already ignored before this review

| Path | Ignored by | Reason |
|---|---|---|
| `.env` | workspace `**/.env` | Live secrets |
| `venv/` | workspace + project `.gitignore` | Python environment |
| `__pycache__/` | workspace + project | Python bytecode cache |
| `*.pyc`, `*.pyo` | workspace + project | Compiled Python |
| `.vscode/`, `.idea/`, `*.swp` | project `.gitignore` | IDE/machine state |
| `logs/*.log*`, `logs/*.pid`, `logs/*.json*` | project `.gitignore` | Runtime logs |
| `data/ohlcv/*.csv`, `data/derivatives/*.db`, `data/cache/*.json`, `data/*.session*`, `data/*.session-journal` | project `.gitignore` | Runtime data/cache/session |
| `state/snapshots/*`, `state/cache/*`, `state/*.db`, `state/*.json` | project `.gitignore` | Runtime DB/state |
| `backups/` | project `.gitignore` | Backups |
| `.pytest_cache/`, `.coverage`, `htmlcov/` | project `.gitignore` | Test artifacts |

### Newly ignored by this patch

| Path | Reason |
|---|---|
| `.hermes/` | Hermes agent runtime plans/state; machine-local |
| `watchlist/dynamic-watchlist.json` | Generated proposal output |
| `watchlist/dynamic-watchlist.md` | Generated proposal output |
| `reports/backtest_report_*.md` | Generated backtest report |
| `reports/backtest-dashboard.*` | Generated dashboard |
| `reports/daily_report_*.md` | Generated daily report |
| `reports/optimization_results_*.csv` | Generated optimization CSV |
| `reports/parameter-recommendations.*` | Generated recommendations |
| `reports/calibration/` | Generated calibration artifacts |
| `reports/daily/` | Generated daily reports |
| `reports/flash/` | Generated flash reports |
| `reports/quick/` | Generated quick reports |
| `reports/reconciliation/` | Generated reconciliation reports |
| `reports/screening/` | Generated screening reports |
| `*.session`, `*.session-journal` | Telegram/session artifacts anywhere |
| `*.db`, `*.sqlite`, `*.sqlite3` | SQLite DBs anywhere |
| `data/phone_code_hash.pkl` | Telegram auth transient pickle file |
| `.cache/`, `.mypy_cache/` | Cache directories |

---

## 6. Needs sanitization

**None identified.**

Inspected source files (including Telegram auth scripts, `telegram_bot/bot.py`, `state/database.py`, `ops/systemd/*.example`, `main.py`) use environment variables or function parameters for credentials. No hardcoded API keys, tokens, phone numbers, passwords, or session strings were observed.

---

## 7. Telegram auth scripts classification

| Script | Classification | Rationale |
|---|---|---|
| `scripts/auth_telegram.py` | **a) safe helper source to track after review** | Reads `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_PHONE`, `TELEGRAM_CODE`, `TELEGRAM_2FA` from env; writes session to ignored `data/telegram_session.session`; no hardcoded secrets |
| `scripts/auth_telegram_cli.py` | **a) safe helper source to track after review** | Same pattern; takes code/2FA via CLI args; env-only credentials |
| `scripts/auth_telegram_step1.py` | **a) safe helper source to track after review** | Reads env credentials; sends code request; writes transient `data/phone_code_hash.pkl` (now ignored) |
| `scripts/auth_telegram_step2.py` | **a) safe helper source to track after review** | Reads env credentials + pickle; signs in; deletes pickle; writes session to ignored path |
| `scripts/authenticate_telegram.py` | **a) safe helper source to track after review** | Interactive version; reads env credentials; writes session to ignored path |

**Operational note:** These scripts should only be run manually by Julius when setting up Telegram. They should never be invoked by automated tests or CI.

---

## 8. Human decisions applied

### 8.1 `reports/phase10a/` — analysis notes moved to docs

**Finding:** `reports/phase10a/` contains three markdown analysis notes that read like documentation:

- `reports/phase10a/bias-investigation.md`
- `reports/phase10a/multi-symbol-comparison.md`
- `reports/phase10a/promotion-decisions.md`

They reference generated calibration data in `reports/calibration/` (now ignored) but the notes themselves are human-written analysis. They are currently the only untracked content under `reports/` after the `.gitignore` patch.

**Decision applied:** moved the three analysis notes to `docs/phase10a/` and track them there. This keeps `reports/` reserved for generated runtime output.

### 8.2 `watchlist/watchlist.json` — live config or runtime data?

**Finding:** `watchlist/watchlist.json` is a tiny config file:

```json
{
  "coins": ["BTC", "ETH", "SOL"]
}
```

It is referenced by `utils/watchlist.py` and is effectively live trading configuration. `watchlist/dynamic-watchlist.*` are generated proposals and are now ignored.

**Decision applied:** track `watchlist/watchlist.json` as source config; keep `watchlist/dynamic-watchlist.*` ignored as generated proposal output.

---

## 9. Recommended `.gitignore` changes

Patched file: `ai-labs/projects/trading-agents/.gitignore`

### Diff

```diff
diff --git a/ai-labs/projects/trading-agents/.gitignore b/ai-labs/projects/trading-agents/.gitignore
index 12c3532..560ef37 100644
--- a/ai-labs/projects/trading-agents/.gitignore
+++ b/ai-labs/projects/trading-agents/.gitignore
@@ -48,6 +48,41 @@ reports/manual-trade-report-smoke.md
 # Jupyter
 .ipynb_checkpoints/

+# Hermes / agent runtime state
+.hermes/
+
+# Runtime-generated watchlist proposals
+watchlist/dynamic-watchlist.json
+watchlist/dynamic-watchlist.md
+
+# Generated reports (runtime output) — keep reports/phase10a/ analysis notes
+reports/backtest_report_*.md
+reports/backtest-dashboard.*
+reports/daily_report_*.md
+reports/optimization_results_*.csv
+reports/parameter-recommendations.*
+reports/calibration/
+reports/daily/
+reports/flash/
+reports/quick/
+reports/reconciliation/
+reports/screening/
+
+# Session / DB artifacts anywhere in project
+*.session
+*.session-journal
+*.db
+*.sqlite
+*.sqlite3
+
+# Auth transient state
+data/phone_code_hash.pkl
+
+# Cache directories
+.cache/
+.mypy_cache/
+
 # Testing
 .pytest_cache/
 .coverage
```

### Why not broad `*auth*`, `*token*`, `*secret*` ignores?

No broad auth/token/secret ignore patterns were added because:

- The only source files matching `*auth*` are the five Telegram auth scripts, which are safe source code.
- Broad patterns risk accidentally ignoring legitimate modules in the future (e.g., an `authenticator.py` utility).
- All actual secret material lives in `.env` (already ignored by workspace `**/.env`) and `*.session` files (now ignored).

---

## 10. Suggested staging batches

**Do NOT run `git add ai-labs/projects/trading-agents/`.** Use explicit batches.

### Batch 1 — Core source + entry point

```bash
git add -- ai-labs/projects/trading-agents/__init__.py \
           ai-labs/projects/trading-agents/main.py \
           ai-labs/projects/trading-agents/requirements.txt
```

### Batch 2 — Agent modules

```bash
git add -- ai-labs/projects/trading-agents/agents/
```

### Batch 3 — Dataflows + utilities

```bash
git add -- ai-labs/projects/trading-agents/dataflows/ \
           ai-labs/projects/trading-agents/utils/
```

### Batch 4 — State source modules (not DB/cache)

```bash
git add -- ai-labs/projects/trading-agents/state/__init__.py \
           ai-labs/projects/trading-agents/state/database.py \
           ai-labs/projects/trading-agents/state/entry_guard.py \
           ai-labs/projects/trading-agents/state/portfolio_context.py \
           ai-labs/projects/trading-agents/state/reconciliation.py \
           ai-labs/projects/trading-agents/state/runtime_health.py \
           ai-labs/projects/trading-agents/state/schema.sql \
           ai-labs/projects/trading-agents/state/signal_recorder.py
```

### Batch 5 — Trading + Telegram bot

```bash
git add -- ai-labs/projects/trading-agents/trading/ \
           ai-labs/projects/trading-agents/telegram_bot/
```

### Batch 6 — Scripts (including reviewed auth helpers)

```bash
git add -- ai-labs/projects/trading-agents/scripts/
```

### Batch 7 — Config + config example

```bash
git add -- ai-labs/projects/trading-agents/.env.example \
           ai-labs/projects/trading-agents/config/default_params.yaml \
           ai-labs/projects/trading-agents/config/thresholds.yaml \
           ai-labs/projects/trading-agents/config/coin_params/BTC.yaml.example
```

### Batch 8 — Docs

```bash
git add -- ai-labs/projects/trading-agents/docs/ \
           ai-labs/projects/trading-agents/ops/README.md \
           ai-labs/projects/trading-agents/trading-agent-idea.md
```

### Batch 9 — Ops templates

```bash
git add -- ai-labs/projects/trading-agents/ops/systemd/*.example
```

### Batch 10 — Pending Julius decision

```bash
# Track base watchlist as source config
git add -- ai-labs/projects/trading-agents/watchlist/watchlist.json

# Track moved phase10a analysis notes
git add -- ai-labs/projects/trading-agents/docs/phase10a/
```

### One-liner safe staging command (excludes generated/private/decision items)

```bash
git add -- ai-labs/projects/trading-agents/__init__.py \
           ai-labs/projects/trading-agents/main.py \
           ai-labs/projects/trading-agents/requirements.txt \
           ai-labs/projects/trading-agents/agents/ \
           ai-labs/projects/trading-agents/dataflows/ \
           ai-labs/projects/trading-agents/utils/ \
           ai-labs/projects/trading-agents/state/__init__.py \
           ai-labs/projects/trading-agents/state/database.py \
           ai-labs/projects/trading-agents/state/entry_guard.py \
           ai-labs/projects/trading-agents/state/portfolio_context.py \
           ai-labs/projects/trading-agents/state/reconciliation.py \
           ai-labs/projects/trading-agents/state/runtime_health.py \
           ai-labs/projects/trading-agents/state/schema.sql \
           ai-labs/projects/trading-agents/state/signal_recorder.py \
           ai-labs/projects/trading-agents/trading/ \
           ai-labs/projects/trading-agents/telegram_bot/ \
           ai-labs/projects/trading-agents/scripts/ \
           ai-labs/projects/trading-agents/.env.example \
           ai-labs/projects/trading-agents/config/default_params.yaml \
           ai-labs/projects/trading-agents/config/thresholds.yaml \
           ai-labs/projects/trading-agents/config/coin_params/BTC.yaml.example \
           ai-labs/projects/trading-agents/docs/ \
           ai-labs/projects/trading-agents/ops/README.md \
           ai-labs/projects/trading-agents/ops/systemd/*.example \
           ai-labs/projects/trading-agents/trading-agent-idea.md
```

**After staging, verify with:**

```bash
git status --short -- ai-labs/projects/trading-agents
```

Expected: only generated/private/decision items remain untracked (and the staged items show `A`).

---

## 11. Risks / unknowns

1. **`.env` is ignored but exists on disk.** This is correct behavior. Do not track it. If Julius wants a backup, use a password manager, not Git.
2. **`data/telegram_session.session` exists on disk.** It is ignored. It should be regenerated on a new machine from `.env` + auth scripts.
3. **`state/trading.db` and `state/test_recon.db` exist on disk.** They are ignored. They contain paper-trading state and should not be tracked.
4. **`docs/phase10a/` contains former `reports/phase10a/` analysis notes.** They are project knowledge, not generated runtime reports.
5. **Not all 136 files were read line-by-line.** Classification is based on path conventions, directory listings, and spot checks of representative files. A secret could theoretically hide in an uninspected file, but the path-based ignores (.env, *.session, *.db) cover the highest-risk categories.
6. **Some scripts may perform live exchange actions when executed.** They are safe to *track* as source, but they must not be *run* without Julius's explicit dry-run/single-cycle scope. This review does not validate runtime behavior.
7. **`.gitignore` patch assumes generated report patterns should stay ignored.** Keep future project knowledge under `docs/`, not `reports/`.

---

## 12. Commands run

All commands are non-mutating except the `.gitignore` edit.

```bash
# Read inventory report
# (read file: ai-labs/projects/trading-agents-repo-inventory.md)

# Inspect git status
git status --short -- ai-labs/projects/trading-agents

# Find .gitignore files
glob **/.gitignore

# Read project .gitignore and workspace .gitignore
# Read .env.example, config files, watchlist files, state source files
# Read Telegram auth scripts (5 files)
# Read telegram_bot/bot.py, main.py, requirements.txt, ops files

# Find auth/token/secret/session/DB files
find ai-labs/projects/trading-agents -type f \( \
  -iname '*auth*' -o -iname '*token*' -o -iname '*secret*' -o \
  -iname '*.session' -o -iname '*.session-journal' -o \
  -iname '*.db' -o -iname '*.sqlite' -o -iname '*.sqlite3' \
\) | sort

# List key directories
find ai-labs/projects/trading-agents/data -maxdepth 3 -type f | head -50
find ai-labs/projects/trading-agents/logs -maxdepth 2 -type f | head -50
find ai-labs/projects/trading-agents/backtests -maxdepth 2 -type f | head -50
find ai-labs/projects/trading-agents/venv -maxdepth 2 -type f | head -20
find ai-labs/projects/trading-agents/reports -type f | sort

# Verify .gitignore effect after patch
git diff -- ai-labs/projects/trading-agents/.gitignore
git status --short -- ai-labs/projects/trading-agents ai-labs/projects/trading-agents-inventory-review.md
```

---

## 13. Next steps for Julius / Hermes

1. **Approve the `.gitignore` patch** (already applied; Hermes removed one duplicate ignore entry after this review; review current diff before staging).
2. **Stage the approved baseline**, including `watchlist/watchlist.json` and `docs/phase10a/`.
3. **Inspect `git status` and `git diff --cached --name-only`** before committing.
5. **Do not run live trading scripts** during staging verification.
6. **After staging, commit** only if explicitly instructed.

---

*End of review.*
