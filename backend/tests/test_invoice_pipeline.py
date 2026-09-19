from app.services.invoice_compliance import evaluate_invoice_compliance
from app.services.invoice_confidence import calculate_invoice_confidence
from app.services.invoice_extraction import extract_invoice_fields


SAMPLE_INVOICE = """
ABC TRADERS PVT. LTD.
GSTIN: 29ABCDE1234F1Z5
TAX INVOICE
Invoice No: INV-2026-001
Invoice Date: 10/09/2026
Bill To: XYZ SOLUTIONS
GSTIN: 29XYZAB9876C1Z2
PO Number: PO-7788

1 Laptop 84713000 2 40000 80000
2 Mouse 84716000 3 500 1500
Subtotal: INR 81500
CGST (9%): INR 7335
SGST (9%): INR 7335
Total Tax: INR 14670
Grand Total: INR 96170
"""


def test_invoice_extraction_covers_required_structured_fields():
    fields = extract_invoice_fields(SAMPLE_INVOICE)

    assert fields.invoice_number == "INV-2026-001"
    assert fields.invoice_date == "10/09/2026"
    assert fields.vendor_name == "ABC TRADERS PVT. LTD."
    assert fields.vendor_gstin == "29ABCDE1234F1Z5"
    assert fields.buyer_name == "XYZ SOLUTIONS"
    assert fields.buyer_gstin == "29XYZAB9876C1Z2"
    assert fields.po_number == "PO-7788"
    assert fields.subtotal == 81500
    assert fields.tax_amount == 14670
    assert fields.total_amount == 96170
    assert fields.currency == "INR"
    assert len(fields.tax_breakdown or []) == 2
    assert len(fields.line_items or []) == 2


def test_invoice_compliance_passes_consistent_invoice():
    fields = extract_invoice_fields(SAMPLE_INVOICE)
    result = evaluate_invoice_compliance({
        "invoice_number": fields.invoice_number,
        "invoice_date": fields.invoice_date,
        "vendor_name": fields.vendor_name,
        "buyer_name": fields.buyer_name,
        "vendor_gstin": fields.vendor_gstin,
        "buyer_gstin": fields.buyer_gstin,
        "subtotal": fields.subtotal,
        "tax_amount": fields.tax_amount,
        "total_amount": fields.total_amount,
        "tax_breakdown": [{"tax_type": x.tax_type, "amount": x.amount} for x in fields.tax_breakdown or []],
        "line_items": [
            {"description": x.description, "quantity": x.quantity, "amount": x.amount}
            for x in fields.line_items or []
        ],
        "po_number": fields.po_number,
    })

    assert result["failed"] == 0
    assert result["overall_status"] == "COMPLIANT"


def test_invoice_compliance_detects_amount_mismatch():
    result = evaluate_invoice_compliance({
        "invoice_number": "INV-1",
        "invoice_date": "10/09/2026",
        "vendor_name": "ABC",
        "buyer_name": "XYZ",
        "vendor_gstin": "29ABCDE1234F1Z5",
        "buyer_gstin": "29XYZAB9876C1Z2",
        "subtotal": 1000,
        "tax_amount": 180,
        "total_amount": 1200,
    })

    assert result["failed"] >= 1
    assert any(x["rule"] == "amount_reconciliation" and x["status"] == "FAIL" for x in result["checks"])


def test_invoice_confidence_excludes_missing_optional_fields_from_overall_score():
    fields = extract_invoice_fields(SAMPLE_INVOICE)
    result = calculate_invoice_confidence({
        "invoice_number": fields.invoice_number,
        "invoice_date": fields.invoice_date,
        "due_date": None,
        "vendor_name": fields.vendor_name,
        "vendor_gstin": fields.vendor_gstin,
        "buyer_name": fields.buyer_name,
        "buyer_gstin": fields.buyer_gstin,
        "subtotal": fields.subtotal,
        "tax_amount": fields.tax_amount,
        "total_amount": fields.total_amount,
        "currency": fields.currency,
        "po_number": fields.po_number,
        "tax_breakdown": [{"tax_type": x.tax_type, "amount": x.amount} for x in fields.tax_breakdown or []],
        "line_items": [
            {"description": x.description, "quantity": x.quantity, "amount": x.amount}
            for x in fields.line_items or []
        ],
    })

    assert result.overall_score >= 0.90
    assert result.overall_level == "HIGH"
    due_date = next(item for item in result.fields if item.field == "due_date")
    assert due_date.level == "MISSING"
