# OpenAPI 集成说明

服务启动后可访问 `/docs` 和 `/openapi.json` 获取 OpenAPI 3 描述。生产网关应仅暴露 HTTPS，并通过 `Authorization: Bearer <JWT>` 传递身份。核心接口包括：`/health`、`/api/v1/chat`、`/api/v1/knowledge/markdown`、`/api/v1/approvals`。

API 客户端应设置超时、追踪请求 ID，并将写操作限制在审批接口；不要绕过 Agent 的提案与审计链路直接调用外部电商系统。
