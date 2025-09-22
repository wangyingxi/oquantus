"""Base classes for screening strategies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import pandas as pd


@dataclass
class StrategyResult:
    """The outcome of applying a strategy to a symbol."""

    symbol: str
    strategy: str
    score: float
    metadata: Dict[str, float]


class Strategy:
    """Base class for all screening strategies."""

    name: str

    def evaluate(self, symbol: str, history: pd.DataFrame) -> Optional[StrategyResult]:
        """Return a :class:`StrategyResult` if the symbol passes the screen."""

        raise NotImplementedError
