from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.api.v1.role_guard import require_roles
from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserRoleUpdate
from app.services.audit_log import record_audit

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse, status_code=200)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return the authenticated user's public profile."""
    return UserResponse.model_validate(current_user)


@router.get("", response_model=list[UserResponse])
def list_users(
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    """List workspace accounts. Restricted to administrators."""
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return [UserResponse.model_validate(user) for user in users]


@router.patch("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: str,
    payload: UserRoleUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Change a workspace account's role. Restricted to administrators."""
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.id == current_user.id and payload.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An administrator cannot remove their own admin role",
        )

    old_role = user.role.value
    user.role = payload.role
    db.flush()
    record_audit(
        db,
        user_id=current_user.id,
        action="USER_ROLE_UPDATED",
        details=f"User {user.email}: {old_role} -> {payload.role.value}",
    )
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)
