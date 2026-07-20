from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class SourceRef(BaseModel):
    source: str = "unknown"
    external_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Product(SourceRef):
    id: str
    name: str
    price: Decimal | None = None
    status: str | None = None
    stock: int | None = None


class Sku(SourceRef):
    id: str
    product_id: str
    name: str
    price: Decimal | None = None
    stock: int | None = None


class Inventory(SourceRef):
    sku_id: str
    available: int
    reserved: int = 0


class Order(SourceRef):
    id: str
    order_sn: str
    status: str
    amount: Decimal
    customer_id: str | None = None
    created_at: datetime | None = None


class OrderItem(BaseModel):
    product_id: str
    sku_id: str | None = None
    name: str
    quantity: int
    price: Decimal


class Shipment(BaseModel):
    order_id: str
    channel: str
    tracking_number: str


class AfterSale(SourceRef):
    id: str
    order_id: str
    status: str
    reason: str | None = None
    amount: Decimal | None = None


class Customer(SourceRef):
    id: str
    nickname: str | None = None
    mobile: str | None = None


class Promotion(SourceRef):
    id: str
    name: str
    status: str
    discount: Decimal | None = None


class BusinessMetric(BaseModel):
    name: str
    value: float
    unit: str | None = None
    period: str | None = None
    source: str = "unknown"


class ActionProposal(BaseModel):
    action: str
    arguments: dict[str, Any]
    risk: str
    reason: str
    run_id: str


class ApprovalDecision(BaseModel):
    approval_id: str
    decision: str
    operator: str
    edited_arguments: dict[str, Any] | None = None
    comment: str | None = None
