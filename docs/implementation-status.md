# 当前实现状态

## 已实现并验证

- Python FastAPI 服务骨架和 `/health`。
- 独立模式 Mock 电商连接器、标准 Product/Order 领域模型。
- litemall REST 客户端骨架、Shiro Session 登录和 `errno` 映射。
- MarkItDown Markdown 转换入口、标准化和结构化切块。
- 商品/订单查询 API、SSE 流式事件 API。
- 只读、需审批、禁止三类风险策略及工具提案 API。
- Vue 3 独立控制台的查询和审批演示页面。
- 中文设计规格、实施计划、litemall 集成说明和运维说明。

## 尚待后续迭代

- PostgreSQL/pgvector 持久化和 Redis/Celery 生产任务队列。
- 完整 LangGraph 多 Agent 图、Human-in-the-loop 持久化恢复。
- 混合检索、Embedding、Reranker、来源引用和长期记忆。
- OpenAPI/MCP 通用连接器和只读 SQL 连接器。
- OIDC/RBAC、OpenTelemetry、Prometheus、评估运行器和 E2E 测试。
- 商品、订单、售后、营销等完整业务工具和审批中心页面。

当前版本是可运行的纵向切片，不应被描述为已经完成全部企业级生产能力。生产部署前必须完成上述安全、持久化、评估和连接器增强。
