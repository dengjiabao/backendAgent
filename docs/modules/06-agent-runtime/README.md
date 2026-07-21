# 模块 06：Agent 编排与流式会话

## 完成范围

- 类型化 `AgentState`，公开传递计划、观察结果、分析、引用、审批和运行 ID，不包含隐藏思维链。
- Supervisor 图接入 Planner、Commerce、Knowledge、Analyst、Safety、Reflection 节点。
- 只读查询、知识问答和写操作审批均进入统一状态图。
- 定义公开 SSE 事件：`run_started`、`tool_proposed`、`tool_result`、`approval_required`、`citation`、`final`。
- 支持 `conversation_id`/thread ID，写操作审批状态可以暂停并恢复。
- 提供内存检查点和数据库检查点，数据库实现使用 `run_checkpoints` 表。
- `/api/v1/chat/stream` 支持会话 ID；`/api/v1/chat/resume` 支持恢复状态补丁。
- 数据库模式自动使用持久化检查点，独立模式使用内存检查点。

## 架构边界

- 节点只通过 `AgentState` 交互，连接器和审批服务通过既有端口注入。
- 检查点通过 `RunCheckpointPort` 抽象，后续可替换为 Redis 或 LangGraph PostgreSQL Checkpointer。
- SSE 事件只输出状态、工具名称、参数键、结果和引用，不输出隐藏推理。

## 验证结果

- `uv run pytest -q`：52 个测试通过。
- `uv run ruff check .`：通过。
- `uv run mypy src/ecommerce_agent`：通过。
- 临时 SQLite 数据库执行 `uv run alembic upgrade head`：成功到达 `0005_run_checkpoints`。

## Git 提交

本模块按小功能提交：

- `3d7ad34 增加 Agent 规划分析反思节点`
- `f9b8ec5 增加 Agent 流式事件协议`
- `90b3e19 增加可恢复运行状态检查点`
- `8913bac 接入 Agent 会话暂停与恢复`
- `827197e 完善会话流式接口与恢复端点`
- `4da767b 接入规划与反思状态节点`
- `d4e6c4d 接入 Agent 分析节点`
- `eed92e9 增加数据库运行检查点`
- `5a46808 接入数据库会话检查点`
- `31ee21c 补充工具提案流式事件`
