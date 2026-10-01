# Step 15 - AI and Data Governance

## Principles
- Human review for low-confidence or failed-compliance invoices.
- Least-privilege access through Admin, Employee and Auditor roles.
- Auditability of authenticated mutations and role changes.
- Data minimization: retain only fields and source documents needed for the invoice workflow.
- Reproducibility: version code, tests, extraction rules and experiment metrics.
- Security: secrets belong in environment variables, never source control.

## Controls
| Risk | Control |
|---|---|
| OCR/extraction error | Confidence score and data-quality checks |
| Financial inconsistency | Amount/tax/line-item reconciliation |
| Unauthorized access | JWT authentication and RBAC |
| Untraceable changes | Audit log |
| Model/rule regression | pytest, Ruff and CI |
| Experiment drift | MLflow experiment history |

## Review policy
LOW/MISSING confidence, NON_COMPLIANT status, or POOR data quality should route to manual review. Production retention periods and organization-specific privacy requirements must be configured by the deploying organization.
