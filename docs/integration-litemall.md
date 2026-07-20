# litemall 集成说明

当前项目已经提供 litemall 适配骨架：`src/ecommerce_agent/adapters/litemall/`。

适配器使用专用后台账号调用 `/admin/auth/login`，维护 Shiro Cookie，并将 litemall 的 `errno/errmsg/data` 映射为通用领域对象。核心 Agent 不直接引用 litemall Java 类型。

后续接入步骤：

1. 配置 litemall 管理 API 地址、专用账号和最小权限。
2. 将 `COMMERCE_ADAPTER` 切换为 `litemall`。
3. 补充商品、订单、售后和统计接口的映射测试。
4. 先启用只读能力，再按审批策略逐个启用发货等普通写操作。
5. 退款、删除、权限管理保持禁用，除非经过独立安全评审。
