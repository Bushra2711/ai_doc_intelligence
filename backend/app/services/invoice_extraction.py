from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation

@dataclass(slots=True)
class InvoiceLineItem:
    line_number: int | None = None
    description: str | None = None
    hsn_code: str | None = None
    quantity: float | None = None
    unit_price: float | None = None
    amount: float | None = None

@dataclass(slots=True)
class TaxBreakdown:
    tax_type: str
    rate: float | None = None
    amount: float | None = None

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
    tax_breakdown: list[TaxBreakdown] | None = None
    line_items: list[InvoiceLineItem] | None = None

GSTIN_PATTERN = re.compile(r"\b\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d]Z[A-Z\d]\b", re.IGNORECASE)
DATE_PATTERN = r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"

def _clean(value: str | None) -> str | None:
    if value is None: return None
    value = re.sub(r"\s+", " ", value).strip(" :|-\t")
    return value or None

def _first_group(text: str, patterns: tuple[str, ...]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match: return _clean(match.group(1))
    return None

def _parse_amount(value: str | None) -> float | None:
    if not value: return None
    # OCR can split a leading digit from a comma-grouped amount: 7 96,170. 00 -> 96,170.00.
    normalized_value = re.sub(r"(?<!\d)(\d)\s+(?=\d{2,3}(?:,\d{3})+\.)", "", value)
    normalized_value = re.sub(r"\s+", "", normalized_value)
    normalized = re.sub(r"[^0-9.,-]", "", normalized_value).replace(",", "")
    try: return float(Decimal(normalized))
    except (InvalidOperation, ValueError): return None

def _parse_number(value: str | None) -> float | None:
    if not value: return None
    try: return float(Decimal(re.sub(r"\s+", "", value).replace(",", "").strip()))
    except (InvalidOperation, ValueError): return None

def _amount_pattern() -> str:
    return r"([0-9][0-9,]*(?:\s[0-9][0-9,]*)*(?:\.\s*[0-9]{1,2})?)"

def _extract_labeled_amount(text: str, labels: tuple[str, ...]) -> float | None:
    label_pattern = "|".join(rf"\b{re.escape(label)}\b" for label in labels)
    pattern = rf"(?:{label_pattern})\s*(?:\([^)]*\))?\s*(?:[:=\-])?\s*(?:INR|Rs\.?|₹|USD|EUR|\$|€)?\s*{_amount_pattern()}"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return _parse_amount(match.group(1)) if match else None

def _extract_currency(text: str) -> str | None:
    if re.search(r"(?:₹|INR|Rs\.?|Rupees)", text, flags=re.IGNORECASE): return "INR"
    if re.search(r"(?:\$|USD|US Dollars?)", text, flags=re.IGNORECASE): return "USD"
    if re.search(r"(?:€|EUR|Euros?)", text, flags=re.IGNORECASE): return "EUR"
    if re.search(r"(?:£|GBP|Pounds?)", text, flags=re.IGNORECASE): return "GBP"
    return None

def _extract_party_name(text: str, labels: tuple[str, ...]) -> str | None:
    lines = text.splitlines(); label_pattern = "|".join(re.escape(label) for label in labels)
    same_line = re.compile(rf"(?:{label_pattern})\s*(?:[:=-])?\s*([^\n|]+)", re.IGNORECASE)
    next_line = re.compile(rf"^\s*(?:{label_pattern})\s*[:=-]?\s*$", re.IGNORECASE)
    for index, line in enumerate(lines):
        match = same_line.search(line)
        if match:
            value = _clean(match.group(1))
            if value and value.lower() not in {"gstin", "gstin:"}: return value
        if next_line.match(line):
            for candidate in lines[index + 1:index + 3]:
                value = _clean(candidate)
                if value and not re.search(r"\bgstin\b", value, re.IGNORECASE): return value
    return None

def _extract_tax_breakdown(text: str) -> list[TaxBreakdown]:
    taxes: list[TaxBreakdown] = []
    pattern = re.compile(rf"\b(CGST|SGST|IGST|UTGST|GST)\s*(?:\((\d+(?:\.\d+)?)%\))?\s*[:=-]?\s*(?:INR|Rs\.?|₹)?\s*{_amount_pattern()}", flags=re.IGNORECASE)
    for match in pattern.finditer(text): taxes.append(TaxBreakdown(tax_type=match.group(1).upper(), rate=_parse_number(match.group(2)), amount=_parse_amount(match.group(3))))
    return taxes

def _extract_line_items(text: str) -> list[InvoiceLineItem]:
    items: list[InvoiceLineItem] = []; amount = r"[0-9][0-9,]*(?:\.\s*[0-9]{1,2})?"
    for line in text.splitlines():
        line = line.strip().rstrip("|").strip()
        if not line or line.lower().startswith("s.no"): continue
        match = re.match(rf"^(\d+)\s+(.+?)\s+(\d{{6,8}})\s+(\d+(?:\.\d+)?)\s+({amount})\s+({amount})\s*$", line)
        if not match: continue
        items.append(InvoiceLineItem(line_number=int(match.group(1)), description=_clean(match.group(2)), hsn_code=match.group(3), quantity=_parse_number(match.group(4)), unit_price=_parse_amount(match.group(5)), amount=_parse_amount(match.group(6))))
    return items

def extract_invoice_fields(text: str) -> InvoiceFields:
    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")
    invoice_number = _first_group(normalized_text, (r"(?:invoice\s*(?:no|number|#))\s*[:=-]?\s*([^\n|]+)", r"(?:inv\.?\s*(?:no|#))\s*[:=-]?\s*([^\n|]+)"))
    invoice_date = _first_group(normalized_text, (rf"(?:invoice\s*date|date\s*of\s*invoice)\s*[:=-]?\s*({DATE_PATTERN})",))
    due_date = _first_group(normalized_text, (rf"(?:due\s*date|payment\s*due)\s*[:=-]?\s*({DATE_PATTERN})",))
    gstins = [match.upper() for match in GSTIN_PATTERN.findall(normalized_text)]
    vendor_gstin = gstins[0] if gstins else None; buyer_gstin = gstins[1] if len(gstins) > 1 else None
    vendor_name = _extract_party_name(normalized_text, ("vendor", "supplier", "seller", "from", "vendor name", "supplier name"))
    buyer_name = _extract_party_name(normalized_text, ("buyer", "customer", "bill to", "billed to", "buyer name", "customer name"))
    po_number = _first_group(normalized_text, (r"(?:purchase\s*order|order|po)\s*(?:no|number|#)?\s*[:=-]?\s*(PO[-\w]+)",))
    subtotal = _extract_labeled_amount(normalized_text, ("subtotal", "sub total", "taxable value", "net amount"))
    taxes = _extract_tax_breakdown(normalized_text)
    explicit_tax = _extract_labeled_amount(normalized_text, ("tax amount", "total tax", "gst amount"))
    tax_amount = explicit_tax if explicit_tax is not None else (sum(t.amount for t in taxes if t.amount is not None) or None)
    total_amount = _extract_labeled_amount(normalized_text, ("grand total", "invoice total", "total amount", "amount due"))
    if total_amount is None: total_amount = _extract_labeled_amount(normalized_text, ("total",))
    return InvoiceFields(invoice_number=invoice_number, invoice_date=invoice_date, due_date=due_date, vendor_name=vendor_name, vendor_gstin=vendor_gstin, buyer_name=buyer_name, buyer_gstin=buyer_gstin, subtotal=subtotal, tax_amount=tax_amount, total_amount=total_amount, currency=_extract_currency(normalized_text), po_number=po_number, tax_breakdown=taxes, line_items=_extract_line_items(normalized_text))

def extract_invoice_fields_dict(text: str) -> dict[str, object]:
    return asdict(extract_invoice_fields(text))
