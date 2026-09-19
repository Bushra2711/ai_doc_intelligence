# Step 12 - MLflow / MLOps

DocuMind AI includes MLflow integration for experiment tracking. The tracking server is part of Docker Compose and persists experiment artifacts. The backend can wrap extraction/evaluation experiments in tracked runs and log metrics.

Tracked examples include extraction accuracy, confidence and data-quality metrics. This creates an auditable experiment history without coupling core document processing to MLflow availability.
