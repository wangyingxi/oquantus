"""Reference strategy implementations."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .base import Strategy, StrategyResult


@dataclass
class MovingAverageCrossoverStrategy(Strategy):
    """Simple moving average crossover momentum strategy."""

    name: str
    short_window: int = 5
    long_window: int = 20
    min_volume: float = 1_000_000

    def evaluate(self, symbol: str, history: pd.DataFrame) -> StrategyResult | None:
        if history.empty or len(history) < self.long_window + 1:
            return None
        closes = history["close"].astype(float)
        volumes = history["volume"].astype(float)
        short_ma = closes.rolling(self.short_window).mean()
        long_ma = closes.rolling(self.long_window).mean()
        if short_ma.iloc[-1] <= long_ma.iloc[-1]:
            return None
        if short_ma.iloc[-2] > long_ma.iloc[-2]:
            return None
        avg_volume = volumes.tail(self.long_window).mean()
        if np.isnan(avg_volume) or avg_volume < self.min_volume:
            return None
        slope = (short_ma.iloc[-1] / short_ma.iloc[-3]) - 1 if short_ma.iloc[-3] != 0 else 0
        score = float((short_ma.iloc[-1] / long_ma.iloc[-1]) - 1)
        return StrategyResult(
            symbol=symbol,
            strategy=self.name,
            score=score,
            metadata={
                "short_ma": float(short_ma.iloc[-1]),
                "long_ma": float(long_ma.iloc[-1]),
                "avg_volume": float(avg_volume),
                "slope": float(slope),
            },
        )


@dataclass
class RSIOversoldReboundStrategy(Strategy):
    """Relative strength index mean reversion strategy."""

    name: str
    period: int = 14
    oversold: float = 30
    exit_threshold: float = 40

    def evaluate(self, symbol: str, history: pd.DataFrame) -> StrategyResult | None:
        if history.empty or len(history) < self.period + 1:
            return None
        closes = history["close"].astype(float)
        delta = closes.diff().dropna()
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)
        avg_gain = gains.rolling(self.period).mean()
        avg_loss = losses.rolling(self.period).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        latest_rsi = float(rsi.iloc[-1])
        if np.isnan(latest_rsi) or latest_rsi > self.exit_threshold:
            return None
        min_rsi = float(rsi.tail(5).min())
        if min_rsi > self.oversold:
            return None
        score = float(self.exit_threshold - latest_rsi)
        return StrategyResult(
            symbol=symbol,
            strategy=self.name,
            score=score,
            metadata={
                "rsi": latest_rsi,
                "min_rsi": min_rsi,
            },
        )
