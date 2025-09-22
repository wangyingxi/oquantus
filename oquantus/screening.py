"""High level orchestration for the daily screening workflow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, List

from .config import AppConfig
from .data.fetchers import HistoricalDataFetcher
from .stock_pool import StockPool
from .strategies import Strategy, StrategyFactory


@dataclass
class ScreeningCandidate:
    symbol: str
    results: List


class ScreeningEngine:
    """Coordinates data fetching, strategy execution and pool updates."""

    def __init__(
        self,
        config: AppConfig,
        fetcher: HistoricalDataFetcher,
        strategies: Iterable[Strategy],
        stock_pool: StockPool,
    ) -> None:
        self.config = config
        self.fetcher = fetcher
        self.strategies = list(strategies)
        self.stock_pool = stock_pool

    def screen(self, symbols: Iterable[str], start: date, end: date) -> List[ScreeningCandidate]:
        candidates: List[ScreeningCandidate] = []
        for symbol in symbols:
            try:
                daily_k = self.fetcher.fetch(symbol, start, end)
            except Exception:  # noqa: BLE001
                # Skip problematic symbols but continue processing others
                continue
            history = daily_k.data
            symbol_results = []
            for strategy in self.strategies:
                result = strategy.evaluate(symbol, history)
                if result:
                    symbol_results.append(result)
                    self.stock_pool.add(result)
            if symbol_results:
                candidates.append(ScreeningCandidate(symbol=symbol, results=symbol_results))
        self.stock_pool.save()
        return candidates

    @classmethod
    def from_config(cls, config: AppConfig, base_path: Path) -> "ScreeningEngine":
        from .data.fetchers import YahooFinanceFetcher

        fetcher = YahooFinanceFetcher()
        strategies = [
            StrategyFactory.create(item.name, item.type, item.params)
            for item in config.strategies
        ]
        stock_pool = StockPool(base_path / config.stock_pool.path)
        return cls(config=config, fetcher=fetcher, strategies=strategies, stock_pool=stock_pool)
