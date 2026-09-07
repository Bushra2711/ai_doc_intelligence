from __future__ import annotations

from collections.abc import Generator
import logging
from typing import Any

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import settings
from app.models.base import Base

logger = logging.getLogger(__name__)

def _build_engine() -> Engine:
    """Create the SQLAlchemy engine using the configured database URL."""

    if not settings.database_url:
        raise ValueError("DATABASE_URL is not configured")

    try:
        engine_kwargs: dict[str, Any] = {
            "pool_pre_ping": True,
            "pool_recycle": 3600,
            "future": True,
        }

        if settings.database_url.startswith("sqlite"):
            engine_kwargs["connect_args"] = {
                "check_same_thread": False
            }

        return create_engine(
            settings.database_url,
            **engine_kwargs,
        )

    except Exception as exc:
        logger.exception("Failed to create SQLAlchemy engine")
        raise RuntimeError(
            "Unable to initialize database engine"
        ) from exc


engine: Engine = _build_engine()


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    """Provide a database session for FastAPI dependencies."""

    db = SessionLocal()

    try:
        yield db

    except Exception:
        logger.exception(
            "Database session error; rolling back transaction"
        )
        db.rollback()
        raise

    finally:
        db.close()