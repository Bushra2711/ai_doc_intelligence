# Final Submission Status

## Ready in GitHub

- Structured final submission folders 00-09
- Submission index
- Project-document summary
- Native Power BI PBIX artifacts
- BI-ready dataset
- Evaluation documentation
- Testing documents
- Governance/data-lineage/checklist
- Data dictionary
- MLflow/SHAP/domain-adaptation/drift/retraining evidence
- Docker/Kubernetes configuration
- Final TCS readiness/completion/verification documents

## Still required from the local/external submission package

### A. Final project report binaries
Place in:
`Final_Submission/01_Project_Report/`

Files:
- `DocuMind_AI_Final_Project_Report.docx`
- `DocuMind_AI_Final_Project_Report.pdf`

### B. Machine-readable evaluation results
Place in:
`Final_Submission/03_Evaluation_Reports/`

Copy the final executed files from the local `evaluation/results/` directory, especially the invoice accuracy, OCR, invoice-quality/confidence, processing-time, multilingual and handwritten reports.

### C. Final execution video
Place/link through:
`Final_Submission/08_Execution_Video/`

File:
`DocuMind_AI_Final_Execution_Video.mp4`

The current final MP4 is approximately 199 MB, so it should normally be hosted in approved external storage rather than committed as a normal GitHub file. Put the share link in the video submission notes.

### D. Runtime evidence
Place in:
`Final_Submission/07_Deployment_Evidence/`

Only after actual execution:
- live Azure deployment screenshot/URL, if Azure deployment was completed;
- live Kubernetes rollout screenshot/log, if Kubernetes was completed;
- Power BI Service publish/refresh evidence, if actually executed.

### E. Report cover metadata
Update the report before submission using the official record:
- company/sponsoring organization
- institute
- start date
- end date
- total effort in hours

## Temporary files to exclude

Do not submit:
- `build-error.txt`
- `*.bak`
- local `mlflow.db`
- unrelated intermediate screen recordings
- stale/duplicate evaluation outputs

## Evidence rule

Only include artifacts that correspond to an actual execution or an explicitly documented project result.