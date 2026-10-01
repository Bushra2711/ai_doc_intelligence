# Step 7 — Dashboard / KPI Analytics

## Objective
Provide an operational dashboard that turns document-processing activity into measurable KPIs.

## Live KPIs
- Total documents
- Completed documents
- Processing documents
- Pending documents
- Failed documents
- Invoice documents
- Analyzed documents
- Average invoice extraction confidence
- Compliance checks passed / warnings / failed

## Analytics views
- Document status distribution
- Document type distribution
- Seven-day document ingestion trend
- Invoice confidence quality indicator
- Compliance health indicator

## Data scope
All metrics are restricted to the authenticated workspace user. Invoice confidence and compliance metrics are calculated from the structured invoice extraction already implemented in Steps 3–6.

## API
`GET /api/v1/dashboard/metrics`

The endpoint is authenticated and returns KPI totals, status/type distributions, seven-day activity counts, invoice confidence, and compliance totals.

## TCS mapping
This step addresses the dashboard/KPI requirement by exposing measurable operational performance and AI quality indicators rather than only a document list.
