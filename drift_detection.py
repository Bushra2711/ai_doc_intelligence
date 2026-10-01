import pandas as pd
import numpy as np
from pathlib import Path
import mlflow
from datetime import datetime

# =========================
# Configuration
# =========================

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "evaluation" / "50_invoice_review.csv"

MLFLOW_URI = "http://127.0.0.1:5000"
EXPERIMENT_NAME = "DocuMind_AI_Invoice_Evaluation"

PSI_THRESHOLD = 0.20


# =========================
# PSI Calculation
# =========================

def calculate_psi(expected, actual, bins=10):

    expected = pd.Series(expected).dropna().astype(float)
    actual = pd.Series(actual).dropna().astype(float)

    if len(expected) < 2 or len(actual) < 2:
        return 0.0

    min_value = min(expected.min(), actual.min())
    max_value = max(expected.max(), actual.max())

    if min_value == max_value:
        return 0.0

    edges = np.linspace(min_value, max_value, bins + 1)

    expected_counts, _ = np.histogram(expected, bins=edges)
    actual_counts, _ = np.histogram(actual, bins=edges)

    expected_pct = expected_counts / len(expected)
    actual_pct = actual_counts / len(actual)

    expected_pct = np.where(expected_pct == 0, 0.0001, expected_pct)
    actual_pct = np.where(actual_pct == 0, 0.0001, actual_pct)

    psi = np.sum(
        (actual_pct - expected_pct)
        * np.log(actual_pct / expected_pct)
    )

    return float(psi)


# =========================
# Load Dataset
# =========================

print("\n======================================")
print("DocuMind AI - Drift Detection")
print("======================================")

print(f"\nDataset: {DATA_FILE}")

df = pd.read_csv(DATA_FILE)

print(f"Total records: {len(df)}")

if len(df) < 10:
    raise ValueError("Not enough records for drift detection.")


# =========================
# Split Baseline / Current
# =========================

split_index = int(len(df) * 0.7)

baseline = df.iloc[:split_index].copy()
current = df.iloc[split_index:].copy()

print(f"Baseline records: {len(baseline)}")
print(f"Current records: {len(current)}")


# =========================
# Numeric Features
# =========================

numeric_columns = df.select_dtypes(
    include=[np.number]
).columns.tolist()

print("\nNumeric features detected:")

for column in numeric_columns:
    print(f" - {column}")


# =========================
# Drift Detection
# =========================

drift_results = []

for column in numeric_columns:

    psi = calculate_psi(
        baseline[column],
        current[column]
    )

    drift_status = (
        "DRIFT_DETECTED"
        if psi >= PSI_THRESHOLD
        else "NO_DRIFT"
    )

    drift_results.append({
        "feature": column,
        "psi": psi,
        "status": drift_status
    })

    print(
        f"{column}: PSI={psi:.4f} -> {drift_status}"
    )


# =========================
# Overall Result
# =========================

drifted_features = [
    r for r in drift_results
    if r["status"] == "DRIFT_DETECTED"
]

drift_detected = len(drifted_features) > 0


# =========================
# MLflow Logging
# =========================

mlflow.set_tracking_uri(MLFLOW_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

with mlflow.start_run(run_name="drift_detection"):

    mlflow.log_param(
        "dataset",
        "50_invoice_review.csv"
    )

    mlflow.log_param(
        "baseline_records",
        len(baseline)
    )

    mlflow.log_param(
        "current_records",
        len(current)
    )

    mlflow.log_param(
        "psi_threshold",
        PSI_THRESHOLD
    )

    mlflow.log_param(
        "drift_detected",
        drift_detected
    )

    for result in drift_results:
        mlflow.log_metric(
            f"psi_{result['feature']}",
            result["psi"]
        )


# =========================
# Automated Retraining Trigger
# =========================

trigger_file = BASE_DIR / "retraining_trigger.txt"

if drift_detected:

    trigger_file.write_text(
        "RETRAINING REQUIRED\n"
        f"Timestamp: {datetime.now().isoformat()}\n"
        f"Drifted features: "
        f"{', '.join(r['feature'] for r in drifted_features)}\n"
    )

    print("\n⚠ DRIFT DETECTED")
    print("Automated retraining trigger created:")
    print(trigger_file)

else:

    if trigger_file.exists():
        trigger_file.unlink()

    print("\n✓ NO SIGNIFICANT DRIFT DETECTED")
    print("Model can continue using current configuration.")


# =========================
# Save Report
# =========================

report_file = BASE_DIR / "drift_report.csv"

pd.DataFrame(drift_results).to_csv(
    report_file,
    index=False
)

print("\nDrift report saved:")
print(report_file)

print("\n======================================")
print("Drift Detection Completed")
print("======================================")