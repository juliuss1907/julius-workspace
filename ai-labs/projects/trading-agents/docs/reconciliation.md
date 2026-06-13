# Reconciliation (Binance Futures testnet vs local DB)

## Goal
Keep `state/trading.db` `paper_positions` (futures) consistent with Binance
Futures testnet open positions. Detect three classes of drift and (optionally)
auto-correct or alert:

| Class | Meaning | Auto action (default) |
|---|---|---|
| `orphan_detected` | Binance has open position, DB has no open row | insert `*_SYNC_*` row |
| `db_missing_on_binance` | DB has open futures row, Binance shows zero | mark `status=closed`, `close_reason=closed_external` |
| `qty_mismatch` | Both have same (symbol, side) but qty diffs > tolerance | no auto-fix; alert only |
| `side_mismatch` | Both have same (symbol, side) but entry price diffs > tolerance | alert only |
| `ok` | qty and entry price within tolerance | record event only |

## Config
In `config/default_params.yaml`:
```yaml
runtime:
  reconciliation:
    enabled: false                       # off by default
    interval_seconds: 60
    run_before_cycle: true
    run_after_order: true
    auto_sync_orphans: true
    auto_close_db_missing: true
    auto_fix_qty_mismatch: false         # do NOT auto-fix qty by default
    qty_tolerance_pct: 0.5
    price_tolerance_pct: 0.5
    notify_mismatches: true
    notify_threshold_severity: warning
```

## CLI
```bash
# Single pass
./venv/bin/python scripts/reconcile_positions.py --once
./venv/bin/python scripts/reconcile_positions.py --once --json
./venv/bin/python scripts/reconcile_positions.py --once --no-auto-sync --no-auto-close-db

# Background polling loop (60s interval)
./venv/bin/python scripts/reconcile_positions.py --loop --interval 60
```

## Runtime integration
- Before each trading cycle, `TradingSystem.run_cycle()` calls
  `_run_reconciliation_once()` (gated by `reconciliation.run_before_cycle`).
- After each order, you may also call the same helper (gated by
  `reconciliation.run_after_order`).
- If the threshold severity produces at least one event, a single Telegram
  alert summarizes the diffs (capped at 10 lines).

## Storage
Two new tables in `state/trading.db`:
- `reconciliation_events` — one row per (symbol, side, event_type) per run.
- `reconciliation_state` — single-row last-run summary (id=1).

## Tests
- `scripts/test_reconciliation.py` — 8 unit tests with a mocked Binance client
  and a fresh per-test SQLite DB. Covers: orphan, db-missing, ok, qty-mismatch
  with auto-fix, no-mutation, side-mismatch, persistence, dry-run.

## Safety
- Module never places orders on Binance.
- Auto-mutations are limited to local DB (`paper_positions`).
- All actions and detected diffs are persisted to `reconciliation_events` for
  audit and post-mortem.
- The `qty_tolerance_pct` and `price_tolerance_pct` defaults (0.5%) are
  conservative; tighten only if you have a noisy account.
- Spot reconciliation is intentionally out of scope for this iteration.
  Reuse the same `Reconciler` pattern with a spot client when ready.

## Known limitations
- Single-position mode (`position_side='BOTH'`) only. Hedge mode is not
  detected; an open hedge position will show as a `qty_mismatch`.
- WebSocket user data stream is not used. Polling cadence defaults to 60s.
- The reconciler uses `paper_positions` as its DB source of truth and does not
  touch `paper_trades` except for the `closed_external` mirror.
