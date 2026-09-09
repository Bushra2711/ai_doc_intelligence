from __future__ import annotations

import json
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from google import genai
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_analysis import DocumentAnalysis
from app.models.document_text import ExtractedDocumentText


class DocumentAnalysisError(Exception):
    """Base error for document analysis failures."""


class ExtractedTextNotFoundError(DocumentAnalysisError):
    """Raised when a document has not been processed yet."""


@dataclass(slots=True)
class DocumentAnalysisOutcome:
    analysis: DocumentAnalysis
    message: str


FIELD_DEFAULT = "N/A"


def _clean_field(value: object) -> str:
    """Normalize one extracted field without inventing information."""
    if value is None:
        return FIELD_DEFAULT
    text = str(value).strip()
    return text or FIELD_DEFAULT


def _analyze_with_gemini(text: str) -> tuple[str, ...]:
    """Analyze a document using Gemini with type-specific structured JSON output."""
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise DocumentAnalysisError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an enterprise intelligent document processing system.

Analyze ONLY the document supplied below.
First classify the document. Then extract ONLY the fields that belong to that
classified document type. Never copy fields from another document type.

DOCUMENT:
{text}

Return ONLY one valid JSON object. Do not use Markdown fences. Do not add any
text before or after the JSON.

Use exactly this JSON structure:
{{
  "document_type": "Invoice | Resume | Certificate | Contract | Receipt | Purchase Order | Policy | Email | Report | Assignment | Identity Document | Other",
  "summary": "clear concise summary",
  "key_points": ["point 1", "point 2", "point 3", "point 4", "point 5"],
  "important_information": ["important fact 1", "important fact 2"],
  "fields": {{}}
}}

Field rules by document type:

Invoice fields:
- invoice_number
- vendor
- invoice_date
- total_amount
- gst

Resume fields:
- full_name
- date_of_birth
- education
- skills
- experience
- email
- phone
- height
- father_name
- father_occupation
- mother_occupation
- siblings

Contract fields:
- company
- effective_date
- expiry_date
- payment_terms
- signatures

Purchase Order fields:
- po_number
- supplier
- items
- amount
- delivery_date

Receipt fields:
- receipt_number
- receipt_date
- receipt_items
- receipt_amount
- receipt_tax

Policy fields:
- policy_name
- policy_number
- policy_effective_date
- policy_expiry_date
- department

Email fields:
- sender
- receiver
- subject
- email_date
- email_purpose

Certificate fields:
- certificate_type
- institution
- issue_date
- certificate_number

