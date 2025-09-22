"""Configuration models and helpers for the screening application."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import yaml


@dataclass
class UniverseSource:
    """Represents a source of tickers for a specific market."""

    market: str
    type: str
    path: Optional[Path] = None
    symbols: Optional[List[str]] = None

    def load_symbols(self, base_path: Path) -> List[str]:
        """Return the list of tickers defined by this source."""

        if self.type == "file":
            if not self.path:
                raise ValueError(f"Universe source for {self.market} requires a file path")
            resolved = (base_path / self.path).resolve()
            if not resolved.exists():
                raise FileNotFoundError(f"Universe file not found: {resolved}")
            with resolved.open("r", encoding="utf-8") as handle:
                return [line.strip() for line in handle if line.strip() and not line.startswith("#")]
        if self.type == "inline":
            if not self.symbols:
                raise ValueError(f"Inline universe source for {self.market} requires symbols")
            return list(dict.fromkeys(symbol.upper() for symbol in self.symbols))
        raise ValueError(f"Unsupported universe source type: {self.type}")


@dataclass
class StrategyConfig:
    """Configuration for a single screening strategy."""

    name: str
    type: str
    params: Dict[str, object] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class StockPoolConfig:
    """Configuration for managing the stock pool."""

    path: Path


@dataclass
class FetcherConfig:
    """Configuration describing how to fetch historical data."""

    type: str = "yahoo"
    lookback_days: int = 120
    batch_size: int = 20

    def period(self, today: Optional[date] = None) -> tuple[date, date]:
        end_date = today or date.today()
        start_date = end_date - timedelta(days=self.lookback_days)
        return start_date, end_date


@dataclass
class AppConfig:
    """Root configuration for the screening application."""

    universe: List[UniverseSource]
    fetcher: FetcherConfig
    strategies: List[StrategyConfig]
    stock_pool: StockPoolConfig

    @classmethod
    def load(cls, path: Path) -> "AppConfig":
        with path.open("r", encoding="utf-8") as handle:
            raw = yaml.safe_load(handle)
        universe_sources = [
            UniverseSource(
                market=entry.get("market", key),
                type=entry["type"],
                path=Path(entry["path"]) if "path" in entry else None,
                symbols=entry.get("symbols"),
            )
            for key, entry in raw.get("universe", {}).items()
        ]
        strategies = [
            StrategyConfig(
                name=item["name"],
                type=item["type"],
                params=item.get("params", {}),
                enabled=item.get("enabled", True),
            )
            for item in raw.get("strategies", [])
            if item.get("enabled", True)
        ]
        stock_pool = StockPoolConfig(path=Path(raw["stock_pool"]["path"]))
        fetcher_raw = raw.get("data", {})
        fetcher = FetcherConfig(
            type=fetcher_raw.get("fetcher", "yahoo"),
            lookback_days=fetcher_raw.get("lookback_days", 120),
            batch_size=fetcher_raw.get("batch_size", 20),
        )
        return cls(
            universe=universe_sources,
            fetcher=fetcher,
            strategies=strategies,
            stock_pool=stock_pool,
        )

    def all_symbols(self, base_path: Path) -> List[str]:
        """Aggregate symbols from all configured universe sources."""

        symbols: List[str] = []
        for source in self.universe:
            symbols.extend(source.load_symbols(base_path))
        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for symbol in symbols:
            sym = symbol.upper()
            if sym not in seen:
                seen.add(sym)
                deduped.append(sym)
        return deduped


def load_config(path: Path) -> AppConfig:
    """Convenience wrapper around :meth:`AppConfig.load`."""

    return AppConfig.load(path)
