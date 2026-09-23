from app.services.drift_monitor import (
    assess_drift,
    evaluate_retraining_trigger,
    metric_drop,
    population_stability_index,
)


def test_psi_is_low_for_similar_distributions():
    reference = [0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97]
    current = [0.90, 0.92, 0.91, 0.94, 0.93, 0.95, 0.96, 0.97]

    assert population_stability_index(reference, current) < 0.20


def test_drift_is_detected_for_shifted_distribution():
    reference = [0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97]
    current = [0.55, 0.58, 0.60, 0.62, 0.59, 0.61, 0.57, 0.60]

    report = assess_drift(
        {"confidence": reference},
        {"confidence": current},
    )

    assert report["drift_detected"] is True
    assert report["drifted_features"] == ["confidence"]


def test_retraining_triggered_by_drift_and_metric_degradation():
    decision = evaluate_retraining_trigger(
        {
            "drift_detected": True,
            "drifted_features": ["confidence"],
        },
        reference_metrics={"extraction_accuracy": 1.0},
        current_metrics={"extraction_accuracy": 0.92},
    )

    assert decision["retraining_triggered"] is True
    assert "feature_distribution_drift:confidence" in decision["reasons"]
    assert "performance_degradation:extraction_accuracy" in decision["reasons"]


def test_no_retraining_when_thresholds_are_not_crossed():
    decision = evaluate_retraining_trigger(
        {
            "drift_detected": False,
            "drifted_features": [],
        },
        reference_metrics={"extraction_accuracy": 1.0},
        current_metrics={"extraction_accuracy": 0.97},
    )

    assert decision["retraining_triggered"] is False
    assert decision["reasons"] == []


def test_metric_drop_never_goes_negative():
    assert metric_drop(0.90, 0.95) == 0.0
