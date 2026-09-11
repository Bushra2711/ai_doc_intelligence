from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation


@dataclass(slots=True)
class InvoiceFields:
    invoice_number: str | None = None
    invoice_date: str | None = None
    due_date: str | None = None
    vendor_name: str | None = None
    vendor_gstin: str | None = None
    buyer_name: str | None = None
    buyer_gstin: str | None = None
    subtotal: float | None = None
    tax_amount: float | None = None
    total_amount: float | None = None
    currency: str | None = None
    po_number: str | None = None


GSTIN_PATTERN = re.compile(r"\b\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d]Z[A-Z\d]\b", re.IGNORECASE)
DATE_PATTERN = r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = re.sub(r"\s+", " ", value).strip(" :|-\t")
    return value or None


def _first_group(text: str, patterns: tuple[str, ...]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            return _clean(match.group(1))
    return None


def _parse_amount(value: str | None) -> float | None:
    if not value:
        return None
    normalized = re.sub(r"[^0-9.,-]", "", value).replace(",", "")
    try:
        return float(Decimal(normalized))
    except (InvalidOperation, ValueError):
        return None


def _extract_labeled_amount(text: str, labels: tuple[str, ...]) -> float | None:
    label_pattern = "|".join(re.escape(label) for label in labels)
    pattern = rf"(?:{label_pattern})\s*(?:[:=-])?\s*(?:INR|Rs\.?|₹|USD|EUR|\$|€)?\s*([0-9][0-9,]*(?:\.\d{{1,2}})?)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return _parse_amount(match.group(1)) if match else None


def _extract_currency(text: str) -> str | None:
    if re.search(r"(?:₹|INR|Rs\.?|Rupees)", text, flags=re.IGNORECASE):
        return "INR"
    if re.search(r"(?:\$|USD|US Dollars?)", text, flags=re.IGNORECASE):
        return "USD"
    if re.search(r"(?:€|EUR|Euros?)", text, flags=re.IGNORECASE):
        return "EUR"
    if re.search(r"(?:£|GBP|Pounds?)", text, flags=re.IGNORECASE):
        return "GBP"
    return None


def _extract_party_name(text: str, labels: tuple[str, ...]) -> str | None:
    label_pattern = "|".join(re.escape(label) for label in labels)
    pattern = rf"(?:{label_pattern})\s*(?:[:=-])?\s*([^\n|]+)"
    return _first_group(text, (pattern,))


def extract_invoice_fields(text: str) -> InvoiceFields:
    """Extract common invoice fields from OCR or embedded document text.

    This is a deterministic baseline extractor. It intentionally returns None
    when a field cannot be identified instead of inventing a value. A later
    AI/ML extractor can be layered on top of this contract.
    """
    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")

    invoice_number = _first_group(
        normalized_text,
        (
            r"(?:invoice\s*(?:no|number|#))\s*[:=-]?\s*([^\n|]+)",
            r"(?:inv\.?\s*(?:no|#))\s*[:=-]?\s*([^\n|]+)",
        ),
    )
    invoice_date = _first_group(
        normalized_text,
        (
            rf"(?:invoice\s*date|date\s*of\s*invoice)\s*[:=-]?\s*({DATE_PATTERN})",
        ),
    )
    due_date = _first_group(
        normalized_text,
        (
            rf"(?:due\s*date|payment\s*due)\s*[:=-]?\s*({DATE_PATTERN})",
        ),
    )

    gstins = [match.upper() for match in GSTIN_PATTERN.findall(normalized_text)]
    vendor_gstin = gstins[0] if gstins else None
    buyer_gstin = gstins[1] if len(gstins) > 1 else None

    vendor_name = _extract_party_name(
        normalized_text,
        ("vendor", "supplier", "seller", "from", "vendor name", "supplier name"),
    )
    buyer_name = _extract_party_name(
        normalized_text,
        ("buyer", "customer", "bill to", "billed to", "buyer name", "customer name"),
    )

    po_number = _first_group(
        normalized_text,
        (
            r"(?:purchase\s*order|po)\s*(?:no|number|#)?\s*[:=-]?\s*([^\n|]+)",
        ),
    )

    subtotal = _extract_labeled_amount(
        normalized_text, ("subtotal", "sub total", "taxable value", "net amount")
    )
    tax_amount = _extract_labeled_amount(
        normalized_text, ("tax amount", "total tax", "gst amount", "igst", "cgst", "sgst")
    )
    total_amount = _extract_labeled_amount(
        normalized_text, ("grand total", "invoice total", "total amount", "amount due", "total")
    )

    return InvoiceFields(
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        due_date=due_date,
        vendor_name=vendor_name,
        vendor_gstin=vendor_gstin,
        buyer_name=buyer_name,
        buyer_gstin=buyer_gstin,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,
        currency=_extract_currency(normalized_text),
        po_number=po_number,
    )


def extract_invoice_fields_dict(text: str) -> dict[str, object]:
    """Return invoice fields in a JSON-serializable dictionary."""
    return asdict(extract_invoice_fields(text))
