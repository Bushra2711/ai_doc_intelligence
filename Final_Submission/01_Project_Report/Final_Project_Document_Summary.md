# DocuMind AI - Final TCS Project Document

## 1. Project Title

**AI-Powered Intelligent Document Processing Platform (DocuMind AI)**

## 2. Project Objective

DocuMind AI is an enterprise-oriented document intelligence platform designed to ingest documents, extract text using native parsing and OCR fallback, classify and analyze documents with an LLM-assisted service, extract structured invoice information, validate business rules, calculate confidence/data-quality indicators, expose audit/RBAC controls, and provide analytics-ready outputs.

The implementation is designed to support the TCS project requirements for document ingestion, AI-based document understanding, structured extraction, compliance validation, MLOps monitoring, explainability, testing/governance, and BI reporting.

## 3. Architecture

The repository contains:

- FastAPI backend for document ingestion and processing APIs.
- React/Vite frontend for document upload and workflow interaction.
- PostgreSQL for application persistence in the containerized stack, with SQLite available as a local fallback.
- ChromaDB for vector-store functionality.
- MLflow for experiment/MLOps tracking.
- Tesseract OCR fallback for scanned/image documents.
- PyMuPDF/python-docx/Pillow based document parsing.
- Power BI dashboard artifact and BI-ready CSV output.
- Docker Compose runtime configuration.
- Kubernetes manifests for namespace, PostgreSQL, ChromaDB, MLflow, backend and frontend services.
- GitHub Actions workflow for backend regression and lint checks.

## 4. Document Flow

1. User uploads a supported document.
2. The ingestion service validates file type and upload-size limits and safely stores the document.
3. Text is extracted from PDF/DOCX/image content.
4. OCR fallback is used where embedded PDF text is unavailable.
5. The analysis service performs document classification and structured AI analysis.
6. Invoice-domain rules validate required fields, GSTIN formats, totals/tax reconciliation, line-item reconciliation and PO references where applicable.
7. Data-quality and confidence services calculate transparent validation indicators.
8. Audit/RBAC controls govern application access.
9. Evaluation and BI outputs feed Power BI reporting.
10. MLflow/drift-monitoring components provide experiment/monitoring evidence and retraining-trigger workflow.

## 5. Evaluation Evidence

The repository records the following project evaluation results:

| Area | Recorded result |
|---|---|
| Invoice extraction | 500/500 field comparisons matched; 100.00% on the evaluated synthetic set |
| OCR information retention | 98.80% business-field information retention across 500 comparisons |
| Processing benchmark | 50/50 successful; mean 0.046s; P95 0.054s |
| Confidence | 50/50 HIGH; average 96.00% |
| Compliance checks | 450 PASS, 0 WARNING, 50 FAIL |
| Automated backend regression | 20/20 passed in the recorded execution evidence |
| Multi-source application paths | Portal, API and Batch runtime paths recorded with HTTP 201 evidence |
| SHAP | Executed for the deterministic invoice-validation surrogate layer |
| MLOps | Drift detection and retraining-trigger workflow recorded with MLflow |

These are evaluation results for the project's available test data and environment. They are not presented as universal production performance guarantees.

## 6. Testing and Governance

Testing documentation covers:

- Test design
- Test cases
- Test scenarios
- Test evidence reporting
- Invoice extraction evaluation
- OCR evaluation
- Processing-time benchmarking
- Confidence and compliance validation
- RBAC and auditability
- Domain adaptation
- Explainability
- MLOps drift monitoring

The governance documentation records data-flow lineage, inventory, RBAC/audit requirements and dashboard metric traceability.

## 7. Power BI Deliverable

The final dashboard artifact is retained separately as a native Power BI PBIX submission artifact. The documented dashboard scope includes:

1. Document Processing Status
2. Extraction Accuracy & Confidence
3. Final Evaluation Data
4. Compliance Alerts
5. Summary Reports

The documented KPI evidence includes 50 evaluated invoices, 100.00% evaluated extraction accuracy on the synthetic ground-truth set, 98.80% OCR information retention, 96.00% average confidence, processing-time benchmark results, and compliance-rule outcomes.

## 8. MLOps and Explainability Boundaries

### MLOps

MLflow experiment tracking and PSI/performance monitoring are implemented. When monitored conditions cross configured thresholds, a retraining trigger is persisted.

This repository does **not** claim automatic replacement of a production model after the trigger.

### Explainability

SHAP TreeExplainer is applied to a deterministic invoice-validation surrogate layer. This explains validation features such as field presence, GSTIN validity, amount/tax reconciliation and related rule features.

It does **not** expose or claim to explain the internal reasoning of the LLM.

### Domain Adaptation

The invoice domain adapter is a versioned schema/rule adaptation layer. It is not evidence of LLM model-weight fine-tuning.

## 9. Deployment Evidence Boundaries

### Verified in repository

- Docker Compose configuration exists for PostgreSQL, ChromaDB, MLflow, backend and frontend.
- Kubernetes manifests exist for the application stack.
- GitHub Actions automation exists for backend tests/linting.

### Not claimed as completed from source code alone

- Live Azure/cloud deployment
- Verified live Kubernetes runtime deployment
- Production BI scheduler/refresh service
- Automatic retrained-model replacement/deployment
- Organization-specific retention/privacy configuration
- Enterprise data catalog or formal automated lineage tooling

These items require execution in an external environment and evidence capture.

## 10. Final Submission Artifacts

The final submission package should contain:

- GitHub repository
- Native Power BI PBIX dashboard
- BI-ready CSV/export artifacts
- Evaluation reports and test evidence
- Project documentation
- Governance/data-lineage documentation
- Execution screenshots
- End-to-end execution video

## 11. Known Limitations

- Primary invoice evaluation data is synthetic.
- OCR result is a business-field information-retention metric.
- Processing times are local benchmark measurements.
- Compliance rules do not establish legal or tax compliance.
- Handwritten OCR evidence is limited to a pilot sample.
- Multilingual evidence is based on a small synthetic bilingual/Hindi sample.
- Multi-source evidence covers application-level Portal/API/Batch ingestion rather than live enterprise connectors.
- Cloud and Kubernetes runtime evidence requires external execution.

## 12. Final Completion Procedure

The project should be considered submission-ready only after the remaining external evidence in the companion completion checklist has been executed and saved with the repository/submission package.
