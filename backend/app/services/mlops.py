from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

try:
    import mlflow
except ImportError:  # pragma: no cover
    mlflow = None


@contextmanager
def tracked_run(run_name: str, params: dict[str, Any] | None = None) -> Iterator[None]:
    """Track an experiment when MLflow is available; remain usable without the server."""
    if mlflow is None:
        yield
        return
    with mlflow.start_run(run_name=run_name):
        if params:
            mlflow.log_params(params)
        yield


def log_metrics(metrics: dict[str, float]) -> None:
    if mlflow is not None:
        mlflow.log_metrics(metrics)
