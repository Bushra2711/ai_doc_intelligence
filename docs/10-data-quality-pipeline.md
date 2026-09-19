# Step 10 - Data Quality Pipeline

DocuMind AI evaluates invoice extraction quality across completeness, validity, reconciliation, line items and tax structure. The quality score is normalized to 0-1 and classified as GOOD (>=90%), REVIEW (>=70%) or POOR.

This layer is separate from compliance: compliance answers whether business rules pass, while data quality answers whether extracted data is sufficiently complete and internally consistent for downstream analytics.
