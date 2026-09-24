# Step 21 - Test Evidence Report

## 1. Evidence Summary

| Evidence Area | Dataset / Scope | Result | Evidence Artifact |
|---|---|---|---|
| Invoice extraction accuracy | 50 human-verified synthetic invoices; 10 fields each | 500/500; 100.00% | evaluation/results/invoice_accuracy_report.json |
| OCR information retention | 50 invoices; 500 field comparisons | 98.80% | evaluation/results/ocr_accuracy_report.json |
| Processing time | 50 digital PDF invoices | 50/50 successful; mean 0.046s; P95 0.054s | evaluation/results/processing_time_report.json |
| Confidence evaluation | 50 invoices | 96.00% average; 50 HIGH | evaluation/results/invoice_quality_report.json |
| Compliance evaluation | 50 invoices; 500 checks | 450 PASS, 0 WARNING, 50 FAIL | evaluation/results/invoice_quality_report.json |
| Automated backend tests | Backend regression suite | 20/20 passed | pytest execution log |
| Domain adaptation | Invoice-domain schema/rule adaptation | Versioned domain adapter implemented and tested | docs/28-domain-adaptation.md |
| SHAP explainability | Deterministic invoice-validation surrogate layer | SHAP TreeExplainer executed successfully | backend/app/services/explainability_service.py; API endpoint |
| MLOps drift/retraining | Synthetic distribution/performance shift | Drift detected and retraining trigger persisted; MLflow tracking verified | docs/27-mlops-drift-and-retraining.md |
| Multi-source ingestion | Portal, API, Batch runtime paths | Portal 201; API 201; Batch 201 | docs/29-multi-source-ingestion.md; API/Swagger execution evidence |

## 2. Invoice Extraction Accuracy Evidence

The invoice extraction pipeline was evaluated against human-verified annotations for 50 synthetic GST-style invoices. Ten structured fields were compared for every invoice, producing 500 field-level comparisons. All 500 comparisons matched, resulting in 100.00% field-level accuracy.

Per-field evaluation also reached 100.00% for invoice number, invoice date, vendor name, vendor GSTIN, buyer name, buyer GSTIN, subtotal, tax amount, total amount, and PO number.

## 3. OCR Evidence

The OCR evaluation measured information retention rather than character-perfect transcription. Across 50 invoices and 500 evaluated field-presence comparisons, the observed result was 98.80%.

This metric should not be presented as conventional character-level OCR accuracy because the test PDFs contain synthetic digital content and OCR layout differences can affect CER/WER independently of business-field retention.

## 4. Processing-Time Evidence

The local benchmark processed 50 digital PDF invoices successfully. Observed mean processing time was 0.046 seconds, median 0.045 seconds, P95 0.054 seconds, minimum 0.035 seconds, and maximum 0.092 seconds.

These measurements are local benchmark observations, not a universal production SLA. The benchmark does not represent network/upload latency or scanned-document Tesseract processing time.

## 5. Confidence and Compliance Evidence

The confidence evaluation produced an average score of 96.00%, with all 50 invoices classified HIGH by the project's transparent heuristic.

The compliance engine produced 450 PASS checks, 0 WARNING checks, and 50 FAIL checks. The failure-rule breakdown recorded buyer_gstin_format=50.

The synthetic invoices use GSTIN-like test identifiers. The strict GSTIN structure rule therefore rejects the synthetic buyer identifiers. This result is a compliance-rule outcome and should not be interpreted as an invoice extraction failure or as a statement about legal/tax compliance.

## 6. Automated Regression Evidence

The backend pytest suite was executed after the multi-source ingestion changes.

Observed result: 20 tests passed with no test failures or pytest configuration warnings.

## 7. Domain Adaptation Evidence

The invoice domain adapter provides a versioned schema/rule layer with required and optional invoice fields. This is documented as domain adaptation at the application/schema level and is not model-weight fine-tuning evidence.

## 8. SHAP Explainability Evidence

SHAP TreeExplainer was executed against the deterministic invoice-validation surrogate layer. The explainability API exposes the prediction, confidence, base value, feature contributions, direction, and reason.

This evidence explains the deterministic validation layer; it does not expose or claim to explain Gemini's internal reasoning.

## 9. MLOps Drift and Retraining Evidence

The drift monitor evaluates population stability index (PSI) and performance degradation thresholds, persists a retraining trigger, and records the monitoring run through MLflow. The executed demo produced a retraining trigger under intentionally shifted/degraded evaluation conditions.

This demonstrates monitoring and trigger logic, not automatic retrained-model replacement or production deployment.

## 10. Multi-Source Ingestion Evidence

The ingestion implementation supports three application-level paths:

- Portal upload via `POST /api/v1/documents/upload?ingestion_source=portal`.
- API-source upload via `POST /api/v1/documents/upload?ingestion_source=api`.
- Batch upload via `POST /api/v1/documents/batch-upload`.

Runtime evidence returned HTTP 201 for all three paths. The API-source test used `TCS-TEST-0006.pdf`; the batch test used three test PDFs and returned `ingestion_source="batch"`. The ingestion source is persisted in document metadata and exposed by the document response schema.

This is application-level multi-source evidence. It does not establish live external email, cloud-storage, or enterprise data-lake connectors.

## 11. Evidence Limitations

- The primary invoice dataset is synthetic GST-style test data.
- The 100.00% extraction result is specific to this evaluated dataset.
- OCR evidence measures business-field information retention.
- Processing-time values are local benchmark measurements.
- Compliance checks validate implemented application rules and do not establish legal or tax compliance.
- Handwritten validation remains a one-sample pilot with limited results.
- Multilingual validation uses a small synthetic bilingual/Hindi dataset and should not be treated as general Hindi OCR accuracy.
- SHAP explains the deterministic validation surrogate layer, not Gemini internal reasoning.
- Domain adaptation is schema/rule adaptation, not model-weight fine-tuning.
- MLOps evidence covers drift detection and retraining-trigger logic, not automatic model replacement/deployment.
- Multi-source evidence covers Portal/API/Batch application paths, not live external connectors.
- Kubernetes manifests are prepared, but local runtime deployment was not verified because Docker Desktop Kubernetes initialization failed.
- Cloud/Azure deployment is not included in the verified runtime evidence.
- The native Power BI dashboard is a separately created artifact and should be retained with the final submission package.

## 12. Defect Status

No defect was recorded for the evaluated extraction, OCR-retention, processing-time, confidence, or automated regression test results.

The 50 compliance failures are documented as a known synthetic-test-data interaction with the strict buyer_gstin_format rule rather than being classified as extraction defects.
