import pandas as pd

from oquantus.strategies.implementations import (
    MovingAverageCrossoverStrategy,
    RSIOversoldReboundStrategy,
)


def make_history(values, volume=2_000_000):
    return pd.DataFrame(
        {
            "close": values,
            "open": values,
            "high": values,
            "low": values,
            "volume": [volume] * len(values),
        }
    )


def test_moving_average_crossover_triggers():
    prices = [
        15,
        14.5,
        14,
        13.5,
        13,
        12.8,
        12.5,
        12.3,
        12.1,
        12.0,
        12.2,
        12.2,
        12.2,
    ]
    history = make_history(prices)
    strategy = MovingAverageCrossoverStrategy(
        name="test", short_window=3, long_window=5, min_volume=1000
    )
    result = strategy.evaluate("AAPL", history)
    assert result is not None
    assert result.strategy == "test"


def test_rsi_rebound_triggers():
    prices = [20, 19.5, 19.0, 18.5, 18.0, 17.5, 17.0, 16.8, 16.5, 16.7, 17.0]
    history = make_history(prices)
    strategy = RSIOversoldReboundStrategy(
        name="rsi", period=3, oversold=40, exit_threshold=70
    )
    result = strategy.evaluate("TSLA", history)
    assert result is not None
    assert result.symbol == "TSLA"
