from pathlib import Path

from oquantus.stock_pool import StockPool
from oquantus.strategies.base import StrategyResult


def test_stock_pool_roundtrip(tmp_path: Path):
    pool_file = tmp_path / "pool.json"
    pool = StockPool(pool_file)
    result = StrategyResult(
        symbol="AAPL",
        strategy="test",
        score=0.1,
        metadata={"short_ma": 10.0},
    )
    pool.add(result)
    pool.save()

    reloaded = StockPool(pool_file)
    assert len(reloaded.entries) == 1
    entry = reloaded.entries[0]
    assert entry.symbol == "AAPL"
    assert entry.strategy == "test"
