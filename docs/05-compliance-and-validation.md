# Step 5 — Compliance and Validation

## Objective

Validate extracted invoice data with deterministic business and financial rules before downstream approval or reporting.

## Validation rules

| Rule | Outcome |
|---|---|
| Invoice number present | Pass / Fail |
| Invoice date present | Pass / Fail |
| Vendor present | Pass / Fail |
| Buyer present | Pass / Warning |
| Vendor GSTIN format | Pass / Fail / Warning |
| Buyer GSTIN format | Pass / Fail / Warning |
| Subtotal + tax = total | Pass / Fail / Warning |
| Tax breakdown = total tax | Pass / Fail / Warning |
| Line-item total = subtotal | Pass / Fail / Warning |
| Purchase-order reference | Pass / Warning |

Missing optional information produces a warning. Contradictory financial calculations produce a failure.

## Compliance status

- `COMPLIANT`: all checks pass.
- `COMPLIANT_WITH_WARNINGS`: no failures, but one or more warnings exist.
- `NON_COMPLIANT`: one or more validation rules fail.

## API

`GET /api/v1/documents/{document_id}/compliance`

The endpoint reuses the structured invoice extraction output and returns the overall status, passed/warning/failed counts, and individual rule results.

## UI

The document detail view displays a Compliance Checks section with the overall status, counters, and rule-by-rule results. This makes validation visible alongside structured invoice extraction.

## TCS alignment

This step supports validation, compliance checking, exception handling, traceable processing decisions, and downstream invoice automation requirements.
