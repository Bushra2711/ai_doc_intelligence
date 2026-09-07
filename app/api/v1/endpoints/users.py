from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse, status_code=200)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return the authenticated user's public profile."""
    return UserResponse.model_validate(current_user)
