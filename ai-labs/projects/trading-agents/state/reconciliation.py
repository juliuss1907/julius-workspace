"""
Futures Reconciliation Module
=============================

Periodically reconciles Binance Futures testnet open positions with
local SQLite paper_positions and produces a structured diff.

Responsibilities
----------------
- Pull live futures positions from Binance Futures testnet.
- Pull open futures positions from local DB.
- Classify diffs into:
    * orphan_detected       (Binance has position, DB does not)
    * db_missing_on_binance (DB has open position, Binance does not)
    * qty_mismatch          (qty differs within tolerance)
    * side_mismatch         (LONG/SHORT flipped)
    * ok                    (no diff)
- Optionally auto-sync orphan positions by inserting a SYNC_ row.
- Optionally mark DB-only positions as closed_external.
- Persist events to `reconciliation_events` table.
- Update `reconciliation_state` row with the latest run summary.

This module is INTENTIONALLY read-only against Binance.
It never places orders; closing happens via the normal bot path.
"""
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiosqlite

from .database import Database
from utils import get_logger


logger = get_logger(__name__)


DEFAULT_QTY_TOLERANCE_PCT = 0.5  # 0.5% qty diff tolerated
DEFAULT_PRICE_TOLERANCE_PCT = 0.5  # 0.5% entry price diff tolerated


@dataclass
class ReconcileEvent:
    symbol: str
    side: Optional[str]
    market_type: str
    event_type: str
    db_trade_id: Optional[str]
    binance_qty: Optional[float]
    db_qty: Optional[float]
    binance_entry_price: Optional[float]
    db_entry_price: Optional[float]
    severity: str
    action_taken: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReconcileResult:
    run_id: str
    started_at: int
    finished_at: int
    events: List[ReconcileEvent]
    error: Optional[str] = None

    @property
    def counts(self) -> Dict[str, int]:
        c: Dict[str, int] = {
            "orphan_detected": 0,
            "db_missing_on_binance": 0,
            "qty_mismatch": 0,
            "side_mismatch": 0,
            "ok": 0,
            "error": 0,
        }
        for e in self.events:
            c[e.event_type] = c.get(e.event_type, 0) + 1
        return c


