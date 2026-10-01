# DocuMind AI – Data Dictionary

**Project:** AI-Powered Intelligent Document Processing Platform  
**Evaluation Dataset:** `50_invoice_review.csv`  
**Evaluation Scope:** 50 sample invoice documents  
**BI:** Power BI  
**Experiment Tracking:** MLflow – `DocuMind_AI_Invoice_Evaluation`

## 1. Purpose

This data dictionary documents the business fields, evaluation concepts, compliance attributes, and governance artifacts used by the DocuMind AI invoice-processing and evaluation workflow.

The TCS project guideline requires the governance pack to include a data dictionary, data lineage, and compliance checklist. The project testing report identifies `50_invoice_review.csv` as the evaluation dataset and states that extracted values are compared with verified invoice fields.

## 2. Invoice Evaluation Fields

| Data element | Description | Role in evaluation |
|---|---|---|
| `invoice_number` | Invoice identifier extracted from the invoice | Compared with verified invoice field; extraction accuracy measure |
| `invoice_date` | Invoice date extracted from the invoice | Compared with verified invoice field; extraction accuracy measure |
| `vendor_name` | Name of the invoice vendor/supplier | Compared with verified invoice field; extraction accuracy measure |
| `vendor_gstin` | Vendor GSTIN value extracted from the invoice | Compared with verified invoice field; extraction accuracy measure |
| `buyer_name` | Buyer/customer name extracted from the invoice | Compared with verified invoice field; extraction accuracy measure |
| `buyer_gstin` | Buyer GSTIN value extracted from the invoice | Compared with verified invoice field; extraction accuracy measure |
| `po_number` | Purchase-order reference extracted from the invoice | Compared with verified invoice field; extraction accuracy measure |
| `subtotal` | Invoice subtotal before applicable tax | Numeric field used for extraction and reconciliation checks |
| `tax_amount` | Tax amount represented on the invoice | Numeric field used for extraction and tax reconciliation |
| `total_amount` | Final invoice total | Numeric field used for extraction accuracy and invoice-total acceptance testing |

The project testing report explicitly tracks these ten invoice fields and reports extraction accuracy for each; the current evaluation result is 100% for the listed fields on the 50-invoice review dataset.

## 3. Verification and Ground-Truth Concepts

| Concept | Description |
|---|---|
| Verified invoice fields | Human-verified ground-truth values used to compare against extracted invoice values |
| Human verification rate | Proportion of evaluation invoices available/verified for the evaluation workflow |
| Invoice evaluation record | One invoice-level record in `50_invoice_review.csv` |
| Extraction accuracy | Match rate between extracted values and the corresponding verified values |

The testing report records 50/50 invoices as verified and a 100% verification rate.

## 4. Compliance Data Elements

| Data element / concept | Description |
|---|---|
| Required-field validation | Checks that configured mandatory invoice fields are present |
| GSTIN structure validation | Checks the configured GSTIN-format rule |
| Amount reconciliation | Checks numerical consistency of invoice amount components |
| Tax reconciliation | Checks consistency of tax-related amounts |
| Line-item reconciliation | Checks consistency between line items and invoice totals where available |
| Purchase-order reference validation | Checks the configured purchase-order reference condition |
| Compliance status | Result produced by the configured validation checks |
| Compliance failure rule | Rule identifier associated with a failed compliance check |

The project testing report states that deterministic validation covers required fields, GSTIN structure, amount reconciliation, tax reconciliation, line-item reconciliation, and purchase-order reference.

## 5. Compliance Evaluation Summary

For the verified 50-invoice compliance evaluation:

| Metric | Value |
|---|---:|
| Invoice count | 50 |
| Compliance pass checks | 450 |
| Compliance warning checks | 0 |
| Compliance failed checks | 50 |
| Failure rule | `buyer_gstin_format` |

These figures are from the project's verified `invoice_quality_summary.csv` evaluation output used for the Compliance Alerts Power BI page.

