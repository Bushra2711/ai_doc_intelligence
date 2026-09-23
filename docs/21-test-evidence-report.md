# Step 21 - Test Evidence Report

## 1. Evidence Summary

| Evidence Area | Dataset / Scope | Result | Evidence Artifact |
|---|---|---|---|
| Invoice extraction accuracy | 50 human-verified synthetic invoices; 10 fields each | 500/500; 100.00% | evaluation/results/invoice_accuracy_report.json |
| OCR information retention | 50 invoices; 500 field comparisons | 98.80% | evaluation/results/ocr_accuracy_report.json |
| Processing time | 50 digital PDF invoices | 50/50 successful; mean 0.046s; P95 0.054s | evaluation/results/processing_time_report.json |
| Confidence evaluation | 50 invoices | 96.00% average; 50 HIGH | evaluation/results/invoice_quality_report.json |
| Compliance evaluation | 50 invoices; 500 checks | 450 PASS, 0 WARNING, 50 FAIL | evaluation/results/invoice_quality_report.json |
| Automated backend tests | Backend regression suite | 13/13 passed | pytest execution log |

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

The backend pytest suite was executed after the invoice parser and evaluation changes.

Observed result: 13 tests passed with no test failures or pytest configuration warnings.

## 7. Evidence Limitations

- The primary invoice dataset is synthetic GST-style test data.
- The 100.00% extraction result is specific to the evaluated dataset.
- OCR evidence measures business-field information retention.
- Processing-time values are local benchmark measurements.
- Compliance checks validate implemented application rules and do not establish legal or tax compliance.
- Handwritten and multilingual document validation require separate executed evidence.
- Cloud/Azure, Kubernetes, native Power BI/Tableau, SHAP/LIME, fine-tuning, drift detection, and automated retraining should not be marked complete unless corresponding artifacts or execution evidence are produced.

## 8. Defect Status

No defect was recorded for the evaluated extraction, OCR-retention, processing-time, confidence, or automated regression test results.

The 50 compliance failures are documented as a known synthetic-test-data interaction with the strict buyer_gstin_format rule rather than being classified as extraction defects.