from __future__ import annotations

from .config import BotConfig
from .indicators import pct_changes, rolling_std, rsi, sma
from .models import Candle, Portfolio, Signal


class TrendVolatilityStrategy:
    """Simple, auditable strategy for the first paper-trading MVP.

    This is intentionally not an LLM. It is deterministic and easier to test.
    """

    def __init__(self, config: BotConfig):
        self.config = config

    def decide(self, candles: list[Candle], portfolio: Portfolio | None = None) -> Signal:
        if len(candles) < 80:
            return Signal("HOLD", 0.0, "Need at least 80 candles")

        closes = [c.close for c in candles]
        last = closes[-1]
        fast = sma(closes, 20)
        slow = sma(closes, 60)
        rsi_now = rsi(closes, 14)
        volatility = rolling_std(pct_changes(closes), 20)

        if fast is None or slow is None or rsi_now is None or volatility is None:
            return Signal("HOLD", 0.0, "Indicators not ready")

        if portfolio and portfolio.btc > 0 and portfolio.entry_price:
            pnl_pct = (last - portfolio.entry_price) / portfolio.entry_price
            if pnl_pct <= -self.config.stop_loss_pct:
                return Signal(
                    "SELL",
                    0.95,
                    f"stop_loss triggered: pnl_pct={pnl_pct:.4f}",
                    sell_ratio=1.0,
                )
            if pnl_pct >= self.config.take_profit_pct and fast < slow:
                return Signal(
                    "SELL",
                    0.80,
                    f"take_profit with trend weakening: pnl_pct={pnl_pct:.4f}",
                    sell_ratio=1.0,
                )

        if fast > slow and 45 <= rsi_now <= 72 and volatility < 0.02:
            confidence = 0.62
            if last > fast:
                confidence += 0.03
            if volatility < 0.01:
                confidence += 0.03
            return Signal(
                "BUY",
                min(confidence, 0.75),
                f"trend_up fast_ma={fast:.2f} slow_ma={slow:.2f} rsi={rsi_now:.1f} volatility={volatility:.4f}",
            )

        if fast < slow:
            return Signal(
                "SELL",
                0.65,
                f"trend_down fast_ma={fast:.2f} slow_ma={slow:.2f} rsi={rsi_now:.1f}",
                sell_ratio=1.0,
            )

        if rsi_now >= 78:
            return Signal(
                "SELL",
                0.70,
                f"overbought rsi={rsi_now:.1f}",
                sell_ratio=0.5,
            )

        return Signal(
            "HOLD",
            0.50,
            f"no_edge fast_ma={fast:.2f} slow_ma={slow:.2f} rsi={rsi_now:.1f} volatility={volatility:.4f}",
        )
