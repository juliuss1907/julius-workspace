"""
Database Manager - SQLite storage layer
"""
import aiosqlite
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
from utils import get_logger


logger = get_logger(__name__)


class Database:
    """Database manager for market data and signals"""
    
    def __init__(self, db_path: str = "state/trading.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = None
    
    async def connect(self):
        """Connect to database and initialize schema"""
        self._conn = await aiosqlite.connect(str(self.db_path))
        self._conn.row_factory = aiosqlite.Row
        
        # Load schema
        schema_path = self.db_path.parent / "schema.sql"
        if schema_path.exists():
            with open(schema_path) as f:
                schema = f.read()
            await self._conn.executescript(schema)
            await self._ensure_paper_position_group_columns()
            await self._conn.commit()
            logger.info("Database schema initialized")
        else:
            logger.warning("Schema file not found, skipping initialization")

    async def _ensure_paper_position_group_columns(self):
        """Add DCA/group columns to existing paper_positions tables."""
        async with self._conn.execute("PRAGMA table_info(paper_positions)") as cursor:
            rows = await cursor.fetchall()
        existing = {row[1] for row in rows}
        migrations = []
        if "position_group_id" not in existing:
            migrations.append("ALTER TABLE paper_positions ADD COLUMN position_group_id TEXT")
        if "entry_kind" not in existing:
            migrations.append("ALTER TABLE paper_positions ADD COLUMN entry_kind TEXT DEFAULT 'base'")
        if "dca_index" not in existing:
            migrations.append("ALTER TABLE paper_positions ADD COLUMN dca_index INTEGER DEFAULT 0")
        for stmt in migrations:
            await self._conn.execute(stmt)
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_paper_positions_group ON paper_positions(position_group_id, status)"
        )
    
    async def close(self):
        """Close database connection"""
        if self._conn:
            await self._conn.close()
            logger.info("Database connection closed")
    
    # =========================================================================
    # OHLCV Operations
    # =========================================================================
    
    async def insert_ohlcv(self, symbol: str, timeframe: str, candles: List[Dict]):
        """
        Insert OHLCV candles (bulk insert with IGNORE on conflict)
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe (1m, 5m, 1h, 4h, 1d)
            candles: List of candle dicts from data fetcher
        """
        if not candles:
            return
        
        values = []
        for candle in candles:
            values.append((
                symbol,
                timeframe,
                candle['timestamp'],
                candle['open'],
                candle['high'],
                candle['low'],
                candle['close'],
                candle['volume'],
                candle.get('quote_volume'),
                candle.get('trades')
            ))
        
        await self._conn.executemany(
            """
            INSERT OR IGNORE INTO ohlcv 
            (symbol, timeframe, timestamp, open, high, low, close, volume, quote_volume, trades)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            values
        )
        await self._conn.commit()
        logger.debug(f"Inserted {len(candles)} candles for {symbol} {timeframe}")
    
    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 500,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[Dict]:
        """
        Get OHLCV candles from database
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe
            limit: Max number of candles
            start_time: Start timestamp (unix seconds)
            end_time: End timestamp (unix seconds)
        
        Returns:
            List of candle dicts
        """
        query = """
            SELECT timestamp, open, high, low, close, volume, quote_volume, trades
            FROM ohlcv
            WHERE symbol = ? AND timeframe = ?
        """
        params = [symbol, timeframe]
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        async with self._conn.execute(query, params) as cursor:
            rows = await cursor.fetchall()
        
        candles = []
        for row in rows:
            candles.append({
                'timestamp': row['timestamp'],
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
                'volume': row['volume'],
                'quote_volume': row['quote_volume'],
                'trades': row['trades']
            })
        
        # Reverse to get chronological order
        candles.reverse()
        
        return candles
    
    async def get_latest_ohlcv_timestamp(self, symbol: str, timeframe: str) -> Optional[int]:
        """Get timestamp of latest candle in database"""
        async with self._conn.execute(
            "SELECT MAX(timestamp) as latest FROM ohlcv WHERE symbol = ? AND timeframe = ?",
            (symbol, timeframe)
        ) as cursor:
            row = await cursor.fetchone()
            return row['latest'] if row['latest'] else None
    
    # =========================================================================
    # Ticker Operations
    # =========================================================================
    
    async def insert_ticker(self, ticker: Dict):
        """Insert ticker snapshot"""
        await self._conn.execute(
            """
            INSERT OR REPLACE INTO tickers
            (symbol, price, volume_24h, quote_volume_24h, price_change_24h_pct, 
             high_24h, low_24h, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticker['symbol'],
                ticker['price'],
                ticker.get('volume_24h'),
                ticker.get('quote_volume_24h'),
                ticker.get('price_change_24h_pct'),
                ticker.get('high_24h'),
                ticker.get('low_24h'),
                ticker['timestamp']
            )
        )
        await self._conn.commit()
    
    async def get_latest_ticker(self, symbol: str) -> Optional[Dict]:
        """Get latest ticker for symbol"""
        async with self._conn.execute(
            """
            SELECT * FROM tickers 
            WHERE symbol = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
            """,
            (symbol,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    # =========================================================================
    # Signal Operations
    # =========================================================================
    
    async def insert_signal(self, signal: Dict) -> int:
        """
        Insert trading signal
        
        Returns:
            Signal ID
        """
        async with self._conn.execute(
            """
            INSERT INTO signals
            (signal_id, coin, mode, signal, confidence, entry_price, stop_loss, 
             take_profit, summary, reasoning, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                signal['signal_id'],
                signal['coin'],
                signal['mode'],
                signal['signal'],
                signal.get('confidence'),
                signal.get('entry_price'),
                signal.get('stop_loss'),
                signal.get('take_profit'),
                signal.get('summary'),
                signal.get('reasoning'),
                signal['timestamp']
            )
        ) as cursor:
            signal_id = cursor.lastrowid
        
        await self._conn.commit()
        logger.info(f"Signal inserted: {signal['signal_id']} - {signal['coin']} {signal['signal']}")
        return signal_id
    
    async def update_signal_action(
        self,
        signal_id: str,
        action: str,
        action_time: int
    ):
        """Update Julius's action on a signal"""
        await self._conn.execute(
            """
            UPDATE signals 
            SET julius_action = ?, julius_action_time = ?
            WHERE signal_id = ?
            """,
            (action, action_time, signal_id)
        )
        await self._conn.commit()
    
    async def update_signal_outcome(
        self,
        signal_id: str,
        outcome: str,
        pnl_pct: float
    ):
        """Update signal outcome (win/loss/breakeven)"""
        await self._conn.execute(
            """
            UPDATE signals 
            SET outcome = ?, outcome_pnl_pct = ?
            WHERE signal_id = ?
            """,
            (outcome, pnl_pct, signal_id)
        )
        await self._conn.commit()
    
    async def get_signals(
        self,
        coin: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get signals"""
        query = "SELECT * FROM signals"
        params = []
        
        if coin:
            query += " WHERE coin = ?"
            params.append(coin)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        async with self._conn.execute(query, params) as cursor:
            rows = await cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    # =========================================================================
    # State Operations (key-value store)
    # =========================================================================
    
    async def set_state(self, key: str, value: Any):
        """Set state value (JSON serializable)"""
        value_json = json.dumps(value)
        await self._conn.execute(
            """
            INSERT OR REPLACE INTO state (key, value, updated_at)
            VALUES (?, ?, strftime('%s', 'now'))
            """,
            (key, value_json)
        )
        await self._conn.commit()
    
    async def get_state(self, key: str, default: Any = None) -> Any:
        """Get state value"""
        async with self._conn.execute(
            "SELECT value FROM state WHERE key = ?",
            (key,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return json.loads(row['value'])
            return default
    
    # =========================================================================
    # Analysis Cache Operations
    # =========================================================================
    
    async def cache_analysis(
        self,
        coin: str,
        analyst_type: str,
        analysis_data: Dict,
        timeframe: Optional[str] = None,
        ttl_seconds: int = 3600
    ):
        """Cache analysis result"""
        timestamp = int(datetime.now().timestamp())
        expires_at = timestamp + ttl_seconds
        
        await self._conn.execute(
            """
            INSERT OR REPLACE INTO analyses
            (coin, analyst_type, timeframe, analysis_data, timestamp, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (coin, analyst_type, timeframe, json.dumps(analysis_data), timestamp, expires_at)
        )
        await self._conn.commit()
    
    async def get_cached_analysis(
        self,
        coin: str,
        analyst_type: str,
        timeframe: Optional[str] = None,
        max_age_seconds: Optional[int] = None
    ) -> Optional[Dict]:
        """Get cached analysis if not expired"""
        current_time = int(datetime.now().timestamp())
        
        query = """
            SELECT analysis_data, timestamp, expires_at 
            FROM analyses
            WHERE coin = ? AND analyst_type = ?
        """
        params = [coin, analyst_type]
        
        if timeframe:
            query += " AND timeframe = ?"
            params.append(timeframe)
        
        query += " AND expires_at > ? ORDER BY timestamp DESC LIMIT 1"
        params.append(current_time)
        
        async with self._conn.execute(query, params) as cursor:
            row = await cursor.fetchone()
        
        if not row:
            return None
        
        # Check max_age if specified
        if max_age_seconds:
            age = current_time - row['timestamp']
            if age > max_age_seconds:
                return None
        
        return json.loads(row['analysis_data'])
    
    # =========================================================================
    # Paper Trading Operations
    # =========================================================================
    
    async def insert_paper_position(self, position: Dict) -> int:
        """Insert new paper trading position"""
        async with self._conn.execute(
            """
            INSERT INTO paper_positions
            (trade_id, symbol, side, market_type, entry_price, quantity, leverage,
             stop_loss, take_profit, trailing_stop, status, opened_at, signal_data, order_id,
             position_group_id, entry_kind, dca_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?, ?, ?, ?, ?, ?)
            """,
            (
                position['trade_id'],
                position['symbol'],
                position['side'],
                position['market_type'],
                position['entry_price'],
                position['quantity'],
                position.get('leverage', 1.0),
                position.get('stop_loss'),
                position.get('take_profit'),
                position.get('trailing_stop'),
                position.get('opened_at', int(datetime.now().timestamp())),
                json.dumps(position.get('signal_data', {})),
                position.get('order_id'),
                position.get('position_group_id'),
                position.get('entry_kind', 'base'),
                position.get('dca_index', 0),
            )
        ) as cursor:
            position_id = cursor.lastrowid
        
        await self._conn.commit()
        logger.info(f"Paper position opened: {position['trade_id']} - {position['symbol']} {position['side']}")
        return position_id
    
    async def close_paper_position(
        self,
        trade_id: str,
        close_price: float,
        pnl: float,
        pnl_pct: float,
        close_reason: str,
        fees: float = 0.0
    ):
        """Close a paper position"""
        closed_at = int(datetime.now().timestamp())
        
        await self._conn.execute(
            """
            UPDATE paper_positions 
            SET status = 'closed', closed_at = ?, close_price = ?, pnl = ?, 
                pnl_pct = ?, close_reason = ?, fees = ?
            WHERE trade_id = ?
            """,
            (closed_at, close_price, pnl, pnl_pct, close_reason, fees, trade_id)
        )
        
        # Also insert into paper_trades history
        async with self._conn.execute(
            """
            SELECT * FROM paper_positions WHERE trade_id = ?
            """,
            (trade_id,)
        ) as cursor:
            position = await cursor.fetchone()
        
        if position:
            duration = closed_at - position['opened_at']
            await self._conn.execute(
                """
                INSERT INTO paper_trades
                (trade_id, symbol, side, market_type, entry_price, exit_price, 
                 quantity, leverage, pnl, pnl_pct, fees, opened_at, closed_at, 
                 duration_seconds, close_reason, signal_confidence, signal_score, signal_reasoning)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trade_id,
                    position['symbol'],
                    position['side'],
                    position['market_type'],
                    position['entry_price'],
                    close_price,
                    position['quantity'],
                    position['leverage'],
                    pnl,
                    pnl_pct,
                    fees,
                    position['opened_at'],
                    closed_at,
                    duration,
                    close_reason,
                    position['signal_data'] and json.loads(position['signal_data']).get('confidence'),
                    position['signal_data'] and json.loads(position['signal_data']).get('score'),
                    position['signal_data'] and json.loads(position['signal_data']).get('reasoning')
                )
            )
        
        await self._conn.commit()
        logger.info(f"Paper position closed: {trade_id} - PnL: {pnl:.2f} ({pnl_pct:.2f}%)")
    
    async def get_open_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get all open positions"""
        query = "SELECT * FROM paper_positions WHERE status = 'open'"
        params = []
        
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
        
        query += " ORDER BY opened_at DESC"
        
        async with self._conn.execute(query, params) as cursor:
            rows = await cursor.fetchall()
        
        positions = []
        for row in rows:
            pos = dict(row)
            if pos['signal_data']:
                pos['signal_data'] = json.loads(pos['signal_data'])
            positions.append(pos)
        
        return positions
    
    async def get_paper_trades(
        self,
        symbol: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get paper trading history"""
        query = "SELECT * FROM paper_trades"
        params = []
        
        if symbol:
            query += " WHERE symbol = ?"
            params.append(symbol)
        
        query += " ORDER BY closed_at DESC LIMIT ?"
        params.append(limit)
        
        async with self._conn.execute(query, params) as cursor:
            rows = await cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    async def get_portfolio_stats(self) -> Dict:
        """Get portfolio statistics"""
        # Get open positions
        open_positions = await self.get_open_positions()
        
        # Get closed trades
        async with self._conn.execute(
            "SELECT COUNT(*) as count, SUM(pnl) as total_pnl, AVG(pnl_pct) as avg_pnl_pct FROM paper_trades"
        ) as cursor:
            stats = await cursor.fetchone()
        
        # Get latest portfolio snapshot
        async with self._conn.execute(
            "SELECT * FROM paper_portfolio ORDER BY timestamp DESC LIMIT 1"
        ) as cursor:
            latest_snapshot = await cursor.fetchone()
        
        return {
            'open_positions_count': len(open_positions),
            'total_trades': stats['count'] or 0,
            'total_pnl': stats['total_pnl'] or 0.0,
            'avg_pnl_pct': stats['avg_pnl_pct'] or 0.0,
            'latest_snapshot': dict(latest_snapshot) if latest_snapshot else None
        }
    
    async def update_position_quantity(self, trade_id: str, new_quantity: float):
        """Update quantity for a partially reduced position"""
        await self._conn.execute(
            "UPDATE paper_positions SET quantity = ? WHERE trade_id = ?",
            (new_quantity, trade_id),
        )
        await self._conn.commit()
        logger.debug(f"Position {trade_id} quantity updated to {new_quantity}")

    async def insert_partial_reduce(
        self,
        trade_id: str,
        symbol: str,
        side: str,
        market_type: str,
        entry_price: float,
        exit_price: float,
        reduced_quantity: float,
        remaining_quantity: float,
        pnl: float,
        pnl_pct: float,
        fees: float,
        close_reason: str,
        original_close_reason: str,
    ):
        """Record a partial position reduction in paper_trades"""
        now = int(datetime.now().timestamp())
        await self._conn.execute(
            """
            INSERT INTO paper_trades
            (trade_id, symbol, side, market_type, entry_price, exit_price,
             quantity, leverage, pnl, pnl_pct, fees, opened_at, closed_at,
             duration_seconds, close_reason, signal_confidence, signal_score, signal_reasoning)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1.0, ?, ?, ?, ?, ?, 0, ?, NULL, NULL, ?)
            """,
            (
                trade_id,
                symbol,
                side,
                market_type,
                entry_price,
                exit_price,
                reduced_quantity,
                pnl,
                pnl_pct,
                fees,
                now,
                now,
                close_reason,
                original_close_reason,
            ),
        )
        await self._conn.commit()
        logger.info(f"Partial reduce recorded: {trade_id} qty={reduced_quantity} rem={remaining_quantity}")

    async def update_position_trailing_stop(
        self,
        trade_id: str,
        trailing_stop: float,
        activated: bool = True
    ):
        """Update trailing stop for a position"""
        await self._conn.execute(
            """
            UPDATE paper_positions 
            SET trailing_stop = ?, trailing_activated = ?
            WHERE trade_id = ?
            """,
            (trailing_stop, 1 if activated else 0, trade_id)
        )
        await self._conn.commit()
    
    async def save_portfolio_snapshot(
        self,
        spot_balance: float,
        futures_balance: float,
        spot_unrealized_pnl: float = 0.0,
        futures_unrealized_pnl: float = 0.0
    ):
        """Save portfolio snapshot"""
        total_equity = spot_balance + futures_balance
        open_positions = await self.get_open_positions()
        
        # Calculate daily PnL (last 24h)
        async with self._conn.execute(
            """
            SELECT SUM(pnl) as daily_pnl FROM paper_trades 
            WHERE closed_at >= strftime('%s', 'now', '-1 day')
            """
        ) as cursor:
            result = await cursor.fetchone()
            daily_pnl = result['daily_pnl'] or 0.0
        
        # Calculate total PnL
        async with self._conn.execute(
            "SELECT SUM(pnl) as total_pnl FROM paper_trades"
        ) as cursor:
            result = await cursor.fetchone()
            total_pnl = result['total_pnl'] or 0.0
        
        total_pnl_pct = (total_pnl / 20000 * 100) if total_pnl else 0.0  # Assuming 20k initial
        
        await self._conn.execute(
            """
            INSERT INTO paper_portfolio
            (spot_balance, futures_balance, total_equity, open_positions_count,
             daily_pnl, total_pnl, total_pnl_pct, spot_unrealized_pnl, futures_unrealized_pnl)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                spot_balance,
                futures_balance,
                total_equity,
                len(open_positions),
                daily_pnl,
                total_pnl,
                total_pnl_pct,
                spot_unrealized_pnl,
                futures_unrealized_pnl
            )
        )
        await self._conn.commit()
    
    async def log_notification(
        self,
        trade_id: str,
        notification_type: str,
        message: str,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Log notification to database"""
        await self._conn.execute(
            """
            INSERT INTO trade_notifications
            (trade_id, notification_type, message, success, error_message)
            VALUES (?, ?, ?, ?, ?)
            """,
            (trade_id, notification_type, message, 1 if success else 0, error_message)
        )
        await self._conn.commit()


# Global database instance
db = Database()
