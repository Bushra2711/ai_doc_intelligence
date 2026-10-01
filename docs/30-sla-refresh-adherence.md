# SLA and Refresh Adherence Report

## Purpose
This report formalizes the processing-time benchmark and defines the refresh/adherence controls for the DocuMind AI evaluation pipeline.

## Observed benchmark
The repository's 50-invoice digital-PDF benchmark reports:
- 50/50 successful
- Mean processing time: 0.046 s
- Median processing time: 0.045 s
- P95 processing time: 0.054 s
- Minimum: 0.035 s
- Maximum: 0.092 s

These are local benchmark observations for the embedded-text PDF processing path. They exclude upload/network latency and scanned-document OCR fallback.

## Evaluation SLA target
For project-level evaluation, the benchmark is treated as an internal processing-time target rather than a production service-level guarantee:
- Target: P95 document-processing time <= 0.100 s for the evaluated digital-PDF path.
- Observed P95: 0.054 s.
- Observed benchmark adherence: target met for the evaluated 50-document sample.

This target is an evaluation criterion chosen for the project benchmark; it is not an external contractual SLA.

## Refresh adherence
The evaluation/reporting pipeline should be refreshed whenever a new verified evaluation run is produced. The required refresh sequence is:

1. Run the invoice/OCR/compliance/confidence evaluations.
2. Regenerate the evaluation CSV/JSON outputs.
3. Refresh the BI-ready dataset.
4. Open/refresh the native Power BI dashboard.
5. Validate KPI reconciliation against the generated evaluation outputs.
6. Record the evaluation timestamp, dataset version, and report artifact versions.

## Current evidence boundary
The repository contains repeatable evaluation scripts and a native Power BI dashboard artifact, but it does not contain a production BI scheduler or cloud refresh log. Therefore this report distinguishes:
- Verified: repeatable evaluation and local benchmark adherence for the tested sample.
- Not verified: continuous cloud refresh SLA, enterprise scheduler uptime, or production dashboard refresh latency.

## KPI reconciliation checklist
| KPI | Source | Validation |
|---|---|---|
| Invoice extraction accuracy | BI-ready dataset / evaluation outputs | Match regenerated evaluation result |
| OCR field retention | Evaluation output | Match regenerated evaluation result |
| Average confidence | Evaluation output | Match dashboard KPI |
| Compliance PASS/WARNING/FAIL | Evaluation output | Match dashboard counts |
| Processing P95 | Processing-time evaluation | Match benchmark report |

## TCS mapping
This artifact supports the Evaluation Reports requirement for SLA/refresh adherence while explicitly separating local project evidence from production contractual SLA claims.
