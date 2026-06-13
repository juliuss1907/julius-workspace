"""
Signal Recorder

Persists structured per-symbol signal decisions as JSONL for later evaluation.
"""
import json
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Any

from utils import get_logger


logger = get_logger(__name__)


class SignalRecorder:
    """Append-only JSONL recorder for analyst and trader outputs."""

    def __init__(self, log_path: Optional[Path] = None):
        project_root = Path(__file__).parent.parent
        self.log_path = log_path or project_root / "logs" / "signals.jsonl"

    def record_signal(
        self,
        symbol: str,
        analyst_signals: Dict[str, Optional[Any]],
        draft_signal: Any,
        final_signal: Any,
        research_debate: Optional[Dict] = None,
        market_snapshot: Optional[Dict] = None,
        position_decision: Optional[Dict] = None,
        risk_decision: Optional[Dict] = None,
        trade_result: Optional[Any] = None,
        execution_status: str = "not_evaluated",
    ) -> Dict:
        """Build and append one signal record."""
        record = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "analysts": {
                name: self._agent_to_dict(signal)
                for name, signal in analyst_signals.items()
                if signal is not None
            },
            "missing_analysts": [name for name, signal in analyst_signals.items() if signal is None],
            "draft_signal": self._agent_to_dict(draft_signal),
            "final_signal": self._agent_to_dict(final_signal),
            "research_debate": self._sanitize(research_debate or {}),
            "market_snapshot": self._sanitize(market_snapshot or {}),
            "position_decision": self._sanitize(position_decision or {}),
            "risk_decision": self._sanitize(risk_decision or {}),
            "trade_result": self._trade_to_dict(trade_result),
            "execution_status": execution_status,
        }

        self._append(record)
        return record

    def _append(self, record: Dict):
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(self._sanitize(record), ensure_ascii=True, sort_keys=True) + "\n")
        except Exception as e:
            logger.error(f"Failed to record signal: {e}")

    def _agent_to_dict(self, signal: Optional[Any]) -> Optional[Dict]:
        if signal is None:
            return None
        if hasattr(signal, "to_dict"):
            return self._sanitize(signal.to_dict())
        return self._sanitize(signal)

    def _trade_to_dict(self, trade_result: Optional[Any]) -> Optional[Dict]:
        if trade_result is None:
            return None
        if hasattr(trade_result, "to_dict"):
            return self._sanitize(trade_result.to_dict())
        return self._sanitize(trade_result)

    def _sanitize(self, value):
        """Make nested values JSON-serializable without losing useful context."""
        if isinstance(value, dict):
            return {str(k): self._sanitize(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._sanitize(v) for v in value]
        if isinstance(value, tuple):
            return [self._sanitize(v) for v in value]
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)


signal_recorder = SignalRecorder()
