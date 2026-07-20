# 企业级电商后台 Agent 实施计划

> **面向 Agent 开发者：** 实施时必须逐任务执行本计划；每个步骤使用复选框跟踪。代码、命令、类名和第三方产品名保留标准英文，说明文字全部使用中文。

**目标：** 构建一个可独立运行、也可适配 litemall 和其他电商系统的企业级后台 Agent 平台。

**架构：** 使用 Python FastAPI Sidecar、LangGraph 编排、六边形领域核心、MarkItDown 多模态 RAG、可配置电商连接器、人工审批状态机和 Vue 3 控制台。`runtime.mode=standalone` 使用 Mock/文件连接器；`runtime.mode=integrated` 使用 litemall/OpenAPI/MCP 连接器。

**技术栈：** Python 3.11+、uv、FastAPI、Pydantic v2、LangGraph、OpenAI-compatible SDK、HTTPX、PostgreSQL + pgvector、Redis、Celery、MinIO、MarkItDown、Vue 3、TypeScript、Vite、Element Plus、OpenTelemetry、pytest、Testcontainers、Playwright、Docker Compose。

---

## 任务 1：搭建服务骨架与质量门禁

**文件：**
- 新建：`pyproject.toml`、`.env.example`、`src/ecommerce_agent/__init__.py`
- 新建：`src/ecommerce_agent/config.py`、`src/ecommerce_agent/api/app.py`
- 新建：`tests/unit/test_config.py`、`Makefile`、`README.md`

- [ ] **步骤 1：编写失败的配置测试**

```python
def test_settings_default_to_standalone_mode(monkeypatch):
    monkeypatch.delenv("RUNTIME_MODE", raising=False)
    from ecommerce_agent.config import Settings
    settings = Settings(_env_file=None)
    assert settings.runtime_mode == "standalone"
    assert settings.commerce_adapter == "mock"
```

- [ ] **步骤 2：运行测试并确认失败**

运行：`uv run pytest tests/unit/test_config.py -q`

预期：因为 `ecommerce_agent.config.Settings` 尚不存在而失败。

- [ ] **步骤 3：实现配置和健康检查**

在 `config.py` 中定义 `Settings`，包含 `runtime_mode: Literal["standalone", "integrated"] = "standalone"`、`commerce_adapter: str = "mock"`、数据库/Redis/模型 URL 和 `model_api_key: SecretStr | None`。在 `api/app.py` 暴露 `create_app()` 以及返回 `{"status": "ok"}` 的 `GET /health`。

- [ ] **步骤 4：加入依赖和质量命令**

在 `pyproject.toml` 声明运行时与开发依赖，配置 Ruff 和 pytest。`Makefile` 提供 `test`、`lint`、`typecheck`、`dev`，分别执行 `uv run pytest`、`uv run ruff check .`、`uv run mypy src`、`uv run uvicorn ecommerce_agent.api.app:create_app --factory --reload`。

- [ ] **步骤 5：验证**

运行：`uv sync && uv run pytest -q && uv run ruff check .`

预期：配置测试通过，Ruff 无错误。

## 任务 2：定义通用领域模型和端口

**文件：**
- 新建：`src/ecommerce_agent/domain/models.py`、`src/ecommerce_agent/domain/errors.py`、`src/ecommerce_agent/domain/risk.py`
- 新建：`src/ecommerce_agent/ports/commerce.py`、`src/ecommerce_agent/ports/knowledge.py`、`src/ecommerce_agent/ports/security.py`
- 新建：`tests/unit/test_domain_models.py`、`tests/unit/test_risk_policy.py`

- [ ] **步骤 1：编写领域和策略测试**

```python
def test_refund_is_forbidden_by_default():
    from ecommerce_agent.domain.risk import RiskPolicy
    assert RiskPolicy().classify("order.refund").value == "forbidden"

def test_product_update_requires_approval():
    from ecommerce_agent.domain.risk import RiskPolicy
    assert RiskPolicy().classify("product.update").value == "write_confirm"
```

- [ ] **步骤 2：运行测试并确认失败**

运行：`uv run pytest tests/unit/test_domain_models.py tests/unit/test_risk_policy.py -q`

预期：领域模块不存在而失败。

- [ ] **步骤 3：实现标准领域模型**

定义 Pydantic 模型 `Product`、`Sku`、`Inventory`、`Order`、`OrderItem`、`Shipment`、`AfterSale`、`Customer`、`Promotion`、`BusinessMetric`、`ActionProposal`、`ApprovalDecision`。每个模型都包含稳定的 `id`、可选 `external_id`、`source` 和 `metadata`。

- [ ] **步骤 4：实现端口和统一错误**

