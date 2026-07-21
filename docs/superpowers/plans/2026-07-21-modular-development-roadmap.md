# 企业级电商后台 Agent 模块化开发路线图

> **For agentic workers:** 按模块逐项执行；每个模块使用 TDD，完成后在 `docs/modules/<编号>-<英文短名>/README.md` 记录并使用中文 Git commit。

**目标：** 将剩余企业级能力拆分为边界清晰、可独立验证、可逐步替换适配器的模块，降低跨模块耦合。

**架构：** 领域模型和端口保持稳定，应用服务编排用例，适配器负责 PostgreSQL、MinIO、Celery、litemall、OpenAPI、MCP 等外部系统。模块之间只通过端口、DTO 或事件交互。

**执行顺序：** 04 知识存储与检索 -> 05 审批执行与审计 -> 06 Agent 编排与流式会话 -> 07 身份安全与租户 -> 08 可观测性与评估 -> 09 控制台完善 -> 10 部署验收。

---

## 模块 04：知识存储与混合检索

- [x] 定义租户和来源权限范围，并实现 RRF 融合基础能力；阶段记录见 `docs/modules/04-knowledge-retrieval/README.md`。
- [x] 将 Chunk 元数据持久化，并让持久化检索路径支持权限过滤和 RRF。
- [x] 定义文档快照、索引版本和持久化租户权限端口。
- [x] 实现 MinIO 原始文件/Markdown 快照适配器。
- [x] 将 PostgreSQL 全文检索和 pgvector 检索统一为可替换实现。
- [x] 实现 RRF 融合、可选 Reranker 和引用元数据。
- [x] 增加权限过滤、版本重建基础能力和 Recall@K/MRR 测试。
- [x] 通过全量质量检查并完成 `docs/modules/04-knowledge-retrieval/README.md`。

## 模块 05：审批执行与审计

- [ ] 将工具提案、审批决定和真实执行拆为独立应用服务。
- [ ] 实现编辑后 JSON Schema/权限重新校验。
- [ ] 实现审批超时自动拒绝和写操作幂等键。
- [ ] 对提案、决定、执行、失败写结构化审计事件。
- [ ] 退款、删除、角色权限变更保持默认禁止。
- [ ] 通过状态机、并发和重复决定测试后创建 `docs/modules/05-approval-execution/README.md`。

## 模块 06：Agent 编排与流式会话

- [ ] 将 Planner、Commerce、Knowledge、Analyst、Safety、Reflection 设计为节点端口。
- [ ] 引入可恢复 Checkpointer 和 conversation/thread ID。
- [ ] 定义不暴露隐藏思维链的 SSE 事件协议。
- [ ] 支持审批暂停与恢复、工具观察结果和引用事件。
- [ ] 创建图路由、流式 API 和恢复流程测试后创建 `docs/modules/06-agent-runtime/README.md`。

## 模块 07：身份、安全与租户

- [ ] 定义 Identity/RBAC/Tenant 端口和本地 JWT 实现。
- [ ] 增加 OIDC 验证适配器和工具角色检查。
- [ ] 实现手机号、地址、Cookie、Authorization、API Key 脱敏。
- [ ] 增加 Prompt Injection 检测和文档可信等级。
- [ ] 通过越权、跨租户和敏感泄漏测试后创建 `docs/modules/07-security-identity/README.md`。

## 模块 08：可观测性与评估

- [ ] 定义 Trace/Metric 端口，避免业务代码直接依赖 exporter。
- [ ] 为 HTTP、模型、检索、工具、审批和连接器执行创建 Span。
- [ ] 实现 Golden Questions、Recall、引用准确率、工具正确率、延迟和 Token 成本评估。
- [ ] 增加安全回归与 Mock-only 评估流水线。
- [ ] 通过指标和评估测试后创建 `docs/modules/08-observability-evaluation/README.md`。

## 模块 09：管理控制台完善

- [ ] 保持 API Client、视图和状态管理分层，避免页面直接拼装后端 DTO。
- [ ] 完善对话、审批、知识库、运行轨迹、评估和配置页面。
- [ ] 增加 Playwright 登录、对话、审批和 SSE 展示测试。
- [ ] 通过构建和 E2E 后创建 `docs/modules/09-console/README.md`。

## 模块 10：部署与集成验收

- [ ] 将 API、Worker、PostgreSQL、Redis、MinIO 的配置拆分为可替换服务。
- [ ] 增加非 root、健康检查、资源限制和生产 Secret 约束。
- [ ] 编写中文运维、litemall、OpenAPI、MCP 和安全文档。
- [ ] 编写冒烟脚本覆盖健康检查、入库、查询、审批和审计。
- [ ] 通过 Python、前端、Compose 和冒烟验收后创建 `docs/modules/10-deployment-acceptance/README.md`。
