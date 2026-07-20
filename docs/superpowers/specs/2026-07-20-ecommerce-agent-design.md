# 企业级电商后台 Agent 设计规格

**日期：** 2026-07-20  
**状态：** 已确认，待实施计划  
**目标：** 构建一个可独立运行、也可适配 litemall 和其他电商系统的企业级后台 Agent 平台。

## 1. 背景与目标

目标系统面向运营、客服、仓储、售后、开发和管理员，提供自然语言查询、运营分析、源码与制度问答、知识库管理，以及受控的后台业务操作。系统必须同时满足两种工作模式：

1. **独立模式**：不依赖任何特定电商项目即可启动，拥有自己的身份、审批、审计、知识库、Agent 控制台和通用数据连接器；没有业务数据源时，仍可进行知识问答、文档分析和 Mock 数据演示。
2. **集成模式**：通过连接器接入 litemall 或其他电商系统。Agent 核心不能依赖 litemall 的 Java 类型、路由或响应格式，litemall 只是第一个完整参考适配器。

第一阶段的安全策略为：只读操作自动执行；商品编辑、发货等普通写操作必须人工确认；退款、删除、角色权限变更默认禁止。

## 2. 已掌握的 litemall 约束

- Spring Boot 2.1.5、Java 8、MyBatis、MySQL、Druid、PageHelper。
- 模块链路为 `db -> core -> wx-api/admin-api -> all`。
- 用户 API 为 `/wx/*`，管理 API 为 `/admin/*`。
- 后台使用 Shiro Session 与 `@RequiresPermissions`，权限字符串如 `admin:order:list`、`admin:order:ship`。
- 统一响应为 `{"errno": 0, "errmsg": "成功", "data": ...}`。
- 核心领域包含商品、库存、购物车、订单、支付、发货、售后、优惠券、团购、用户、统计、日志、角色和权限。
- 当前 Java 工作区存在用户已有删除/未跟踪改动，Agent 项目不得覆盖或清理这些改动。

## 3. 总体架构

采用 Ports and Adapters（六边形）架构，Agent 核心、标准电商领域模型与外部项目适配器分离。

```text
Vue 3 Console / API Client
          |
      FastAPI Gateway + SSE
          |
  LangGraph Supervisor Runtime
   |      |       |       |
Planner  Ops   Knowledge Safety
          |       |       |
   Tool Registry  RAG Pipeline  Approval/Audit
          |       |       |
   Commerce Ports  PostgreSQL/pgvector + Redis
          |
  litemall / OpenAPI / MCP / readonly SQL / Mock adapters
```

核心包边界：

```text
domain/       标准电商模型、风险规则、领域错误
application/  用例、Agent 编排、RAG 和上下文工程
ports/        CommerceQueryPort、CommerceCommandPort、KnowledgeSourcePort、IdentityPort、ApprovalPort、AuditPort
adapters/     litemall、generic_openapi、mcp、readonly_sql、mock
api/          FastAPI 路由、SSE 事件和管理端接口
workers/      MarkItDown 转换、OCR、嵌入、评估任务
web/          Vue 3 独立控制台
```

核心代码不得导入 `LitemallGoods`、`LitemallOrder` 等类型，不得写死 `/admin/*`，不得假设 `errno` 响应。所有项目差异在适配器中完成映射。

## 4. 两种运行模式

### 4.1 独立模式

配置 `runtime.mode=standalone`，默认使用 `mock` 或文件/CSV/Excel/JSON 数据源。平台提供自己的 JWT/OIDC 登录、RBAC、知识库、审批、审计、评估、控制台和 API Key。无业务连接器时，实时订单、库存和售后问题必须明确提示“未连接业务数据源”，禁止模型编造结果。

### 4.2 集成模式

配置 `runtime.mode=integrated`，通过 `commerce.adapter` 选择连接器：

- `litemall`：Swagger/REST、Shiro Session、权限映射、`errno` 转换。
- `openapi`：读取任意 OpenAPI 文档生成标准查询工具。
- `mcp`：接入企业 MCP Server。
- `readonly_sql`：只允许参数化查询和白名单视图，不提供写权限。
- `mock`：本地演示和回归测试。

