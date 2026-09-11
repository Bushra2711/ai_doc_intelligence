from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any

GSTIN_PATTERN = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")


def _value(data: dict[str, Any], key: str) -> Any:
    return data.get(key)


def _number(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, ValueError):
        return None


def _result(rule: str, status: str, message: str) -> dict[str, str]:
    return {"rule": rule, "status": status, "message": message}


def evaluate_invoice_compliance(fields: dict[str, Any]) -> dict[str, Any]:
    """Run deterministic invoice validation rules against extracted fields.

    Status values are PASS, WARNING, and FAIL. Missing optional data is a
    warning rather than a failure; contradictory financial values are failures.
    """
    checks: list[dict[str, str]] = []

    invoice_number = _value(fields, "invoice_number")
    invoice_date = _value(fields, "invoice_date")
    vendor = _value(fields, "vendor_name")
    buyer = _value(fields, "buyer_name")
    vendor_gstin = _value(fields, "vendor_gstin")
    buyer_gstin = _value(fields, "buyer_gstin")
    subtotal = _number(_value(fields, "subtotal"))
    tax = _number(_value(fields, "tax_amount"))
    total = _number(_value(fields, "total_amount"))
    breakdown = fields.get("tax_breakdown") or []
    line_items = fields.get("line_items") or []

    checks.append(_result("invoice_number_present", "PASS" if invoice_number else "FAIL", "Invoice number is present." if invoice_number else "Invoice number is missing."))
    checks.append(_result("invoice_date_present", "PASS" if invoice_date else "FAIL", "Invoice date is present." if invoice_date else "Invoice date is missing."))
    checks.append(_result("vendor_present", "PASS" if vendor else "FAIL", "Vendor name is present." if vendor else "Vendor name is missing."))
    checks.append(_result("buyer_present", "PASS" if buyer else "WARNING", "Buyer name is present." if buyer else "Buyer name was not extracted."))

    if vendor_gstin:
        checks.append(_result("vendor_gstin_format", "PASS" if GSTIN_PATTERN.fullmatch(vendor_gstin.upper()) else "FAIL", "Vendor GSTIN format is valid." if GSTIN_PATTERN.fullmatch(vendor_gstin.upper()) else "Vendor GSTIN format is invalid."))
    else:
        checks.append(_result("vendor_gstin_format", "WARNING", "Vendor GSTIN was not extracted."))

    if buyer_gstin:
        checks.append(_result("buyer_gstin_format", "PASS" if GSTIN_PATTERN.fullmatch(buyer_gstin.upper()) else "FAIL", "Buyer GSTIN format is valid." if GSTIN_PATTERN.fullmatch(buyer_gstin.upper()) else "Buyer GSTIN format is invalid."))
    else:
        checks.append(_result("buyer_gstin_format", "WARNING", "Buyer GSTIN was not extracted."))

    if subtotal is not None and tax is not None and total is not None:
        difference = abs((subtotal + tax) - total)
        checks.append(_result("amount_reconciliation", "PASS" if difference <= Decimal("0.01") else "FAIL", "Subtotal + tax matches total amount." if difference <= Decimal("0.01") else f"Subtotal + tax does not match total amount (difference {difference})."))
    else:
        checks.append(_result("amount_reconciliation", "WARNING", "Insufficient extracted amounts to reconcile subtotal, tax, and total."))

    if breakdown and tax is not None:
        breakdown_total = sum((_number(item.get("amount")) or Decimal("0")) for item in breakdown)
        difference = abs(breakdown_total - tax)
        checks.append(_result("tax_reconciliation", "PASS" if difference <= Decimal("0.01") else "FAIL", "Tax breakdown matches total tax." if difference <= Decimal("0.01") else "Tax breakdown does not match total tax."))
    else:
        checks.append(_result("tax_reconciliation", "WARNING", "Tax breakdown is not available for reconciliation."))

    if line_items and subtotal is not None:
        items_total = sum((_number(item.get("amount")) or Decimal("0")) for item in line_items)
        difference = abs(items_total - subtotal)
        checks.append(_result("line_item_reconciliation", "PASS" if difference <= Decimal("0.01") else "FAIL", "Line-item amounts match subtotal." if difference <= Decimal("0.01") else "Line-item amounts do not match subtotal."))
    else:
        checks.append(_result("line_item_reconciliation", "WARNING", "Line items or subtotal are unavailable for reconciliation."))

    if _value(fields, "po_number"):
        checks.append(_result("purchase_order_reference", "PASS", "Purchase order reference is present."))
    else:
        checks.append(_result("purchase_order_reference", "WARNING", "Purchase order reference was not extracted."))

    failures = sum(check["status"] == "FAIL" for check in checks)
    warnings = sum(check["status"] == "WARNING" for check in checks)
    overall = "NON_COMPLIANT" if failures else "COMPLIANT_WITH_WARNINGS" if warnings else "COMPLIANT"
    return {"overall_status": overall, "checks": checks, "passed": len(checks) - failures - warnings, "warnings": warnings, "failed": failures}
