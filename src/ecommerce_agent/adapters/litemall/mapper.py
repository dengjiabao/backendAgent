from decimal import Decimal
from typing import Any

from ecommerce_agent.domain.errors import BusinessOperationFailed
from ecommerce_agent.domain.models import Order, Product


def unwrap_response(payload: dict[str, Any]) -> Any:
    errno = int(payload.get("errno", -1))
    if errno != 0:
        raise BusinessOperationFailed(str(payload.get("errmsg", f"litemall 错误码 {errno}")))
    return payload.get("data")


def map_product(item: dict[str, Any]) -> Product:
    return Product(
        id=str(item.get("id")),
        external_id=str(item.get("id")),
        name=str(item.get("name", "")),
        price=Decimal(str(item["retailPrice"])) if item.get("retailPrice") is not None else None,
        status="on_sale" if item.get("isOnSale", True) else "off_sale",
        source="litemall",
        metadata={"goodsSn": item.get("goodsSn")},
    )


def map_order(item: dict[str, Any]) -> Order:
    return Order(
        id=str(item.get("id")),
        external_id=str(item.get("id")),
        order_sn=str(item.get("orderSn", "")),
        status=str(item.get("orderStatus", "unknown")),
        amount=Decimal(str(item.get("actualPrice", "0"))),
        customer_id=str(item["userId"]) if item.get("userId") is not None else None,
        source="litemall",
    )
