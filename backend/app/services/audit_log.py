from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def record_audit(
    db: Session,
    *,
    user_id: str,
    action: str,
    document_id: str | None = None,
    status: str = "SUCCESS",
    details: str | None = None,
    commit: bool = True,
) -> AuditLog:
    entry = AuditLog(
        user_id=user_id,
        document_id=document_id,
        action=action,
        entity_type="document",
        status=status,
        details=details,
    )
    db.add(entry)
    if commit:
        db.commit()
        db.refresh(entry)
    return entry
