# 模块 07：身份、安全与租户

## 完成范围

- 定义 `Identity`、`TenantContext` 和统一 `RBACService`。
- 工具定义支持 `required_roles`，执行前统一检查角色和租户。
- 独立模式提供 HS256 JWT 签发和验证接口。
- 提供 `OIDCTokenVerifierPort`，企业 OIDC 验证器可通过依赖注入替换。
- FastAPI 提供 `/api/v1/auth/token` 和 `/api/v1/auth/me`。
- 对手机号、地址、Cookie、Authorization Header 和 API Key 执行确定性脱敏。
- 提供 Prompt Injection 检测和 `trusted/internal/external` 文档可信等级。

## 架构边界

- 身份与租户使用稳定领域 DTO，不依赖具体 IdP SDK。
- OIDC 验证通过端口注入，核心不绑定供应商。
- RBAC 校验在工具策略层统一执行，连接器不重复实现平台权限。
- 脱敏函数可复用于日志、Prompt、Trace 和审计载荷。

## 安全约束

- 默认 JWT Secret 只允许本地开发，生产环境必须设置 `JWT_SECRET`。
- OIDC 验证器必须验证 issuer、audience、签名和过期时间。
- 文档可信等级不能绕过工具风险策略，外部文档中的指令覆盖模式会被阻断。

## 验证结果

- `uv run pytest -q`：60 个测试通过。
- `uv run ruff check .`：通过。
- `uv run mypy src/ecommerce_agent`：通过。
- `git diff --check`：通过。

## Git 提交

- `5c5f5d8 增加租户与角色权限模型`
- `90d8f3c 增加本地 JWT 与 OIDC 验证端口`
- `4377fa8 增加敏感信息脱敏能力`
- `16853ed 增加提示注入检测与文档可信等级`
- `1b7bdf1 接入独立模式 JWT 接口`
- `f517f91 接入工具角色与租户校验`
