#!/usr/bin/env python3
"""
Trade Simulation — Phase 6C + 6F.

Walks replay signal JSONL records chronologically per symbol and simulates
entry/exit based on directional signals.

Phase 6C: opposite-signal exit only.
Phase 6F: SL/TP-aware exit using OHLCV high/low.

Exit priority (when use_sl_tp=true):
  1. stop_loss (OHLCV low/high check)
  2. take_profit (OHLCV high/low check)
  3. opposite_signal
  4. max_hold
  5. end_of_data

When use_sl_tp=false, falls back to Phase 6C behavior.

Outputs:
  logs/simulated_trades.jsonl — per-trade records
  logs/simulation_summary.json — aggregate metrics
"""
import argparse
import asyncio
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils import config as cfg


def load_records(path: Path):
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return records


def load_ohlcv_from_db(symbol: str, start_ts: int, end_ts: int, timeframe: str = "1h", db_path: str = "state/trading.db") -> list:
    """Load OHLCV candles from SQLite trading.db for given range. Returns list of dicts sorted ASC."""
    path = Path(db_path)
    if not path.exists():
        return []
    try:
        conn = sqlite3.connect(str(path))
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """
            SELECT timestamp, open, high, low, close, volume
            FROM ohlcv
            WHERE symbol = ? AND timeframe = ?
              AND timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp ASC
            """,
            (symbol, timeframe, start_ts, end_ts),
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []


def load_ohlcv_cached(ohlcv_cache: dict, symbol: str, start_ts: int, end_ts: int, timeframe: str, db_path: str) -> list:
    """Memoized OHLCV loader to avoid re-querying the same window."""
    key = (symbol, start_ts, end_ts, timeframe)
    if key in ohlcv_cache:
        return ohlcv_cache[key]
    candles = load_ohlcv_from_db(symbol, start_ts, end_ts, timeframe, db_path)
    ohlcv_cache[key] = candles
    return candles


def compute_sl_tp(entry_price: float, side: str, sl_pct: float, tp_pct: float):
    """Compute stop_loss and take_profit price levels for a position."""
    if side == "LONG":
        return entry_price * (1 - sl_pct), entry_price * (1 + tp_pct)
    return entry_price * (1 + sl_pct), entry_price * (1 - tp_pct)


def check_candle_exit(candle: dict, side: str, stop_loss: float, take_profit: float, same_candle_priority: str = "stop_loss"):
    """Check if a single candle triggers SL or TP for an open position.

    Returns (exit_reason, exit_price) or (None, None) if no exit.
    """
    high = float(candle.get("high", 0) or 0)
    low = float(candle.get("low", 0) or 0)
    if high <= 0 or low <= 0:
        return None, None

    if side == "LONG":
        sl_hit = low <= stop_loss
        tp_hit = high >= take_profit
    else:
        sl_hit = high >= stop_loss
        tp_hit = low <= take_profit

    if sl_hit and tp_hit:
        if same_candle_priority == "take_profit":
            return "take_profit", take_profit
        return "stop_loss", stop_loss
    if sl_hit:
        return "stop_loss", stop_loss
    if tp_hit:
        return "take_profit", take_profit
    return None, None


def compute_mae_mfe(candles: list, side: str, entry_price: float):
    """Compute max adverse/favorable excursion % from entry."""
    if not candles:
        return 0.0, 0.0
    worst = 0.0
    best = 0.0
    for c in candles:
        high = float(c.get("high", 0) or 0)
        low = float(c.get("low", 0) or 0)
        if high <= 0 or low <= 0:
            continue
        if side == "LONG":
            pnl_high = (high - entry_price) / entry_price
            pnl_low = (low - entry_price) / entry_price
        else:
            pnl_high = (entry_price - low) / entry_price
            pnl_low = (entry_price - high) / entry_price
        if pnl_low < worst:
            worst = pnl_low
        if pnl_high > best:
            best = pnl_high
    return worst, best


def avg(values):
    values = [v for v in values if isinstance(v, (int, float))]
    return sum(values) / len(values) if values else 0.0


def extract_action(record: dict) -> str:
    final = record.get("final_signal") or {}
    analysis = final.get("analysis") or {}
    trader = analysis.get("trader") or {}
    return (trader.get("action") or final.get("metadata", {}).get("final_action") or "HOLD").upper()


