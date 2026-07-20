from decimal import Decimal

from ecommerce_agent.domain.models import BusinessMetric, Order, Product


class MockCommerceAdapter:
    def __init__(self) -> None:
        self.products = [
            Product(
                id="p-100",
                name="企业级智能客服套装",
                price=Decimal("1999.00"),
                status="on_sale",
                stock=42,
                source="mock",
            ),
            Product(
                id="p-200",
                name="仓储管理终端",
                price=Decimal("899.00"),
                status="on_sale",
                stock=18,
                source="mock",
            ),
        ]
        self.orders = [
            Order(
                id="o-100",
                order_sn="MOCK20260720001",
                status="paid",
                amount=Decimal("1999.00"),
                source="mock",
            ),
        ]

    def capabilities(self) -> dict[str, bool]:
        return {
            "product.search": True,
            "product.get": True,
            "order.list": True,
            "order.get": True,
            "order.ship": False,
        }

    async def search_products(self, query: str) -> list[Product]:
        return [p for p in self.products if query.lower() in p.name.lower()]

    async def list_orders(self, status: str | None = None) -> list[Order]:
        return [o for o in self.orders if status is None or o.status == status]

    async def get_order(self, order_id: str) -> Order | None:
        return next((o for o in self.orders if o.id == order_id or o.order_sn == order_id), None)

    async def get_metrics(self, name: str) -> list[BusinessMetric]:
        return [BusinessMetric(name=name, value=42.0, unit="count", period="2026-07", source="mock")]
