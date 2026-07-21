# 当前实现状态

## 已实现并验证

- Python FastAPI 服务骨架和 `/health`。
- 独立模式 Mock 电商连接器、标准 Product/Order 领域模型。
- litemall REST 客户端骨架、Shiro Session 登录和 `errno` 映射。
- MarkItDown Markdown 转换入口、标准化和结构化切块。
- 商品/订单查询 API、SSE 流式事件 API。
- 只读、需审批、禁止三类风险策略及工具提案 API。
- LangGraph 1.2 稳定运行时和最小可执行状态图。
- 内存审批状态机、批准/拒绝 API、幂等决定和审计事件。
- 独立模式知识库检索、来源引用和入库后即时查询。
- SQLAlchemy 持久化接口、SQLite 独立模式回退和 PostgreSQL 配置。
- Alembic 初始迁移、PostgreSQL pgvector 扩展初始化。
- Redis/Celery 后台任务骨架以及 PostgreSQL/Redis/MinIO Docker Compose。
- pgvector 向量字段、HNSW 索引迁移、Hash/OpenAI-compatible Embedding Provider。
- 持久化混合检索、确定性离线向量、来源引用和幂等文档入库。
- Supervisor、Commerce、Knowledge、Safety 多节点 LangGraph 与 Checkpointer。
- Vue 3 独立控制台的查询和审批演示页面。
- Tool Registry 与 ToolPolicy：按连接器能力注册 JSON Schema 工具，查询工具执行前统一做风险和参数校验；Mock/litemall 只读商品、订单工具已接入 AgentService。
- MarkItDown 入库任务服务：支持源文件 SHA-256 幂等、标准化/结构切块、任务状态查询及失败重试；可作为 Celery Worker 的执行核心。
- 知识入库已通过 `KnowledgeDocumentStorePort` 和 `EmbeddingPort` 解耦具体存储与模型，后续接入 PostgreSQL、MinIO 或其他 Embedding 服务无需修改任务核心。
- 模块 04 知识存储与混合检索已完成：对象快照端口/MinIO 适配、权限过滤、RRF、关键词检索、查询改写、上下文压缩、可替换 Reranker 和 Recall@K/MRR 评估。
- 模块 05 审批执行与审计已完成：Schema 重校验、编辑、超时拒绝、幂等执行、持久化执行结果和结构化审计。
- 模块 06 Agent 编排与流式会话已完成：Planner/Analyst/Reflection 节点、公开 SSE 事件、会话检查点、审批暂停与恢复。
- 模块 07 身份、安全与租户已完成：JWT/OIDC 端口、RBAC、租户隔离、工具角色校验、敏感信息脱敏和 Prompt Injection 检测。
- 模块 08 可观测性与评估已完成：Trace/Metric 端口、Prometheus 输出、Golden Questions、RAG 指标和安全回归。
- 中文设计规格、实施计划、litemall 集成说明和运维说明。

## 尚待后续迭代

- 完整 Celery 多模态入库任务、生产 Reranker 和 PostgreSQL 全文检索优化。
- 完整 LangGraph 多 Agent 节点、Checkpointer 和 Human-in-the-loop 持久化恢复。
- 混合检索、Embedding、Reranker、来源引用和长期记忆。
- OpenAPI/MCP 通用连接器和只读 SQL 连接器。
- OIDC/RBAC、OpenTelemetry、Prometheus、评估运行器和 E2E 测试。
- 商品、订单、售后、营销等完整业务工具和审批中心页面。

当前版本是可运行的纵向切片，不应被描述为已经完成全部企业级生产能力。生产部署前必须完成上述安全、持久化、评估和连接器增强。

## 模块化开发记录

后续开发按 `docs/modules/README.md` 的模块边界执行，路线图见 `docs/superpowers/plans/2026-07-21-modular-development-roadmap.md`。每个模块完成后必须在 `docs/modules/<编号>-<英文短名>/README.md` 记录实际变更、验证结果、扩展边界和中文 Git 提交信息。
