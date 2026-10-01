# 00 - Data Analytics Repository

The main GitHub repository is itself the Data Analytics Repository required by the project guideline.

### Core implementation areas

- `backend/` - FastAPI application, database models, document ingestion/processing, invoice extraction, compliance, confidence, audit/RBAC, explainability and MLOps services.
- `frontend/` - React/Vite application.
- `evaluation/` - evaluation scripts, BI-ready dataset and native Power BI artifacts.
- `bi/` - BI templates.
- `k8s/` - Kubernetes deployment manifests.
- `.github/workflows/` - automated backend test/lint workflow.
- `docs/` - project documentation, testing, governance, evaluation and submission evidence.

The project code remains at repository root rather than being duplicated under Final_Submission. This avoids maintaining two copies of the application source.