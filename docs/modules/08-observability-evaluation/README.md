# 模块 08：可观测性与评估

## 完成范围

- `InMemoryTracer` 和 `Span`，支持工具/Agent 运行 Span、耗时和属性脱敏。
- `MetricsRegistry`，支持运行、失败等指标计数和 Prometheus 文本格式输出。
- Evaluation Runner 读取 JSONL Golden Questions，仅通过注入的回答函数执行，不调用生产连接器。
- 评估报告记录用例数、工具正确率、安全决策正确率、平均延迟和 Token 成本。
- 提供 RAG Recall@K、MRR 评估函数和安全回归样例。
- Agent 运行路径接入 `agent.run` Span 和 `agent_runs`/`agent_failures` 指标。

## 架构边界

- Trace/Metric 使用可替换实现，业务代码不直接依赖 exporter SDK。
- 字符串属性统一脱敏，密钥类属性按键名强制替换。
- 评估运行器只依赖回答函数协议，Mock、离线图和测试连接器均可注入。

## 验证结果

- `uv run pytest -q`：65 个测试通过。
- `uv run ruff check .`：通过。
- `uv run mypy src/ecommerce_agent`：通过。
- `git diff --check`：通过。

## Git 提交

- `4dec59b 增加可替换链路追踪与指标`
- `3ef0c17 增加黄金问题评估运行器`
- `2bee009 增加黄金问题与安全评估样例`
- `041cf40 接入 Agent 运行追踪与指标`
- `2c3490e 增加 Prometheus 指标输出`
