"""Historical price data fetchers."""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, Optional

import pandas as pd
import requests


class DataFetchError(RuntimeError):
    """Raised when price data cannot be downloaded."""


@dataclass
class DailyK:
    """Represents the OHLCV data for a security."""

    symbol: str
    data: pd.DataFrame


class HistoricalDataFetcher:
    """Base class for historical data providers."""

    def fetch(self, symbol: str, start: date, end: date) -> DailyK:
        raise NotImplementedError


class YahooFinanceFetcher(HistoricalDataFetcher):
    """Fetch daily candles using Yahoo Finance public endpoints."""

    BASE_URL = "https://query1.finance.yahoo.com/v7/finance/chart/{symbol}"

    def __init__(self, session: Optional[requests.Session] = None, pause: float = 0.5):
        self.session = session or requests.Session()
        self.pause = pause

    def fetch(self, symbol: str, start: date, end: date) -> DailyK:
        params = {
            "interval": "1d",
            "period1": int(time.mktime(start.timetuple())),
            "period2": int(time.mktime((end).timetuple())),
        }
        url = self.BASE_URL.format(symbol=symbol)
        response = self.session.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise DataFetchError(f"Failed to download {symbol}: HTTP {response.status_code}")
        payload = response.json()
        result = payload.get("chart", {}).get("result")
        if not result:
            raise DataFetchError(f"No chart data returned for {symbol}")
        result = result[0]
        timestamps = result.get("timestamp", [])
        indicators = result.get("indicators", {})
        quotes = indicators.get("quote", [{}])[0]
        if not timestamps or not quotes:
            raise DataFetchError(f"Incomplete price data for {symbol}")
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(timestamps, unit="s").dt.tz_localize("UTC").dt.tz_convert("Asia/Hong_Kong"),
                "open": quotes.get("open"),
                "high": quotes.get("high"),
                "low": quotes.get("low"),
                "close": quotes.get("close"),
                "volume": quotes.get("volume"),
            }
        ).dropna(subset=["close"])
        df = df.set_index("date").sort_index()
        time.sleep(self.pause)
        return DailyK(symbol=symbol, data=df)


def batched(iterable: Iterable[str], size: int) -> Iterable[list[str]]:
    """Yield successive batches from *iterable* of length *size*."""

    batch: list[str] = []
    for item in iterable:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch
