from __future__ import annotations

from math import isclose
from typing import Any


DEFAULT_FIELDS = (
    "invoice_number",
    "invoice_date",
    "vendor_name",
    "vendor_gstin",
    "buyer_name",
    "buyer_gstin",
    "subtotal",
    "tax_amount",
    "total_amount",
    "po_number",
)


def _normalize(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().lower().split())


def _matches(predicted: Any, expected: Any) -> bool:
    if predicted is None or expected is None:
        return predicted is None and expected is None

    if isinstance(predicted, (int, float)) and isinstance(expected, (int, float)):
        return isclose(float(predicted), float(expected), rel_tol=0.0, abs_tol=0.01)

    return _normalize(predicted) == _normalize(expected)


def evaluate_invoice_accuracy(
    predicted: dict[str, Any],
    expected: dict[str, Any],
    fields: tuple[str, ...] = DEFAULT_FIELDS,
) -> dict[str, Any]:
    """Compare extracted invoice fields against human-verified ground truth.

    Accuracy is calculated at field level. A missing expected field is not
    silently treated as correct; it is reported as a mismatch when a field is
    included in the evaluation set.
    """
    results: dict[str, dict[str, Any]] = {}
    correct = 0

    for field in fields:
        predicted_value = predicted.get(field)
        expected_value = expected.get(field)
        matched = _matches(predicted_value, expected_value)
        if matched:
            correct += 1
        results[field] = {
            "predicted": predicted_value,
            "expected": expected_value,
            "match": matched,
        }

    total = len(fields)
    accuracy = round((correct / total) * 100, 2) if total else 0.0
    return {
        "accuracy_percent": accuracy,
        "correct_fields": correct,
        "total_fields": total,
        "field_results": results,
    }
