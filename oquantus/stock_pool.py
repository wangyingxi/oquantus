"""Persistent storage for shortlisted securities."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from .strategies import StrategyResult


@dataclass
class StockPoolEntry:
    symbol: str
    strategy: str
    score: float
    timestamp: str
    metadata: Dict[str, float]


@dataclass
class StockPool:
    """Maintain the daily list of interesting securities."""

    path: Path
    entries: List[StockPoolEntry] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as handle:
                raw_entries = json.load(handle)
            self.entries = [StockPoolEntry(**entry) for entry in raw_entries]
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, result: StrategyResult) -> None:
        entry = StockPoolEntry(
            symbol=result.symbol,
            strategy=result.strategy,
            score=result.score,
            timestamp=datetime.utcnow().isoformat(),
            metadata=result.metadata,
        )
        self.entries.append(entry)

    def save(self) -> None:
        serializable = [entry.__dict__ for entry in self.entries]
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(serializable, handle, ensure_ascii=False, indent=2)

    def clear(self) -> None:
        self.entries.clear()
        if self.path.exists():
            self.path.unlink()
