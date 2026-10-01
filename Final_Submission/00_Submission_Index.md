# Final Submission Index

This folder is organized around the required industry-project submission components and the project's actual evidence.

| Submission component | Location in Final_Submission | Current state |
|---|---|---|
| Data Analytics Repository | `00_Data_Analytics_Repository` + repository root | Source code remains at repository root; submission folder contains the repository map |
| Project Report | `01_Project_Report` | Report summary and upload instructions are present; final DOCX/PDF still need to be added from the local submission package |
| Power BI Dashboard | `02_PowerBI_Dashboard` | PBIX artifacts and BI-ready dataset copied |
| Evaluation Reports | `03_Evaluation_Reports` | Core documented reports copied; final machine-readable result files still need to be added from the executed local evaluation results where available |
| Testing Documents | `04_Testing_Documents` | Test design, cases, scenarios and evidence report copied |
| Governance / Data Lineage | `05_Governance_and_Lineage` | Governance, lineage, checklist and data dictionary copied |
| MLOps / Explainability | `06_MLOps_and_Explainability` | MLflow, SHAP, domain-adaptation, drift and retraining-trigger evidence copied |
| Deployment Evidence | `07_Deployment_Evidence` | Docker/Kubernetes configuration copied; live runtime evidence must be added only after actual execution |
| Execution Video | `08_Execution_Video` | Instructions present; final video must be supplied externally because the recorded MP4 is larger than GitHub's normal single-file limit |
| Supplementary Evidence | `09_Supplementary_Artifacts` | Final readiness, completion matrix and verification notes copied |

## Required local files to add

### 1. Final project report
Copy into `Final_Submission/01_Project_Report/`:
- `DocuMind_AI_Final_Project_Report.docx`
- `DocuMind_AI_Final_Project_Report.pdf`

### 2. Evaluation result artifacts
From the locally generated `evaluation/results/` directory, add the final executed reports that correspond to the submitted evaluation run, especially:
- invoice accuracy result/report
- OCR retention result/report
- invoice quality/confidence result/report
- processing-time result/report
- multilingual OCR report
- handwritten OCR report

### 3. Execution video
Use the already prepared:
- `DocuMind_AI_Final_Execution_Video.mp4`

Keep the video in the institute/company's approved external storage if it exceeds GitHub's file-size limit, and place the share link in the final submission notes.

### 4. Runtime evidence
Add only actual execution proof:
- Azure deployment screenshot + working URL, if Azure was deployed
- Kubernetes rollout screenshot/log, if Kubernetes was deployed
- Power BI Service publish/refresh screenshot, if actually performed
- MLflow/SHAP/Docker screenshots when required as evidence

## Do not submit

Do not copy temporary/debug artifacts such as:
- `build-error.txt`
- `*.bak`
- local `mlflow.db`
- unrelated screen recordings
- duplicate experimental outputs

## Final report metadata

Before submitting the report, fill the approved:
- Start Date
- End Date
- Total Effort (hours)
- Company/sponsoring organization name, if required
- Institute name, if required

These fields must come from the official project record and should not be invented.