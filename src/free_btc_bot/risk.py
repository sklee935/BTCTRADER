from __future__ import annotations

import time
from dataclasses import dataclass

from .config import BotConfig
from .models import Portfolio, Signal


@dataclass
class RiskDecision:
    approved: bool
    message: str
    order_value_krw: float = 0.0


class RiskManager:
    def __init__(self, config: BotConfig):
        self.config = config

    def approve(self, signal: Signal, portfolio: Portfolio, price: float, now_ts: float | None = None) -> RiskDecision:
        now_ts = now_ts if now_ts is not None else time.time()
        equity = portfolio.equity(price)

        if equity <= 0:
            return RiskDecision(False, "equity is zero or negative")

        if portfolio.daily_start_equity is None:
            portfolio.daily_start_equity = equity

        daily_loss_ratio = (portfolio.daily_start_equity - equity) / portfolio.daily_start_equity
        if daily_loss_ratio >= self.config.max_daily_loss_ratio and signal.action == "BUY":
            return RiskDecision(False, f"daily loss limit reached; new BUY blocked: {daily_loss_ratio:.4f}")

        if signal.action == "HOLD":
            return RiskDecision(False, "HOLD signal")

        if signal.confidence < self.config.min_confidence:
            return RiskDecision(False, f"confidence too low: {signal.confidence:.2f}")

        bypass_cooldown = signal.action == "SELL" and "stop_loss" in signal.reason
        if portfolio.last_trade_ts is not None and not bypass_cooldown:
            elapsed = now_ts - portfolio.last_trade_ts
            if elapsed < self.config.cooldown_seconds:
                return RiskDecision(False, f"cooldown active: wait {self.config.cooldown_seconds - elapsed:.0f}s")

        position_value = portfolio.position_value(price)

        if signal.action == "BUY":
            max_position_value = equity * self.config.max_position_ratio
            max_trade_value = equity * self.config.max_trade_ratio
            remaining_position_room = max_position_value - position_value
            order_value = min(max_trade_value, remaining_position_room, portfolio.cash)

            if order_value < self.config.min_order_krw:
                return RiskDecision(False, f"buy order below minimum or position limit reached: {order_value:.0f}")

            return RiskDecision(True, "approved BUY", order_value)

        if signal.action == "SELL":
            if portfolio.btc <= 0:
                return RiskDecision(False, "no BTC position to sell")

            sell_ratio = min(max(signal.sell_ratio, 0.0), 1.0)
            order_value = position_value * sell_ratio

            if order_value < self.config.min_order_krw and sell_ratio < 1.0:
                return RiskDecision(False, f"partial sell below minimum: {order_value:.0f}")

            return RiskDecision(True, "approved SELL", order_value)

        return RiskDecision(False, "unknown signal")