## 6. Confidence and Quality Metrics

| Metric | Meaning |
|---|---|
| Confidence score | Confidence value associated with the evaluated document/extraction result |
| Average confidence score | Mean confidence across the evaluated invoices |
| High-confidence invoices | Count of invoices meeting the project's high-confidence classification |
| Medium-confidence invoices | Count of invoices meeting the project's medium-confidence classification |
| Low-confidence invoices | Count of invoices meeting the project's low-confidence classification |
| Missing-confidence invoices | Count of invoices without a confidence value |

The verified evaluation summary reports an average confidence score of 0.96 across 50 invoices, with all 50 classified as high confidence.

## 7. MLOps / Monitoring Artifacts

| Artifact | Purpose |
|---|---|
| `DocuMind_AI_Invoice_Evaluation` | MLflow experiment used for project evaluation and MLOps tracking |
| `drift_report.csv` | Output of the PSI-based drift detection workflow |
| `retraining_trigger.txt` | Workflow handoff marker used by the automated retraining-trigger process |
| `automated_retraining` MLflow run | Records the retraining-trigger workflow execution |

The current implementation demonstrates drift detection and an automated retraining-trigger workflow; it does not claim that a new supervised extraction model was actually trained.

## 8. Evaluation and Governance Artifacts

| Artifact | Purpose |
|---|---|
| `evaluation/50_invoice_review.csv` | Primary 50-invoice evaluation dataset |
| `evaluation/results/invoice_quality_summary.csv` | Invoice quality and compliance summary metrics |
| `evaluation/results/invoice_quality_report.json` | Detailed invoice quality evaluation report |
| `evaluation/results/invoice_quality_invoice_results.csv` | Invoice-level evaluation results |
| `evaluation/results/multilingual_ocr_summary.csv` | Multilingual OCR evaluation summary |
| `evaluation/results/handwritten_ocr_report.json` | Handwritten OCR evaluation output |
| Power BI dashboard | Processing, accuracy, compliance, and summary reporting |
| Testing & Governance report | Test results, governance status, lineage, and evidence references |

## 9. Data Lineage

```text
Document Upload
      ↓
OCR / Text Extraction
      ↓
AI / NLP Document Processing
      ↓
Structured Invoice Fields
      ↓
Validation & Confidence Checks
      ↓
Database / Evaluation Dataset
      ↓
Human Verification
      ↓
Power BI Dashboard
      ↓
Accuracy / Compliance / Audit Reporting
```

This lineage is the workflow documented in the project's Testing & Governance report.

## 10. Governance Notes

- **Source of evaluation truth:** 50-invoice review dataset with verified invoice fields.
- **Primary evaluation purpose:** compare extracted invoice values against verified values and report accuracy.
- **Human verification:** documented as 50/50 verified in the current evaluation.
- **Compliance:** deterministic validation rules are used for configured invoice checks.
- **Auditability:** processing and verification activity is intended to be traceable through application/audit information.
- **RBAC:** Admin, Employee, and Auditor roles are implemented; Admin-only user-management endpoints are protected by role guards.
- **Multilingual/handwritten scope:** evaluated with limitations and should not be represented as universally high-accuracy capabilities.
- **MLOps limitation:** the current workflow demonstrates drift detection and retraining-trigger handoff rather than verified model replacement.

## 11. Schema Note

This document records the business fields and governance concepts that are explicitly documented in the project materials. Exact physical CSV column names, database column types, and nullable constraints are not expanded beyond what is explicitly supported by the available project documentation; no unverified schema details are intentionally invented.

## 12. Governance Pack Status

| Governance item | Status |
|---|---|
| Data dictionary | Completed |
| Data lineage | Documented |
| Compliance checklist | Documented in project governance materials |
| Testing report | Completed |
| Power BI evidence | Completed for required dashboard views |
| MLflow evidence | Available |
