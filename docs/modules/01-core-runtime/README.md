# 模块 01：核心领域与运行基础

## 范围

提供独立模式可启动的 FastAPI、配置、通用电商领域模型、风险等级、状态存储、SQLAlchemy/Alembic 基础和健康检查。

## 架构边界

- `domain/` 不依赖 litemall、HTTP 客户端或数据库实现。
- `ports/` 只定义异步能力和存储协议。
- `adapters/`、`persistence/` 和 `api/` 依赖端口，不反向污染领域模型。

## 当前验证

- `uv run pytest -q`
- `uv run ruff check .`
- `uv run mypy src/ecommerce_agent`

当前基线验证结果已在后续模块回归中持续保持通过。

## 扩展注意事项

新增业务对象必须先进入通用领域模型和端口，禁止直接在 API 路由中使用外部系统 DTO。
