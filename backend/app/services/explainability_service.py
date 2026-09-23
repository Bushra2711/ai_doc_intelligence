from __future__ import annotations

from typing import Any
import numpy as np
import shap
from sklearn.ensemble import RandomForestClassifier

FEATURES = (
    "invoice_number_present", "invoice_date_present", "vendor_present",
    "buyer_present", "vendor_gstin_valid", "buyer_gstin_valid",
    "amount_reconciled", "tax_reconciled", "line_items_reconciled",
    "po_reference_present",
)

def _present(value: Any) -> float:
    return 1.0 if value not in (None, "", "N/A") else 0.0

def _gstin_valid(value: Any) -> float:
    import re
    if not value:
        return 0.0
    pattern = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")
    return 1.0 if pattern.fullmatch(str(value).strip().upper()) else 0.0

def _number(value: Any) -> float | None:
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None

def _invoice_features(fields: dict[str, Any]) -> np.ndarray:
    subtotal = _number(fields.get("subtotal"))
    tax = _number(fields.get("tax_amount"))
    total = _number(fields.get("total_amount"))
    amount_reconciled = 1.0 if (
        subtotal is not None and tax is not None and total is not None
        and abs((subtotal + tax) - total) <= 0.01
    ) else 0.0
    breakdown = fields.get("tax_breakdown") or []
    breakdown_total = sum((_number(item.get("amount")) or 0.0) for item in breakdown)
    tax_reconciled = 1.0 if (
        breakdown and tax is not None and abs(breakdown_total - tax) <= 0.01
    ) else 0.0
    line_items = fields.get("line_items") or []
    items_total = sum((_number(item.get("amount")) or 0.0) for item in line_items)
    line_items_reconciled = 1.0 if (
        line_items and subtotal is not None and abs(items_total - subtotal) <= 0.01
    ) else 0.0
    return np.array([[
        _present(fields.get("invoice_number")), _present(fields.get("invoice_date")),
        _present(fields.get("vendor_name")), _present(fields.get("buyer_name")),
        _gstin_valid(fields.get("vendor_gstin")), _gstin_valid(fields.get("buyer_gstin")),
        amount_reconciled, tax_reconciled, line_items_reconciled,
        _present(fields.get("po_number")),
    ]], dtype=float)

def _surrogate_training_data() -> tuple[np.ndarray, np.ndarray]:
    rows, labels = [], []
    for mask in range(1, 1 << len(FEATURES)):
        row = [(mask >> i) & 1 for i in range(len(FEATURES))]
        critical = row[0] and row[1] and row[2] and row[4] and row[5] and row[6]
        rows.append(row)
        labels.append(1 if critical else 0)
    return np.asarray(rows, dtype=float), np.asarray(labels, dtype=int)

def explain_invoice_validation(fields: dict[str, Any]) -> dict[str, Any]:
    x = _invoice_features(fields)
    train_x, train_y = _surrogate_training_data()
    model = RandomForestClassifier(
        n_estimators=80, random_state=42, max_depth=6, class_weight="balanced"
    )
    model.fit(train_x, train_y)
    probability = float(model.predict_proba(x)[0, 1])
    prediction = "VALIDATION_PASS" if probability >= 0.5 else "VALIDATION_REVIEW"

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(x)
    if isinstance(shap_values, list):
        values = np.asarray(shap_values[-1])[0]
        base_value = float(np.asarray(explainer.expected_value)[-1])
    else:
        values_array = np.asarray(shap_values)
        if values_array.ndim == 3:
            values = values_array[0, :, -1]
            base_value = float(np.asarray(explainer.expected_value)[-1])
        else:
            values = values_array[0]
            base_value = float(np.asarray(explainer.expected_value).reshape(-1)[0])

    reasons = {
        "invoice_number_present": "Invoice number is available for validation.",
        "invoice_date_present": "Invoice date is available for validation.",
        "vendor_present": "Vendor name is available.",
        "buyer_present": "Buyer name is available.",
        "vendor_gstin_valid": "Vendor GSTIN passes the deterministic GSTIN format check.",
        "buyer_gstin_valid": "Buyer GSTIN passes the deterministic GSTIN format check.",
        "amount_reconciled": "Subtotal, tax, and total amounts reconcile within tolerance.",
        "tax_reconciled": "Tax breakdown reconciles with the extracted tax amount.",
        "line_items_reconciled": "Line-item amounts reconcile with the subtotal.",
        "po_reference_present": "Purchase-order reference is available.",
    }
    features = []
    for index, name in enumerate(FEATURES):
        contribution = float(values[index])
        features.append({
            "feature": name,
            "value": float(x[0, index]),
            "contribution": round(contribution, 6),
            "direction": "supports" if contribution >= 0 else "reduces",
            "reason": reasons[name],
        })
    features.sort(key=lambda item: abs(item["contribution"]), reverse=True)
    return {
        "method": "SHAP TreeExplainer",
        "model_layer": "deterministic invoice validation surrogate",
        "prediction": prediction,
        "confidence": round(max(probability, 1 - probability), 4),
        "base_value": round(base_value, 6),
        "features": features,
        "explanation": "SHAP contributions show how each invoice validation feature moves the validation decision relative to its baseline.",
        "limitation": "SHAP explains the deterministic validation layer, not Gemini's internal LLM reasoning. It is validation-layer explainability, not token-level LLM attribution.",
    }
