from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import (
    login_user,
    register_user,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Register a new user.
    """

    logger.info("Registration request received for %s", user_in.email)

    return register_user(
        db=db,
        user_in=user_in,
    )


@router.post(
    "/login",
)
def login(
    user_in: UserLogin,
    db: Session = Depends(get_db),
) -> dict:
    """
    Authenticate a user and return JWT token.
    """

    logger.info("Login request received for %s", user_in.email)

    return login_user(
        db=db,
        user_in=user_in,
    )