# Step 23 - Power BI Dashboard Evidence

## Native dashboard artifact

A native Power BI Desktop dashboard was created from the consolidated BI-ready dataset:

- Artifact: `AI_Document_Intelligence_Evaluation_Dashboard.pbix`
- Tool: Microsoft Power BI Desktop
- Source dataset: `evaluation/powerbi_dashboard_data.csv`
- Dashboard title: **AI-Powered Intelligent Document Processing — Evaluation Dashboard**

The dashboard contains KPI and evaluation visuals for:

- Invoices evaluated: 50
- Overall extraction accuracy: 100.00%
- Overall OCR field retention: 98.80%
- Average confidence: 96.00%
- Mean processing time: 46.04 ms
- Compliance checks: 450 PASS, 50 FAIL, 0 WARNING
- Invoice compliance status: 50 non-compliant invoices in the evaluated synthetic dataset

## Evidence interpretation

The dashboard is an evaluation/monitoring view of the tested document-processing pipeline. The displayed values are derived from the project's evaluation outputs.

The 100.00% extraction result is specific to the 50 synthetic GST-style invoices evaluated. The OCR metric is business-field information retention, not character-perfect transcription accuracy. The compliance result reflects the application's implemented validation rules and is not a statement of legal or tax compliance.

## Submission handling

The `.pbix` file should be retained with the final submission package because GitHub's text-file workflow does not store the native Power BI binary artifact in this documentation file.
