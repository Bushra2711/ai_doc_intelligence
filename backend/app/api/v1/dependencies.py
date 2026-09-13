from __future__ import annotations

import logging

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.user import User
from app.services.audit_log import record_audit

logger = logging.getLogger(__name__)
http_bearer = HTTPBearer()


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: Session = Depends(get_db),
) -> User:
    """Validate JWT credentials and return the authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise credentials_exception from exc
    subject = payload.get("sub")
    if not subject:
        raise credentials_exception
    try:
        user = db.scalar(select(User).where(User.id == subject))
    except SQLAlchemyError:
        logger.exception("Database error while loading authenticated user")
        raise credentials_exception
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found", headers={"WWW-Authenticate": "Bearer"})
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user", headers={"WWW-Authenticate": "Bearer"})

    if request.method != "GET":
        action = f"{request.method} {request.url.path}"
        record_audit(db, user_id=user.id, action=action, details="Authenticated document/workspace action")
    return user
