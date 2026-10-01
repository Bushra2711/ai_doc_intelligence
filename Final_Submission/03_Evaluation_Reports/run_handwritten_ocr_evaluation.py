from __future__ import annotations

import json
import re
from pathlib import Path
from decimal import Decimal, InvalidOperation

from PIL import Image
import pytesseract

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGE_PATH = PROJECT_ROOT / "evaluation" / "handwritten_samples" / "HW-001.jpg"
RESULTS_DIR = PROJECT_ROOT / "evaluation" / "results"

GROUND_TRUTH = {
    "invoice_number": "HW-001",
    "invoice_date": "23-09-2026",
    "vendor": "Kisan hardware",
    "buyer": "Mohammdi Retail",
    "subtotal": "5000.00",
    "tax_amount": "900.00",
    "total_amount": "5900.00",
    "po_number": "PO-1001",
}

def normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())

def normalize_amount(value: str) -> str:
    try:
        return format(Decimal(str(value).replace(",", "").strip()), "f")
    except (InvalidOperation, ValueError):
        return normalize_text(value)

def field_present(field: str, expected: str, ocr_text: str) -> bool:
    text = normalize_text(ocr_text)
    expected_norm = normalize_text(expected)
    if field in {"subtotal", "tax_amount", "total_amount"}:
        return normalize_amount(expected) in text
    return expected_norm in text

def run_ocr(psm: int) -> str:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    image = Image.open(IMAGE_PATH)
    return pytesseract.image_to_string(image, lang="eng", config=f"--psm {psm}")

def evaluate(ocr_text: str) -> dict:
    rows = []
    for field, expected in GROUND_TRUTH.items():
        rows.append({
            "field": field,
            "expected": expected,
            "present_in_ocr": field_present(field, expected, ocr_text),
        })
    correct = sum(row["present_in_ocr"] for row in rows)
    return {
        "fields": len(rows),
        "correct_field_presences": correct,
        "field_presence_accuracy_percent": round(correct / len(rows) * 100, 2),
        "details": rows,
    }

def main() -> None:
    if not IMAGE_PATH.exists():
        raise FileNotFoundError(
            f"Handwritten sample not found: {IMAGE_PATH}. "
            "Place the test image at evaluation/handwritten_samples/HW-001.jpg."
        )
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    psm_results = {}
    for psm in (6, 11):
        text = run_ocr(psm)
        psm_results[str(psm)] = {
            "ocr_text": text,
            "evaluation": evaluate(text),
        }
    report = {
        "evaluation": "handwritten_ocr",
        "dataset": "1 real handwritten invoice-style sample",
        "image": "evaluation/handwritten_samples/HW-001.jpg",
        "ocr_engine": "Tesseract 5.5.3",
        "language": "eng",
        "psm_modes_tested": [6, 11],
        "ground_truth_fields": list(GROUND_TRUTH.keys()),
        "results": psm_results,
        "interpretation": (
            "Both PSM 6 and PSM 11 were tested on the same handwritten sample. "
            "The exact field-match metric is intentionally conservative: a field is "
            "counted correct only when its normalized expected value is present in "
            "the OCR output. Partial or approximate recognition is not counted as "
            "an exact match."
        ),
        "limitations": [
            "Only one handwritten sample was evaluated.",
            "The sample is a handwritten invoice-style note, not a representative real-world handwritten document corpus.",
            "Results should be treated as a pilot validation, not a production accuracy estimate.",
        ],
    }
    (RESULTS_DIR / "handwritten_ocr_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Handwritten OCR evaluation complete: {IMAGE_PATH}")
    for psm, result in psm_results.items():
        ev = result["evaluation"]
        print(
            f"PSM {psm}: {ev['correct_field_presences']}/{ev['fields']} "
            f"field-presence matches ({ev['field_presence_accuracy_percent']:.2f}%)"
        )
    print(f"Report: {RESULTS_DIR / 'handwritten_ocr_report.json'}")

if __name__ == "__main__":
    main()
