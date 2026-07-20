from decimal import Decimal

import pytest

from ecommerce_agent.adapters.litemall.mapper import map_product, unwrap_response
from ecommerce_agent.domain.errors import BusinessOperationFailed


def test_litemall_product_maps_to_standard_model():
    product = map_product({"id": 1, "name": "测试商品", "retailPrice": 19.9, "isOnSale": True})
    assert product.id == "1"
    assert product.price == Decimal("19.9")
    assert product.source == "litemall"


def test_non_zero_errno_raises_domain_error():
    with pytest.raises(BusinessOperationFailed, match="无权限"):
        unwrap_response({"errno": 506, "errmsg": "无权限"})
