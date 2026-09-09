# DocuMind AI - AI-Powered Intelligent Document Processing Platform

DocuMind AI is an enterprise-grade intelligent document processing platform for uploading documents, OCR, classification, extraction, summarization, compliance checks, dashboards, and auditability.

## Initial Architecture

- `backend/` FastAPI service with SQLAlchemy, Alembic, JWT auth, and domain modules
- `frontend/` React + Vite + Tailwind UI
- `infra/` deployment and container artifacts
- `docs/` architecture and delivery documentation

## Step 1 Delivered

- Monorepo scaffold
- Backend service foundation
- Frontend application shell
- Root documentation and container composition baseline

## Run Later

After dependencies are installed, run the backend from `backend/` with `uvicorn app.main:app --reload`, then run the frontend with `npm run dev` from `frontend/`.

Copy `backend/.env.example` to `backend/.env` and provide the database, JWT, and Gemini settings before starting the API.

<!-- ChatGPT Codex Connector write test -->
