from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.document import Document


class DocumentAnalysis(Base):
    __tablename__ = "document_analyses"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )

    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    key_points: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    important_information: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    document_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Other",
    )

    invoice_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    vendor: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    invoice_date: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    total_amount: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
        # Resume / Bio-Data fields
    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    date_of_birth: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    education: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    experience: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    height: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    father_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    father_occupation: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    mother_occupation: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    siblings: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    # =========================
    # Contract fields
    # =========================

    company: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    effective_date: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    expiry_date: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    payment_terms: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    signatures: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # =========================
    # Purchase Order fields
    # =========================

    po_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    supplier: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    items: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    amount: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    delivery_date: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # =========================
    # Receipt fields
    # =========================

    receipt_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    receipt_date: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    receipt_items: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    receipt_amount: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    receipt_tax: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # =========================
    # Policy fields
    # =========================

    policy_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    policy_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    policy_effective_date: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    policy_expiry_date: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    department: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # =========================
    # Email fields
    # =========================

    sender: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    receiver: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    subject: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    email_date: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    email_purpose: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # =========================
    # Certificate fields
    # =========================

    certificate_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    institution: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    issue_date: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    certificate_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    
    gst: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    compliance_alerts: Mapped[str] = mapped_column(
    Text,
    nullable=False,
    default="[]",
)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    document: Mapped["Document"] = relationship(
        "Document",
        lazy="selectin",
    )