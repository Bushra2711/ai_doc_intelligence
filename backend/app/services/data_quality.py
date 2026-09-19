from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.schemas.invoice_extraction import InvoiceExtractionResult


@dataclass(slots=True)
class DataQualityResult:
    score: float
    status: str
    checks: list[dict[str, Any]]


def evaluate_invoice_data_quality(invoice: InvoiceExtractionResult) -> DataQualityResult:
    """Evaluate completeness, validity and reconciliation of extracted invoice data."""
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, weight: float, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "weight": weight, "detail": detail})

    add("invoice_number", bool(invoice.invoice_number), 15, "Invoice number is present")
    add("invoice_date", bool(invoice.invoice_date), 10, "Invoice date is present")
    add("vendor_name", bool(invoice.vendor_name), 10, "Vendor name is present")
    add("total_amount", invoice.total_amount is not None and invoice.total_amount >= 0, 15, "Total amount is valid")
    add("currency", bool(invoice.currency), 5, "Currency is present")

    if invoice.subtotal is not None and invoice.tax_amount is not None and invoice.total_amount is not None:
        reconciled = abs((invoice.subtotal + invoice.tax_amount) - invoice.total_amount) <= 1.0
        add("amount_reconciliation", reconciled, 20, "Subtotal + tax matches total")
    else:
        add("amount_reconciliation", False, 20, "Amounts are incomplete")

    add("line_items", bool(invoice.line_items), 15, "At least one line item was extracted")
    add("tax_breakdown", bool(invoice.tax_breakdown), 10, "Tax breakdown was extracted")

    possible = sum(float(item["weight"]) for item in checks)
    earned = sum(float(item["weight"]) for item in checks if item["passed"])
    score = round(earned / possible, 4) if possible else 0.0
    status = "GOOD" if score >= 0.9 else "REVIEW" if score >= 0.7 else "POOR"
    return DataQualityResult(score=score, status=status, checks=checks)
