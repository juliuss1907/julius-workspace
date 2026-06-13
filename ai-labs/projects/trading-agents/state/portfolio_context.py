"""
Portfolio Context

Builds a compact exposure snapshot from open paper positions for risk checks.
"""
from typing import Dict, List, Optional

from utils import config


class PortfolioContextBuilder:
    """Summarize open positions into symbol, market, side, and correlation exposure."""

    def __init__(self, config_override: Optional[Dict] = None):
        default_config = config.load_default_params()
        self.config = {**default_config, **(config_override or {})}
        risk_manager_config = self.config.get("risk_manager", {})
        self.correlated_groups = risk_manager_config.get("correlated_groups", {})

    def build(
        self,
        open_positions: Optional[List[Dict]] = None,
        portfolio_stats: Optional[Dict] = None,
        current_prices: Optional[Dict[str, float]] = None,
    ) -> Dict:
        open_positions = open_positions or []
        portfolio_stats = portfolio_stats or {}
        current_prices = current_prices or {}

        total_balance = self._float(portfolio_stats.get("total_balance"))
        if total_balance <= 0:
            latest_snapshot = portfolio_stats.get("latest_snapshot") or {}
            total_balance = self._float(latest_snapshot.get("total_equity"))

        symbol_exposure = {}
        market_exposure = {}
        side_exposure = {}
        position_details = []
        total_notional = 0.0

        for position in open_positions:
            symbol = position.get("symbol", "unknown")
            market_type = position.get("market_type", "unknown")
            side = position.get("side", "unknown")
            price = self._float(current_prices.get(symbol)) or self._float(position.get("entry_price"))
            quantity = self._float(position.get("quantity"))
            leverage = max(1.0, self._float(position.get("leverage")) or 1.0)
            notional = abs(quantity * price * leverage)

            symbol_exposure[symbol] = symbol_exposure.get(symbol, 0.0) + notional
            market_exposure[market_type] = market_exposure.get(market_type, 0.0) + notional
            side_exposure[side] = side_exposure.get(side, 0.0) + notional
            total_notional += notional
            position_details.append({
                "symbol": symbol,
                "side": side,
                "market_type": market_type,
                "notional": notional,
                "exposure_pct": self._pct(notional, total_balance),
            })

        correlated_exposure = self._correlated_exposure(symbol_exposure)
        return {
            "total_balance": total_balance,
            "open_positions_count": len(open_positions),
            "total_notional": total_notional,
            "total_exposure_pct": self._pct(total_notional, total_balance),
            "symbol_exposure": symbol_exposure,
            "symbol_exposure_pct": {symbol: self._pct(value, total_balance) for symbol, value in symbol_exposure.items()},
            "market_exposure": market_exposure,
            "market_exposure_pct": {market: self._pct(value, total_balance) for market, value in market_exposure.items()},
            "side_exposure": side_exposure,
            "side_exposure_pct": {side: self._pct(value, total_balance) for side, value in side_exposure.items()},
            "correlated_exposure": correlated_exposure,
            "correlated_exposure_pct": {
                group: self._pct(value, total_balance) for group, value in correlated_exposure.items()
            },
            "positions": position_details,
        }

    def group_for_symbol(self, symbol: str) -> Optional[str]:
        coin = self._coin(symbol)
        for group, coins in self.correlated_groups.items():
            if coin in coins:
                return group
        return None

    def _correlated_exposure(self, symbol_exposure: Dict[str, float]) -> Dict[str, float]:
        exposure = {group: 0.0 for group in self.correlated_groups}
        for symbol, notional in symbol_exposure.items():
            coin = self._coin(symbol)
            for group, coins in self.correlated_groups.items():
                if coin in coins:
                    exposure[group] += notional
        return {group: value for group, value in exposure.items() if value > 0}

    def _coin(self, symbol: str) -> str:
        return symbol[:-4] if symbol.endswith("USDT") else symbol

    def _pct(self, value: float, total: float) -> float:
        return (value / total) if total > 0 else 0.0

    def _float(self, value) -> float:
        try:
            return float(value or 0.0)
        except (TypeError, ValueError):
            return 0.0
