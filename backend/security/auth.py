from dataclasses import dataclass
import os
from typing import Iterable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from jose import jwt

from audit import log_security_event
from security.roles import Role

security = HTTPBearer(auto_error=False)

APP_ROLE_MAP = {
    "auditor": Role.AUDITOR,
    "compliance": Role.COMPLIANCE,
    "ai_owner": Role.AI_OWNER,
    "admin": Role.ADMIN,
}


@dataclass
class User:
    user_id: str | None
    username: str
    mapped_roles: list[Role]

    @property
    def role(self) -> Role:
        return self.mapped_roles[0] if self.mapped_roles else Role.AUDITOR


def _map_roles(role_values: Iterable[str]) -> list[Role]:
    mapped = []
    for role in role_values:
        mapped_role = APP_ROLE_MAP.get(role)
        if mapped_role:
            mapped.append(mapped_role)
    return mapped


def _mock_user() -> User:
    return User(user_id="local-user", username="local-user", mapped_roles=[Role.ADMIN])


def get_current_user(request: Request, token=Depends(security)):
    try:
        # Layer 1: Check for Easy Auth token (when App Service authentication is enabled)
        easyauth_token = request.headers.get("X-MS-TOKEN-AAD-ID-TOKEN")

        # Determine which token to use
        token_str = None
        if easyauth_token:
            # Use token from Easy Auth (App Service authentication)
            token_str = easyauth_token
        elif token is not None:
            # Use token from Authorization Bearer header (direct API calls)
            token_str = token.credentials

        # Layer 2: Handle missing token
        if not token_str:
            if os.getenv("AUTH_MODE", "").lower() == "mock":
                return _mock_user()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token is missing",
            )

        # Layer 3: Validate token and extract claims
        payload = jwt.get_unverified_claims(token_str)
        roles = payload.get("roles", [])
        user_id = payload.get("oid")
        username = payload.get("preferred_username") or payload.get("name") or user_id or "unknown"
        user = User(user_id=user_id, username=username, mapped_roles=_map_roles(roles))
        log_security_event(user.user_id, "login_success")
        return user
    except Exception:
        log_security_event(None, "login_failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )


def get_current_user_with_roles(user: User = Depends(get_current_user)):
    return user


def require_roles(*allowed_roles: Role):
    def dependency(request: Request, user: User = Depends(get_current_user)):
        if not any(role in user.mapped_roles for role in allowed_roles):
            log_security_event(
                user.user_id,
                "unauthorized_access",
                {"required_roles": [role.value for role in allowed_roles]},
            )
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action.",
            )
        state = request.scope.setdefault("state", {})
        state["user"] = user
        return user

    return dependency


def require_role(*allowed_roles: Role):
    return require_roles(*allowed_roles)


def require_not_auditor(user: User = Depends(get_current_user)):
    """Enforce read-only access for auditors.

    This dependency prevents auditors from modifying operational data.
    Auditors can view all data but cannot create, update, or delete records.
    This enforces segregation of duties required by regulatory frameworks.
    """
    if user.role == Role.AUDITOR:
        log_security_event(
            user.user_id,
            "auditor_write_attempt",
            {"message": "Auditor attempted to modify data"},
        )
        raise HTTPException(
            status_code=403,
            detail="Auditors have read-only access.",
        )
    return user
