from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.api.v1.dependencies import get_current_user
from app.models.user import User, UserRole


def require_roles(*allowed_roles: UserRole) -> Callable[..., User]:
    """Return a dependency that permits only the supplied workspace roles."""

    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_dependency
