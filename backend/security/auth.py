from fastapi import Depends, HTTPException, Request

from backend.security.roles import Role


class MockUser:
    def __init__(self, username: str, role: Role):
        self.username = username
        self.role = role


def get_current_user():
    """
    Temporary mock user.
    Replace with Entra ID integration later.
    """
    return MockUser(username="mofasshara", role=Role.COMPLIANCE)


def require_roles(*allowed_roles: Role):
    def dependency(request: Request, user: MockUser = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"User role '{user.role}' not permitted for this action",
            )
        state = request.scope.setdefault("state", {})
        state["user"] = user
        return user

    return dependency
