# Domain Adaptation — Invoice Processing

## Objective

The DocuMind document-processing pipeline is specialized for the invoice domain. This document records the implemented domain-adaptation layer and distinguishes it from model-weight fine-tuning.

## Implemented approach

The current implementation uses **invoice-domain schema and rule specialization**:

1. Invoice text is extracted through the existing invoice extraction service.
2. The extracted `InvoiceFields` object is passed through a versioned invoice-domain adapter.
3. The adapter declares required and optional invoice fields.
4. Missing required fields are surfaced as `REVIEW_REQUIRED`.
5. Complete domain records are marked `READY`.
6. The adapter preserves the extracted structured fields for downstream compliance, confidence, audit, and analytics processing.

Implementation:

- `backend/app/services/invoice_domain_adapter.py`
- `backend/tests/test_domain_adapter.py`

## Invoice-domain schema

Required fields:

- invoice number
- invoice date
- vendor name
- vendor GSTIN
- buyer name
- buyer GSTIN
- subtotal
- tax amount
- total amount
- currency

Optional fields:

- due date
- PO number
- tax breakdown
- line items

The adapter is versioned as `1.0`.

## Evaluation evidence

The adapter is tested against the existing representative invoice fixture used by the invoice pipeline. The test verifies that the domain-specific schema is populated from the existing extraction result and that missing mandatory fields produce `REVIEW_REQUIRED`.

The broader invoice-domain evaluation already contains 50 synthetic GST-style invoices with 500 required-field comparisons and reported 100% field-level extraction accuracy for the evaluated fields.

That 50-invoice result is evidence for the existing invoice extraction pipeline; it should not be interpreted as an independent benchmark of LLM fine-tuning.

## Relationship to Gemini

The project currently uses Gemini for document analysis/classification. **No Gemini model-weight fine-tuning is claimed by this implementation.**

The domain adaptation layer specializes the application around the invoice domain using:

- a versioned invoice schema,
- invoice-specific extraction rules,
- GST/tax structure handling,
- compliance validation,
- confidence/data-quality processing, and
- explicit review handling for missing required fields.

This provides application-level domain adaptation without claiming that the underlying LLM was fine-tuned.

## TCS guideline mapping

| Requirement | Evidence | Status |
|---|---|---|
| Domain-specific model/application adaptation | Versioned invoice-domain adapter and invoice-specific extraction/validation logic | Implemented |
| Domain-specific structured fields | Required/optional invoice schema | Implemented |
| Validation of domain output | Existing invoice compliance and confidence services plus adapter tests | Implemented |
| Fine-tuning of underlying LLM weights | No model-weight fine-tuning artifact is present | Not claimed |
| Domain adaptation evaluation | Existing 50-invoice evaluation plus adapter unit tests | Evidence available |

## Verification

From the backend directory:

```powershell
python -m pytest tests/test_domain_adapter.py -q
python -m pytest -q
```

The expected full-suite count after adding these tests is 20 tests.
