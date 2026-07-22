# 安全集成要求

- 生产设置 `APP_ENV=production` 时，必须提供长度至少 32 的随机 `JWT_SECRET`；开发默认值会被拒绝。
- PostgreSQL、Redis、MinIO 密码通过部署 Secret 注入，不提交真实 `.env`。
- 生产 API/Worker 容器使用非 root 用户运行，并限制 CPU/内存。
- 日志和审计中不得写入模型密钥、Cookie、Authorization、手机号和地址；写操作必须可追溯到审批与审计事件。
