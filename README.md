# Oquantus 自动选股工具

本项目提供一个可扩展的自动化交易辅助框架，每天批量下载港股和美股的日 K 数据，
按照多套可配置的筛选策略生成值得关注的“股票池”。

## 功能概览

- **多市场标的管理**：通过配置文件定义港股、美股等市场的股票列表，支持文件或内联方式扩展。
- **可插拔数据源**：默认集成 Yahoo Finance 日线行情下载，可按需替换。
- **策略引擎**：内置均线突破、RSI 反弹等示例策略，支持在配置文件中启用、禁用或新增参数化策略。
- **股票池维护**：筛选结果自动写入 JSON 文件，便于与其他流程联动或进一步分析。
- **命令行入口**：`python main.py` 一键执行每日筛选任务，可通过参数控制处理日期和标的数量。

## 快速开始

1. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

2. 查看并按需求修改 `config/default.yaml`（路径以配置文件所在目录为基准，例如默认配置会引用 `../data/...`）：

   - `universe`：定义港股、美股代码来源，可通过文本文件维护，也可改成 `inline`。
   - `strategies`：新增或调整策略、参数、启用状态。
   - `stock_pool.path`：股票池输出路径。

3. 运行筛选：

   ```bash
   python main.py --config config/default.yaml
   ```

   可选参数：

   - `--limit`：限制当次处理的股票数量，便于测试。
   - `--today`：指定日期（格式 `YYYY-MM-DD`），用于回测或补数据。

运行完成后，筛选通过的标的会写入 `data/stock_pool.json`，并在命令行输出每只股票对应的策略结果和关键指标。

## 扩展方向

- 实现更多数据源（如券商、聚宽、tushare 等），在 `oquantus/data/fetchers.py` 中新增类并在配置中切换。
- 添加自定义策略：继承 `oquantus.strategies.base.Strategy` 并在 `StrategyFactory` 注册后即可在配置中启用。
- 将股票池结果推送到消息系统、数据库或 Web 界面，实现全自动监控。
