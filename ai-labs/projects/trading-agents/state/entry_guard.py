"""
Entry Guard - DCA-aware policy enforcement for new entries.

The EntryGuard sits immediately before OrderManager places a new order.
It is intentionally a policy layer only: it does not place orders,
close positions, or mutate DB state.

Rules:
  1. If enabled and enforce_trade_watchlist is true, symbols outside
     trade_watchlist are analyze-only and cannot auto-open.
  2. If an open position exists on the opposite side, block. Opposite
     side entries must use reverse flow, not a fresh entry.
  3. If no open same-side position exists, allow a first entry.
  4. If same-side positions exist, treat the candidate as DCA/add:
     - DCA must be enabled.
     - max_adds_per_symbol_side caps base + adds. With max_adds=3,
       max open same-side rows is 4 (base + 3 adds).
     - current price must be far enough from the nearest open entry.
     - confidence must be >= dca.min_confidence.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from utils import get_logger


logger = get_logger(__name__)


@dataclass
class GuardDecision:
    allowed: bool
    reason: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "details": self.details,
        }


class EntryGuard:
    """Evaluates whether a new entry is allowed."""

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        trade_watchlist: Optional[List[str]] = None,
    ):
        cfg = config or {}
        self.enabled: bool = bool(cfg.get("enabled", True))
        self.enforce_trade_watchlist: bool = bool(
            cfg.get("enforce_trade_watchlist", True)
        )
        self.block_opposite_side: bool = bool(cfg.get("block_opposite_side", True))
        self.notify_on_block: bool = bool(cfg.get("notify_on_block", True))
        self.trade_watchlist: List[str] = list(trade_watchlist or [])

        dca_cfg = cfg.get("dca") or {}
        self.dca_enabled: bool = bool(dca_cfg.get("enabled", True))
        self.max_adds_per_symbol_side: int = int(
            dca_cfg.get("max_adds_per_symbol_side", 3)
        )
        self.min_price_distance_pct: float = float(
            dca_cfg.get("min_price_distance_pct", 0.02)
        )
        self.dca_min_confidence: float = float(dca_cfg.get("min_confidence", 0.80))
        self.max_symbol_portfolio_pct: float = float(
            dca_cfg.get("max_symbol_portfolio_pct", 0.20)
        )
        self.max_leverage: float = float(dca_cfg.get("max_leverage", 10))
        self.close_behavior: str = str(dca_cfg.get("close_behavior", "close_group"))

    def set_trade_watchlist(self, watchlist: List[str]) -> None:
        self.trade_watchlist = list(watchlist or [])

    async def check(
        self,
        symbol: str,
        side: str,
        current_price: float,
        confidence: float,
        get_open_positions: Any,
        proposed_notional: float = 0.0,
        portfolio_value: float = 0.0,
        leverage: float = 1.0,
    ) -> GuardDecision:
        """Check whether a new entry is allowed.

        Args:
            symbol: e.g. "BTCUSDT".
            side: "LONG" or "SHORT".
            current_price: candidate entry price.
            confidence: final signal confidence.
            proposed_notional: notional value of the candidate new leg.
            portfolio_value: current portfolio value used for exposure cap.
            leverage: proposed leverage.
            get_open_positions: async callable(symbol) -> open position dicts
                for that symbol. Each dict should include side, entry_price,
                quantity, and trade_id.
        """
        side = (side or "").upper()
        if not self.enabled:
            return GuardDecision(True, "entry_guard_disabled")

        if not symbol or side not in ("LONG", "SHORT"):
            return GuardDecision(
                False,
                "missing_symbol_or_side",
                {"symbol": symbol, "side": side},
            )

        if current_price <= 0:
            return GuardDecision(
                False,
                "invalid_current_price",
                {"symbol": symbol, "side": side, "current_price": current_price},
            )

        if leverage > self.max_leverage:
            return GuardDecision(
                False,
                "leverage_too_high",
                {
                    "symbol": symbol,
                    "side": side,
                    "leverage": leverage,
                    "max_leverage": self.max_leverage,
                },
            )

        if self.enforce_trade_watchlist and self.trade_watchlist:
            if symbol not in self.trade_watchlist:
                return GuardDecision(
                    False,
                    "not_in_trade_watchlist",
                    {"symbol": symbol, "trade_watchlist": self.trade_watchlist},
                )

        open_positions = await get_open_positions(symbol)
        open_positions = open_positions or []
        same_side = [
            p for p in open_positions
            if (p.get("side") or "").upper() == side
        ]
        opposite_side = [
            p for p in open_positions
            if (p.get("side") or "").upper() in ("LONG", "SHORT")
            and (p.get("side") or "").upper() != side
        ]

        if opposite_side and self.block_opposite_side:
            return GuardDecision(
                False,
                "opposite_side_open",
                {
                    "symbol": symbol,
                    "candidate_side": side,
                    "opposite_trade_ids": [p.get("trade_id") for p in opposite_side],
                },
            )

        if not same_side:
            exposure_decision = self._check_symbol_exposure(
                symbol=symbol,
                side=side,
                open_positions=[],
                proposed_notional=proposed_notional,
                portfolio_value=portfolio_value,
            )
            if not exposure_decision.allowed:
                return exposure_decision
            return GuardDecision(
                True,
                "first_entry_allowed",
                {
                    "symbol": symbol,
                    "side": side,
                    "entry_kind": "base",
                    "dca_index": 0,
                    "position_group_id": None,
                    "close_behavior": self.close_behavior,
                },
            )

        return self._check_dca(
            symbol=symbol,
            side=side,
            current_price=current_price,
            confidence=confidence,
            same_side_positions=same_side,
            proposed_notional=proposed_notional,
            portfolio_value=portfolio_value,
        )

    def _check_dca(
        self,
        symbol: str,
        side: str,
        current_price: float,
        confidence: float,
        same_side_positions: List[Dict[str, Any]],
        proposed_notional: float,
        portfolio_value: float,
    ) -> GuardDecision:
        if not self.dca_enabled:
            return GuardDecision(
                False,
                "dca_disabled",
                {"symbol": symbol, "side": side},
            )

        max_open_rows = 1 + self.max_adds_per_symbol_side
        if len(same_side_positions) >= max_open_rows:
            return GuardDecision(
                False,
                "max_dca_adds_reached",
                {
                    "symbol": symbol,
                    "side": side,
                    "open_same_side_count": len(same_side_positions),
                    "max_open_rows": max_open_rows,
                    "max_adds_per_symbol_side": self.max_adds_per_symbol_side,
                },
            )

        if confidence < self.dca_min_confidence:
            return GuardDecision(
                False,
                "dca_confidence_too_low",
                {
                    "symbol": symbol,
                    "side": side,
                    "confidence": confidence,
                    "min_confidence": self.dca_min_confidence,
                },
            )

        exposure_decision = self._check_symbol_exposure(
            symbol=symbol,
            side=side,
            open_positions=same_side_positions,
            proposed_notional=proposed_notional,
            portfolio_value=portfolio_value,
        )
        if not exposure_decision.allowed:
            return exposure_decision

        entries = [float(p.get("entry_price") or 0) for p in same_side_positions]
        entries = [e for e in entries if e > 0]
        if not entries:
            return GuardDecision(
                False,
                "missing_existing_entry_price",
                {"symbol": symbol, "side": side},
            )

        nearest_entry = min(entries, key=lambda e: abs(current_price - e))
        distance_pct = abs(current_price - nearest_entry) / nearest_entry
        if distance_pct < self.min_price_distance_pct:
            return GuardDecision(
                False,
                "dca_price_too_close",
                {
                    "symbol": symbol,
                    "side": side,
                    "current_price": current_price,
                    "nearest_entry_price": nearest_entry,
                    "distance_pct": distance_pct,
                    "min_price_distance_pct": self.min_price_distance_pct,
                },
            )

        return GuardDecision(
            True,
            "dca_allowed",
            {
                "symbol": symbol,
                "side": side,
                "entry_kind": "dca",
                "position_group_id": self._resolve_group_id(same_side_positions),
                "dca_index": len(same_side_positions),
                "current_price": current_price,
                "nearest_entry_price": nearest_entry,
                "distance_pct": distance_pct,
                "confidence": confidence,
                "open_same_side_count": len(same_side_positions),
                "max_open_rows": max_open_rows,
                "close_behavior": self.close_behavior,
            },
        )

    def _check_symbol_exposure(
        self,
        symbol: str,
        side: str,
        open_positions: List[Dict[str, Any]],
        proposed_notional: float,
        portfolio_value: float,
    ) -> GuardDecision:
        if portfolio_value <= 0 or proposed_notional <= 0:
            return GuardDecision(True, "exposure_check_skipped")
        existing_notional = sum(
            float(p.get("entry_price") or 0) * float(p.get("quantity") or 0)
            for p in open_positions
        )
        projected = existing_notional + proposed_notional
        projected_pct = projected / portfolio_value
        if projected_pct > self.max_symbol_portfolio_pct:
            return GuardDecision(
                False,
                "symbol_exposure_cap_exceeded",
                {
                    "symbol": symbol,
                    "side": side,
                    "existing_notional": existing_notional,
                    "proposed_notional": proposed_notional,
                    "projected_notional": projected,
                    "portfolio_value": portfolio_value,
                    "projected_pct": projected_pct,
                    "max_symbol_portfolio_pct": self.max_symbol_portfolio_pct,
                },
            )
        return GuardDecision(True, "exposure_ok")

    def _resolve_group_id(self, same_side_positions: List[Dict[str, Any]]) -> Optional[str]:
        for p in same_side_positions:
            gid = p.get("position_group_id")
            if gid:
                return gid
        return same_side_positions[0].get("trade_id") if same_side_positions else None
