#!/usr/bin/env python3
"""
Replay dependency readiness checker.

Stdlib-only utility for checking whether the active Python environment can run
fresh signal replay. It does not load .env, open network connections, connect to
state databases, collect replay data, or import trading execution modules.
"""
import argparse
import importlib.util
import json
import platform
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_MODULES = {
    "aiosqlite": "state database access used by replay SignalRecorder/db",
    "aiohttp": "Binance REST client HTTP transport",
    "dotenv": "python-dotenv runtime environment loader",
    "numpy": "technical indicators and market regime calculations",
    "yaml": "YAML config loading via PyYAML",
}

OPTIONAL_MODULES = {
    "feedparser": "RSS/news ingestion; not required for core OHLCV replay help",
    "telethon": "Telegram scraping; not required for core OHLCV replay help",
    "vaderSentiment": "news sentiment analysis; not required for core technical-only replay path",
}


def module_status(name: str, required: bool) -> dict:
    spec = importlib.util.find_spec(name)
    return {
        "module": name,
        "required": required,
        "available": spec is not None,
        "origin": getattr(spec, "origin", None) if spec is not None else None,
        "purpose": (REQUIRED_MODULES if required else OPTIONAL_MODULES)[name],
    }


def build_report() -> dict:
    required = [module_status(name, True) for name in sorted(REQUIRED_MODULES)]
    optional = [module_status(name, False) for name in sorted(OPTIONAL_MODULES)]
    missing_required = [item["module"] for item in required if not item["available"]]
    missing_optional = [item["module"] for item in optional if not item["available"]]
    return {
        "status": "pass" if not missing_required else "blocked",
        "python": {
            "executable": sys.executable,
            "version": sys.version.split()[0],
            "implementation": platform.python_implementation(),
        },
        "project_root": str(PROJECT_ROOT),
        "required_modules": required,
        "optional_modules": optional,
        "missing_required": missing_required,
        "missing_optional": missing_optional,
        "boundaries": {
            "loads_env": False,
            "opens_network": False,
            "connects_database": False,
            "runs_replay": False,
            "runs_live_trading": False,
            "places_orders": False,
        },
    }


def render_text(report: dict) -> str:
    lines = [
        f"status: {report['status']}",
        f"python: {report['python']['executable']} ({report['python']['version']})",
        "required modules:",
    ]
    for item in report["required_modules"]:
        marker = "PASS" if item["available"] else "MISSING"
        lines.append(f"  {marker} {item['module']} - {item['purpose']}")
    lines.append("optional modules:")
    for item in report["optional_modules"]:
        marker = "PASS" if item["available"] else "MISSING"
        lines.append(f"  {marker} {item['module']} - {item['purpose']}")
    return "\n".join(lines) + "\n"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Check replay runtime dependency readiness")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    report = build_report()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_text(report), end="")
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
