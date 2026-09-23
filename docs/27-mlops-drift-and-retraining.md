# MLOps: MLflow, Drift Detection and Automated Retraining Trigger

## Objective

This document provides execution-ready MLOps evidence for three TCS requirements:

1. experiment/metric tracking with MLflow;
2. feature and performance drift detection;
3. an automated, machine-readable retraining trigger when configured thresholds are crossed.

## MLflow tracking

DocuMind AI already includes an MLflow tracking service in Docker Compose. The backend MLOps helper now:

- reads `MLFLOW_TRACKING_URI` when supplied;
- activates the `DocuMind AI` experiment by default;
- logs parameters and metrics inside named runs;
- remains usable when MLflow is unavailable, so document processing is not coupled to the tracking server.

MLflow supports configuring a tracking URI and experiment, then logging parameters and metrics in a run. See the official MLflow tracking API documentation.

## Drift detection

The monitoring service uses **Population Stability Index (PSI)** to compare a reference distribution with a current distribution.

Default policy:

| Control | Default |
|---|---:|
| PSI drift threshold | 0.20 |
| Performance degradation threshold | 0.05 |

The implementation reports PSI per monitored feature and identifies which features crossed the threshold.

For this project, suitable monitored signals include:

- extraction accuracy;
- invoice confidence;
- other numeric quality/model-monitoring signals added later.

These thresholds are monitoring policy defaults, not evidence that a production population has already drifted.

## Automated retraining trigger

A retraining request is generated when either:

- at least one monitored feature has PSI >= 0.20; or
- a configured performance metric drops by >= 0.05 from its reference value.

The trigger is persisted as:

`mlops/retraining_trigger.json`

or the path configured through `RETRAINING_TRIGGER_PATH`.

The artifact is intentionally a **trigger**, not an automatic model replacement. A production training pipeline can consume this artifact and start a controlled retraining/evaluation/deployment workflow.

## Verification

From the backend directory:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest -q tests/test_mlops_monitoring.py
python -m app.services.drift_monitor
```

The demo intentionally uses a shifted current distribution and reduced metrics, so it should produce:

- `drift_detected: true`;
- `retraining_triggered: true`;
- reasons for feature drift and performance degradation;
- a `mlops/retraining_trigger.json` artifact.

If MLflow is running locally on port 5000:

```powershell
$env:MLFLOW_TRACKING_URI="http://127.0.0.1:5000"
python -m app.services.drift_monitor
```

Then inspect the MLflow UI at `http://127.0.0.1:5000` and look for the `DocuMind AI` experiment and `documind-drift-monitor` run.

## Evidence interpretation

A successful demo proves the monitoring and trigger mechanism. It does **not** prove that the production invoice population has drifted, nor that a retrained model has been deployed.

## TCS mapping

| TCS MLOps requirement | Repository evidence |
|---|---|
| MLflow experiment tracking | `backend/app/services/mlops.py`, Docker Compose MLflow service |
| Drift detection | `backend/app/services/drift_monitor.py` using PSI |
| Threshold-based monitoring | PSI 0.20 and performance-drop 0.05 defaults |
| Automated retraining trigger | `evaluate_retraining_trigger()` + trigger JSON artifact |
| Test evidence | `backend/tests/test_mlops_monitoring.py` |
| Execution evidence | Run the verification commands above |
