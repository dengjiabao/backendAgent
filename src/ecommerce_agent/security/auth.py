import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

from ecommerce_agent.security.identity import Identity


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


class LocalJWTService:
    """独立模式 HS256 JWT，企业模式可替换为 OIDC。"""

    def __init__(self, secret: str) -> None:
        if len(secret) < 8:
            raise ValueError("JWT Secret 长度不足")
        self.secret = secret.encode("utf-8")

    def issue(self, subject: str, tenant_id: str, roles: set[str], ttl: timedelta) -> str:
        header = _encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
        payload = _encode(
            json.dumps(
                {
                    "sub": subject,
                    "tenant_id": tenant_id,
                    "roles": sorted(roles),
                    "exp": int((datetime.now(UTC) + ttl).timestamp()),
                },
                separators=(",", ":"),
            ).encode()
        )
        signature = _encode(hmac.new(self.secret, f"{header}.{payload}".encode(), hashlib.sha256).digest())
        return f"{header}.{payload}.{signature}"

    def verify(self, token: str) -> Identity:
        try:
            header, payload, signature = token.split(".")
        except ValueError as exc:
            raise ValueError("JWT 格式无效") from exc
        expected = _encode(hmac.new(self.secret, f"{header}.{payload}".encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError("JWT 签名无效")
        claims = json.loads(_decode(payload))
        if int(claims["exp"]) <= int(datetime.now(UTC).timestamp()):
            raise ValueError("JWT 已过期")
        return Identity(str(claims["sub"]), str(claims["tenant_id"]), set(claims.get("roles", [])))


class OIDCTokenVerifierPort(Protocol):
    async def verify(self, token: str) -> dict[str, Any]: ...


class OIDCIdentityService:
    def __init__(self, verifier: OIDCTokenVerifierPort) -> None:
        self.verifier = verifier

    async def verify(self, token: str) -> Identity:
        claims = await self.verifier.verify(token)
        return Identity(str(claims["sub"]), str(claims["tenant_id"]), set(claims.get("roles", [])))
