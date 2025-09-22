from pathlib import Path

from oquantus.config import AppConfig


def test_load_config(tmp_path: Path):
    config_file = tmp_path / "config.yaml"
    universe_file = tmp_path / "symbols.txt"
    universe_file.write_text("AAPL\n")
    config_file.write_text(
        """
        universe:
          us:
            market: us
            type: file
            path: symbols.txt
        data:
          fetcher: yahoo
          lookback_days: 30
        strategies:
          - name: test
            type: moving_average_crossover
        stock_pool:
          path: pool.json
        """
    )
    config = AppConfig.load(config_file)
    symbols = config.all_symbols(tmp_path)
    assert symbols == ["AAPL"]
    assert config.fetcher.lookback_days == 30
    assert config.stock_pool.path == Path("pool.json")
