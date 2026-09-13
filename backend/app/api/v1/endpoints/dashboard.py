from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.db.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.document_analysis import DocumentAnalysis
from app.models.document_text import ExtractedDocumentText
from app.models.user import User
from app.schemas.dashboard import DashboardMetricsResponse
from app.services.invoice_compliance import evaluate_invoice_compliance
from app.services.invoice_confidence import invoice_confidence_dict
from app.services.invoice_extraction import extract_invoice_fields_dict

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics", response_model=DashboardMetricsResponse)
def dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardMetricsResponse:
    documents = db.scalars(
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
    ).all()

    status_counts = Counter(document.status.value if isinstance(document.status, DocumentStatus) else str(document.status) for document in documents)
    analyses = db.scalars(
        select(DocumentAnalysis).join(Document, DocumentAnalysis.document_id == Document.id).where(Document.user_id == current_user.id)
    ).all()
    analysis_by_document = {analysis.document_id: analysis for analysis in analyses}

    document_types = Counter(analysis.document_type for analysis in analyses if analysis.document_type)
    invoice_documents = [document for document in documents if analysis_by_document.get(document.id) and analysis_by_document[document.id].document_type.lower() == "invoice"]

    confidence_scores: list[float] = []
    compliance_passed = compliance_warnings = compliance_failed = 0
    invoice_ids = {document.id for document in invoice_documents}
    if invoice_ids:
        texts = db.scalars(
            select(ExtractedDocumentText).where(ExtractedDocumentText.document_id.in_(invoice_ids))
        ).all()
        for extracted in texts:
            fields = extract_invoice_fields_dict(extracted.extracted_text)
            confidence = invoice_confidence_dict(fields)
            confidence_scores.append(float(confidence["overall_score"]))
            compliance = evaluate_invoice_compliance(fields)
            compliance_passed += int(compliance["passed"])
            compliance_warnings += int(compliance["warnings"])
            compliance_failed += int(compliance["failed"])

    today = datetime.now().date()
    daily_counter = Counter(
        document.created_at.date().isoformat()
        for document in documents
        if document.created_at is not None and document.created_at.date() >= today - timedelta(days=6)
    )
    recent_daily_counts = [
        {"date": (today - timedelta(days=offset)).isoformat(), "count": daily_counter[(today - timedelta(days=offset)).isoformat()]}
        for offset in range(6, -1, -1)
    ]

    return DashboardMetricsResponse(
        total_documents=len(documents),
        completed_documents=status_counts.get(DocumentStatus.COMPLETED.value, 0),
        processing_documents=status_counts.get(DocumentStatus.PROCESSING.value, 0),
        pending_documents=status_counts.get(DocumentStatus.UPLOADED.value, 0) + status_counts.get(DocumentStatus.PENDING.value, 0),
        failed_documents=status_counts.get(DocumentStatus.FAILED.value, 0),
        invoice_documents=len(invoice_documents),
        analyzed_documents=len(analyses),
        average_invoice_confidence=(sum(confidence_scores) / len(confidence_scores)) if confidence_scores else None,
        compliance_passed=compliance_passed,
        compliance_warnings=compliance_warnings,
        compliance_failed=compliance_failed,
        document_types=dict(document_types),
        status_counts=dict(status_counts),
        recent_daily_counts=recent_daily_counts,
    )
