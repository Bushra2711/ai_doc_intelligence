from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.db.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("", response_model=list[AuditLogResponse])
def list_audit_logs(
    document_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AuditLogResponse]:
    statement = select(AuditLog).where(AuditLog.user_id == current_user.id)
    if document_id:
        statement = statement.where(AuditLog.document_id == document_id)
    entries = db.scalars(statement.order_by(AuditLog.created_at.desc()).limit(limit)).all()
    return [AuditLogResponse.model_validate(entry) for entry in entries]
