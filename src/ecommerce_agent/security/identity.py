from dataclasses import dataclass, field


@dataclass(frozen=True)
class Identity:
    subject: str
    tenant_id: str
    roles: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class TenantContext:
    tenant_id: str


class RBACService:
    """统一校验角色和租户，避免业务服务自行拼装权限判断。"""

    def require(self, identity: Identity, required_roles: set[str], tenant: TenantContext) -> None:
        if identity.tenant_id != tenant.tenant_id:
            raise PermissionError("租户不匹配")
        if required_roles and not required_roles.intersection(identity.roles):
            raise PermissionError("角色不足")
