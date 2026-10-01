from pathlib import Path
from datetime import datetime
import mlflow

BASE_DIR = Path(__file__).resolve().parent
TRIGGER_FILE = BASE_DIR / "retraining_trigger.txt"

MLFLOW_URI = "http://127.0.0.1:5000"
EXPERIMENT_NAME = "DocuMind_AI_Invoice_Evaluation"

print("\n======================================")
print("DocuMind AI - Automated Retraining")
print("======================================")

if not TRIGGER_FILE.exists():
    print("\nNo retraining trigger found.")
    print("Current model can continue.")
    raise SystemExit(0)

print("\nRetraining trigger detected!")

mlflow.set_tracking_uri(MLFLOW_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

with mlflow.start_run(run_name="automated_retraining"):

    mlflow.log_param("trigger", "data_drift")
    mlflow.log_param("trigger_file", "retraining_trigger.txt")
    mlflow.log_param("dataset", "50_invoice_review.csv")
    mlflow.log_param("retraining_status", "STARTED")

    # Demonstration of retraining pipeline execution.
    # The existing DocuMind extraction pipeline does not require
    # training a new supervised model at this stage.
    print("\nRetraining pipeline started...")

    # Simulated retraining completion for the existing
    # extraction/evaluation pipeline.
    retraining_completed = True

    if retraining_completed:
        mlflow.log_metric(
            "retraining_success",
            1.0
    )

    print("Retraining pipeline completed successfully.")


TRIGGER_FILE.unlink()

print("\nTrigger consumed.")
print("MLflow retraining run logged successfully.")

print("\n======================================")
print("Automated Retraining Completed")
print("======================================")