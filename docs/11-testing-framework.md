# Step 11 - Testing Framework

The backend uses pytest for unit tests and Ruff for static quality checks. Tests cover invoice extraction, compliance, confidence aggregation, ingestion validation, RBAC and data quality.

GitHub Actions runs on pushes and pull requests to main with Python 3.11:
- install backend and dev dependencies
- pytest -q
- ruff check app tests

A workflow run is the authoritative CI verification; code being committed is not itself proof that CI passed.
