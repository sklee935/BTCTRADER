from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from .models import Candle


class UpbitApiError(RuntimeError):
    pass


@dataclass
class UpbitResponse:
    data: Any
    remaining_req: str | None


class UpbitPublicClient:
    """Small Upbit quotation client using only Python standard library."""

    def __init__(self, base_url: str = "https://api.upbit.com/v1", timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get_json(self, path: str, params: dict[str, Any]) -> UpbitResponse:
        query = urllib.parse.urlencode(params)
        url = f"{self.base_url}{path}?{query}"
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "free-btc-paper-bot/0.1",
            },
            method="GET",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
                remaining = response.headers.get("Remaining-Req")
                return UpbitResponse(data=json.loads(body), remaining_req=remaining)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")
            raise UpbitApiError(f"Upbit HTTP {e.code}: {detail}") from e
        except urllib.error.URLError as e:
            raise UpbitApiError(f"Upbit network error: {e}") from e

    def get_minute_candles(
        self,
        market: str = "KRW-BTC",
        unit: int = 5,
        count: int = 200,
        to: str | None = None,
    ) -> tuple[list[Candle], str | None]:
        if count < 1 or count > 200:
            raise ValueError("count must be between 1 and 200")

        params: dict[str, Any] = {"market": market, "count": count}
        if to:
            params["to"] = to

        response = self._get_json(f"/candles/minutes/{unit}", params)
        candles = [self._parse_candle(item, unit) for item in response.data]
        candles.sort(key=lambda x: x.time_utc)
        return candles, response.remaining_req

    def get_historical_minute_candles(
        self,
        market: str = "KRW-BTC",
        unit: int = 5,
        pages: int = 5,
        per_page: int = 200,
        sleep_seconds: float = 0.12,
    ) -> list[Candle]:
        """Fetch multiple pages of minute candles.

        Upbit returns newest candles first. We paginate by using the oldest candle time
        as the exclusive `to` cursor for the next request.
        """
        all_candles: dict[str, Candle] = {}
        cursor: str | None = None

        for _ in range(max(1, pages)):
            candles, _remaining = self.get_minute_candles(
                market=market,
                unit=unit,
                count=per_page,
                to=cursor,
            )
            if not candles:
                break

            for candle in candles:
                all_candles[candle.time_utc] = candle

            oldest = candles[0].time_utc
            cursor = oldest
            time.sleep(sleep_seconds)

        result = list(all_candles.values())
        result.sort(key=lambda x: x.time_utc)
        return result

    @staticmethod
    def _parse_candle(item: dict[str, Any], unit: int) -> Candle:
        return Candle(
            market=str(item["market"]),
            time_utc=str(item["candle_date_time_utc"]),
            time_kst=str(item.get("candle_date_time_kst", "")),
            timestamp_ms=int(item["timestamp"]),
            open=float(item["opening_price"]),
            high=float(item["high_price"]),
            low=float(item["low_price"]),
            close=float(item["trade_price"]),
            volume=float(item["candle_acc_trade_volume"]),
            value=float(item["candle_acc_trade_price"]),
            unit=int(item.get("unit", unit)),
        )
