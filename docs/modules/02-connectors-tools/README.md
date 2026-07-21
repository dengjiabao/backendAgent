# 模块 02：连接器与工具治理

## 范围

提供 Mock 与 litemall 基础连接器、统一响应映射、连接器能力声明、Tool Registry、JSON Schema 参数校验和只读工具策略。

## 关键能力

- litemall 的 `errno/errmsg/data` 在适配器内转换为领域错误和标准模型。
- 商品搜索、订单列表、订单详情通过注册工具执行。
- 工具执行前校验注册状态、风险等级、参数 Schema 和超时。
- 外部连接器未声明的能力不能被 Agent 选择。

## 当前验证

- `uv run pytest -q`：包含连接器、工具注册和 AgentService 回归测试。
- `uv run ruff check .`
- `uv run mypy src/ecommerce_agent`

## 扩展注意事项

新增 OpenAPI、MCP 或只读 SQL 连接器时，只实现 `CommerceQueryPort`/能力声明和适配器映射，不修改 `domain/` 与 Agent 核心路由。
