# 运维说明

## 本地启动

```powershell
$env:PYTHONPATH = "src"
python -m uvicorn ecommerce_agent.api.app:create_app --factory --reload
```

## 健康检查

访问 `GET /health`。返回的 `mode` 用于确认当前是 `standalone` 还是 `integrated`。

## 安全要求

- 生产环境必须使用独立 Agent 账号和最小 litemall 权限。
- 不得把模型 API Key、Cookie、密码写入日志或知识库。
- MarkItDown 文件转换应放入隔离 Worker，并限制输入目录、大小、插件和超时。
- 写操作必须有审批记录和幂等键。