定义异步协议 `CommerceQueryPort`（`search_products`、`get_order`、`list_orders`、`list_after_sales`、`get_metrics`）和 `CommerceCommandPort`（`update_product`、`ship_order`、`collect_order`）。定义 `KnowledgeSourcePort`、`ApprovalPort`、`AuditPort`、`IdentityPort`，以及 `ConnectorUnavailable`、`PermissionDenied`、`BusinessOperationFailed`、`UnsupportedCapability`。

- [ ] **步骤 5：实现风险策略**

使用 `read`、`write_confirm`、`forbidden` 三种枚举值。默认将 `*.list`、`*.get`、`*.metrics` 标记为只读，将 `product.update`、`order.ship`、`order.pay` 标记为需确认，将 `order.refund`、`resource.delete`、`role.permission.update` 标记为禁止，并支持通过 `Settings` 的 YAML 配置覆盖。

- [ ] **步骤 6：验证**

运行：`uv run pytest tests/unit/test_domain_models.py tests/unit/test_risk_policy.py -q && uv run mypy src/ecommerce_agent/domain src/ecommerce_agent/ports`

预期：测试全部通过，mypy 无错误。

## 任务 3：加入持久化、迁移和独立模式存储

**文件：**
- 新建：`src/ecommerce_agent/persistence/database.py`、`src/ecommerce_agent/persistence/models.py`
- 新建：`alembic.ini`、`alembic/env.py`、`alembic/versions/0001_initial.py`
- 新建：`tests/integration/test_persistence.py`、`docker-compose.yml`

- [ ] **步骤 1：编写持久化测试**

测试在临时 PostgreSQL 中创建 `KnowledgeDocument`、`Approval`、`AuditEvent`，并能按 `run_id`、`source_hash` 读取。

- [ ] **步骤 2：运行测试并确认失败**

运行：`uv run pytest tests/integration/test_persistence.py -q`

预期：SQLAlchemy 模型和迁移不存在而失败。

- [ ] **步骤 3：实现模型和迁移**

创建 `knowledge_sources`、`knowledge_documents`、`knowledge_chunks`、`conversations`、`runs`、`approvals`、`audit_events`、`evaluations`、`connector_capabilities` 表，并为 `source_hash`、`run_id`、`status` 和 pgvector 余弦距离建立索引。迁移必须启用 `vector` 扩展。

- [ ] **步骤 4：加入本地基础设施**

`docker-compose.yml` 启动带 pgvector 的 PostgreSQL、Redis 和 MinIO，凭据来自 `.env.example`。集成模式缺少必需 URL 时，应用必须给出明确配置错误并快速失败。

- [ ] **步骤 5：验证**

运行：`docker compose up -d postgres redis minio; uv run alembic upgrade head; uv run pytest tests/integration/test_persistence.py -q`

预期：迁移成功，持久化测试通过。

## 任务 4：实现 MarkItDown 多模态入库管线

**文件：**
- 新建：`src/ecommerce_agent/rag/markitdown_converter.py`、`src/ecommerce_agent/rag/normalizer.py`、`src/ecommerce_agent/rag/chunker.py`
- 新建：`src/ecommerce_agent/workers/ingestion.py`、`src/ecommerce_agent/api/knowledge.py`
- 新建：`tests/unit/test_markitdown_pipeline.py`、`tests/integration/test_ingestion_job.py`

- [ ] **步骤 1：编写转换和切块测试**

使用包含标题、表格、Java 代码块和来源路径的 Markdown fixture。断言标题/表格/代码被保留，重复页眉被移除，Chunk 具有 `heading_path`、`source_uri` 和确定性 ID。

- [ ] **步骤 2：运行测试并确认失败**

运行：`uv run pytest tests/unit/test_markitdown_pipeline.py -q`

预期：转换器、标准化器和切块器不存在而失败。

- [ ] **步骤 3：实现 MarkItDown 转换器**

封装 `MarkItDown(enable_plugins=settings.markitdown_enable_plugins, llm_client=..., llm_model=...)`。只接受配置的输入目录和 MIME/扩展名白名单，返回 Markdown 与转换元数据。OCR 插件可选且默认关闭。

- [ ] **步骤 4：实现标准化和结构切块**

统一 Unicode，移除重复页眉页脚，保留表格和 fenced code，先按标题切分，再按语义段落在可配置 Token/字符上限内切分。尽可能保存页码、标题、代码符号和行号。

- [ ] **步骤 5：实现异步入库**

Celery 任务负责将原文件存入 MinIO，计算 SHA-256，转换 Markdown，保存版本化文档，创建 Chunk，并将任务标记为 `completed` 或 `failed`。相同 hash 重复提交必须幂等。

