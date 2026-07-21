# 企业级电商后台 Agent

这是一个可独立运行、也可适配 litemall 和其他电商系统的 Agent 平台原型。核心 Agent 不依赖具体 Java 类、路由或数据库，业务差异通过连接器隔离。

## 当前能力

- 独立模式：Mock 电商数据、商品/订单查询、知识问答占位、写操作风险判断。
- 集成骨架：litemall REST/Session 客户端、`errno` 响应映射、通用领域模型。
- RAG：MarkItDown 转 Markdown、标准化、标题结构切块、来源元数据。
- Agent API：健康检查、同步问答、SSE 流式问答、工具提案、Markdown 入库。
- 安全策略：查询自动执行；商品编辑等普通写操作进入审批；退款、删除、权限变更默认阻断。
- 中文设计与实施文档：见 `docs/superpowers/`。

## 启动后端

```powershell
$env:PYTHONPATH = "src"
python -m uvicorn ecommerce_agent.api.app:create_app --factory --reload
```

打开 `http://127.0.0.1:8000/docs` 查看 OpenAPI 文档。

## 示例请求

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/chat `
  -Method Post -ContentType 'application/json' `
  -Body '{"message":"查询商品"}'

Invoke-RestMethod http://127.0.0.1:8000/api/v1/tools/propose `
  -Method Post -ContentType 'application/json' `
  -Body '{"action":"product.update","arguments":{"id":"p-100"}}'
```

Markdown 入库接口使用原始请求体，并通过 `X-Filename` 指定来源文件名：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/knowledge/markdown `
  -Method Post -Headers @{ 'X-Filename' = '运营制度.md' } `
  -ContentType 'text/markdown' -Body (Get-Content .\docs\demo.md -Raw)
```

## 运行测试

```powershell
$env:PYTHONPATH = "src"
python -m pytest -q
```

需要处理 PDF、Office、音频或嵌入图片 OCR 时，再按需安装 `markitdown[pdf,docx,pptx,xlsx,xls,audio-transcription]` 和 `markitdown-ocr`，避免默认安装 Azure 预发布依赖。

## 运行模式

默认配置为 `RUNTIME_MODE=standalone`、`COMMERCE_ADAPTER=mock`。后续集成 litemall 或其他项目时，只需实现 `CommerceQueryPort`/`CommerceCommandPort` 连接器并切换配置，不修改 Agent 核心。

状态默认存入内存。需要持久化审批与审计时，设置 `STATE_BACKEND=database` 和 `DATABASE_URL`。本地可使用 SQLite，生产环境建议 PostgreSQL + pgvector。

## 启动基础设施

```powershell
Copy-Item .env.example .env
docker compose up -d postgres redis minio
uv run alembic upgrade head
```

Celery Worker：

```powershell
uv run celery -A ecommerce_agent.workers.celery_app:celery_app worker --loglevel=INFO
```
