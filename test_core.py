from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from free_btc_bot.backtest import fetch_and_backtest
from free_btc_bot.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Backtest the free BTC paper trading strategy")
    parser.add_argument("--config", default=None, help="Path to config.json")
    parser.add_argument("--pages", type=int, default=5, help="Number of 200-candle pages to fetch")
    args = parser.parse_args()

    config = load_config(args.config)
    result = fetch_and_backtest(config, pages=args.pages)

    print("\nBacktest result")
    print("-" * 40)
    print(f"start_equity      {result.start_equity:,.0f}")
    print(f"final_equity      {result.final_equity:,.0f}")
    print(f"return_pct        {result.return_pct * 100:.2f}%")
    print(f"max_drawdown_pct  {result.max_drawdown_pct * 100:.2f}%")
    print(f"trades            {result.trades}")
    print(f"buys              {result.buys}")
    print(f"sells             {result.sells}")
    print(f"fees_paid         {result.fees_paid:,.0f}")
    print(f"realized_pnl      {result.realized_pnl:,.0f}")


if __name__ == "__main__":
    main()
