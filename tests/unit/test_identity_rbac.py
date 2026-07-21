import pytest

from ecommerce_agent.security.identity import Identity, RBACService, TenantContext


def test_rbac_requires_role_and_matching_tenant():
    identity = Identity(subject="u-1", tenant_id="tenant-a", roles={"operator"})
    service = RBACService()
    service.require(identity, required_roles={"operator"}, tenant=TenantContext("tenant-a"))
    with pytest.raises(PermissionError, match="租户不匹配"):
        service.require(identity, required_roles={"operator"}, tenant=TenantContext("tenant-b"))
    with pytest.raises(PermissionError, match="角色不足"):
        service.require(identity, required_roles={"admin"}, tenant=TenantContext("tenant-a"))
