from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from typing import Any, Iterator

logger = logging.getLogger(__name__)

try:
    import mlflow
except ImportError:  # pragma: no cover
    mlflow = None


DEFAULT_EXPERIMENT_NAME = "DocuMind AI"


def _configure_mlflow() -> None:
    if mlflow is None:
        return

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)

    experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", DEFAULT_EXPERIMENT_NAME)
    mlflow.set_experiment(experiment_name)


@contextmanager
def tracked_run(run_name: str, params: dict[str, Any] | None = None) -> Iterator[None]:
    """Track an experiment when MLflow is available; remain usable without the server."""
    if mlflow is None:
        yield
        return

    try:
        _configure_mlflow()
        run_context = mlflow.start_run(run_name=run_name)
    except Exception:  # pragma: no cover - depends on external MLflow availability
        yield
        return

    with run_context:
        if params:
            try:
                mlflow.log_params(params)
            except Exception as exc:  # pragma: no cover - external tracking failure
                logger.warning("MLflow parameter logging failed: %s", exc)
        yield


def log_metrics(metrics: dict[str, float]) -> None:
    if mlflow is None:
        return
    try:
        mlflow.log_metrics(metrics)
    except Exception as exc:  # pragma: no cover - external tracking failure
        logger.warning("MLflow metric logging failed: %s", exc)
