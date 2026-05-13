from __future__ import annotations

import time
from dataclasses import dataclass

from .config import BotConfig
from .models import Portfolio, Signal


@dataclass
class Execution:
    action: str
    price: float
    quantity_btc: float
    order_value_krw: float
    fee_krw: float
    cash_after: float
    btc_after: float
    equity_after: float
    message: str


class PaperBroker:
    def __init__(self, config: BotConfig):
        self.config = config

    def execute(self, signal: Signal, portfolio: Portfolio, market_price: float, order_value_krw: float, now_ts: float | None = None) -> Execution:
        now_ts = now_ts if now_ts is not None else time.time()

        if signal.action == "BUY":
            return self._buy(portfolio, market_price, order_value_krw, now_ts)
        if signal.action == "SELL":
            return self._sell(portfolio, market_price, order_value_krw, now_ts)
        raise ValueError("PaperBroker can only execute BUY or SELL")

    def _buy(self, portfolio: Portfolio, market_price: float, order_value_krw: float, now_ts: float) -> Execution:
        spend = min(order_value_krw, portfolio.cash)
        execution_price = market_price * (1.0 + self.config.slippage_rate)
        fee = spend * self.config.fee_rate
        net_spend = spend - fee
        qty = net_spend / execution_price if execution_price > 0 else 0.0

        old_total_qty = portfolio.btc
        old_cost_basis = (portfolio.entry_price or 0.0) * old_total_qty

        portfolio.cash -= spend
        portfolio.btc += qty
        portfolio.fees_paid += fee
        portfolio.last_trade_ts = now_ts

        if portfolio.btc > 0:
            if portfolio.entry_price is None or old_total_qty <= 0:
                portfolio.entry_price = execution_price
            else:
                added_cost_basis = execution_price * qty
                portfolio.entry_price = (old_cost_basis + added_cost_basis) / portfolio.btc

        equity = portfolio.equity(market_price)
        return Execution(
            action="BUY",
            price=execution_price,
            quantity_btc=qty,
            order_value_krw=spend,
            fee_krw=fee,
            cash_after=portfolio.cash,
            btc_after=portfolio.btc,
            equity_after=equity,
            message="paper buy executed",
        )

    def _sell(self, portfolio: Portfolio, market_price: float, order_value_krw: float, now_ts: float) -> Execution:
        execution_price = market_price * (1.0 - self.config.slippage_rate)
        qty_to_sell = min(portfolio.btc, order_value_krw / execution_price if execution_price > 0 else 0.0)
        gross = qty_to_sell * execution_price
        fee = gross * self.config.fee_rate
        cash_received = gross - fee

        if portfolio.entry_price is not None:
            portfolio.realized_pnl += (execution_price - portfolio.entry_price) * qty_to_sell - fee

        portfolio.btc -= qty_to_sell
        if portfolio.btc < 1e-12:
            portfolio.btc = 0.0
            portfolio.entry_price = None
        portfolio.cash += cash_received
        portfolio.fees_paid += fee
        portfolio.last_trade_ts = now_ts

        equity = portfolio.equity(market_price)
        return Execution(
            action="SELL",
            price=execution_price,
            quantity_btc=qty_to_sell,
            order_value_krw=gross,
            fee_krw=fee,
            cash_after=portfolio.cash,
            btc_after=portfolio.btc,
            equity_after=equity,
            message="paper sell executed",
        )