def extract_confidence(record: dict) -> float:
    final = record.get("final_signal") or {}
    return float(final.get("confidence", 0.0) or 0.0)


def extract_price(record: dict) -> float:
    ms = record.get("market_snapshot") or {}
    return float(ms.get("last_close", 0) or 0)


def extract_timestamp(record: dict):
    ts = (record.get("market_snapshot") or {}).get("candle_timestamp")
    if ts:
        return int(ts)
    try:
        return int(datetime.fromisoformat(record["timestamp"]).timestamp())
    except (ValueError, KeyError):
        return 0


def _confidence_bucket(conf: float) -> str:
    if conf >= 0.80:
        return "0.80-1.00"
    if conf >= 0.70:
        return "0.70-0.80"
    if conf >= 0.60:
        return "0.60-0.70"
    return "0.50-0.60"


def _record_stats(stats, symbol, side, conf, pnl_pct, exit_reason, hold_candles):
    stats["simulated_trades"] += 1
    if pnl_pct > 0.001:
        stats["wins"] += 1
    elif pnl_pct < -0.001:
        stats["losses"] += 1
    else:
        stats["breakeven"] += 1
    stats["pnls"].append(pnl_pct)
    stats["pnl_pcts"].append(pnl_pct)
    stats["hold_durations"].append(hold_candles)
    stats["exit_reasons"][exit_reason] += 1
    stats["by_symbol"][symbol]["trades"] += 1
    stats["by_symbol"][symbol]["pnl_pct_total"] += pnl_pct
    if pnl_pct > 0:
        stats["by_symbol"][symbol]["wins"] += 1
    elif pnl_pct < 0:
        stats["by_symbol"][symbol]["losses"] += 1
    stats["by_side"][side]["trades"] += 1
    stats["by_side"][side]["pnl_pct_total"] += pnl_pct
    if pnl_pct > 0:
        stats["by_side"][side]["wins"] += 1
    elif pnl_pct < 0:
        stats["by_side"][side]["losses"] += 1
    bucket = _confidence_bucket(conf)
    stats["by_confidence_bucket"][bucket]["trades"] += 1
    stats["by_confidence_bucket"][bucket]["pnl_pct_total"] += pnl_pct
    if pnl_pct > 0:
        stats["by_confidence_bucket"][bucket]["wins"] += 1
    elif pnl_pct < 0:
        stats["by_confidence_bucket"][bucket]["losses"] += 1