- [ ] **步骤 6：暴露知识库 API**

实现上传、列表、详情、重试和重建索引接口。转换采用异步任务，立即返回 job ID，并通过 `/api/v1/knowledge/jobs/{job_id}` 查询状态。

- [ ] **步骤 7：验证**

运行：`uv run pytest tests/unit/test_markitdown_pipeline.py tests/integration/test_ingestion_job.py -q`

预期：转换、OCR 关闭、幂等和失败重试测试通过。

## 任务 5：实现混合检索、引用、记忆和上下文工程

**文件：**
- 新建：`src/ecommerce_agent/rag/embeddings.py`、`src/ecommerce_agent/rag/retriever.py`、`src/ecommerce_agent/rag/citations.py`
- 新建：`src/ecommerce_agent/memory/store.py`、`src/ecommerce_agent/context/builder.py`
- 新建：`tests/unit/test_retriever.py`、`tests/unit/test_context_builder.py`

- [ ] **步骤 1：编写检索测试**

断言查询可以同时召回精确 Java 权限字符串和语义相似的中文制度 Chunk，使用 RRF 合并，按租户/来源权限过滤，并返回引用元数据。

- [ ] **步骤 2：运行测试并确认失败**

运行：`uv run pytest tests/unit/test_retriever.py tests/unit/test_context_builder.py -q`

预期：检索和上下文模块不存在而失败。

- [ ] **步骤 3：实现 Embedding 和混合检索**

创建 OpenAI-compatible Embedding 客户端、pgvector 余弦搜索、基于中文分词 `search_text` 的 PostgreSQL 全文检索、RRF 融合和可选 Reranker 接口。不得写死供应商模型名称。

- [ ] **步骤 4：实现记忆和上下文预算**

Redis 保存带 TTL 的近期消息，PostgreSQL 保存持久化会话摘要。上下文顺序固定为系统策略、用户请求、已批准工具、检索证据、会话记忆、输出 Schema，并强制 Token 预算和输入脱敏。

- [ ] **步骤 5：实现引用**

每个证据 Chunk 生成包含文档标题、来源 URI、标题/页码/行号和 Chunk ID 的稳定引用；没有证据时必须能明确返回“未找到依据”。

- [ ] **步骤 6：验证**

运行：`uv run pytest tests/unit/test_retriever.py tests/unit/test_context_builder.py -q`

预期：权限过滤、融合、记忆、预算和引用测试通过。

## 任务 6：实现连接器 SPI 和 litemall 适配

**文件：**
- 新建：`src/ecommerce_agent/adapters/registry.py`、`src/ecommerce_agent/adapters/mock.py`
- 新建：`src/ecommerce_agent/adapters/litemall/client.py`、`src/ecommerce_agent/adapters/litemall/mapper.py`
- 新建：`src/ecommerce_agent/adapters/openapi.py`、`src/ecommerce_agent/adapters/mcp.py`
- 新建：`tests/unit/test_adapter_registry.py`、`tests/unit/test_litemall_mapper.py`、`tests/integration/test_litemall_adapter.py`

- [ ] **步骤 1：编写连接器契约测试**

断言 Mock Adapter 声明 `product.read`、`order.read`，不声明 `order.refund`；断言 litemall 的 `{"errno":0,"data":...}` 映射为标准模型，非零 errno 抛出 `BusinessOperationFailed`。

- [ ] **步骤 2：运行测试并确认失败**

运行：`uv run pytest tests/unit/test_adapter_registry.py tests/unit/test_litemall_mapper.py -q`

预期：连接器 SPI 不存在而失败。

- [ ] **步骤 3：实现注册表和 Mock Adapter**

按名称注册连接器，暴露 `capabilities()`，并根据 `Settings.commerce_adapter` 选择连接器。Mock 数据必须确定性生成并标记 `source="mock"`。

- [ ] **步骤 4：实现 litemall 客户端**

使用带 Cookie Jar 的 HTTPX，使用专用账号调用 `/admin/auth/login`，401 时只刷新一次，统一处理超时、`errno`、分页和 Shiro 权限失败。禁止记录密码、Cookie 和 Token。

- [ ] **步骤 5：实现通用 OpenAPI 和 MCP 适配器**

优先从 OpenAPI operationId 和 Schema 生成只读工具描述。MCP 适配器使用相同标准端口并保留远程工具风险元数据；SQL 适配器仅作为可选只读能力。

- [ ] **步骤 6：验证**

运行：`uv run pytest tests/unit/test_adapter_registry.py tests/unit/test_litemall_mapper.py tests/integration/test_litemall_adapter.py -q`

