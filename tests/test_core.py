from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from free_btc_bot.config import BotConfig
from free_btc_bot.indicators import rsi, sma
from free_btc_bot.models import Candle, Portfolio, Signal
from free_btc_bot.risk import RiskManager
from free_btc_bot.strategy import TrendVolatilityStrategy


def make_candles(n: int, start: float = 100.0, step: float = 1.0) -> list[Candle]:
    candles = []
    for i in range(n):
        close = start + i * step
        candles.append(
            Candle(
                market="KRW-BTC",
                time_utc=f"2026-01-01T00:{i:02d}:00",
                time_kst="",
                timestamp_ms=i,
                open=close - 0.5,
                high=close + 1,
                low=close - 1,
                close=close,
                volume=1.0,
                value=close,
                unit=5,
            )
        )
    return candles


class CoreTests(unittest.TestCase):
    def test_sma(self) -> None:
        self.assertEqual(sma([1, 2, 3, 4], 2), 3.5)
        self.assertIsNone(sma([1], 2))

    def test_rsi_range(self) -> None:
        value = rsi([1, 2, 3, 2, 4, 5, 6, 5, 7, 8, 9, 8, 10, 11, 12], 14)
        self.assertIsNotNone(value)
        self.assertGreaterEqual(value, 0)
        self.assertLessEqual(value, 100)

    def test_strategy_needs_enough_data(self) -> None:
        cfg = BotConfig()
        strategy = TrendVolatilityStrategy(cfg)
        signal = strategy.decide(make_candles(10))
        self.assertEqual(signal.action, "HOLD")

    def test_risk_blocks_low_confidence(self) -> None:
        cfg = BotConfig(min_confidence=0.6)
        risk = RiskManager(cfg)
        portfolio = Portfolio(cash=1_000_000)
        signal = Signal("BUY", 0.5, "too weak")
        decision = risk.approve(signal, portfolio, 100_000_000)
        self.assertFalse(decision.approved)

    def test_risk_approves_valid_buy(self) -> None:
        cfg = BotConfig(min_confidence=0.6, cooldown_seconds=0)
        risk = RiskManager(cfg)
        portfolio = Portfolio(cash=1_000_000)
        signal = Signal("BUY", 0.7, "valid")
        decision = risk.approve(signal, portfolio, 100_000_000)
        self.assertTrue(decision.approved)
        self.assertGreaterEqual(decision.order_value_krw, cfg.min_order_krw)


if __name__ == "__main__":
    unittest.main()
