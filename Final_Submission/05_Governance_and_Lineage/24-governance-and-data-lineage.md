# Governance and Data Lineage

## Purpose
This document defines governance controls and end-to-end data lineage for the DocuMind AI document intelligence platform.

## End-to-End Data Lineage
Document Source -> File Upload/Ingestion -> Metadata -> Document Storage -> Native Text Extraction or OCR -> Document Classification -> AI/LLM Analysis -> Structured Fields and Line Items -> Compliance Validation -> Confidence/Data Quality Scoring -> Audit Trail -> Application UI / Analytics -> Power BI Dashboard.

## Data Inventory
| Data category | Examples | Purpose | Control |
|---|---|---|---|
| Document content | PDF, DOCX, JPG, PNG | Source processing | File type and size validation |
| File metadata | filename, type, size, timestamp, user | Traceability | Audit/access controls |
| Extracted text | OCR/native text | AI analysis | Processing pipeline |
| Structured fields | invoice number, date, GSTIN, amounts, PO | Business processing | Validation rules |
| Compliance results | PASS/WARNING/FAIL | Compliance assessment | Rule validation |
| Confidence | extraction/document confidence | Quality monitoring | Confidence scoring |
| Processing metrics | status, processing time | Performance monitoring | Analytics |
| Audit events | action, document, status, timestamp | Accountability | Audit logging |
| BI metrics | accuracy, OCR retention, confidence, compliance | Reporting | Power BI dataset |

## Governance Controls
- Authentication protects application APIs.
- Role-based access control is implemented for application operations.
- Document operations are recorded in the audit trail with action, document context, status and timestamp.
- Required fields, GSTIN format, amount reconciliation, tax reconciliation, line-item reconciliation and PO reference checks are part of validation.
- Confidence scoring provides quality monitoring.
- Evaluation ground truth is kept separate from application logic.
- Power BI metrics are sourced from evaluation artifacts; values are not manually invented.

## Traceability
For an evaluated invoice: source invoice -> ingestion metadata -> extracted/OCR text -> structured invoice fields -> compliance checks -> confidence score -> audit event -> BI/evaluation metric.

## Current Evidence
- docs/08-audit-trail.md
- docs/09-role-based-access-control.md
- docs/10-data-quality-pipeline.md
- docs/05-compliance-and-validation.md
- docs/06-confidence-scoring.md
- docs/07-dashboard-kpi-analytics.md
- docs/23-powerbi-dashboard-evidence.md
- evaluation/powerbi_dashboard_data.csv

## Limitations
The current evidence is primarily based on synthetic GST-style invoices and controlled evaluation samples. Production retention automation, enterprise data catalog integration, cloud governance controls, formal automated lineage tooling and organization-specific privacy policies are not claimed as implemented.
