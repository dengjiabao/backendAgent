from ecommerce_agent.adapters.litemall.client import LitemallClient
from ecommerce_agent.adapters.mock import MockCommerceAdapter
from ecommerce_agent.config import Settings


def build_adapter(settings: Settings) -> MockCommerceAdapter | LitemallClient:
    if settings.commerce_adapter == "mock":
        return MockCommerceAdapter()
    if settings.commerce_adapter == "litemall":
        if not settings.litemall_username or settings.litemall_password is None:
            raise ValueError("litemall 连接器需要 LITEMALL_USERNAME 和 LITEMALL_PASSWORD")
        return LitemallClient(
            settings.litemall_base_url,
            settings.litemall_username,
            settings.litemall_password.get_secret_value(),
        )
    raise ValueError(f"当前版本尚未启用连接器：{settings.commerce_adapter}")
