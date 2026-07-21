import asyncio
from datetime import timedelta

import pytest

from ecommerce_agent.security.auth import LocalJWTService, OIDCIdentityService


def test_local_jwt_round_trip_and_signature_validation():
    service = LocalJWTService("test-secret")
    token = service.issue("u-1", "tenant-a", {"operator"}, ttl=timedelta(minutes=5))
    identity = service.verify(token)
    assert identity.subject == "u-1"
    assert identity.tenant_id == "tenant-a"
    with pytest.raises(ValueError, match="签名无效"):
        LocalJWTService("wrong-secret").verify(token)


def test_oidc_service_uses_replaceable_verifier():
    class Verifier:
        async def verify(self, token):
            return {"sub": "u-2", "tenant_id": "tenant-b", "roles": ["admin"]}

    identity = asyncio.run(OIDCIdentityService(Verifier()).verify("token"))
    assert identity.roles == {"admin"}
