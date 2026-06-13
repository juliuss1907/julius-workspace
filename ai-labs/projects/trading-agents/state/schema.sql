-- Trading Agents Database Schema
-- SQLite database for storing market data, signals, and state

-- OHLCV Data (candlesticks)
CREATE TABLE IF NOT EXISTS ohlcv (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    quote_volume REAL,
    trades INTEGER,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    UNIQUE(symbol, timeframe, timestamp)
);

-- Index for fast queries
CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_timeframe 
    ON ohlcv(symbol, timeframe, timestamp DESC);

-- Market Tickers (snapshot data)
CREATE TABLE IF NOT EXISTS tickers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    price REAL NOT NULL,
    volume_24h REAL,
    quote_volume_24h REAL,
    price_change_24h_pct REAL,
    high_24h REAL,
    low_24h REAL,
    timestamp INTEGER NOT NULL,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    UNIQUE(symbol, timestamp)
);

CREATE INDEX IF NOT EXISTS idx_tickers_symbol_time 
    ON tickers(symbol, timestamp DESC);

-- Trading Signals
CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id TEXT NOT NULL UNIQUE,
    coin TEXT NOT NULL,
    mode TEXT NOT NULL, -- 'full', 'quick', 'flash', 'lite'
    signal TEXT NOT NULL, -- 'BUY', 'SELL', 'HOLD'
    confidence REAL,
    entry_price REAL,
    stop_loss REAL,
    take_profit REAL,
    summary TEXT,
    reasoning TEXT,
    timestamp INTEGER NOT NULL,
    julius_action TEXT, -- 'executed', 'rejected', 'ignored', NULL
    julius_action_time INTEGER,
    outcome TEXT, -- 'win', 'loss', 'breakeven', NULL (pending)
    outcome_pnl_pct REAL,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_signals_coin_time 
    ON signals(coin, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_signals_outcome 
    ON signals(outcome, timestamp DESC);

-- Agent Analysis Results (cached)
CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coin TEXT NOT NULL,
    analyst_type TEXT NOT NULL, -- 'technical', 'fundamental', 'sentiment', 'news'
    timeframe TEXT,
    analysis_data TEXT NOT NULL, -- JSON blob
    timestamp INTEGER NOT NULL,
    expires_at INTEGER NOT NULL,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    UNIQUE(coin, analyst_type, timeframe, timestamp)
);

CREATE INDEX IF NOT EXISTS idx_analyses_lookup 
    ON analyses(coin, analyst_type, timeframe, timestamp DESC);

-- System State (key-value store)
CREATE TABLE IF NOT EXISTS state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

-- Paper Trading Portfolio
CREATE TABLE IF NOT EXISTS portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coin TEXT NOT NULL,
    quantity REAL NOT NULL,
    avg_entry_price REAL NOT NULL,
    current_price REAL,
    pnl_pct REAL,
    signal_id TEXT, -- Reference to signals table
    opened_at INTEGER NOT NULL,
    closed_at INTEGER,
    status TEXT NOT NULL DEFAULT 'open', -- 'open', 'closed'
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_portfolio_status 
    ON portfolio(status, coin);

-- Paper Trading Transactions
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER,
    coin TEXT NOT NULL,
    type TEXT NOT NULL, -- 'buy', 'sell'
    quantity REAL NOT NULL,
    price REAL NOT NULL,
    total_value REAL NOT NULL,
    fee REAL DEFAULT 0,
    signal_id TEXT,
    timestamp INTEGER NOT NULL,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (portfolio_id) REFERENCES portfolio(id)
);

CREATE INDEX IF NOT EXISTS idx_transactions_time 
    ON transactions(timestamp DESC);

-- =============================================================================
-- Paper Trading Positions (Spot + Futures)
-- =============================================================================
CREATE TABLE IF NOT EXISTS paper_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id TEXT UNIQUE NOT NULL,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,  -- LONG/SHORT
    market_type TEXT NOT NULL,  -- spot/futures
    entry_price REAL NOT NULL,
    quantity REAL NOT NULL,
    leverage REAL DEFAULT 1.0,
    stop_loss REAL,
    take_profit REAL,
    trailing_stop REAL,
    trailing_activated INTEGER DEFAULT 0,
    status TEXT DEFAULT 'open',  -- open/closed
    opened_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    closed_at INTEGER,
    close_price REAL,
    pnl REAL,
    pnl_pct REAL,
    fees REAL DEFAULT 0.0,
    close_reason TEXT,  -- sl_hit/tp_hit/trailing_stop/manual/timeout
    signal_data TEXT,  -- JSON of signal that triggered this trade
    order_id TEXT,  -- Exchange order ID
    position_group_id TEXT,
    entry_kind TEXT DEFAULT 'base',  -- base/dca
    dca_index INTEGER DEFAULT 0,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_paper_positions_status 
    ON paper_positions(status, symbol);

