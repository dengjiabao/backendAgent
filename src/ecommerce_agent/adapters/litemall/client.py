from typing import Any

import httpx

from ecommerce_agent.adapters.litemall.mapper import map_order, map_product, unwrap_response
from ecommerce_agent.domain.models import Order, Product


class LitemallClient:
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.username = username
        self.password = password
        self.client = httpx.AsyncClient(base_url=base_url, timeout=10, transport=transport)
        self._authenticated = False

    def capabilities(self) -> dict[str, bool]:
        return {
            "product.search": True,
            "product.get": True,
            "order.list": True,
            "order.get": True,
            "order.ship": True,
            "order.refund": False,
        }

    async def close(self) -> None:
        await self.client.aclose()

    async def login(self) -> None:
        response = await self.client.post("/admin/auth/login", json={"username": self.username, "password": self.password})
        response.raise_for_status()
        unwrap_response(response.json())
        self._authenticated = True

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        if not self._authenticated:
            await self.login()
        response = await self.client.request(method, path, **kwargs)
        if response.status_code == 401:
            self._authenticated = False
            await self.login()
            response = await self.client.request(method, path, **kwargs)
        response.raise_for_status()
        return unwrap_response(response.json())

    async def search_products(self, query: str) -> list[Product]:
        data = await self._request("GET", "/admin/goods/list", params={"name": query})
        return [map_product(item) for item in (data or {}).get("list", [])]

    async def list_orders(self, status: str | None = None) -> list[Order]:
        params = {"orderStatusArray": status} if status else {}
        data = await self._request("GET", "/admin/order/list", params=params)
        return [map_order(item) for item in (data or {}).get("list", [])]

    async def get_order(self, order_id: str) -> Order | None:
        data = await self._request("GET", "/admin/order/detail", params={"id": order_id})
        order = (data or {}).get("order")
        return map_order(order) if order else None
