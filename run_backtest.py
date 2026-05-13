from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from free_btc_bot.bot import PaperTradingBot
from free_btc_bot.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Free BTC paper trading bot")
    parser.add_argument("--config", default=None, help="Path to config.json")
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    args = parser.parse_args()

    config = load_config(args.config)
    bot = PaperTradingBot(config)
    try:
        if args.once:
            bot.run_once()
        else:
            bot.run_forever()
    finally:
        bot.close()


if __name__ == "__main__":
    main()