CREATE INDEX IF NOT EXISTS idx_paper_positions_trade_id 
    ON paper_positions(trade_id);

-- =============================================================================
-- Paper Trading History (All closed trades)
-- =============================================================================
CREATE TABLE IF NOT EXISTS paper_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id TEXT UNIQUE NOT NULL,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    market_type TEXT NOT NULL,
    entry_price REAL NOT NULL,
    exit_price REAL,
    quantity REAL NOT NULL,
    leverage REAL DEFAULT 1.0,
    pnl REAL,
    pnl_pct REAL,
    fees REAL DEFAULT 0.0,
    opened_at INTEGER NOT NULL,
    closed_at INTEGER,
    duration_seconds INTEGER,
    close_reason TEXT,
    signal_confidence REAL,
    signal_score REAL,
    signal_reasoning TEXT
);

CREATE INDEX IF NOT EXISTS idx_paper_trades_time 
    ON paper_trades(closed_at DESC);

CREATE INDEX IF NOT EXISTS idx_paper_trades_symbol 
    ON paper_trades(symbol, closed_at DESC);

-- =============================================================================
-- Paper Portfolio Snapshots
-- =============================================================================
CREATE TABLE IF NOT EXISTS paper_portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    spot_balance REAL,
    futures_balance REAL,
    total_equity REAL,
    open_positions_count INTEGER,
    daily_pnl REAL,
    total_pnl REAL,
    total_pnl_pct REAL,
    spot_unrealized_pnl REAL,
    futures_unrealized_pnl REAL
);

CREATE INDEX IF NOT EXISTS idx_paper_portfolio_time 
    ON paper_portfolio(timestamp DESC);

-- =============================================================================
-- Trade Notifications Log
-- =============================================================================
CREATE TABLE IF NOT EXISTS trade_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id TEXT NOT NULL,
    notification_type TEXT NOT NULL,  -- trade_opened/trade_closed/sl_tp_hit/daily_summary
    message TEXT NOT NULL,
    sent_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    success INTEGER DEFAULT 1,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_trade_notifications_time 
    ON trade_notifications(sent_at DESC);

-- =============================================================================
-- Reconciliation Events (Binance vs local DB diffs)
-- =============================================================================
CREATE TABLE IF NOT EXISTS reconciliation_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    side TEXT,
    market_type TEXT NOT NULL DEFAULT 'futures',
    event_type TEXT NOT NULL,  -- orphan_detected, db_missing_on_binance, qty_mismatch, side_mismatch, ok
    db_trade_id TEXT,
    binance_qty REAL,
    db_qty REAL,
    binance_entry_price REAL,
    db_entry_price REAL,
    severity TEXT NOT NULL DEFAULT 'info',  -- info, warning, high
    action_taken TEXT,  -- inserted, updated, marked_closed, none
    details TEXT,  -- JSON
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_reconciliation_events_time
    ON reconciliation_events(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_reconciliation_events_run
    ON reconciliation_events(run_id);

CREATE INDEX IF NOT EXISTS idx_reconciliation_events_type
    ON reconciliation_events(event_type, created_at DESC);

-- =============================================================================
-- Reconciliation State (last run summary)
-- =============================================================================
CREATE TABLE IF NOT EXISTS reconciliation_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    last_run_at INTEGER NOT NULL,
    last_run_id TEXT NOT NULL,
    orphan_count INTEGER NOT NULL DEFAULT 0,
    db_missing_count INTEGER NOT NULL DEFAULT 0,
    qty_mismatch_count INTEGER NOT NULL DEFAULT 0,
    side_mismatch_count INTEGER NOT NULL DEFAULT 0,
    ok_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    raw_summary TEXT
);

INSERT OR IGNORE INTO reconciliation_state (id, last_run_at, last_run_id, raw_summary)
VALUES (1, 0, 'init', '{}');
