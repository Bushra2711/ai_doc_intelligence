from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any

from app.services.mlops import tracked_run, log_metrics


DEFAULT_PSI_THRESHOLD = 0.20
DEFAULT_PERFORMANCE_DROP_THRESHOLD = 0.05


def _quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        raise ValueError("Cannot calculate a quantile for an empty sample.")
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * weight


def _bin_edges(reference: list[float], bins: int) -> list[float]:
    values = sorted(float(v) for v in reference)
    if not values:
        raise ValueError("Reference sample cannot be empty.")
    quantile_edges = [_quantile(values, i / bins) for i in range(bins + 1)]
    unique_edges = sorted(set(quantile_edges))
    if len(unique_edges) == 1:
        value = unique_edges[0]
        epsilon = max(abs(value) * 1e-6, 1e-6)
        return [value - epsilon, value + epsilon]
    return unique_edges


def _histogram(values: list[float], edges: list[float]) -> list[float]:
    counts = [0] * (len(edges) - 1)
    for value in values:
        if value <= edges[0]:
            index = 0
        elif value >= edges[-1]:
            index = len(counts) - 1
        else:
            index = 0
            while index < len(edges) - 2 and value > edges[index + 1]:
                index += 1
        counts[index] += 1
    total = len(values)
    return [count / total for count in counts]


def population_stability_index(
    reference: list[float],
    current: list[float],
    bins: int = 10,
    epsilon: float = 1e-6,
) -> float:
    """Calculate PSI between a reference distribution and a current distribution."""
    if not reference or not current:
        raise ValueError("Both reference and current samples are required.")
    if bins < 2:
        raise ValueError("bins must be at least 2.")

    edges = _bin_edges(reference, bins)
    reference_pct = _histogram([float(v) for v in reference], edges)
    current_pct = _histogram([float(v) for v in current], edges)

    psi = 0.0
    for expected, actual in zip(reference_pct, current_pct):
        expected = max(expected, epsilon)
        actual = max(actual, epsilon)
        psi += (actual - expected) * math.log(actual / expected)
    return round(psi, 6)


def metric_drop(reference: float, current: float) -> float:
    """Return absolute performance drop, clipped at zero."""
    return round(max(0.0, float(reference) - float(current)), 6)


def assess_drift(
    reference_features: dict[str, list[float]],
    current_features: dict[str, list[float]],
    *,
    psi_threshold: float = DEFAULT_PSI_THRESHOLD,
) -> dict[str, Any]:
    """Assess feature-distribution drift using PSI."""
    feature_results: dict[str, Any] = {}
    drifted_features: list[str] = []

    for feature, reference_values in reference_features.items():
        current_values = current_features.get(feature)
        if current_values is None:
            continue
        psi = population_stability_index(reference_values, current_values)
        drifted = psi >= psi_threshold
        feature_results[feature] = {
            "psi": psi,
            "threshold": psi_threshold,
            "drift_detected": drifted,
        }
        if drifted:
            drifted_features.append(feature)

    return {
        "method": "Population Stability Index (PSI)",
        "threshold": psi_threshold,
        "features": feature_results,
        "drift_detected": bool(drifted_features),
        "drifted_features": drifted_features,
    }