预期：Mock、映射和模拟 HTTP 集成测试通过，不依赖真实 litemall 数据库。

## 任务 7：实现工具注册、策略、审批和审计

**文件：**
- 新建：`src/ecommerce_agent/tools/registry.py`、`src/ecommerce_agent/tools/policy.py`
- 新建：`src/ecommerce_agent/approvals/service.py`、`src/ecommerce_agent/audit/service.py`
- 新建：`src/ecommerce_agent/api/approvals.py`
- 新建：`tests/unit/test_tool_policy.py`、`tests/unit/test_approval_state_machine.py`

- [ ] **步骤 1：编写策略和状态机测试**

测试只读工具立即执行；`product.update` 进入 `WAITING_APPROVAL`；编辑参数后重新做 Schema 校验；拒绝后不能执行；同一幂等键的第二次审批被忽略。

- [ ] **步骤 2：运行测试并确认失败**

运行：`uv run pytest tests/unit/test_tool_policy.py tests/unit/test_approval_state_machine.py -q`

预期：注册表和审批服务不存在而失败。

- [ ] **步骤 3：实现注册表和策略**

工具描述必须包含名称、说明、JSON Schema、连接器能力、风险等级、所需角色、超时、重试策略和幂等要求。所有参数执行前都必须校验。

- [ ] **步骤 4：实现审批持久化和服务**

持久化提案和决定，支持 `approve`、`edit`、`reject`、自动超时拒绝和唯一幂等键。对提案、决定、执行和失败都写审计事件。

- [ ] **步骤 5：暴露审批 API**

实现列表、详情、批准、编辑、拒绝接口，并提供 RBAC。响应包含适合 SSE 客户端展示的 `approval_required` 内容。

- [ ] **步骤 6：验证**

运行：`uv run pytest tests/unit/test_tool_policy.py tests/unit/test_approval_state_machine.py -q`

预期：风险、审批、编辑、超时、拒绝和幂等测试全部通过。

## 任务 8：实现 LangGraph 编排和流式 API

**文件：**
- 新建：`src/ecommerce_agent/agents/state.py`、`src/ecommerce_agent/agents/graph.py`、`src/ecommerce_agent/agents/prompts/*.md`
- 新建：`src/ecommerce_agent/api/chat.py`
- 新建：`tests/unit/test_graph_routing.py`、`tests/integration/test_chat_stream.py`

- [ ] **步骤 1：编写路由和流式测试**

断言知识问题经过检索；订单查询调用只读工具；写操作提案在审批点暂停；SSE 发出 `run_started`、`tool_proposed`、`approval_required`、`tool_result`、`citation`、`final` 事件。

- [ ] **步骤 2：运行测试并确认失败**

运行：`uv run pytest tests/unit/test_graph_routing.py tests/integration/test_chat_stream.py -q`

预期：Graph 和 Chat 路由不存在而失败。

- [ ] **步骤 3：实现状态和节点**

定义包含消息、计划、证据、工具提案、审批、观察结果、引用和 `run_id` 的类型化状态。构建 Supervisor -> Planner -> Knowledge/Commerce -> Safety -> Approval -> Execute -> Reflection -> Final 节点，并使用按 conversation/thread ID 持久化的 Checkpointer。

- [ ] **步骤 4：实现提示词和工具循环**

提示词必须要求证据引用、禁止虚构业务数据、实时事实必须调用工具并遵守风险策略。ReAct 观察写入状态，Reflection 拒绝无依据结论。

- [ ] **步骤 5：实现 SSE Chat 接口**

`POST /api/v1/chat/stream` 接收 `conversation_id`、`message` 和可选 `connector`，输出类型化 SSE 事件，审批后可恢复暂停的 Run。不得输出隐藏思维链，只输出状态、工具名、参数摘要、证据引用和最终答案。

- [ ] **步骤 6：验证**

运行：`uv run pytest tests/unit/test_graph_routing.py tests/integration/test_chat_stream.py -q`

预期：路由、审批暂停/恢复、引用和 SSE 事件测试通过。

## 任务 9：加入安全、可观测性和评估

**文件：**
- 新建：`src/ecommerce_agent/security/auth.py`、`src/ecommerce_agent/security/redaction.py`
- 新建：`src/ecommerce_agent/observability/otel.py`、`src/ecommerce_agent/evaluation/runner.py`
- 新建：`evals/golden_questions.jsonl`、`tests/unit/test_redaction.py`、`tests/unit/test_evaluation_runner.py`、`prometheus.yml`

- [ ] **步骤 1：编写安全和评估测试**

