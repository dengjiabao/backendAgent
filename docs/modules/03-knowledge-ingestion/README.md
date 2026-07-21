# 模块 03：知识入库

## 范围

提供 MarkItDown 转换、Markdown 标准化、结构化切块、SHA-256 幂等任务、失败重试，以及文档存储和 Embedding 的端口抽象。

## 关键能力

- 相同源文件 Hash 重复提交返回同一个任务 ID。
- 转换失败按配置次数重试并保留错误信息。
- 入库核心只依赖 `KnowledgeDocumentStorePort` 与 `EmbeddingPort`，具体存储和模型通过依赖注入提供。
- Chunk 保留来源 URI、标题路径和确定性 ID。

## 当前验证

- `uv run pytest -q`：28 个测试通过。
- `uv run ruff check .`：通过。
- `uv run mypy src/ecommerce_agent`：通过。

## 尚未纳入本模块的能力

MinIO 原始文件快照、Celery 真实 Worker、OCR 插件、PostgreSQL 全文索引和生产 Reranker 属于模块 04，不在本模块内直接耦合实现。
