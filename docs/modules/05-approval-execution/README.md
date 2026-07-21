# 模块 05：审批执行与审计

## 完成范围

- 审批提案支持唯一幂等键，重复提案返回原记录。
- 写操作参数支持 Pydantic Schema 校验；编辑审批参数时重新校验。
- 支持审批超时拒绝、手动过期和拒绝后禁止执行。
- 新增异步执行端口约定，审批通过后执行结果写入存储，重复执行返回已保存结果。
- 提案、决定、编辑、超时、执行和执行失败均写入审计事件。
- 审批 API 支持批准/拒绝、编辑和过期接口。
- PostgreSQL/SQLite 迁移增加幂等键、超时、编辑和执行结果字段。

## 架构边界

- `ApprovalService` 只依赖 `StateStore` 和执行器协议，不依赖具体电商连接器。
- 具体写操作由外部执行器提供，退款、删除、角色权限变更仍由 `RiskPolicy` 默认禁止。
- 审计统一通过 `AuditService` 写入，业务代码不直接拼装数据库行。

## 验证结果

- `uv run pytest -q`：43 个测试通过。
- `uv run ruff check .`：通过。
- `uv run mypy src/ecommerce_agent`：通过。
- 使用临时 SQLite 数据库执行 `uv run alembic upgrade head`：迁移到 `0004_approval_execution` 成功。

## Git 提交

本模块完成提交信息：`完成审批执行与审计模块`。