def evaluate_retraining_trigger(
    drift_report: dict[str, Any],
    *,
    reference_metrics: dict[str, float] | None = None,
    current_metrics: dict[str, float] | None = None,
    performance_drop_threshold: float = DEFAULT_PERFORMANCE_DROP_THRESHOLD,
) -> dict[str, Any]:
    """Convert drift/performance degradation into a machine-readable retraining decision."""
    reference_metrics = reference_metrics or {}
    current_metrics = current_metrics or {}

    metric_results: dict[str, Any] = {}
    degraded_metrics: list[str] = []

    for metric, reference_value in reference_metrics.items():
        if metric not in current_metrics:
            continue
        drop = metric_drop(reference_value, current_metrics[metric])
        degraded = drop >= performance_drop_threshold
        metric_results[metric] = {
            "reference": float(reference_value),
            "current": float(current_metrics[metric]),
            "drop": drop,
            "threshold": performance_drop_threshold,
            "degradation_detected": degraded,
        }
        if degraded:
            degraded_metrics.append(metric)

    triggered = bool(drift_report.get("drift_detected") or degraded_metrics)
    reasons: list[str] = []
    if drift_report.get("drift_detected"):
        reasons.append(
            "feature_distribution_drift:" + ",".join(drift_report.get("drifted_features", []))
        )
    if degraded_metrics:
        reasons.append("performance_degradation:" + ",".join(degraded_metrics))

    return {
        "retraining_triggered": triggered,
        "reasons": reasons,
        "drift": drift_report,
        "metrics": metric_results,
        "performance_drop_threshold": performance_drop_threshold,
    }


def persist_retraining_trigger(
    decision: dict[str, Any],
    path: str | Path | None = None,
) -> str | None:
    """Persist a retraining request when monitoring crosses a configured threshold."""
    if not decision["retraining_triggered"]:
        return None

    target = Path(path or os.getenv("RETRAINING_TRIGGER_PATH", "mlops/retraining_trigger.json"))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {
                "status": "RETRAINING_REQUIRED",
                "decision": decision,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return str(target)


def run_drift_monitor(
    reference_features: dict[str, list[float]],
    current_features: dict[str, list[float]],
    *,
    reference_metrics: dict[str, float] | None = None,
    current_metrics: dict[str, float] | None = None,
    psi_threshold: float = DEFAULT_PSI_THRESHOLD,
    performance_drop_threshold: float = DEFAULT_PERFORMANCE_DROP_THRESHOLD,
    persist_trigger: bool = True,
) -> dict[str, Any]:
    """Run drift detection, log monitoring metrics to MLflow, and trigger retraining."""
    drift_report = assess_drift(
        reference_features,
        current_features,
        psi_threshold=psi_threshold,
    )
    decision = evaluate_retraining_trigger(
        drift_report,
        reference_metrics=reference_metrics,
        current_metrics=current_metrics,
        performance_drop_threshold=performance_drop_threshold,
    )

    psi_metrics = {
        f"psi_{feature}": float(result["psi"])
        for feature, result in drift_report["features"].items()
    }
    metric_values = {
        f"metric_drop_{metric}": float(result["drop"])
        for metric, result in decision["metrics"].items()
    }

    with tracked_run(
        "documind-drift-monitor",
        params={
            "psi_threshold": psi_threshold,
            "performance_drop_threshold": performance_drop_threshold,
        },
    ):
        log_metrics(
            {
                **psi_metrics,
                **metric_values,
                "drift_detected": float(drift_report["drift_detected"]),
                "retraining_triggered": float(decision["retraining_triggered"]),
            }
        )

    if persist_trigger:
        decision["trigger_artifact"] = persist_retraining_trigger(decision)
    else:
        decision["trigger_artifact"] = None

    return decision


if __name__ == "__main__":
    reference = {
        "extraction_accuracy": [0.98, 0.99, 1.0, 0.99, 0.98, 1.0, 0.99, 0.98],
        "confidence": [0.94, 0.95, 0.96, 0.97, 0.95, 0.96, 0.94, 0.97],
    }
    current = {
        "extraction_accuracy": [0.72, 0.75, 0.78, 0.74, 0.76, 0.73, 0.77, 0.75],
        "confidence": [0.81, 0.79, 0.82, 0.80, 0.78, 0.81, 0.80, 0.79],
    }
    result = run_drift_monitor(
        reference,
        current,
        reference_metrics={"extraction_accuracy": 1.0, "confidence": 0.96},
        current_metrics={"extraction_accuracy": 0.75, "confidence": 0.80},
    )
    print(json.dumps(result, indent=2))
