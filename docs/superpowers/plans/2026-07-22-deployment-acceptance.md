# 部署与集成验收实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 完成模块 10 的生产容器约束、运维与集成文档、冒烟验证脚本及最终验收记录。

**Architecture:** 保持 API/Worker 与外部 PostgreSQL、Redis、MinIO 的配置边界，通过 Compose 环境变量注入服务地址和密钥。冒烟脚本优先调用可运行的 HTTP API，并对不可用外部依赖给出明确失败信息。

**Tech Stack:** Docker Compose、Dockerfile、FastAPI、Python、PowerShell/pytest、Markdown。

---

### Task 1: 生产容器基线与配置约束

**Files:** `Dockerfile`, `docker-compose.yml`, `.env.example`, tests for compose/config behavior.

- [ ] 检查现有镜像、服务和配置缺口。
- [ ] 先为非 root、健康检查、资源限制和生产密钥拒绝行为补充失败测试/静态校验。
- [ ] 实现最小配置与容器变更并运行针对性校验。

### Task 2: 运维与集成文档

**Files:** `docs/operations.md`, new integration docs under `docs/`.

- [ ] 记录启动、迁移、健康检查、备份和生产密钥要求。
- [ ] 记录 litemall、OpenAPI、MCP 与安全边界及示例环境变量。

### Task 3: 冒烟脚本

**Files:** `scripts/smoke.py` (or existing script location), tests.

- [ ] 先覆盖健康、入库、查询、审批、审计链路的失败测试。
- [ ] 实现可配置 base URL、超时和清晰退出码的脚本。

### Task 4: 模块文档与总体验收

**Files:** `docs/modules/10-deployment-acceptance/README.md`, roadmap/handoff progress.

- [ ] 运行 Python、前端、Compose 静态校验和冒烟流程。
- [ ] 记录实际结果、限制和中文提交信息。

