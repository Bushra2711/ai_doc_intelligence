from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isclose
from typing import Any

@dataclass(slots=True)
class FieldConfidence:
    field: str
    value: Any
    score: float
    level: str
    reason: str

@dataclass(slots=True)
class InvoiceConfidence:
    overall_score: float
    overall_level: str
    fields: list[FieldConfidence]

def _level(score: float) -> str:
    if score >= 0.90: return "HIGH"
    if score >= 0.70: return "MEDIUM"
    if score > 0: return "LOW"
    return "MISSING"

def _field(field: str, value: Any, score: float, reason: str) -> FieldConfidence:
    score = round(max(0.0, min(1.0, score)), 2)
    return FieldConfidence(field=field, value=value, score=score, level=_level(score), reason=reason)

def _number(value: Any) -> float | None:
    try: return float(value) if value is not None else None
    except (TypeError, ValueError): return None

def calculate_invoice_confidence(fields: dict[str, Any]) -> InvoiceConfidence:
    """Calculate transparent confidence from extraction evidence and consistency checks."""
    results: list[FieldConfidence] = []
    rules = {
        "invoice_number": (0.98, "Matched an invoice-number label and value."),
        "invoice_date": (0.98, "Matched an invoice-date label and date pattern."),
        "due_date": (0.96, "Matched a due-date label and date pattern."),
        "vendor_name": (0.88, "Matched a vendor/seller label or nearby party name."),
        "vendor_gstin": (0.99, "Matched a valid GSTIN structure."),
        "buyer_name": (0.88, "Matched a buyer/bill-to label or nearby party name."),
        "buyer_gstin": (0.99, "Matched a valid GSTIN structure."),
        "subtotal": (0.96, "Matched a labeled subtotal/net amount."),
        "currency": (0.95, "Matched an explicit currency symbol or currency code."),
        "po_number": (0.96, "Matched a purchase/order reference label."),
    }
    for name, (score, reason) in rules.items():
        value = fields.get(name)
        results.append(_field(name, value, score if value is not None else 0.0, reason if value is not None else "Field was not found in extracted text."))

    taxes = fields.get("tax_breakdown") or []
    tax_amount = _number(fields.get("tax_amount"))
    results.append(_field("tax_amount", tax_amount, 0.94 if tax_amount is not None and taxes else 0.86 if tax_amount is not None else 0.0, "Total tax was derived from labeled tax values." if tax_amount is not None and taxes else "Tax amount was explicitly labeled." if tax_amount is not None else "No tax amount could be extracted."))

    total = _number(fields.get("total_amount")); subtotal = _number(fields.get("subtotal"))
    tax_sum = sum(_number(item.get("amount")) or 0.0 for item in taxes if isinstance(item, dict))
    if total is not None:
        consistent = subtotal is not None and bool(taxes) and isclose(total, subtotal + tax_sum, rel_tol=0.0, abs_tol=0.02)
        results.append(_field("total_amount", total, 0.99 if consistent else 0.90, "Total matches subtotal plus extracted tax breakdown." if consistent else "Total amount was matched from an invoice total label."))
    else:
        results.append(_field("total_amount", None, 0.0, "No total amount could be extracted."))

    if taxes:
        complete = all(isinstance(item, dict) and item.get("tax_type") and item.get("amount") is not None for item in taxes)
        results.append(_field("tax_breakdown", taxes, 0.97 if complete else 0.75, "Tax rows contain tax type and amount." if complete else "Some tax-row values are incomplete."))
    else:
        results.append(_field("tax_breakdown", [], 0.0, "No tax breakdown rows were extracted."))

    items = fields.get("line_items") or []
    if items:
        complete_items = sum(1 for item in items if isinstance(item, dict) and item.get("description") and item.get("quantity") is not None and item.get("amount") is not None)
        results.append(_field("line_items", items, 0.95 if complete_items == len(items) else 0.75, f"{complete_items} of {len(items)} line items contain description, quantity, and amount."))
    else:
        results.append(_field("line_items", [], 0.0, "No line items were extracted."))

    overall = round(sum(item.score for item in results) / len(results), 2) if results else 0.0
    return InvoiceConfidence(overall_score=overall, overall_level=_level(overall), fields=results)

def invoice_confidence_dict(fields: dict[str, Any]) -> dict[str, Any]:
    result = calculate_invoice_confidence(fields)
    return {"overall_score": result.overall_score, "overall_level": result.overall_level, "fields": [asdict(item) for item in result.fields]}
