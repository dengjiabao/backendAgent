# MCP 集成边界

MCP 工具应先映射到 `ports/` 中的稳定端口，再由 `tools/registry.py` 注册。MCP Server 不得直接访问数据库会话、密钥或 litemall Java 类型；工具声明风险等级、输入模型、超时和所需角色后，写操作仍必须生成审批提案。