For a classified document, include ONLY its relevant fields in "fields".
For fields not present in that document, use "N/A".
Never guess, infer, or invent missing data.
Preserve values from the source document as accurately as possible.
For key_points and important_information, return arrays of concise strings.
For Report, Assignment, Identity Document, or Other, return an empty fields object
unless one of the supported field sets clearly applies.
"""

    try:
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
            contents=prompt,
        )
    except Exception as exc:
        raise DocumentAnalysisError(f"Gemini API request failed: {exc}") from exc

    result = (response.text or "").strip()
    if not result:
        raise DocumentAnalysisError("Gemini returned an empty response.")

    if result.startswith("```") and result.endswith("```"):
        lines = result.splitlines()
        result = "\n".join(lines[1:-1]).strip()

    try:
        payload = json.loads(result)
    except json.JSONDecodeError as exc:
        raise DocumentAnalysisError("Gemini returned invalid structured JSON.") from exc

    if not isinstance(payload, dict):
        raise DocumentAnalysisError("Gemini returned an invalid analysis object.")

    document_type = _clean_field(payload.get("document_type"))
    summary = _clean_field(payload.get("summary"))

    key_points_raw = payload.get("key_points", [])
    if isinstance(key_points_raw, list):
        key_items = [_clean_field(item) for item in key_points_raw]
        key_items = [item for item in key_items if item != FIELD_DEFAULT]
        key_points = "\n".join(f"- {item}" for item in key_items) or FIELD_DEFAULT
    else:
        key_points = _clean_field(key_points_raw)

    important_raw = payload.get("important_information", [])
    if isinstance(important_raw, list):
        important_items = [_clean_field(item) for item in important_raw]
        important_items = [item for item in important_items if item != FIELD_DEFAULT]
        important_information = "\n".join(
            f"- {item}" for item in important_items
        ) or FIELD_DEFAULT
    else:
        important_information = _clean_field(important_raw)

    allowed_fields = {
        "Invoice": {
            "invoice_number", "vendor", "invoice_date", "total_amount", "gst"
        },
        "Resume": {
            "full_name", "date_of_birth", "education", "skills", "experience",
            "email", "phone", "height", "father_name", "father_occupation",
            "mother_occupation", "siblings"
        },
        "Certificate": {
            "certificate_type", "institution", "issue_date", "certificate_number"
        },
        "Contract": {
            "company", "effective_date", "expiry_date", "payment_terms", "signatures"
        },
        "Receipt": {
            "receipt_number", "receipt_date", "receipt_items", "receipt_amount", "receipt_tax"
        },
        "Purchase Order": {
            "po_number", "supplier", "items", "amount", "delivery_date"
        },
        "Policy": {
            "policy_name", "policy_number", "policy_effective_date",
            "policy_expiry_date", "department"
        },
        "Email": {
            "sender", "receiver", "subject", "email_date", "email_purpose"
        },
    }

    fields_raw = payload.get("fields", {})
    if not isinstance(fields_raw, dict):
        fields_raw = {}

    allowed = allowed_fields.get(document_type, set())

    all_field_names = {
        "invoice_number", "vendor", "invoice_date", "total_amount", "gst",
        "full_name", "date_of_birth", "education", "skills", "experience",
        "email", "phone", "height", "father_name", "father_occupation",
        "mother_occupation", "siblings", "company", "effective_date",
        "expiry_date", "payment_terms", "signatures", "po_number", "supplier",
        "items", "amount", "delivery_date", "receipt_number", "receipt_date",
        "receipt_items", "receipt_amount", "receipt_tax", "policy_name",
        "policy_number", "policy_effective_date", "policy_expiry_date",
        "department", "sender", "receiver", "subject", "email_date",
        "email_purpose", "certificate_type", "institution", "issue_date",
        "certificate_number"
    }

    normalized = {
        name: _clean_field(fields_raw.get(name)) if name in allowed else FIELD_DEFAULT
        for name in all_field_names
    }

    return (
        document_type,
        summary,
        key_points,
        important_information,
        normalized["invoice_number"], normalized["vendor"], normalized["invoice_date"],
        normalized["total_amount"], normalized["gst"], normalized["full_name"],
        normalized["date_of_birth"], normalized["education"], normalized["skills"],
        normalized["experience"], normalized["email"], normalized["phone"],
        normalized["height"], normalized["father_name"], normalized["father_occupation"],
        normalized["mother_occupation"], normalized["siblings"], normalized["company"],
        normalized["effective_date"], normalized["expiry_date"], normalized["payment_terms"],
        normalized["signatures"], normalized["po_number"], normalized["supplier"],
        normalized["items"], normalized["amount"], normalized["delivery_date"],
        normalized["receipt_number"], normalized["receipt_date"], normalized["receipt_items"],
        normalized["receipt_amount"], normalized["receipt_tax"], normalized["policy_name"],
        normalized["policy_number"], normalized["policy_effective_date"],
        normalized["policy_expiry_date"], normalized["department"], normalized["sender"],
        normalized["receiver"], normalized["subject"], normalized["email_date"],
        normalized["email_purpose"], normalized["certificate_type"], normalized["institution"],
        normalized["issue_date"], normalized["certificate_number"],
    )


def analyze_document(
    document: Document,
    db: Session,
) -> DocumentAnalysisOutcome:
    """Analyze extracted document text using Gemini and persist the result."""

    extracted_text = db.scalar(
        select(ExtractedDocumentText).where(
            ExtractedDocumentText.document_id == document.id
        )
    )

    if extracted_text is None:
        raise ExtractedTextNotFoundError(
            "Extracted text not found. Process the document first."
        )

    text = extracted_text.extracted_text.strip()
    if not text:
        raise ExtractedTextNotFoundError(
            "Extracted text is empty. Process the document again."
        )

    results = _analyze_with_gemini(text)
    (
        document_type, summary, key_points, important_information,
        invoice_number, vendor, invoice_date, total_amount, gst,
        full_name, date_of_birth, education, skills, experience, email, phone,
        height, father_name, father_occupation, mother_occupation, siblings,
        company, effective_date, expiry_date, payment_terms, signatures,
        po_number, supplier, items, amount, delivery_date,
        receipt_number, receipt_date, receipt_items, receipt_amount, receipt_tax,
        policy_name, policy_number, policy_effective_date, policy_expiry_date,
        department, sender, receiver, subject, email_date, email_purpose,
        certificate_type, institution, issue_date, certificate_number,
    ) = results

    values = {
        "document_type": document_type,
        "summary": summary,
        "key_points": key_points,
        "important_information": important_information,
        "invoice_number": invoice_number,
        "vendor": vendor,
        "invoice_date": invoice_date,
        "total_amount": total_amount,
        "gst": gst,
        "full_name": full_name,
        "date_of_birth": date_of_birth,
        "education": education,
        "skills": skills,
        "experience": experience,
        "email": email,
        "phone": phone,
        "height": height,
        "father_name": father_name,
        "father_occupation": father_occupation,
        "mother_occupation": mother_occupation,
        "siblings": siblings,
        "company": company,
        "effective_date": effective_date,
        "expiry_date": expiry_date,
        "payment_terms": payment_terms,
        "signatures": signatures,
        "po_number": po_number,
        "supplier": supplier,
        "items": items,
        "amount": amount,
        "delivery_date": delivery_date,
        "receipt_number": receipt_number,
        "receipt_date": receipt_date,
        "receipt_items": receipt_items,
        "receipt_amount": receipt_amount,
        "receipt_tax": receipt_tax,
        "policy_name": policy_name,
        "policy_number": policy_number,
        "policy_effective_date": policy_effective_date,
        "policy_expiry_date": policy_expiry_date,
        "department": department,
        "sender": sender,
        "receiver": receiver,
        "subject": subject,
        "email_date": email_date,
        "email_purpose": email_purpose,
        "certificate_type": certificate_type,
        "institution": institution,
        "issue_date": issue_date,
        "certificate_number": certificate_number,
    }

    existing_analysis = db.scalar(
        select(DocumentAnalysis).where(
            DocumentAnalysis.document_id == document.id
        )
    )

    if existing_analysis is None:
        analysis = DocumentAnalysis(document_id=document.id, **values)
    else:
        analysis = existing_analysis
        for field_name, field_value in values.items():
            setattr(analysis, field_name, field_value)

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return DocumentAnalysisOutcome(
        analysis=analysis,
        message="Document analyzed successfully using Gemini AI",
    )
