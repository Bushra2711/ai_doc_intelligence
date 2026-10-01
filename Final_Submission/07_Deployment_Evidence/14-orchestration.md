# Step 14 - Orchestration

The orchestration service provides named pipeline steps with SUCCESS/FAILED state and exception propagation. It is intentionally lightweight so OCR, extraction, validation, compliance, confidence and persistence can be composed without introducing a heavy scheduler into the request path.

For batch production workloads this interface can later be backed by Celery, Prefect or Airflow without changing the business services.
