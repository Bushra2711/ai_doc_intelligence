# Final Verification Notes

## Verified repository capabilities
- Secure multi-format document ingestion with portal/API/batch source tagging.
- PDF text extraction with OCR fallback and image OCR.
- Gemini-based classification/analysis with structured outputs.
- Deterministic invoice extraction and validation.
- Invoice confidence/data-quality scoring.
- Compliance rules and audit trail.
- JWT authentication and Admin/Employee/Auditor RBAC.
- SHAP explainability for the deterministic invoice validation surrogate layer.
- MLflow experiment tracking and PSI/performance drift monitoring.
- Machine-readable retraining trigger generation.
- Backend regression suite and GitHub Actions CI.
- Docker Compose service topology for PostgreSQL, ChromaDB, MLflow, backend, and frontend.
- Kubernetes manifests for the same service boundaries.
- Native Power BI dashboard artifact and BI-ready dataset.

## Explicit evidence boundaries
The repository itself does not verify:
- a successful live Kubernetes rollout;
- a live Azure deployment;
- underlying LLM weight fine-tuning;
- automatic replacement/deployment of a retrained model;
- a production cloud BI refresh scheduler.

Those items remain external-runtime or model-training evidence rather than source-code-only claims.
