from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .config import BotConfig
from .models import Candle, Portfolio, Signal
from .paper_broker import Execution
from .risk import RiskDecision


class SQLiteStore:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.init_schema()

    def close(self) -> None:
        self.conn.close()

    def init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS candles (
                market TEXT NOT NULL,
                unit INTEGER NOT NULL,
                time_utc TEXT NOT NULL,
                time_kst TEXT NOT NULL,
                timestamp_ms INTEGER NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                value REAL NOT NULL,
                PRIMARY KEY (market, unit, time_utc)
            );

            CREATE TABLE IF NOT EXISTS portfolio_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                cash REAL NOT NULL,
                btc REAL NOT NULL,
                entry_price REAL,
                daily_start_equity REAL,
                last_trade_ts REAL,
                realized_pnl REAL NOT NULL,
                fees_paid REAL NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                market TEXT NOT NULL,
                price REAL NOT NULL,
                equity REAL NOT NULL,
                cash REAL NOT NULL,
                btc REAL NOT NULL,
                signal_action TEXT NOT NULL,
                signal_confidence REAL NOT NULL,
                signal_reason TEXT NOT NULL,
                risk_approved INTEGER NOT NULL,
                risk_message TEXT NOT NULL,
                order_value_krw REAL NOT NULL,
                execution_json TEXT
            );
            """
        )
        self.conn.commit()

    def save_candles(self, candles: Iterable[Candle]) -> None:
        rows = [
            (
                c.market,
                c.unit,
                c.time_utc,
                c.time_kst,
                c.timestamp_ms,
                c.open,
                c.high,
                c.low,
                c.close,
                c.volume,
                c.value,
            )
            for c in candles
        ]
        if not rows:
            return
        self.conn.executemany(
            """
            INSERT OR REPLACE INTO candles
            (market, unit, time_utc, time_kst, timestamp_ms, open, high, low, close, volume, value)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        self.conn.commit()

    def load_recent_candles(self, market: str, unit: int, limit: int = 200) -> list[Candle]:
        rows = self.conn.execute(
            """
            SELECT * FROM candles
            WHERE market = ? AND unit = ?
            ORDER BY time_utc DESC
            LIMIT ?
            """,
            (market, unit, limit),
        ).fetchall()
        candles = [self._row_to_candle(row) for row in rows]
        candles.sort(key=lambda x: x.time_utc)
        return candles

    def load_portfolio(self, config: BotConfig) -> Portfolio:
        row = self.conn.execute("SELECT * FROM portfolio_state WHERE id = 1").fetchone()
        if row is None:
            portfolio = Portfolio(cash=config.initial_cash)
            self.save_portfolio(portfolio)
            return portfolio
        return Portfolio(
            cash=float(row["cash"]),
            btc=float(row["btc"]),
            entry_price=None if row["entry_price"] is None else float(row["entry_price"]),
            daily_start_equity=None if row["daily_start_equity"] is None else float(row["daily_start_equity"]),
            last_trade_ts=None if row["last_trade_ts"] is None else float(row["last_trade_ts"]),
            realized_pnl=float(row["realized_pnl"]),
            fees_paid=float(row["fees_paid"]),
        )

    def save_portfolio(self, portfolio: Portfolio) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO portfolio_state
            (id, cash, btc, entry_price, daily_start_equity, last_trade_ts, realized_pnl, fees_paid, updated_at)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                portfolio.cash,
                portfolio.btc,
                portfolio.entry_price,
                portfolio.daily_start_equity,
                portfolio.last_trade_ts,
                portfolio.realized_pnl,
                portfolio.fees_paid,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        self.conn.commit()

    def log_event(
        self,
        market: str,
        price: float,
        portfolio: Portfolio,
        signal: Signal,
        risk: RiskDecision,
        execution: Execution | None = None,
    ) -> None:
        execution_json = json.dumps(asdict(execution), ensure_ascii=False) if execution else None
        self.conn.execute(
            """
            INSERT INTO events
            (created_at, market, price, equity, cash, btc, signal_action, signal_confidence, signal_reason,
             risk_approved, risk_message, order_value_krw, execution_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                market,
                price,
                portfolio.equity(price),
                portfolio.cash,
                portfolio.btc,
                signal.action,
                signal.confidence,
                signal.reason,
                1 if risk.approved else 0,
                risk.message,
                risk.order_value_krw,
                execution_json,
            ),
        )
        self.conn.commit()

    @staticmethod
    def _row_to_candle(row: sqlite3.Row) -> Candle:
        return Candle(
            market=row["market"],
            unit=int(row["unit"]),
            time_utc=row["time_utc"],
            time_kst=row["time_kst"],
            timestamp_ms=int(row["timestamp_ms"]),
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=float(row["volume"]),
            value=float(row["value"]),
        )
