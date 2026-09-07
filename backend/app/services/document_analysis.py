from __future__ import annotations

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


def _analyze_with_gemini(text: str) -> tuple[str, ...]:
    """Analyze extracted document text using Google Gemini."""

    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise DocumentAnalysisError(
            "GEMINI_API_KEY is not configured."
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an intelligent enterprise document analysis assistant.

Analyze the following document carefully.

DOCUMENT:
{text}

Return the result in EXACTLY this labeled format.
Do not change any label names.

DOCUMENT_TYPE:
Choose exactly ONE:
Invoice
Resume
Certificate
Contract
Receipt
Purchase Order
Policy
Email
Report
Assignment
Identity Document
Other

SUMMARY:
Write a clear concise summary.

KEY_POINTS:
- Point 1
- Point 2
- Point 3
- Point 4
- Point 5

IMPORTANT_INFORMATION:
Mention important facts, dates, names, qualifications,
amounts, terms, or other useful information.

========================
INVOICE
========================

INVOICE_NUMBER:
Invoice number if present, otherwise N/A.

VENDOR:
Vendor/supplier name if present, otherwise N/A.

INVOICE_DATE:
Invoice date if present, otherwise N/A.

TOTAL_AMOUNT:
Total invoice amount if present, otherwise N/A.

GST:
GST amount if present, otherwise N/A.

========================
RESUME / BIO-DATA
========================

FULL_NAME:
Full name if present, otherwise N/A.

DATE_OF_BIRTH:
Date of birth if present, otherwise N/A.

EDUCATION:
Education/qualifications if present, otherwise N/A.

SKILLS:
Skills if present, otherwise N/A.

EXPERIENCE:
Work experience if present, otherwise N/A.

EMAIL:
Email if present, otherwise N/A.

PHONE:
Phone/mobile number if present, otherwise N/A.

HEIGHT:
Height if present, otherwise N/A.

FATHER_NAME:
Father's name if present, otherwise N/A.

FATHER_OCCUPATION:
Father's occupation if present, otherwise N/A.

MOTHER_OCCUPATION:
Mother's occupation if present, otherwise N/A.

SIBLINGS:
Sibling information if present, otherwise N/A.

========================
CONTRACT
========================

COMPANY:
Company/organization name if present, otherwise N/A.

EFFECTIVE_DATE:
Contract effective date if present, otherwise N/A.

EXPIRY_DATE:
Contract expiry date if present, otherwise N/A.

PAYMENT_TERMS:
Payment terms if present, otherwise N/A.

SIGNATURES:
Mention whether signatures/signing information is present.
Do not assume a signature exists. Otherwise N/A.

========================
PURCHASE ORDER
========================

PO_NUMBER:
Purchase order number if present, otherwise N/A.

SUPPLIER:
Supplier name if present, otherwise N/A.

ITEMS:
List the ordered items if present, otherwise N/A.

AMOUNT:
Purchase order amount if present, otherwise N/A.

DELIVERY_DATE:
Delivery date if present, otherwise N/A.

========================
RECEIPT
========================

RECEIPT_NUMBER:
Receipt number if present, otherwise N/A.

RECEIPT_DATE:
Receipt date if present, otherwise N/A.

RECEIPT_ITEMS:
Receipt items if present, otherwise N/A.

RECEIPT_AMOUNT:
Receipt amount if present, otherwise N/A.

RECEIPT_TAX:
Tax amount if present, otherwise N/A.

========================
POLICY
========================

POLICY_NAME:
Policy name if present, otherwise N/A.

POLICY_NUMBER:
Policy number if present, otherwise N/A.

POLICY_EFFECTIVE_DATE:
Policy effective date if present, otherwise N/A.

POLICY_EXPIRY_DATE:
Policy expiry date if present, otherwise N/A.

DEPARTMENT:
Department if present, otherwise N/A.

========================
EMAIL
========================

SENDER:
Sender if present, otherwise N/A.

RECEIVER:
Receiver if present, otherwise N/A.

SUBJECT:
Email subject if present, otherwise N/A.

EMAIL_DATE:
Email date if present, otherwise N/A.

EMAIL_PURPOSE:
Main purpose of the email if present, otherwise N/A.

========================
CERTIFICATE
========================

CERTIFICATE_TYPE:
Certificate type if present, otherwise N/A.

INSTITUTION:
Issuing institution/organization if present, otherwise N/A.

ISSUE_DATE:
Certificate issue date if present, otherwise N/A.

CERTIFICATE_NUMBER:
Certificate number if present, otherwise N/A.

========================
RULES
========================

1. Do not invent information.
2. Only use information actually present in the document.
3. Use N/A when a field is unavailable or not applicable.
4. Preserve important values exactly where possible.
5. Do not put explanations outside the requested format.
"""

    try:
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
            contents=prompt,
        )
    except Exception as exc:
        raise DocumentAnalysisError(
            f"Gemini API request failed: {exc}"
        ) from exc

    result = response.text

    if not result:
        raise DocumentAnalysisError(
            "Gemini returned an empty response."
        )

    def extract_section(
        section_name: str,
        next_section: str,
    ) -> str:
        if section_name not in result:
            return ""

        section_part = result.split(
            section_name,
            1,
        )[1]

        if next_section and next_section in section_part:
            return section_part.split(
                next_section,
                1,
            )[0].strip()

        return section_part.strip()

    # =========================
    # General AI analysis
    # =========================

    document_type = extract_section(
        "DOCUMENT_TYPE:",
        "SUMMARY:",
    )

    summary = extract_section(
        "SUMMARY:",
        "KEY_POINTS:",
    )

    key_points = extract_section(
        "KEY_POINTS:",
        "IMPORTANT_INFORMATION:",
    )

    important_information = extract_section(
        "IMPORTANT_INFORMATION:",
        "INVOICE_NUMBER:",
    )

    # =========================
    # Invoice
    # =========================

    invoice_number = extract_section(
        "INVOICE_NUMBER:",
        "VENDOR:",
    )

    vendor = extract_section(
        "VENDOR:",
        "INVOICE_DATE:",
    )

    invoice_date = extract_section(
        "INVOICE_DATE:",
        "TOTAL_AMOUNT:",
    )

    total_amount = extract_section(
        "TOTAL_AMOUNT:",
        "GST:",
    )

    gst = extract_section(
        "GST:",
        "FULL_NAME:",
    )

    # =========================
    # Resume / Bio-Data
    # =========================

    full_name = extract_section(
        "FULL_NAME:",
        "DATE_OF_BIRTH:",
    )

    date_of_birth = extract_section(
        "DATE_OF_BIRTH:",
        "EDUCATION:",
    )

    education = extract_section(
        "EDUCATION:",
        "SKILLS:",
    )

    skills = extract_section(
        "SKILLS:",
        "EXPERIENCE:",
    )

    experience = extract_section(
        "EXPERIENCE:",
        "EMAIL:",
    )

    email = extract_section(
        "EMAIL:",
        "PHONE:",
    )

    phone = extract_section(
        "PHONE:",
        "HEIGHT:",
    )

    height = extract_section(
        "HEIGHT:",
        "FATHER_NAME:",
    )

    father_name = extract_section(
        "FATHER_NAME:",
        "FATHER_OCCUPATION:",
    )

    father_occupation = extract_section(
        "FATHER_OCCUPATION:",
        "MOTHER_OCCUPATION:",
    )

    mother_occupation = extract_section(
        "MOTHER_OCCUPATION:",
        "SIBLINGS:",
    )

    siblings = extract_section(
        "SIBLINGS:",
        "COMPANY:",
    )

    # =========================
    # Contract
    # =========================

    company = extract_section(
        "COMPANY:",
        "EFFECTIVE_DATE:",
    )

    effective_date = extract_section(
        "EFFECTIVE_DATE:",
        "EXPIRY_DATE:",
    )

    expiry_date = extract_section(
        "EXPIRY_DATE:",
        "PAYMENT_TERMS:",
    )

    payment_terms = extract_section(
        "PAYMENT_TERMS:",
        "SIGNATURES:",
    )

    signatures = extract_section(
        "SIGNATURES:",
        "PO_NUMBER:",
    )

    # =========================
    # Purchase Order
    # =========================

    po_number = extract_section(
        "PO_NUMBER:",
        "SUPPLIER:",
    )

    supplier = extract_section(
        "SUPPLIER:",
        "ITEMS:",
    )

    items = extract_section(
        "ITEMS:",
        "AMOUNT:",
    )

    amount = extract_section(
        "AMOUNT:",
        "DELIVERY_DATE:",
    )

    delivery_date = extract_section(
        "DELIVERY_DATE:",
        "RECEIPT_NUMBER:",
    )

    # =========================
    # Receipt
    # =========================

    receipt_number = extract_section(
        "RECEIPT_NUMBER:",
        "RECEIPT_DATE:",
    )

    receipt_date = extract_section(
        "RECEIPT_DATE:",
        "RECEIPT_ITEMS:",
    )

    receipt_items = extract_section(
        "RECEIPT_ITEMS:",
        "RECEIPT_AMOUNT:",
    )

    receipt_amount = extract_section(
        "RECEIPT_AMOUNT:",
        "RECEIPT_TAX:",
    )

    receipt_tax = extract_section(
        "RECEIPT_TAX:",
        "POLICY_NAME:",
    )

    # =========================
    # Policy
    # =========================

    policy_name = extract_section(
        "POLICY_NAME:",
        "POLICY_NUMBER:",
    )

    policy_number = extract_section(
        "POLICY_NUMBER:",
        "POLICY_EFFECTIVE_DATE:",
    )

    policy_effective_date = extract_section(
        "POLICY_EFFECTIVE_DATE:",
        "POLICY_EXPIRY_DATE:",
    )

    policy_expiry_date = extract_section(
        "POLICY_EXPIRY_DATE:",
        "DEPARTMENT:",
    )

    department = extract_section(
        "DEPARTMENT:",
        "SENDER:",
    )

    # =========================
    # Email
    # =========================

    sender = extract_section(
        "SENDER:",
        "RECEIVER:",
    )

    receiver = extract_section(
        "RECEIVER:",
        "SUBJECT:",
    )

    subject = extract_section(
        "SUBJECT:",
        "EMAIL_DATE:",
    )

    email_date = extract_section(
        "EMAIL_DATE:",
        "EMAIL_PURPOSE:",
    )

    email_purpose = extract_section(
        "EMAIL_PURPOSE:",
        "CERTIFICATE_TYPE:",
    )

    # =========================
    # Certificate
    # =========================

    certificate_type = extract_section(
        "CERTIFICATE_TYPE:",
        "INSTITUTION:",
    )

    institution = extract_section(
        "INSTITUTION:",
        "ISSUE_DATE:",
    )

    issue_date = extract_section(
        "ISSUE_DATE:",
        "CERTIFICATE_NUMBER:",
    )

    certificate_number = extract_section(
        "CERTIFICATE_NUMBER:",
        "",
    )

    # =========================
    # Safety fallbacks
    # =========================

    if not document_type:
        document_type = "Other"

    if not summary:
        summary = result[:2000]

    if not key_points:
        key_points = (
            "Gemini did not return separately formatted key points."
        )

    if not important_information:
        important_information = result[:3000]

    field_values = {
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

    for field_name, field_value in field_values.items():
        if not field_value:
            field_values[field_name] = "N/A"

    return (
        document_type,
        summary,
        key_points,
        important_information,
        invoice_number,
        vendor,
        invoice_date,
        total_amount,
        gst,
        full_name,
        date_of_birth,
        education,
        skills,
        experience,
        email,
        phone,
        height,
        father_name,
        father_occupation,
        mother_occupation,
        siblings,
        company,
        effective_date,
        expiry_date,
        payment_terms,
        signatures,
        po_number,
        supplier,
        items,
        amount,
        delivery_date,
        receipt_number,
        receipt_date,
        receipt_items,
        receipt_amount,
        receipt_tax,
        policy_name,
        policy_number,
        policy_effective_date,
        policy_expiry_date,
        department,
        sender,
        receiver,
        subject,
        email_date,
        email_purpose,
        certificate_type,
        institution,
        issue_date,
        certificate_number,
    )


def analyze_document(
    document: Document,
    db: Session,
) -> DocumentAnalysisOutcome:
    """Analyze extracted document text using Gemini."""

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
        document_type,
        summary,
        key_points,
        important_information,
        invoice_number,
        vendor,
        invoice_date,
        total_amount,
        gst,
        full_name,
        date_of_birth,
        education,
        skills,
        experience,
        email,
        phone,
        height,
        father_name,
        father_occupation,
        mother_occupation,
        siblings,
        company,
        effective_date,
        expiry_date,
        payment_terms,
        signatures,
        po_number,
        supplier,
        items,
        amount,
        delivery_date,
        receipt_number,
        receipt_date,
        receipt_items,
        receipt_amount,
        receipt_tax,
        policy_name,
        policy_number,
        policy_effective_date,
        policy_expiry_date,
        department,
        sender,
        receiver,
        subject,
        email_date,
        email_purpose,
        certificate_type,
        institution,
        issue_date,
        certificate_number,
    ) = results

    existing_analysis = db.scalar(
        select(DocumentAnalysis).where(
            DocumentAnalysis.document_id == document.id
        )
    )

    values = {
        "document_type": document_type,
        "summary": summary,
        "key_points": key_points,
        "important_information": important_information,

        # Invoice
        "invoice_number": invoice_number,
        "vendor": vendor,
        "invoice_date": invoice_date,
        "total_amount": total_amount,
        "gst": gst,

        # Resume
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

        # Contract
        "company": company,
        "effective_date": effective_date,
        "expiry_date": expiry_date,
        "payment_terms": payment_terms,
        "signatures": signatures,

        # Purchase Order
        "po_number": po_number,
        "supplier": supplier,
        "items": items,
        "amount": amount,
        "delivery_date": delivery_date,

        # Receipt
        "receipt_number": receipt_number,
        "receipt_date": receipt_date,
        "receipt_items": receipt_items,
        "receipt_amount": receipt_amount,
        "receipt_tax": receipt_tax,

        # Policy
        "policy_name": policy_name,
        "policy_number": policy_number,
        "policy_effective_date": policy_effective_date,
        "policy_expiry_date": policy_expiry_date,
        "department": department,

        # Email
        "sender": sender,
        "receiver": receiver,
        "subject": subject,
        "email_date": email_date,
        "email_purpose": email_purpose,

        # Certificate
        "certificate_type": certificate_type,
        "institution": institution,
        "issue_date": issue_date,
        "certificate_number": certificate_number,
    }

    if existing_analysis is None:
        analysis = DocumentAnalysis(
            document_id=document.id,
            **values,
        )
    else:
        analysis = existing_analysis

        for field_name, field_value in values.items():
            setattr(
                analysis,
                field_name,
                field_value,
            )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return DocumentAnalysisOutcome(
        analysis=analysis,
        message="Document analyzed successfully using Gemini AI",
    )