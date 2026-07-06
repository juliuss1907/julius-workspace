# Batch 4D-B — Fresh Clone Integrity Audit for the-trading-guy

Date: 2026-07-06

## Goal

Verify from a fresh clone that the standalone GitHub repo `the-trading-guy` is a clean single-commit repository after Batch 4C.

## Inputs

- Remote: `git@github.com:juliuss1907/the-trading-guy.git`
- Expected commit: `89194f3009d7c0eabb91d505be4adea834d5d94d`
- Temp root: `/tmp/batch4d-fresh-clone-the-trading-guy-20260706-143256`
- Fresh clone dir: `/tmp/batch4d-fresh-clone-the-trading-guy-20260706-143256/the-trading-guy`

## Fresh Clone Result

- Branch: `main`
- HEAD commit: `89194f3009d7c0eabb91d505be4adea834d5d94d`
- Remote `main`: `89194f3009d7c0eabb91d505be4adea834d5d94d`
- Latest log: `89194f3 (HEAD -> main, origin/main, origin/HEAD) chore: initial standalone trading agents snapshot`
- Commit count: `1`
- File count: `341`

Remote URLs:

~~~text
origin	git@github.com:juliuss1907/the-trading-guy.git (fetch)
origin	git@github.com:juliuss1907/the-trading-guy.git (push)
~~~

## Integrity Audit

- Forbidden HEAD files: `0`
- Forbidden HEAD sample: `none`
- Unique history paths: `341`
- Forbidden history paths: `0`
- Forbidden history sample: `none`
- Secret marker file count: `21`
- Secret marker file sample: `trading/trade_notifier.py,trading/spot_demo_trader.py trading/futures_testnet_trader.py,telegram_bot/bot.py scripts/test_data_fetchers.py,scripts/test_binance_futures_history.py scripts/sync_futures_positions_to_db.py,scripts/run_paper_trading.py scripts/reconcile_positions.py,scripts/reconcile_futures_positions.py scripts/notify_synced_closes.py,scripts/build_sync_correction_report.py scripts/auth_telegram_step2.py,scripts/auth_telegram_step1.py scripts/auth_telegram_cli.py,scripts/apply_sync_corrections.py docs/TELEGRAM_BOT.md,docs/PAPER_TRADING.md docs/02-data-sources.md,dataflows/data_manager.py agents/news_sentiment.py`

Secret marker scan is conservative and reports filenames only, not matched values.

## Safety Boundaries

- Live trading: not executed
- Order placement: not executed
- Simulate-live: not executed
- StrategySignal-to-order mapping: not added
- Runtime/default config changes: not changed
- Raw replay logs committed: none
- `.env` files committed: none
- Remote mutation: none
- Push executed: no

## Status

`passed`

## Conclusion

The fresh clone audit confirms whether GitHub `main` is clean, single-commit, and free of forbidden generated/local-only paths.
