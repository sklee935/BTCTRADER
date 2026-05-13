from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class BotConfig:
    market: str = "KRW-BTC"
    candle_unit: int = 5
    candle_count: int = 200
    poll_seconds: int = 60
    initial_cash: float = 1_000_000
    fee_rate: float = 0.0005
    slippage_rate: float = 0.0005
    max_position_ratio: float = 0.30
    max_trade_ratio: float = 0.10
    max_daily_loss_ratio: float = 0.02
    min_confidence: float = 0.60
    min_order_krw: float = 5_000
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.04
    cooldown_seconds: int = 300
    db_path: str = "data/paper_trading.sqlite3"
    dry_run: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_config(path: str | None = None) -> BotConfig:
    if not path:
        return BotConfig()

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with config_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    allowed = set(BotConfig.__dataclass_fields__.keys())
    unknown = sorted(set(raw.keys()) - allowed)
    if unknown:
        raise ValueError(f"Unknown config keys: {unknown}")

    cfg = BotConfig(**raw)
    validate_config(cfg)
    return cfg


def validate_config(cfg: BotConfig) -> None:
    if cfg.market != cfg.market.upper() or "-" not in cfg.market:
        raise ValueError("market must look like KRW-BTC")
    if cfg.candle_unit not in {1, 3, 5, 10, 15, 30, 60, 240}:
        raise ValueError("candle_unit must be one of 1, 3, 5, 10, 15, 30, 60, 240")
    if not 1 <= cfg.candle_count <= 200:
        raise ValueError("candle_count must be between 1 and 200")
    if cfg.poll_seconds < 10:
        raise ValueError("poll_seconds should be at least 10 seconds")
    for name in ["fee_rate", "slippage_rate", "max_position_ratio", "max_trade_ratio", "max_daily_loss_ratio", "min_confidence"]:
        value = getattr(cfg, name)
        if value < 0:
            raise ValueError(f"{name} must be non-negative")
    if cfg.max_position_ratio > 1:
        raise ValueError("max_position_ratio must be <= 1")
    if cfg.max_trade_ratio > 1:
        raise ValueError("max_trade_ratio must be <= 1")
    if not cfg.dry_run:
        raise ValueError("This MVP is paper-trading only. Keep dry_run=true.")
