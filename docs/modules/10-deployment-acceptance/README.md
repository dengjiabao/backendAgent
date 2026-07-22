# 模块 10：部署与集成验收

## 范围

本模块补齐 API、Worker、PostgreSQL、Redis、MinIO 的 Compose 部署基线，加入非 root 容器、健康检查、资源限制和生产密钥校验，并提供运维、litemall、OpenAPI、MCP、安全说明及 HTTP 冒烟脚本。

## 架构边界

Compose 只负责注入外部服务地址和凭据；业务代码仍通过配置与端口访问数据库、对象存储、队列和 litemall。生产环境由 `APP_ENV=production` 开关强制拒绝开发 JWT 默认值。

## 验证命令

- `uv run pytest -q`
- `uv run ruff check .`
- `uv run mypy src`
- `npm --prefix web run build`
- `docker compose config --quiet`
- `uv run python scripts/smoke.py --base-url http://127.0.0.1:8000`（需要 API 已启动）

## 已知限制

本地环境未必有 Docker daemon，因此 `docker compose config` 只能证明静态配置可解析，不能替代容器运行验收。Playwright 浏览器运行时仍未安装，控制台继续以构建验证为基线。
