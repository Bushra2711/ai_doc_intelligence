# Step 4 — Invoice Accuracy Evaluation

## Objective

Measure how accurately the invoice extraction pipeline converts OCR/document text into structured invoice fields.

## Evaluation approach

A human-verified ground-truth record is compared with the fields extracted by the deterministic invoice extractor.

Initial evaluation fields:

- Invoice number
- Invoice date
- Vendor name
- Vendor GSTIN
- Buyer name
- Buyer GSTIN
- Subtotal
- Tax amount
- Total amount
- PO number

Text fields are normalized for case and whitespace before comparison. Numeric values are compared with a small absolute tolerance of 0.01.

## Metrics

**Field accuracy** = correctly matched fields / evaluated fields × 100

The API also returns the predicted value, expected value, and match result for every evaluated field so extraction errors can be reviewed instead of hiding them inside one percentage.

## API

`POST /api/v1/documents/{document_id}/evaluate-accuracy`

Example request body:

```json
{
  "expected": {
    "invoice_number": "INV-2026-001",
    "invoice_date": "10/09/2026",
    "vendor_name": "ABC TRADERS PVT. LTD.",
    "vendor_gstin": "29ABCDE1234F1Z5",
    "buyer_name": "XYZ SOLUTIONS",
    "buyer_gstin": "29XYZAB9876C1Z2",
    "subtotal": 81500,
    "tax_amount": 14670,
    "total_amount": 96170,
    "po_number": "PO-7788"
  }
}
```

## TCS alignment

This step establishes a measurable invoice extraction accuracy KPI and creates a repeatable path from annotated ground truth to evaluation results. Future iterations can add line-item accuracy, confidence calibration, dataset-level reports, and regression testing.
