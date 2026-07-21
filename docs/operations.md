# 运维说明

## 本地启动

```powershell
$env:PYTHONPATH = "src"
python -m uvicorn ecommerce_agent.api.app:create_app --factory --reload
```

## 健康检查

访问 `GET /health`。返回的 `mode` 用于确认当前是 `standalone` 还是 `integrated`。

## 持久化模式

- `STATE_BACKEND=memory`：默认模式，无外部依赖，重启后审批和审计状态清空。
- `STATE_BACKEND=database`：将审批与审计写入 SQLAlchemy 数据库。
- 运行 `uv run alembic upgrade head` 创建或升级数据库结构。
- PostgreSQL 模式会在首次迁移时启用 pgvector 扩展。
- `EMBEDDING_PROVIDER=hash` 可离线运行；生产环境可切换为 `openai` 并配置模型地址、密钥和维度。

## Redis 与后台任务

Redis 用作 Celery Broker 和结果存储。启动 Worker：

```powershell
uv run celery -A ecommerce_agent.workers.celery_app:celery_app worker --loglevel=INFO
```

## 安全要求

- 生产环境必须使用独立 Agent 账号和最小 litemall 权限。
- 不得把模型 API Key、Cookie、密码写入日志或知识库。
- MarkItDown 文件转换应放入隔离 Worker，并限制输入目录、大小、插件和超时。
- 写操作必须有审批记录和幂等键。
