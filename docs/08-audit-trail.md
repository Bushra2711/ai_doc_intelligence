# Step 8 — Audit Trail and Traceability

## Objective
Provide a persistent, user-scoped audit trail for important workspace write actions so document processing activity is traceable and reviewable.

## Captured information
- Timestamp
- Authenticated user ID
- Action and HTTP operation
- Document ID when available
- Entity type
- Action status
- Human-readable details

## Architecture
Authenticated non-GET API actions are recorded in the `audit_logs` table. The audit API exposes the latest events for the signed-in user and supports filtering by document ID.

Endpoint: `GET /api/v1/audit-logs`

Optional query parameters:
- `document_id` — filter events for one document
- `limit` — 1–100 events, default 50

## UI
The Dashboard contains a Governance → Audit trail panel showing recent events, status, action, details, and timestamp.

## Security
Audit records are filtered by the authenticated user's ID. Users cannot retrieve another user's audit records through the API.

## Migration
Alembic revision `c81a7d4e2f10` creates the audit log table and indexes for user, document, action, and timestamp queries.
