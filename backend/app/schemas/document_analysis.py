from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentAnalysisBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DocumentAnalysisCreate(DocumentAnalysisBase):
    document_id: str = Field(
        min_length=1,
        max_length=36,
    )

    # =========================
    # AI analysis
    # =========================

    summary: str = Field(min_length=1)
    key_points: str = Field(min_length=1)
    important_information: str = Field(min_length=1)

    # =========================
    # Document classification
    # =========================

    document_type: str = Field(
        min_length=1,
        max_length=100,
    )

    # =========================
    # Invoice fields
    # =========================

    invoice_number: str | None = None
    vendor: str | None = None
    invoice_date: str | None = None
    total_amount: str | None = None
    gst: str | None = None

    # =========================
    # Resume / Bio-Data fields
    # =========================

    full_name: str | None = None
    date_of_birth: str | None = None
    education: str | None = None
    skills: str | None = None
    experience: str | None = None
    email: str | None = None
    phone: str | None = None
    height: str | None = None
    father_name: str | None = None
    father_occupation: str | None = None
    mother_occupation: str | None = None
    siblings: str | None = None

    # =========================
    # Contract fields
    # =========================

    company: str | None = None
    effective_date: str | None = None
    expiry_date: str | None = None
    payment_terms: str | None = None
    signatures: str | None = None

    # =========================
    # Purchase Order fields
    # =========================

    po_number: str | None = None
    supplier: str | None = None
    items: str | None = None
    amount: str | None = None
    delivery_date: str | None = None

    # =========================
    # Receipt fields
    # =========================

    receipt_number: str | None = None
    receipt_date: str | None = None
    receipt_items: str | None = None
    receipt_amount: str | None = None
    receipt_tax: str | None = None

    # =========================
    # Policy fields
    # =========================

    policy_name: str | None = None
    policy_number: str | None = None
    policy_effective_date: str | None = None
    policy_expiry_date: str | None = None
    department: str | None = None

    # =========================
    # Email fields
    # =========================

    sender: str | None = None
    receiver: str | None = None
    subject: str | None = None
    email_date: str | None = None
    email_purpose: str | None = None

    # =========================
    # Certificate fields
    # =========================

    certificate_type: str | None = None
    institution: str | None = None
    issue_date: str | None = None
    certificate_number: str | None = None


class DocumentAnalysisResponse(DocumentAnalysisBase):
    id: str
    document_id: str

    # =========================
    # AI analysis
    # =========================

    summary: str
    key_points: str
    important_information: str

    # =========================
    # Document classification
    # =========================

    document_type: str

    # =========================
    # Invoice fields
    # =========================

    invoice_number: str | None = None
    vendor: str | None = None
    invoice_date: str | None = None
    total_amount: str | None = None
    gst: str | None = None
    compliance_alerts: str

    # =========================
    # Resume / Bio-Data fields
    # =========================

    full_name: str | None = None
    date_of_birth: str | None = None
    education: str | None = None
    skills: str | None = None
    experience: str | None = None
    email: str | None = None
    phone: str | None = None
    height: str | None = None
    father_name: str | None = None
    father_occupation: str | None = None
    mother_occupation: str | None = None
    siblings: str | None = None

    # =========================
    # Contract fields
    # =========================

    company: str | None = None
    effective_date: str | None = None
    expiry_date: str | None = None
    payment_terms: str | None = None
    signatures: str | None = None

    # =========================
    # Purchase Order fields
    # =========================

    po_number: str | None = None
    supplier: str | None = None
    items: str | None = None
    amount: str | None = None
    delivery_date: str | None = None

    # =========================
    # Receipt fields
    # =========================

    receipt_number: str | None = None
    receipt_date: str | None = None
    receipt_items: str | None = None
    receipt_amount: str | None = None
    receipt_tax: str | None = None

    # =========================
    # Policy fields
    # =========================

    policy_name: str | None = None
    policy_number: str | None = None
    policy_effective_date: str | None = None
    policy_expiry_date: str | None = None
    department: str | None = None

    # =========================
    # Email fields
    # =========================

    sender: str | None = None
    receiver: str | None = None
    subject: str | None = None
    email_date: str | None = None
    email_purpose: str | None = None

    # =========================
    # Certificate fields
    # =========================

    certificate_type: str | None = None
    institution: str | None = None
    issue_date: str | None = None
    certificate_number: str | None = None

    # =========================
    # Audit timestamps
    # =========================

    created_at: datetime
    updated_at: datetime