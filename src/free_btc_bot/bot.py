from __future__ import annotations

import time
from datetime import datetime

from .config import BotConfig
from .paper_broker import PaperBroker
from .risk import RiskManager
from .storage import SQLiteStore
from .strategy import TrendVolatilityStrategy
from .upbit_public import UpbitPublicClient


class PaperTradingBot:
    def __init__(self, config: BotConfig):
        self.config = config
        self.client = UpbitPublicClient()
        self.store = SQLiteStore(config.db_path)
        self.strategy = TrendVolatilityStrategy(config)
        self.risk = RiskManager(config)
        self.broker = PaperBroker(config)

    def close(self) -> None:
        self.store.close()

    def run_once(self) -> None:
        candles, remaining = self.client.get_minute_candles(
            market=self.config.market,
            unit=self.config.candle_unit,
            count=self.config.candle_count,
        )
        self.store.save_candles(candles)

        recent = self.store.load_recent_candles(
            market=self.config.market,
            unit=self.config.candle_unit,
            limit=self.config.candle_count,
        )
        if not recent:
            print("No candles available")
            return

        price = recent[-1].close
        portfolio = self.store.load_portfolio(self.config)
        if portfolio.daily_start_equity is None:
            portfolio.daily_start_equity = portfolio.equity(price)

        signal = self.strategy.decide(recent, portfolio)
        decision = self.risk.approve(signal, portfolio, price)
        execution = None

        if decision.approved:
            execution = self.broker.execute(signal, portfolio, price, decision.order_value_krw)
            self.store.save_portfolio(portfolio)
        else:
            self.store.save_portfolio(portfolio)

        self.store.log_event(self.config.market, price, portfolio, signal, decision, execution)
        self._print_status(price, portfolio, signal, decision, execution, remaining)

    def run_forever(self) -> None:
        while True:
            try:
                self.run_once()
                time.sleep(self.config.poll_seconds)
            except KeyboardInterrupt:
                print("Stopped by user")
                break
            except Exception as exc:
                print(f"[ERROR] {exc}")
                time.sleep(min(self.config.poll_seconds, 30))

    def _print_status(self, price, portfolio, signal, decision, execution, remaining) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        print(
            f"\n[{now}] {self.config.market} price={price:,.0f} "
            f"equity={portfolio.equity(price):,.0f} cash={portfolio.cash:,.0f} btc={portfolio.btc:.8f}"
        )
        print(f"signal={signal.action} confidence={signal.confidence:.2f} reason={signal.reason}")
        print(f"risk={decision.message} order_value={decision.order_value_krw:,.0f}")
        if execution:
            print(
                f"execution={execution.action} price={execution.price:,.0f} "
                f"qty={execution.quantity_btc:.8f} fee={execution.fee_krw:,.0f}"
            )
        if remaining:
            print(f"upbit_remaining_req={remaining}")