断言手机号、地址、Cookie、Authorization Header 和 API Key 都会脱敏；评估用例记录检索 Recall、引用正确率、工具正确率、延迟和 Token 成本。

- [ ] **步骤 2：运行测试并确认失败**

运行：`uv run pytest tests/unit/test_redaction.py tests/unit/test_evaluation_runner.py -q`

预期：安全和评估模块不存在而失败。

- [ ] **步骤 3：实现认证和脱敏**

独立模式提供本地 JWT，企业模式提供 OIDC 验证接口、角色检查和确定性 Secret 脱敏，确保日志、Prompt、Trace 和审计载荷都不泄露密钥。

- [ ] **步骤 4：实现 OpenTelemetry 和指标**

为 HTTP、模型、检索、工具提案、审批和连接器执行创建 Span；统计 Run、失败、审批、Token、延迟、检索命中率和连接器错误。根据配置导出 OTLP 或控制台。

- [ ] **步骤 5：实现评估运行器**

读取包含问题、期望来源、期望工具和安全决策的 JSONL，用 Mock Adapter 执行，持久化分数并导出报告。评估测试不得调用生产连接器。

- [ ] **步骤 6：验证**

运行：`uv run pytest tests/unit/test_redaction.py tests/unit/test_evaluation_runner.py -q && uv run ruff check . && uv run mypy src`

预期：安全和评估测试通过，Ruff 与 mypy 无错误。

## 任务 10：构建独立 Vue 控制台

**文件：**
- 新建：`web/package.json`、`web/src/router/index.ts`、`web/src/stores/auth.ts`、`web/src/api/client.ts`
- 新建：`web/src/views/ChatView.vue`、`ApprovalView.vue`、`KnowledgeView.vue`、`RunTraceView.vue`、`EvaluationView.vue`
- 新建：`web/tests/chat.spec.ts`

- [ ] **步骤 1：编写失败的 UI 测试**

Playwright 测试使用本地测试用户登录，提交 Chat 消息，显示 SSE 最终事件，显示写操作审批卡片，并提交审批决定。

- [ ] **步骤 2：运行测试并确认失败**

运行：`npm --prefix web test -- --run`

预期：Vue 应用不存在而失败。

- [ ] **步骤 3：实现控制台骨架**

创建 Vite/Vue/TypeScript 应用，加入 Element Plus 布局、认证守卫、路由权限和使用 `EventSource`/Fetch Stream 的 API Client。

- [ ] **步骤 4：实现页面**

Chat 页面显示状态/工具/引用/最终事件；审批页面支持批准/编辑/拒绝；知识库页面上传文件并轮询任务；执行轨迹页面显示审计 ID 和时间线；评估页面显示分数和失败用例。

- [ ] **步骤 5：验证**

运行：`npm --prefix web install && npm --prefix web run build && npm --prefix web test -- --run`

预期：生产构建成功，Playwright 测试通过。

## 任务 11：部署、文档和最终验收

**文件：**
- 修改：`docker-compose.yml`、`README.md`
- 新建：`Dockerfile`、`docs/operations.md`、`docs/integration-litemall.md`、`docs/integration-openapi.md`、`docs/security.md`、`scripts/smoke.ps1`

- [ ] **步骤 1：编写双模式和连接器文档**

用中文记录 `runtime.mode=standalone` 的 Mock/文件连接器启动方法，以及 `runtime.mode=integrated` 的 litemall REST/Swagger 方法；说明新增连接器而不修改 Agent 核心的流程。

- [ ] **步骤 2：加入生产化 Docker 服务**

构建 API/Worker 镜像，配置健康检查、非 root 用户、资源限制、PostgreSQL/Redis/MinIO 依赖，并区分开发凭据和生产 Secret。

- [ ] **步骤 3：编写冒烟脚本**

`scripts/smoke.ps1` 依次调用 `/health`、上传 Markdown fixture、轮询入库完成、用 Mock 执行只读问题、验证写操作产生审批提案，并查询审计接口。

- [ ] **步骤 4：运行全量验证**

运行：`uv run pytest -q; uv run ruff check .; uv run mypy src; npm --prefix web run build; docker compose config; powershell -ExecutionPolicy Bypass -File scripts/smoke.ps1`

预期：Python 测试通过，Ruff/mypy 无错误，前端构建成功，Compose 配置有效，冒烟脚本逐项通过。

- [ ] **步骤 5：执行验收清单**

确认独立模式不依赖 litemall；集成 Mock litemall 能映射 `errno`；MarkItDown 入库幂等；写工具不能绕过审批；禁止动作被阻断；回答包含引用；审计包含 `trace_id`；日志不含 Secret。