每个连接器启动时声明能力，例如 `product.read=true`、`order.ship=false`。Supervisor 只能选择实际声明的工具。

## 5. 技术栈

- Python 3.11+、uv、pyproject、Ruff、mypy。
- FastAPI、Uvicorn、Pydantic v2、HTTPX、SSE。
- LangGraph 作为有状态编排、流式执行、持久化和 Human-in-the-loop runtime。
- OpenAI-compatible SDK，模型、Embedding、Reranker 通过配置切换。
- PostgreSQL + pgvector：业务标准模型、文档、Chunk、向量、会话、审批和审计。
- Redis：短期记忆、缓存、分布式锁、限流和任务队列状态。
- Celery：文档转换、OCR、嵌入、批量索引和离线评估任务。
- MinIO：原始文件与 Markdown 快照。
- Vue 3 + TypeScript + Vite + Element Plus + Pinia + Vue Router + ECharts。
- OpenTelemetry、Prometheus、Grafana、Jaeger、Structlog。
- pytest、pytest-asyncio、respx、Testcontainers、Hypothesis、Playwright。
- Docker Compose 第一阶段部署；Kubernetes/Helm 作为后续生产部署选项。

## 6. Agent 角色与 Hello-Agents 对应

- Supervisor：任务路由与多 Agent 编排。
- Planner：Plan-and-Solve 任务拆解。
- Commerce：商品、库存、订单、售后、用户和统计工具调用。
- Knowledge：RAG、源码/API/制度问答和来源引用。
- Analyst：指标聚合和运营报告。
- Safety：权限、风险、敏感字段、Prompt Injection 和审批策略。
- Reflection：证据检查、工具结果检查和最终答案校验。

技术映射：ReAct 为工具循环；Function Calling 使用 JSON Schema/Pydantic；Memory 使用 Redis 短期记忆和 PostgreSQL 长期记忆；Context Engineering 使用查询改写、分层上下文、压缩和 Token 预算；MCP 使用 Client 与可选 Server；Agent Skills 使用 Markdown/YAML 技能目录；Agentic RL 只导出轨迹到离线数据集，不进入在线生产链路；评估使用黄金问题集、RAG 指标和 Agent 场景回归。

## 7. MarkItDown 多模态 RAG

### 7.1 入库管线

```text
原始文件
  -> 安全隔离 Worker
  -> MarkItDown[all]
  -> 可选 markitdown-ocr + Vision 模型
  -> MarkdownNormalizer
  -> 结构解析与语义切块
  -> Embedding + 关键词索引
  -> pgvector / PostgreSQL / MinIO 快照
```

MarkItDown 负责 PDF、Word、PPT、Excel、图片、音频、HTML、CSV、JSON、XML、ZIP 等格式统一转 Markdown；`markitdown-ocr` 作为可选插件处理文档内嵌图片和扫描内容。默认关闭第三方插件，只有显式配置才启用。

### 7.2 数据源

- litemall Java 源码、SQL、Swagger、源码阅读文档；
- 企业制度、售后手册、运营手册、FAQ；
- PDF、Word、PPT、Excel、图片、音频和 Markdown；
- 商品、分类、订单状态等结构化导出；
- 后续客服记录和业务知识。

### 7.3 检索

查询改写 -> 权限过滤 -> 向量检索 + 中文关键词检索 -> RRF 融合 -> Reranker -> 上下文压缩 -> 带来源生成。Chunk 保存来源文件、版本、页码/标题、代码文件和行号等定位信息。通过 `source_hash`、解析器版本、模型版本和索引版本实现幂等重建。

MarkItDown 运行在独立 Worker，限制输入目录、文件大小、插件、网络访问和执行时长；失败保留原文件、错误日志和可重试状态。

## 8. litemall 适配器