def simulate(records, config, output_path, summary_path, ohlcv_provider=None):
    """Simulate trades.

    Args:
        records: list of replay signal records
        config: full config dict
        output_path: where to write trades JSONL
        summary_path: where to write summary JSON
        ohlcv_provider: optional callable(symbol, start_ts, end_ts) -> list of candles.
                        If None, falls back to SQLite via load_ohlcv_from_db.
    """
    sim_cfg = config.get("simulation", {})
    fee_pct = sim_cfg.get("fee_pct", 0.001)
    slippage_pct = sim_cfg.get("slippage_pct", 0.0005)
    min_conf = sim_cfg.get("min_confidence", 0.55)
    total_cost_pct = fee_pct + slippage_pct

    use_sl_tp = sim_cfg.get("use_sl_tp", False)
    sl_pct = sim_cfg.get("stop_loss_pct", 0.03)
    tp_pct = sim_cfg.get("take_profit_pct", 0.06)
    max_hold = sim_cfg.get("max_hold_candles", 48)
    same_candle = sim_cfg.get("same_candle_priority", "stop_loss")
    ohlcv_timeframe = sim_cfg.get("ohlcv_timeframe", "1h")
    db_path = sim_cfg.get("db_path", "state/trading.db")

    if ohlcv_provider is None:
        ohlcv_provider = lambda sym, s, e: load_ohlcv_from_db(sym, s, e, ohlcv_timeframe, db_path)

    by_symbol = defaultdict(list)
    for rec in records:
        symbol = rec.get("symbol", "unknown")
        by_symbol[symbol].append(rec)
    for sym in by_symbol:
        by_symbol[sym].sort(key=extract_timestamp)

    trades = []
    stats = {
        "total_signals": len(records),
        "signals_by_action": Counter(),
        "simulated_trades": 0,
        "wins": 0,
        "losses": 0,
        "breakeven": 0,
        "pnls": [],
        "pnl_pcts": [],
        "hold_durations": [],
        "by_symbol": defaultdict(lambda: {"trades": 0, "pnl_pct_total": 0.0, "wins": 0, "losses": 0}),
        "by_side": defaultdict(lambda: {"trades": 0, "pnl_pct_total": 0.0, "wins": 0, "losses": 0}),
        "by_confidence_bucket": defaultdict(lambda: {"trades": 0, "pnl_pct_total": 0.0, "wins": 0, "losses": 0}),
        "exit_reasons": Counter(),
        "maes": [],
        "mfes": [],
    }

    for symbol, sym_records in by_symbol.items():
        position = None
        for rec in sym_records:
            action = extract_action(rec)
            confidence = extract_confidence(rec)
            price = extract_price(rec)
            ts = extract_timestamp(rec)

            stats["signals_by_action"][action] += 1

            if position is None:
                if confidence < min_conf:
                    continue
                if action not in ("BUY", "SELL"):
                    continue
                if price <= 0:
                    continue
                position = {
                    "side": "LONG" if action == "BUY" else "SHORT",
                    "entry_price": price,
                    "entry_ts": ts,
                    "entry_conf": confidence,
                    "entry_action": action,
                }
                continue

            opp = "SELL" if position["side"] == "LONG" else "BUY"

            close_reason = None
            close_price = None
            close_ts = ts
            max_hold_exit_price = None
            max_hold_exit_ts = None

            if use_sl_tp:
                stop_loss, take_profit = compute_sl_tp(
                    position["entry_price"], position["side"], sl_pct, tp_pct,
                )
                candles = ohlcv_provider(symbol, position["entry_ts"], ts)
                candles_in_trade = [c for c in candles if c.get("timestamp", 0) > position["entry_ts"]]

                sl_tp_exit = None
                for c in candles_in_trade:
                    reason, exit_px = check_candle_exit(
                        c, position["side"], stop_loss, take_profit, same_candle,
                    )
                    if reason:
                        sl_tp_exit = (reason, exit_px, c["timestamp"])
                        break

                if max_hold > 0 and len(candles_in_trade) >= max_hold:
                    exit_candle = candles_in_trade[max_hold - 1]
                    max_hold_exit_price = float(exit_candle.get("close", 0)) or position["entry_price"]
                    max_hold_exit_ts = exit_candle["timestamp"]

                if sl_tp_exit:
                    close_reason, close_price, close_ts = sl_tp_exit
                elif max_hold_exit_price is not None and action != opp:
                    close_reason = "max_hold"
                    close_price = max_hold_exit_price
                    close_ts = max_hold_exit_ts

            if close_reason is None and action == opp and confidence >= min_conf:
                close_reason = "opposite_signal"
                close_price = price
                close_ts = ts

            if close_reason is None:
                continue

            entry_price = position["entry_price"]
            side = position["side"]
            if side == "LONG":
                raw_pnl_pct = (close_price - entry_price) / entry_price
            else:
                raw_pnl_pct = (entry_price - close_price) / entry_price

            pnl_pct = raw_pnl_pct - total_cost_pct * 2
            hold_candles = max(1, (close_ts - position["entry_ts"]) // 3600)

            trade = {
                "symbol": symbol,
                "side": side,
                "entry_price": entry_price,
                "exit_price": close_price,
                "entry_ts": position["entry_ts"],
                "exit_ts": close_ts,
                "entry_action": position["entry_action"],
                "exit_action": action,
                "entry_confidence": position["entry_conf"],
                "exit_confidence": confidence,
                "pnl_pct": round(pnl_pct, 6),
                "hold_candles": hold_candles,
                "exit_reason": close_reason,
            }
            if use_sl_tp:
                trade["stop_loss"] = round(compute_sl_tp(entry_price, side, sl_pct, tp_pct)[0], 6)
                trade["take_profit"] = round(compute_sl_tp(entry_price, side, sl_pct, tp_pct)[1], 6)
                mae, mfe = compute_mae_mfe(
                    ohlcv_provider(symbol, position["entry_ts"], close_ts),
                    side, entry_price,
                )
                trade["max_adverse_excursion_pct"] = round(mae, 6)
                trade["max_favorable_excursion_pct"] = round(mfe, 6)
                stats["maes"].append(mae)
                stats["mfes"].append(mfe)

            trades.append(trade)
            _record_stats(stats, symbol, side, position["entry_conf"], pnl_pct, close_reason, hold_candles)
            position = None

        if position is not None:
            entry_price = position["entry_price"]
            side = position["side"]
            last_record = sym_records[-1] if sym_records else None
            exit_price = extract_price(last_record) if last_record else entry_price
            ts = extract_timestamp(last_record) if last_record else position["entry_ts"]

            close_reason = "end_of_data"
            if use_sl_tp:
                candles = ohlcv_provider(symbol, position["entry_ts"], ts)
                candles_in_trade = [c for c in candles if c.get("timestamp", 0) > position["entry_ts"]]
                stop_loss, take_profit = compute_sl_tp(entry_price, side, sl_pct, tp_pct)
                for c in candles_in_trade:
                    reason, exit_px = check_candle_exit(c, side, stop_loss, take_profit, same_candle)
                    if reason:
                        close_reason = reason
                        exit_price = exit_px
                        ts = c["timestamp"]
                        break

            if side == "LONG":
                raw_pnl_pct = (exit_price - entry_price) / entry_price
            else:
                raw_pnl_pct = (entry_price - exit_price) / entry_price

            pnl_pct = raw_pnl_pct - total_cost_pct * 2
            hold_candles = max(1, (ts - position["entry_ts"]) // 3600)

            trade = {
                "symbol": symbol,
                "side": side,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "entry_ts": position["entry_ts"],
                "exit_ts": ts,
                "entry_action": position["entry_action"],
                "exit_action": "EOD",
                "entry_confidence": position["entry_conf"],
                "exit_confidence": 0.0,
                "pnl_pct": round(pnl_pct, 6),
                "hold_candles": hold_candles,
                "exit_reason": close_reason,
            }
            if use_sl_tp:
                trade["stop_loss"] = round(compute_sl_tp(entry_price, side, sl_pct, tp_pct)[0], 6)
                trade["take_profit"] = round(compute_sl_tp(entry_price, side, sl_pct, tp_pct)[1], 6)
                mae, mfe = compute_mae_mfe(
                    ohlcv_provider(symbol, position["entry_ts"], ts),
                    side, entry_price,
                )
                trade["max_adverse_excursion_pct"] = round(mae, 6)
                trade["max_favorable_excursion_pct"] = round(mfe, 6)
                stats["maes"].append(mae)
                stats["mfes"].append(mfe)

            trades.append(trade)
            _record_stats(stats, symbol, side, position["entry_conf"], pnl_pct, close_reason, hold_candles)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        for t in trades:
            f.write(json.dumps(t, ensure_ascii=True) + "\n")
    print(f"Wrote {len(trades)} simulated trades to {output_path}")

    summary_data = {
        "generated_at": datetime.now().isoformat(),
        "config": {
            "fee_pct": fee_pct,
            "slippage_pct": slippage_pct,
            "min_confidence": min_conf,
            "use_sl_tp": use_sl_tp,
            "stop_loss_pct": sl_pct,
            "take_profit_pct": tp_pct,
            "max_hold_candles": max_hold,
        },
        "total_signals": stats["total_signals"],
        "signals_by_action": dict(stats["signals_by_action"].most_common()),
        "simulated_trades": stats["simulated_trades"],
        "wins": stats["wins"],
        "losses": stats["losses"],
        "breakeven": stats["breakeven"],
        "win_rate": round(stats["wins"] / max(stats["simulated_trades"], 1), 4),
        "total_pnl_pct": round(sum(stats["pnl_pcts"]), 4),
        "avg_pnl_pct": round(avg(stats["pnl_pcts"]), 4),
        "max_pnl_pct": round(max(stats["pnl_pcts"]), 4) if stats["pnl_pcts"] else 0,
        "min_pnl_pct": round(min(stats["pnl_pcts"]), 4) if stats["pnl_pcts"] else 0,
        "avg_hold_candles": round(avg(stats["hold_durations"]), 1),
        "by_symbol": {sym: dict(d) for sym, d in stats["by_symbol"].items()},
        "by_side": {side: dict(d) for side, d in stats["by_side"].items()},
        "by_confidence_bucket": {b: dict(d) for b, d in stats["by_confidence_bucket"].items()},
        "exit_reasons": dict(stats["exit_reasons"].most_common()),
    }
    if use_sl_tp:
        summary_data["avg_mae_pct"] = round(avg(stats["maes"]), 4) if stats["maes"] else 0
        summary_data["avg_mfe_pct"] = round(avg(stats["mfes"]), 4) if stats["mfes"] else 0
    summary = Path(summary_path)
    with summary.open("w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=True)
    print(f"Wrote summary to {summary_path}")

    return trades, stats


def print_report(stats: dict):
    total = stats["simulated_trades"]
    print(f"\n{'=' * 60}")
    print("Trade Simulation Report")
    print("=" * 60)
    print(f"Total signals: {stats['total_signals']}")
    print(f"Signals by action: {dict(stats['signals_by_action'].most_common())}")
    print(f"Simulated trades: {total}")
    if total == 0:
        print("No trades simulated.")
        return
    win_rate = stats["wins"] / max(total, 1) * 100
    print(f"Win/Loss/BE: {stats['wins']}W / {stats['losses']}L / {stats['breakeven']}BE ({win_rate:.1f}%)")
    print(f"Total PnL%: {sum(stats['pnl_pcts']):+.2f}%")
    print(f"Avg PnL%: {avg(stats['pnl_pcts']):+.2f}%")
    print(f"Max PnL%: {max(stats['pnl_pcts']):+.2f}%")
    print(f"Min PnL%: {min(stats['pnl_pcts']):+.2f}%")
    print(f"Avg hold candles: {avg(stats['hold_durations']):.1f}")
    print(f"Exit reasons: {dict(stats['exit_reasons'].most_common())}")
    if stats.get("maes"):
        print(f"Avg MAE: {avg(stats['maes']):.2%}  Avg MFE: {avg(stats['mfes']):.2%}")

    if stats["by_symbol"]:
        print("\nBy Symbol")
        for sym, d in sorted(stats["by_symbol"].items()):
            wr = d["wins"] / max(d["trades"], 1) * 100
            print(f"  {sym}: {d['trades']} trades, PnL%={d['pnl_pct_total']:+.2f}%, {d['wins']}W/{d['losses']}L ({wr:.0f}%)")

    if stats["by_side"]:
        print("\nBy Side")
        for side, d in sorted(stats["by_side"].items()):
            wr = d["wins"] / max(d["trades"], 1) * 100
            print(f"  {side}: {d['trades']} trades, PnL%={d['pnl_pct_total']:+.2f}%, {d['wins']}W/{d['losses']}L ({wr:.0f}%)")

    if stats["by_confidence_bucket"]:
        print("\nBy Confidence Bucket")
        for bucket in sorted(stats["by_confidence_bucket"].keys()):
            d = stats["by_confidence_bucket"][bucket]
            wr = d["wins"] / max(d["trades"], 1) * 100
            print(f"  {bucket}: {d['trades']} trades, PnL%={d['pnl_pct_total']:+.2f}%, {d['wins']}W/{d['losses']}L ({wr:.0f}%)")


def main():
    parser = argparse.ArgumentParser(description="Simulate trades from replay signal logs")
    parser.add_argument("--input", default="logs/replay_signals.jsonl", help="Path to replay JSONL")
    parser.add_argument("--output", default="logs/simulated_trades.jsonl", help="Output path for trades JSONL")
    parser.add_argument("--summary", default="logs/simulation_summary.json", help="Output path for summary JSON")
    parser.add_argument("--min-confidence", type=float, default=None, help="Override min confidence")
    parser.add_argument("--use-sl-tp", action="store_true", help="Enable SL/TP-aware exit (overrides config)")
    parser.add_argument("--no-sl-tp", action="store_true", help="Disable SL/TP-aware exit (overrides config)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        sys.exit(1)

    records = load_records(input_path)
    print(f"Loaded {len(records)} signal records from {input_path}")

    sim_config = cfg.load_default_params()
    if args.min_confidence is not None:
        sim_config.setdefault("simulation", {})["min_confidence"] = args.min_confidence
    if args.use_sl_tp:
        sim_config.setdefault("simulation", {})["use_sl_tp"] = True
    elif args.no_sl_tp:
        sim_config.setdefault("simulation", {})["use_sl_tp"] = False

    trades, stats = simulate(records, sim_config, args.output, args.summary)
    print_report(stats)


if __name__ == "__main__":
    main()
