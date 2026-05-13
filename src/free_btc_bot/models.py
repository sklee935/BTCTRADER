from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal, Optional

Action = Literal["BUY", "SELL", "HOLD"]


@dataclass
class Candle:
    market: str
    time_utc: str
    time_kst: str
    timestamp_ms: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    value: float
    unit: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Signal:
    action: Action
    confidence: float
    reason: str
    sell_ratio: float = 1.0


@dataclass
class Portfolio:
    cash: float
    btc: float = 0.0
    entry_price: Optional[float] = None
    daily_start_equity: Optional[float] = None
    last_trade_ts: Optional[float] = None
    realized_pnl: float = 0.0
    fees_paid: float = 0.0

    def position_value(self, price: float) -> float:
        return self.btc * price

    def equity(self, price: float) -> float:
        return self.cash + self.position_value(price)
