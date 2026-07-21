# 模块 04：知识存储与混合检索

## 完成范围

- 新增 `AccessScope`，在检索层按租户和允许来源过滤 Chunk。
- 新增 `RRFHybridRetriever`，将关键词候选和语义候选按 Reciprocal Rank Fusion 合并。
- `Chunk` 增加可选元数据字段，为后续文档可信等级、页码、租户和权限标签保留扩展位。
- `KnowledgeRepository` 持久化 Chunk 元数据，`PersistentHybridRetriever` 支持租户/来源过滤。
- 持久化路径的向量排名和关键词排名使用 RRF 融合，保持引用信息稳定。
- 新增 `FileObjectStore` 和 MinIO 客户端适配器，入库任务保存原始文件和 Markdown 快照。
- 增加查询改写、上下文字符预算压缩和可替换 `RerankerPort`。
- 增加 PostgreSQL `match` 关键词检索及 SQLite LIKE 回退。
- 增加 Recall@K、MRR 评估函数。
- 保持 `InMemoryRetriever` 的原有接口和行为不变，避免独立模式现有调用方破坏。

## 架构边界

- 权限范围使用独立 DTO，不直接依赖 JWT/OIDC 或具体 RBAC 实现。
- 语义排序器通过可选 Callable 注入，后续可替换为 pgvector、Reranker 或远程模型。
- 检索器只消费 `Chunk` 和范围对象，不访问数据库、MinIO 或连接器内部结构。

## 验证结果

- `uv run pytest tests/unit/test_retriever.py -q`：3 个测试通过。
- `uv run pytest -q`：31 个测试通过。
- `uv run ruff check .`：通过。
- `uv run mypy src/ecommerce_agent`：通过。

## 后续增量

生产环境仍需根据部署规模选择具体 MinIO 客户端、中文分词配置和远程 Reranker；这些实现通过现有端口替换，不需要修改检索核心。

## Git 提交

模块完成相关提交：`实现带权限过滤的混合检索`、`完善持久化混合检索`，以及后续扩展提交。