适配器包含 Swagger Scanner、REST Client、Shiro Session Client、Permission Mapper、Response Adapter、Circuit Breaker 和 Mock Adapter。只读请求调用现有 `/admin/*` 接口；普通写操作通过专用 Agent 账号、权限白名单和审批后执行。后续可增加 Java `/internal/agent/*` 或 MCP Server，而不修改 Agent 核心。

标准领域对象包括 `Product`、`Sku`、`Inventory`、`Order`、`OrderItem`、`Shipment`、`AfterSale`、`Customer`、`Coupon`、`Promotion`、`BusinessMetric`、`ActionProposal` 和 `ApprovalDecision`。

## 9. 工具风险与审批

工具声明 `READ`、`WRITE_CONFIRM` 或 `FORBIDDEN` 风险级别。状态机为：

```text
PROPOSED -> READ:EXECUTING
PROPOSED -> WRITE_CONFIRM:WAITING_APPROVAL
WAITING_APPROVAL -> APPROVED:EXECUTING
WAITING_APPROVAL -> EDITED:VALIDATING -> EXECUTING
WAITING_APPROVAL -> REJECTED:REJECTED
PROPOSED -> FORBIDDEN:BLOCKED
```

审批记录工具、方法、路径、参数摘要、风险级别、操作者、问题、模型版本、审批人、时间和结果。审批超时自动拒绝；写操作使用幂等键防止重复发货或退款。退款、删除、角色权限变更默认为 `FORBIDDEN`。

## 10. API 与控制台

FastAPI 提供 `/api/v1/chat/stream`、`/api/v1/approvals`、`/api/v1/knowledge/sources`、`/api/v1/knowledge/reindex`、`/api/v1/tools`、`/api/v1/runs`、`/api/v1/evaluations` 和健康检查接口。SSE 事件包含 `run_started`、`thinking`、`tool_proposed`、`approval_required`、`tool_result`、`citation`、`final`、`error`。

Vue 控制台包括对话工作台、审批中心、知识库、数据源、工具权限、执行轨迹、评估中心和系统配置。可作为独立后台运行，后续通过菜单、iframe 或路由方式集成到现有电商管理端。

## 11. 错误处理与安全

- `errno != 0` 转为结构化领域错误，禁止模型猜测成功。
- 401/403 刷新 Session 一次，仍失败则报告权限不足。
- 429/5xx 指数退避并熔断；危险写操作不自动重试。
- 无 RAG 命中时声明无依据；无业务连接器时声明无实时数据。
- 参数 Schema 校验、权限白名单、敏感字段脱敏、Prompt Injection 检测。
- 平台 JWT/OIDC、RBAC、API Key Secret、操作审计和 Trace ID。
- MarkItDown 输入隔离和插件最小权限。

## 12. 测试与验收

- 单元：风险状态机、领域映射、响应解析、MarkItDown 清洗、切块、脱敏。
- 集成：Mock litemall REST、Shiro Session、分页、errno、PostgreSQL、Redis。
- RAG：Recall@K、MRR、引用准确率、版本重建和失败重试。
- Agent：工具选择、参数正确率、审批命中率、任务完成率、Token 和延迟。
- 安全：越权、提示注入、敏感泄漏、审批绕过、重复写操作。
- E2E：登录 -> 对话 -> 检索 -> 工具 -> 审批 -> 执行 -> 审计。
- 首次生产验收仅打开只读工具和 Mock Adapter，逐个启用实际写工具。

## 13. 非目标

- 不在 Agent 项目中复制 litemall 的完整交易、支付或库存实现。
- 不直接读写 litemall MySQL 作为默认集成方式。
- 不在在线链路执行 Agentic RL 训练。
- 不在第一阶段提供无人审批的退款、删除或权限管理。

## 14. 外部依据

- [Hello-Agents 项目](https://github.com/datawhalechina/hello-agents)
- [LangGraph Overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [FastAPI SSE](https://fastapi.tiangolo.com/tutorial/server-sent-events/)
- [Microsoft MarkItDown](https://github.com/microsoft/markitdown)
- [MarkItDown OCR Plugin](https://github.com/microsoft/markitdown-ocr)
- [pgvector](https://github.com/pgvector/pgvector)
- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/)