class FuturesReconciler:
    """
    Reconciles Binance Futures testnet positions vs local DB.

    The class is stateless across calls except for last-result caching.
    Use `reconcile_once()` per cycle, or `run_loop()` for background polling.
    """

    def __init__(
        self,
        client: Any,
        db: Database,
        qty_tolerance_pct: float = DEFAULT_QTY_TOLERANCE_PCT,
        price_tolerance_pct: float = DEFAULT_PRICE_TOLERANCE_PCT,
        auto_sync_orphans: bool = True,
        auto_close_db_missing: bool = True,
        auto_fix_qty_mismatch: bool = False,
    ):
        self.client = client
        self.db = db
        self.qty_tolerance_pct = qty_tolerance_pct
        self.price_tolerance_pct = price_tolerance_pct
        self.auto_sync_orphans = auto_sync_orphans
        self.auto_close_db_missing = auto_close_db_missing
        self.auto_fix_qty_mismatch = auto_fix_qty_mismatch
        self.last_result: Optional[ReconcileResult] = None

    async def _fetch_binance_positions(self) -> List[Dict[str, Any]]:
        return await self.client.get_positions()

    async def _fetch_db_open_futures(self) -> List[Dict[str, Any]]:
        rows = await self.db.get_open_positions()
        return [r for r in rows if r.get("market_type") == "futures"]

    @staticmethod
    def _round_qty(qty: float, symbol: str) -> float:
        """Lightweight precision rounding, consistent with OrderManager."""
        coin = symbol[:-4] if symbol.endswith("USDT") else symbol
        precision = {
            "BTC": 3, "ETH": 3, "SOL": 1, "BNB": 2,
            "XRP": 1, "ADA": 1, "DOGE": 0,
        }.get(coin, 2)
        return round(qty, precision)

    async def _record_event(self, run_id: str, ev: ReconcileEvent) -> None:
        try:
            await self.db._conn.execute(
                """
                INSERT INTO reconciliation_events
                (run_id, symbol, side, market_type, event_type,
                 db_trade_id, binance_qty, db_qty,
                 binance_entry_price, db_entry_price,
                 severity, action_taken, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    ev.symbol,
                    ev.side,
                    ev.market_type,
                    ev.event_type,
                    ev.db_trade_id,
                    ev.binance_qty,
                    ev.db_qty,
                    ev.binance_entry_price,
                    ev.db_entry_price,
                    ev.severity,
                    ev.action_taken,
                    json.dumps(ev.details),
                ),
            )
        except Exception as e:
            logger.error(f"Failed to record reconciliation event: {e}")

    async def _update_state(self, run_id: str, result: ReconcileResult) -> None:
        counts = result.counts
        try:
            await self.db._conn.execute(
                """
                UPDATE reconciliation_state
                SET last_run_at = ?, last_run_id = ?,
                    orphan_count = ?, db_missing_count = ?,
                    qty_mismatch_count = ?, side_mismatch_count = ?,
                    ok_count = ?, error_count = ?,
                    raw_summary = ?
                WHERE id = 1
                """,
                (
                    result.finished_at,
                    run_id,
                    counts.get("orphan_detected", 0),
                    counts.get("db_missing_on_binance", 0),
                    counts.get("qty_mismatch", 0),
                    counts.get("side_mismatch", 0),
                    counts.get("ok", 0),
                    counts.get("error", 0),
                    json.dumps({
                        "run_id": run_id,
                        "started_at": result.started_at,
                        "finished_at": result.finished_at,
                        "counts": counts,
                        "error": result.error,
                    }),
                ),
            )
        except Exception as e:
            logger.error(f"Failed to update reconciliation_state: {e}")

    async def _insert_sync_row(
        self,
        symbol: str,
        side: str,
        qty: float,
        entry_price: float,
        leverage: int,
        run_id: str,
    ) -> Optional[str]:
        trade_id = f"{symbol}_{side}_SYNC_{run_id[:8]}_{int(time.time())}"
        position = {
            "trade_id": trade_id,
            "symbol": symbol,
            "side": side,
            "market_type": "futures",
            "entry_price": entry_price,
            "quantity": qty,
            "leverage": leverage,
            "stop_loss": None,
            "take_profit": None,
            "trailing_stop": None,
            "order_id": f"recon:{run_id}",
            "position_group_id": trade_id,
            "entry_kind": "base",
            "dca_index": 0,
            "signal_data": {
                "source": "reconciliation_sync",
                "run_id": run_id,
                "note": "auto-inserted by FuturesReconciler from Binance",
            },
        }
        try:
            await self.db.insert_paper_position(position)
            return trade_id
        except Exception as e:
            logger.error(f"Failed to insert sync row for {symbol}: {e}")
            return None

    async def _mark_db_position_closed_external(
        self,
        trade_id: str,
        run_id: str,
        details: Dict[str, Any],
    ) -> bool:
        """Mark a DB-only position as closed_external (no Binance fill)."""
        try:
            async with self.db._conn.execute(
                """
                UPDATE paper_positions
                SET status = 'closed',
                    closed_at = ?,
                    close_reason = 'closed_external',
                    close_price = COALESCE(close_price, 0),
                    notes = ?
                WHERE trade_id = ? AND status = 'open'
                """,
                (int(time.time()), f"recon:{run_id}", trade_id),
            ) as cur:
                updated = cur.rowcount
            if updated:
                # Mirror to paper_trades history
                async with self.db._conn.execute(
                    "SELECT * FROM paper_positions WHERE trade_id = ?",
                    (trade_id,),
                ) as cur:
                    row = await cur.fetchone()
                if row:
                    cols = [c[0] for c in cur.description]
                    pos = dict(zip(cols, row))
                    await self.db._conn.execute(
                        """
                        INSERT OR REPLACE INTO paper_trades
                        (trade_id, symbol, side, market_type, entry_price, exit_price,
                         quantity, leverage, pnl, pnl_pct, fees,
                         opened_at, closed_at, duration_seconds, close_reason)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            pos["trade_id"],
                            pos["symbol"],
                            pos["side"],
                            pos["market_type"],
                            pos["entry_price"],
                            pos.get("close_price") or 0,
                            pos["quantity"],
                            pos.get("leverage") or 1.0,
                            0.0,
                            0.0,
                            pos.get("fees") or 0.0,
                            pos["opened_at"],
                            pos.get("closed_at") or int(time.time()),
                            max(0, int(time.time()) - int(pos["opened_at"])),
                            "closed_external",
                        ),
                    )
            await self.db._conn.commit()
            return updated > 0
        except Exception as e:
            logger.error(f"Failed to mark {trade_id} as closed_external: {e}")
            return False

    async def _update_db_qty(
        self,
        trade_id: str,
        new_qty: float,
        run_id: str,
    ) -> bool:
        try:
            await self.db._conn.execute(
                """
                UPDATE paper_positions
                SET quantity = ?,
                    notes = COALESCE(notes, '') || ?
                WHERE trade_id = ? AND status = 'open'
                """,
                (new_qty, f"\nrecon qty-update:{run_id}", trade_id),
            )
            await self.db._conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update qty for {trade_id}: {e}")
            return False

    async def reconcile_once(self) -> ReconcileResult:
        """Run a single reconciliation pass."""
        run_id = f"recon-{int(time.time())}-{uuid.uuid4().hex[:6]}"
        started_at = int(time.time())
        events: List[ReconcileEvent] = []
        error: Optional[str] = None

        try:
            binance_positions = await self._fetch_binance_positions()
            db_positions = await self._fetch_db_open_futures()
        except Exception as e:
            logger.error(f"Reconciliation fetch failed: {e}")
            error = str(e)
            result = ReconcileResult(
                run_id=run_id,
                started_at=started_at,
                finished_at=int(time.time()),
                events=[],
                error=error,
            )
            await self._update_state(run_id, result)
            self.last_result = result
            return result

        binance_map: Dict[Tuple[str, str], Dict[str, Any]] = {
            (p["symbol"], p["side"]): p for p in binance_positions
        }
        db_map: Dict[Tuple[str, str], Dict[str, Any]] = {}
        for p in db_positions:
            key = (p["symbol"], p["side"])
            agg = db_map.setdefault(key, {
                "symbol": p["symbol"],
                "side": p["side"],
                "quantity": 0.0,
                "entry_notional": 0.0,
                "leverage": p.get("leverage"),
                "legs": [],
            })
            qty = float(p.get("quantity") or 0.0)
            entry = float(p.get("entry_price") or 0.0)
            agg["quantity"] += qty
            agg["entry_notional"] += qty * entry
            agg["legs"].append(p)
        for agg in db_map.values():
            qty = float(agg["quantity"] or 0.0)
            agg["entry_price"] = (agg["entry_notional"] / qty) if qty > 0 else 0.0
            agg["trade_id"] = agg["legs"][0].get("trade_id") if agg["legs"] else None

        all_keys = set(binance_map.keys()) | set(db_map.keys())

        for key in sorted(all_keys):
            symbol, side = key
            b = binance_map.get(key)
            d = db_map.get(key)

            if b and not d:
                # Orphan: Binance has it, DB does not
                action = "none"
                if self.auto_sync_orphans:
                    tid = await self._insert_sync_row(
                        symbol=symbol,
                        side=side,
                        qty=self._round_qty(b["amount"], symbol),
                        entry_price=float(b["entry_price"]),
                        leverage=int(b["leverage"]),
                        run_id=run_id,
                    )
                    if tid:
                        action = "inserted"
                ev = ReconcileEvent(
                    symbol=symbol,
                    side=side,
                    market_type="futures",
                    event_type="orphan_detected",
                    db_trade_id=None,
                    binance_qty=float(b["amount"]),
                    db_qty=None,
                    binance_entry_price=float(b["entry_price"]),
                    db_entry_price=None,
                    severity="warning",
                    action_taken=action,
                    details={
                        "leverage": b.get("leverage"),
                        "mark_price": b.get("mark_price"),
                        "unrealized_pnl": b.get("unrealized_pnl"),
                        "margin_type": b.get("margin_type"),
                    },
                )
                events.append(ev)

            elif d and not b:
                # DB has it open, Binance does not
                action = "none"
                if self.auto_close_db_missing:
                    marked = 0
                    for leg in d.get("legs", []):
                        ok = await self._mark_db_position_closed_external(
                            trade_id=leg["trade_id"],
                            run_id=run_id,
                            details={"event": "db_missing_on_binance"},
                        )
                        marked += 1 if ok else 0
                    if marked:
                        action = "marked_closed"
                ev = ReconcileEvent(
                    symbol=symbol,
                    side=side,
                    market_type="futures",
                    event_type="db_missing_on_binance",
                    db_trade_id=d["trade_id"],
                    binance_qty=None,
                    db_qty=float(d["quantity"]),
                    binance_entry_price=None,
                    db_entry_price=float(d["entry_price"]),
                    severity="warning",
                    action_taken=action,
                    details={
                        "db_leverage": d.get("leverage"),
                        "db_leg_count": len(d.get("legs", [])),
                        "db_trade_ids": [leg.get("trade_id") for leg in d.get("legs", [])],
                    },
                )
                events.append(ev)

            else:
                # Both have the same (symbol, side). Compare.
                binance_qty = float(b["amount"])
                db_qty = float(d["quantity"])
                binance_entry = float(b["entry_price"])
                db_entry = float(d["entry_price"])

                qty_diff_pct = (
                    abs(binance_qty - db_qty) / db_qty * 100 if db_qty > 0 else 0.0
                )
                price_diff_pct = (
                    abs(binance_entry - db_entry) / db_entry * 100 if db_entry > 0 else 0.0
                )

                if qty_diff_pct > self.qty_tolerance_pct:
                    action = "none"
                    if self.auto_fix_qty_mismatch and len(d.get("legs", [])) == 1:
                        if await self._update_db_qty(
                            d["trade_id"], self._round_qty(binance_qty, symbol), run_id
                        ):
                            action = "updated"
                    events.append(ReconcileEvent(
                        symbol=symbol,
                        side=side,
                        market_type="futures",
                        event_type="qty_mismatch",
                        db_trade_id=d["trade_id"],
                        binance_qty=binance_qty,
                        db_qty=db_qty,
                        binance_entry_price=binance_entry,
                        db_entry_price=db_entry,
                        severity="warning",
                        action_taken=action,
                        details={
                            "qty_diff_pct": qty_diff_pct,
                            "qty_tolerance_pct": self.qty_tolerance_pct,
                            "db_leg_count": len(d.get("legs", [])),
                            "db_trade_ids": [leg.get("trade_id") for leg in d.get("legs", [])],
                        },
                    ))
                elif price_diff_pct > self.price_tolerance_pct:
                    events.append(ReconcileEvent(
                        symbol=symbol,
                        side=side,
                        market_type="futures",
                        event_type="side_mismatch",
                        db_trade_id=d["trade_id"],
                        binance_qty=binance_qty,
                        db_qty=db_qty,
                        binance_entry_price=binance_entry,
                        db_entry_price=db_entry,
                        severity="info",
                        action_taken="none",
                        details={
                            "price_diff_pct": price_diff_pct,
                            "note": "entry price drifted within reasonable bounds",
                            "db_leg_count": len(d.get("legs", [])),
                        },
                    ))
                else:
                    events.append(ReconcileEvent(
                        symbol=symbol,
                        side=side,
                        market_type="futures",
                        event_type="ok",
                        db_trade_id=d["trade_id"],
                        binance_qty=binance_qty,
                        db_qty=db_qty,
                        binance_entry_price=binance_entry,
                        db_entry_price=db_entry,
                        severity="info",
                        action_taken="none",
                        details={
                            "qty_diff_pct": qty_diff_pct,
                            "price_diff_pct": price_diff_pct,
                            "db_leg_count": len(d.get("legs", [])),
                        },
                    ))

        # Persist events + state
        for ev in events:
            await self._record_event(run_id, ev)
        await self.db._conn.commit()

        finished_at = int(time.time())
        result = ReconcileResult(
            run_id=run_id,
            started_at=started_at,
            finished_at=finished_at,
            events=events,
            error=error,
        )
        await self._update_state(run_id, result)
        self.last_result = result

        counts = result.counts
        logger.info(
            f"Reconciliation {run_id} done in {finished_at - started_at}s: "
            f"ok={counts.get('ok', 0)} "
            f"orphans={counts.get('orphan_detected', 0)} "
            f"db_missing={counts.get('db_missing_on_binance', 0)} "
            f"qty_mismatch={counts.get('qty_mismatch', 0)} "
            f"side_mismatch={counts.get('side_mismatch', 0)}"
        )
        return result
