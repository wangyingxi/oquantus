"""Factory for building strategies from configuration."""

from __future__ import annotations

from typing import Dict, Type

from .base import Strategy
from .implementations import (
    MovingAverageCrossoverStrategy,
    RSIOversoldReboundStrategy,
)


class StrategyFactory:
    """Create strategy instances from configuration dictionaries."""

    registry: Dict[str, Type[Strategy]] = {
        "moving_average_crossover": MovingAverageCrossoverStrategy,
        "rsi_rebound": RSIOversoldReboundStrategy,
    }

    @classmethod
    def create(cls, name: str, type_: str, params: Dict[str, object]) -> Strategy:
        if type_ not in cls.registry:
            raise ValueError(f"Unknown strategy type: {type_}")
        strategy_cls = cls.registry[type_]
        return strategy_cls(name=name, **params)
