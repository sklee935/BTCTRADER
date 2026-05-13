from __future__ import annotations

from dataclasses import dataclass

from .config import BotConfig
from .models import Candle, Portfolio
from .paper_broker import PaperBroker
from .risk import RiskManager
from .strategy import TrendVolatilityStrategy
from .upbit_public import UpbitPublicClient


@dataclass
class BacktestResult:
    start_equity: float
    final_equity: float
    return_pct: float
    max_drawdown_pct: float
    trades: int
    buys: int
    sells: int
    fees_paid: float
    realized_pnl: float


def run_backtest(candles: list[Candle], config: BotConfig) -> BacktestResult:
    if len(candles) < 100:
        raise ValueError("Need at least 100 candles for this simple backtest")

    portfolio = Portfolio(cash=config.initial_cash)
    strategy = TrendVolatilityStrategy(config)
    risk = RiskManager(config)
    broker = PaperBroker(config)

    equity_curve: list[float] = []
    buys = 0
    sells = 0

    # Disable cooldown during backtest by spacing synthetic timestamps.
    synthetic_ts = 0.0

    for i in range(80, len(candles)):
        window = candles[: i + 1]
        price = window[-1].close
        if portfolio.daily_start_equity is None:
            portfolio.daily_start_equity = portfolio.equity(price)

        signal = strategy.decide(window, portfolio)
        decision = risk.approve(signal, portfolio, price, now_ts=synthetic_ts)
        if decision.approved:
            execution = broker.execute(signal, portfolio, price, decision.order_value_krw, now_ts=synthetic_ts)
            if execution.action == "BUY":
                buys += 1
            elif execution.action == "SELL":
                sells += 1

        equity_curve.append(portfolio.equity(price))
        synthetic_ts += max(config.cooldown_seconds, 1)

    final_price = candles[-1].close
    final_equity = portfolio.equity(final_price)
    start_equity = config.initial_cash
    return_pct = (final_equity - start_equity) / start_equity
    max_dd = _max_drawdown(equity_curve)

    return BacktestResult(
        start_equity=start_equity,
        final_equity=final_equity,
        return_pct=return_pct,
        max_drawdown_pct=max_dd,
        trades=buys + sells,
        buys=buys,
        sells=sells,
        fees_paid=portfolio.fees_paid,
        realized_pnl=portfolio.realized_pnl,
    )


def fetch_and_backtest(config: BotConfig, pages: int = 5) -> BacktestResult:
    client = UpbitPublicClient()
    candles = client.get_historical_minute_candles(
        market=config.market,
        unit=config.candle_unit,
        pages=pages,
        per_page=config.candle_count,
    )
    return run_backtest(candles, config)


def _max_drawdown(equity_curve: list[float]) -> float:
    if not equity_curve:
        return 0.0
    peak = equity_curve[0]
    max_dd = 0.0
    for equity in equity_curve:
        if equity > peak:
            peak = equity
        if peak > 0:
            dd = (peak - equity) / peak
            if dd > max_dd:
                max_dd = dd
    return max_dd
