from ecommerce_agent.domain.risk import RiskLevel, RiskPolicy


def test_refund_is_forbidden_by_default():
    assert RiskPolicy().classify("order.refund") is RiskLevel.FORBIDDEN


def test_product_update_requires_approval():
    assert RiskPolicy().classify("product.update") is RiskLevel.WRITE_CONFIRM
