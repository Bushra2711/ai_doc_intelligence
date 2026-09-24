from app.services.invoice_domain_adapter import (
    DOMAIN_ADAPTER_VERSION,
    DOMAIN_NAME,
    REQUIRED_FIELDS,
    adapt_invoice_text,
)


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


def test_invoice_domain_adapter_applies_versioned_schema():
    result = adapt_invoice_text(SAMPLE_INVOICE)

    assert result.domain == DOMAIN_NAME
    assert result.adapter_version == DOMAIN_ADAPTER_VERSION
    assert result.required_fields == REQUIRED_FIELDS
    assert result.adaptation_status == "READY"
    assert result.missing_required_fields == []
    assert result.fields["invoice_number"] == "INV-2026-001"
    assert result.fields["vendor_gstin"] == "29ABCDE1234F1Z5"
    assert result.fields["buyer_gstin"] == "29XYZAB9876C1Z2"
    assert result.fields["subtotal"] == 81500
    assert result.fields["tax_amount"] == 14670
    assert result.fields["total_amount"] == 96170


def test_invoice_domain_adapter_flags_missing_required_fields():
    text = """
    TAX INVOICE
    Invoice No: INV-2026-002
    Invoice Date: 11/09/2026
    Vendor: ABC TRADERS
    Subtotal: INR 1000
    Total Tax: INR 180
    Grand Total: INR 1180
    """

    result = adapt_invoice_text(text)

    assert result.adaptation_status == "REVIEW_REQUIRED"
    assert "vendor_gstin" in result.missing_required_fields
    assert "buyer_name" in result.missing_required_fields
    assert "buyer_gstin" in result.missing_required_fields
