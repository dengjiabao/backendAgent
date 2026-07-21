from ecommerce_agent.security.redaction import redact


def test_redaction_removes_mobile_address_and_secrets():
    text = "手机号 13812345678，地址 上海市浦东新区世纪大道100号，Cookie: sid=abc Authorization: Bearer token123 api_key=sk-secret"
    result = redact(text)
    assert "13812345678" not in result
    assert "世纪大道100号" not in result
    assert "token123" not in result
    assert "sk-secret" not in result
    assert "[手机号]" in result
