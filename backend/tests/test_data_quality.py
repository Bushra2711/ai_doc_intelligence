from app.schemas.invoice_extraction import (
    InvoiceFieldsResponse,
    InvoiceLineItemResponse,
    TaxBreakdownResponse,
)
from app.services.data_quality import evaluate_invoice_data_quality


def test_high_quality_invoice():
    invoice = InvoiceFieldsResponse(
        invoice_number="INV-001",
        invoice_date="10/09/2026",
        vendor_name="ABC Traders",
        subtotal=100.0,
        tax_amount=18.0,
        total_amount=118.0,
        currency="INR",
        line_items=[
            InvoiceLineItemResponse(
                description="Item", quantity=1, unit_price=100, amount=100
            )
        ],
        tax_breakdown=[
            TaxBreakdownResponse(tax_type="CGST", rate=9.0, amount=9.0),
            TaxBreakdownResponse(tax_type="SGST", rate=9.0, amount=9.0),
        ],
    )
    result = evaluate_invoice_data_quality(invoice)
    assert result.score >= 0.9
    assert result.status == "GOOD"


def test_incomplete_invoice_requires_review():
    invoice = InvoiceFieldsResponse(total_amount=100.0)
    result = evaluate_invoice_data_quality(invoice)
    assert result.score < 0.7
    assert result.status == "POOR"
