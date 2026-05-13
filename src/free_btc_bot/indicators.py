from __future__ import annotations

import math
from typing import Sequence


def sma(values: Sequence[float], period: int) -> float | None:
    if period <= 0:
        raise ValueError("period must be positive")
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


def pct_changes(values: Sequence[float]) -> list[float]:
    changes: list[float] = []
    for prev, cur in zip(values, values[1:]):
        if prev == 0:
            changes.append(0.0)
        else:
            changes.append((cur - prev) / prev)
    return changes


def rolling_std(values: Sequence[float], period: int) -> float | None:
    if len(values) < period:
        return None
    window = list(values[-period:])
    mean = sum(window) / len(window)
    variance = sum((x - mean) ** 2 for x in window) / len(window)
    return math.sqrt(variance)


def rsi(closes: Sequence[float], period: int = 14) -> float | None:
    if len(closes) < period + 1:
        return None

    gains = []
    losses = []
    recent = closes[-(period + 1):]
    for prev, cur in zip(recent, recent[1:]):
        diff = cur - prev
        if diff >= 0:
            gains.append(diff)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(abs(diff))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))
