"""
Watchlist Manager
"""
import json
from pathlib import Path
from typing import List, Optional, Tuple


class Watchlist:
    """Manage watchlist of coins to analyze"""
    
    def __init__(self, filepath: str = "watchlist/watchlist.json"):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(exist_ok=True)
        self._coins = None
    
    def load(self) -> List[str]:
        """Load watchlist from file"""
        if self.filepath.exists():
            with open(self.filepath) as f:
                data = json.load(f)
                self._coins = data.get("coins", [])
        else:
            # Default watchlist
            self._coins = ["BTC", "ETH", "SOL"]
            self.save()
        
        return self._coins
    
    def save(self):
        """Save watchlist to file"""
        with open(self.filepath, "w") as f:
            json.dump({"coins": self._coins}, f, indent=2)
    
    def add(self, coin: str):
        """Add coin to watchlist"""
        if self._coins is None:
            self.load()
        
        if coin not in self._coins:
            self._coins.append(coin)
            self.save()
    
    def remove(self, coin: str):
        """Remove coin from watchlist"""
        if self._coins is None:
            self.load()
        
        if coin in self._coins:
            self._coins.remove(coin)
            self.save()
    
    def get_all(self) -> List[str]:
        """Get all coins in watchlist"""
        if self._coins is None:
            self.load()
        return self._coins.copy()


# Global watchlist instance
watchlist = Watchlist()


# ============================================================================
# Phase 8C: Guarded Runtime Watchlist Loader
# ============================================================================

# Symbol form expected by runtime (e.g. "BTCUSDT"). Set of allowed forms.
_USDT_SUFFIX = "USDT"


def _normalize_symbol(symbol: str) -> str:
    """Ensure symbol ends with USDT (uppercase)."""
    sym = str(symbol or "").upper().strip()
    if not sym:
        return ""
    if not sym.endswith(_USDT_SUFFIX):
        sym = sym + _USDT_SUFFIX
    return sym


def _normalize_list(symbols) -> List[str]:
    """Normalize, filter empties, and dedupe while preserving order."""
    seen = set()
    out = []
    for s in symbols or []:
        norm = _normalize_symbol(s)
        if not norm or norm in seen:
            continue
        seen.add(norm)
        out.append(norm)
    return out


def _read_json(path: Path):
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _resolve_path(path_str: str, project_root: Path) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        p = project_root / p
    return p


def evaluate_dynamic_watchlist(
    config: dict,
    project_root: Optional[Path] = None,
) -> Tuple[Optional[List[str]], str]:
    """
    Evaluate whether the dynamic watchlist proposal should be promoted to
    runtime. Returns a tuple (symbols, reason).

    - (None, reason)  → do NOT use dynamic; reason explains why
    - (list, reason)  → safe to use these symbols; reason explains why
    """
    if not config:
        return None, "config_missing"

    dw_cfg = config.get("dynamic_watchlist") or {}
    if not dw_cfg.get("enabled", False):
        return None, "dynamic_disabled_in_config"

    root = project_root or Path(__file__).parent.parent
    file_str = dw_cfg.get("output_json") or "watchlist/dynamic-watchlist.json"
    file_path = _resolve_path(file_str, root)
    data = _read_json(file_path)
    if data is None:
        return None, f"dynamic_file_missing:{file_path}"

    if not isinstance(data, dict):
        return None, "dynamic_file_malformed"

    if data.get("status") != "approved":
        return None, f"dynamic_status_not_approved:{data.get('status', 'unknown')}"

    if data.get("enabled_for_runtime") is not True:
        return None, "dynamic_enabled_for_runtime_false"

    selected = data.get("selected_symbols") or []
    if not selected:
        return None, "dynamic_selected_symbols_empty"

    normalized = _normalize_list(selected)
    if not normalized:
        return None, "dynamic_selected_symbols_invalid"

    allowed = dw_cfg.get("allowed_symbols") or []
    allowed_set = {_normalize_symbol(s) for s in allowed} if allowed else None
    if allowed_set is not None:
        before = len(normalized)
        normalized = [s for s in normalized if s in allowed_set]
        if not normalized:
            return None, "all_dynamic_symbols_filtered_by_allowlist"
        if len(normalized) < before:
            return normalized, f"dynamic_filtered_by_allowlist:{before - len(normalized)}_removed"

    return normalized, "dynamic_active"


def load_runtime_watchlist(
    config: dict,
    project_root: Optional[Path] = None,
    logger=None,
) -> List[str]:
    """
    Resolve the watchlist to use at runtime.

    Order of precedence (with safety):
      1. Static watchlist from `config.default_params.yaml -> watchlist`
         is always used as the base fallback.
      2. If `dynamic_watchlist.enabled` is true AND the dynamic proposal
         passes all guards, the dynamic list is used instead.
      3. Any guard failure logs a reason and falls back to the static list.

    This function never raises; any error falls back to static.
    """
    static_raw = (config or {}).get("watchlist") or ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    static = _normalize_list(static_raw) or ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

    if not (config or {}).get("dynamic_watchlist", {}).get("enabled", False):
        return static

    try:
        symbols, reason = evaluate_dynamic_watchlist(config, project_root=project_root)
    except Exception as e:
        if logger:
            logger.warning(f"Dynamic watchlist evaluation failed: {e}; using static")
        return static

    if symbols is None:
        if logger:
            logger.info(f"Dynamic watchlist inactive ({reason}); using static watchlist")
        return static

    if logger:
        logger.info(
            f"Dynamic watchlist active ({reason}); "
            f"using {len(symbols)} symbols: {symbols}"
        )
    return symbols

