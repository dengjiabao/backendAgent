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
- `npm --prefix web run typecheck`
- `npm --prefix web run e2e`（自动启动 API 与 Vite，使用 Playwright Chromium）
- `docker compose config --quiet`
- `uv run python scripts/smoke.py --base-url http://127.0.0.1:8000`（需要 API 已启动）
- `docker compose up -d --build` 后检查 `docker compose ps`，所有服务应为 healthy

## 已知限制

Playwright Chromium 需要首次执行 `npx playwright install chromium` 下载浏览器。Worker 不监听 HTTP 端口，使用 Celery `inspect ping` 健康检查；API 使用 pgvector 镜像并在初始化时启用 vector 扩展。
