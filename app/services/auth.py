"""Caller identity for the admin-app chat.

The tenant comes only from a verified source: the login JWT (``auth.mode: jwt``)
or the identity the API gateway signs after verifying that JWT
(``auth.mode: gateway``).
"""

from __future__ import annotations

import hashlib
import hmac
import re
import time
from dataclasses import dataclass
from typing import Any

import jwt
from fastapi import HTTPException, Request

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_TENANT_RE = re.compile(r"^[a-z0-9_]{1,40}$")
# How old a gateway signature may be, in seconds (also covers clock drift).
_GATEWAY_MAX_AGE_SECONDS = 60
_dev_warning_logged = False


@dataclass(frozen=True)
class CallerScope:
    """Who is asking. Built only by ``resolve_scope``; never from the request body."""

    tenant: str
    user_id: str
    role: str | None = None


def normalize_tenant(raw: Any) -> str | None:
    t = str(raw or "").strip().lower()
    return t if _TENANT_RE.match(t) else None


def _bearer_token(request: Request) -> str:
    raw = request.headers.get("auth") or request.headers.get("authorization") or ""
    raw = raw.strip()
    if raw.lower().startswith("bearer "):
        raw = raw[7:].strip()
    return raw


def _first_claim(payload: dict[str, Any], names: list[str]) -> Any:
    for name in names:
        value = payload.get(name)
        if value not in (None, ""):
            return value
    return None


def _decode(token: str) -> tuple[dict[str, Any], bool]:
    """Return (claims, verified). Raises 401 on any invalid token."""
    global _dev_warning_logged
    s = get_settings()
    key = None
    if s.app_chat_jwt_public_key:
        key = s.app_chat_jwt_public_key.get_secret_value().strip() or None
    if key is None and s.app_chat_jwt_secret:
        key = s.app_chat_jwt_secret.get_secret_value().strip() or None

    try:
        if key:
            claims = jwt.decode(
                token,
                key,
                algorithms=s.auth.jwt_algorithms,
                options={"verify_aud": False},
            )
            return claims, True
        if s.app_chat_allow_unverified_dev_tokens:
            if not _dev_warning_logged:
                logger.warning(
                    "app_chat_auth | token signatures are NOT verified "
                    "(APP_CHAT_ALLOW_UNVERIFIED_DEV_TOKENS): only tenant and "
                    "expiry are checked, so a forged token would be accepted.",
                )
                _dev_warning_logged = True
            # A token with no expiry must not count as valid forever.
            claims = jwt.decode(
                token,
                options={
                    "verify_signature": False,
                    "verify_exp": True,
                    "require": ["exp"],
                },
            )
            return claims, False
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Session expired") from e
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e

    logger.error("app_chat_auth | no JWT key configured (APP_CHAT_JWT_SECRET)")
    raise HTTPException(status_code=503, detail="Chat authentication is not configured")


def _build_scope(tenant: str, user: Any, role: Any) -> CallerScope:
    allowed = {t.strip().lower() for t in get_settings().auth.allowed_tenants if t.strip()}
    if allowed and tenant not in allowed:
        logger.warning("security | tenant %r is not served by this deployment", tenant)
        raise HTTPException(status_code=403, detail="Tenant not allowed")
    user_id = re.sub(r"[^A-Za-z0-9_-]", "_", str(user or "anonymous"))[:64]
    return CallerScope(
        tenant=tenant,
        user_id=user_id,
        role=str(role) if role is not None else None,
    )


def _scope_from_token(request: Request) -> CallerScope:
    token = _bearer_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="Sign in to use the assistant")
    claims, verified = _decode(token)
    s = get_settings()

    header_tenant = normalize_tenant(request.headers.get("tenant"))
    claim_tenant = normalize_tenant(_first_claim(claims, s.auth.tenant_claims))

    # The tenant always comes from the token, never from a header alone.
    if claim_tenant is None:
        logger.error("app_chat_auth | token has no tenant claim (verified=%s)", verified)
        raise HTTPException(status_code=403, detail="Token carries no tenant")
    if header_tenant is not None and header_tenant != claim_tenant:
        logger.warning(
            "security | tenant header %r does not match token tenant %r",
            header_tenant,
            claim_tenant,
        )
        raise HTTPException(status_code=403, detail="Tenant mismatch")
    return _build_scope(
        claim_tenant,
        _first_claim(claims, s.auth.user_claims),
        _first_claim(claims, s.auth.role_claims),
    )


def gateway_signature(secret: bytes, timestamp: str, tenant: str, user: str, role: str) -> str:
    """HMAC the gateway puts in X-Chat-Signature (same code in gateway chatbot_service.py)."""
    message = "\n".join(("v1", timestamp, tenant, user, role))
    return hmac.new(secret, message.encode("utf-8"), hashlib.sha256).hexdigest()


def _scope_from_gateway(request: Request) -> CallerScope:
    """Identity forwarded by the API gateway after it verified the login token."""
    s = get_settings()
    secret = ""
    if s.chatbot_internal_secret:
        secret = s.chatbot_internal_secret.get_secret_value().strip()
    if not secret:
        logger.error("app_chat_auth | auth.mode is gateway but CHATBOT_INTERNAL_SECRET is unset")
        raise HTTPException(status_code=503, detail="Chat authentication is not configured")

    h = request.headers
    tenant_raw, user, role, timestamp, signature = (
        (h.get(name) or "").strip()
        for name in ("x-chat-tenant", "x-chat-user", "x-chat-role", "x-chat-timestamp", "x-chat-signature")
    )
    expected = gateway_signature(secret.encode("utf-8"), timestamp, tenant_raw, user, role)
    if not hmac.compare_digest(expected, signature):
        logger.warning("security | bad gateway signature (tenant header %r)", tenant_raw)
        raise HTTPException(status_code=401, detail="Invalid gateway signature")
    try:
        age = abs(time.time() - int(timestamp))
    except ValueError:
        age = float("inf")
    if age > _GATEWAY_MAX_AGE_SECONDS:
        logger.warning("security | expired gateway signature (age %s s)", age)
        raise HTTPException(status_code=401, detail="Gateway signature expired")

    tenant = normalize_tenant(tenant_raw)
    if tenant is None:
        raise HTTPException(status_code=403, detail="Request carries no tenant")
    return _build_scope(tenant, user, role)


def resolve_scope(request: Request) -> CallerScope:
    if get_settings().auth.mode == "gateway":
        return _scope_from_gateway(request)
    return _scope_from_token(request)


def require_scope(request: Request) -> CallerScope:
    """FastAPI dependency for every admin-app chat route."""
    return resolve_scope(request)


def require_service_key(request: Request) -> None:
    """FastAPI dependency for ingest/delete/upload. Fails closed when unset."""
    s = get_settings()
    expected = ""
    if s.knowledge_service_key:
        expected = s.knowledge_service_key.get_secret_value().strip()
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="KNOWLEDGE_SERVICE_KEY is not configured on the server",
        )
    given = (request.headers.get("x-service-key") or "").strip()
    if not given or not hmac.compare_digest(given.encode(), expected.encode()):
        raise HTTPException(status_code=401, detail="Invalid service key")
