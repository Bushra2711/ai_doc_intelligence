from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.services.invoice_extraction import InvoiceFields, extract_invoice_fields

DOMAIN_NAME = "invoice"
DOMAIN_ADAPTER_VERSION = "1.0"

REQUIRED_FIELDS = (
    "invoice_number",
    "invoice_date",
    "vendor_name",
    "vendor_gstin",
    "buyer_name",
    "buyer_gstin",
    "subtotal",
    "tax_amount",
    "total_amount",
    "currency",
)

OPTIONAL_FIELDS = (
    "due_date",
    "po_number",
    "tax_breakdown",
    "line_items",
)


@dataclass(slots=True)
class InvoiceDomainAdaptation:
    domain: str
    adapter_version: str
    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...]
    fields: dict[str, Any]
    missing_required_fields: list[str]
    adaptation_status: str


def adapt_invoice_fields(fields: InvoiceFields) -> InvoiceDomainAdaptation:
    """Apply the invoice-domain schema to the generic invoice extraction result.

    This is domain adaptation through a versioned schema and invoice-specific
    field requirements. It does not fine-tune or modify Gemini model weights.
    """
    field_data = asdict(fields)
    missing = [
        field_name
        for field_name in REQUIRED_FIELDS
        if field_data.get(field_name) in (None, "")
    ]

    return InvoiceDomainAdaptation(
        domain=DOMAIN_NAME,
        adapter_version=DOMAIN_ADAPTER_VERSION,
        required_fields=REQUIRED_FIELDS,
        optional_fields=OPTIONAL_FIELDS,
        fields=field_data,
        missing_required_fields=missing,
        adaptation_status="READY" if not missing else "REVIEW_REQUIRED",
    )


def adapt_invoice_text(text: str) -> InvoiceDomainAdaptation:
    """Extract an invoice and apply the versioned invoice-domain adapter."""
    return adapt_invoice_fields(extract_invoice_fields(text))


def adapt_invoice_fields_dict(fields: InvoiceFields) -> dict[str, Any]:
    """Return the domain-adapted invoice as a JSON-serializable dictionary."""
    return asdict(adapt_invoice_fields(fields))


def adapt_invoice_text_dict(text: str) -> dict[str, Any]:
    """Extract, adapt, and return an invoice-domain dictionary."""
    return asdict(adapt_invoice_text(text))
