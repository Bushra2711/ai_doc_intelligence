from __future__ import annotations

import logging
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
)

logger = logging.getLogger(__name__)


def register_user(
    db: Session,
    user_in: UserCreate,
) -> UserResponse:
    """
    Register a new user.
    """

    try:
        existing_user = db.scalar(
            select(User).where(User.email == user_in.email)
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered.",
            )

        new_user = User(
            full_name=user_in.full_name,
            email=user_in.email,
            hashed_password=hash_password(user_in.password),
            role=UserRole.EMPLOYEE,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info("User registered successfully: %s", new_user.email)

        return UserResponse.model_validate(new_user)

    except IntegrityError as exc:
        db.rollback()

        logger.exception("Integrity error while registering user.")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to register user.",
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()

        logger.exception("Database error while registering user.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        ) from exc


def authenticate_user(
    db: Session,
    user_in: UserLogin,
) -> User | None:
    """
    Authenticate user credentials.
    """

    try:
        user = db.scalar(
            select(User).where(User.email == user_in.email)
        )

        if user is None:
            return None

        if not verify_password(
            user_in.password,
            user.hashed_password,
        ):
            return None

        if not user.is_active:
            return None

        return user

    except SQLAlchemyError as exc:
        logger.exception("Database error during authentication.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error.",
        ) from exc


def login_user(
    db: Session,
    user_in: UserLogin,
) -> dict[str, Any]:
    """
    Authenticate user and generate JWT access token.
    """

    user = authenticate_user(db, user_in)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
        }
    )

    logger.info("User logged in successfully: %s", user.email)

    return {
        "access_token": token,
        "token_type": "bearer",
    }