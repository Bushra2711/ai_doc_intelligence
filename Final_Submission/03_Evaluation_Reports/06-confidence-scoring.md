# Step 6 — Confidence Scoring

## Objective
Provide transparent confidence scores for structured invoice extraction so users can distinguish high-confidence values from fields that need review.

## Design
The confidence service is deterministic and explainable. It does not claim to be a calibrated probability from an ML model. Scores are based on extraction evidence and consistency checks.

### Confidence levels
- HIGH: 90–100%
- MEDIUM: 70–89%
- LOW: 1–69%
- MISSING: 0%

### Evidence examples
- Invoice number/date matched with explicit labels and expected patterns: high confidence.
- GSTIN matched against the GSTIN structure: very high confidence.
- Vendor/buyer party names found near recognized labels: high confidence.
- Total amount matching subtotal + extracted tax: confidence is increased.
- Complete line items with description, quantity and amount: high confidence.
- Missing values receive 0% and are surfaced as missing rather than fabricated.

## API
`GET /api/v1/documents/{document_id}/confidence`

Response includes:
- overall score and level
- field-level score
- extracted value
- confidence level
- human-readable reason

## UI
Invoice document details now show an **AI Quality → Confidence Scores** section with an overall confidence badge and per-field percentage meters.

## TCS mapping
This step supports the requirement for confidence scores and human-review prioritization in intelligent document processing.
