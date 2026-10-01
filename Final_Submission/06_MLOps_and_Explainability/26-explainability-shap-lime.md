# Step 2 — SHAP Explainability

## Objective
The TCS guideline requires explainability for model decisions. DocuMind provides SHAP-based explanations for the deterministic invoice validation layer.

## Architecture
Document -> OCR / extracted text -> invoice field extraction -> deterministic validation -> validation decision -> SHAP explanation -> API / audit-ready output.

## Why the validation layer is explained
Gemini performs generative document understanding and extraction. SHAP is therefore not presented as an explanation of Gemini's hidden token-level reasoning. Instead, SHAP explains the transparent validation decision layer that consumes extracted invoice fields.

## Explained features
- Invoice number present
- Invoice date present
- Vendor present
- Buyer present
- Vendor GSTIN format valid
- Buyer GSTIN format valid
- Subtotal + tax reconciled with total
- Tax breakdown reconciled
- Line items reconciled with subtotal
- Purchase-order reference present

## Method
A deterministic validation surrogate classifier is evaluated with SHAP TreeExplainer. Each feature receives an additive contribution relative to the model baseline.

The API exposes method, model layer, prediction, confidence, base value, per-feature contribution, direction, reason, and limitation.

## API
GET /api/v1/documents/{document_id}/explainability

The endpoint uses the same authenticated document ownership check as the existing document APIs.

## Limitation
SHAP explains the deterministic validation surrogate, not Gemini's internal LLM reasoning. This distinction should remain explicit in the final report and demo.

## TCS mapping
TCS Step 5 asks for dashboards, extraction accuracy, compliance alerts, SHAP/LIME explainability, RBAC, and audit logs. The existing project already provides the dashboard, compliance, RBAC, and audit capabilities; this module adds the SHAP explainability evidence.
