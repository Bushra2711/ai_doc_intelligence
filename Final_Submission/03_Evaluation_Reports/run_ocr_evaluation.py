from __future__ import annotations

import csv
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.ocr_service import ocr_pdf


UPLOADS = ROOT / "backend" / "uploads"
GROUND_TRUTH = ROOT / "evaluation" / "invoice_ground_truth.csv"
RESULTS = ROOT / "evaluation" / "results"

FIELDS = [
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
]

NUMERIC_FIELDS = {"subtotal", "tax_amount", "total_amount"}


def normalize(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def variants(value: object) -> set[str]:
    raw = str(value or "").strip()
    normalized = normalize(raw)
    values = {normalized}

    numeric = normalized.replace(",", "")
    if numeric:
        values.add(numeric)

    return {v for v in values if v}


def parse_decimal(value: object) -> Decimal | None:
    raw = str(value or "").strip()
    if not raw:
        return None

    cleaned = re.sub(r"[^0-9.\-+]", "", raw)
    if not cleaned or cleaned in {"-", "+", "."}:
        return None

    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def ocr_numeric_values(ocr_text: str) -> set[Decimal]:
    values: set[Decimal] = set()

    for match in re.findall(
        r"(?<![A-Za-z0-9])[-+]?\d[\d,]*(?:\.\d+)?",
        ocr_text,
    ):
        parsed = parse_decimal(match)
        if parsed is not None:
            values.add(parsed)

    return values


def field_present(ocr_text: str, expected: object, field: str) -> bool:
    text = normalize(ocr_text)

    if field not in NUMERIC_FIELDS:
        return any(value in text for value in variants(expected))

    expected_number = parse_decimal(expected)
    if expected_number is None:
        return any(value in text for value in variants(expected))

    return expected_number in ocr_numeric_values(ocr_text)


def main() -> None:
    if not GROUND_TRUTH.exists():
        raise SystemExit(f"Ground truth not found: {GROUND_TRUTH}")

    with GROUND_TRUTH.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if len(rows) != 50:
        raise SystemExit(f"Expected exactly 50 invoices, found {len(rows)}")

    pdfs = list(UPLOADS.glob("*_TCS-TEST-*.pdf"))
    pdf_by_invoice: dict[str, Path] = {}

    for pdf in pdfs:
        match = re.search(r"(TCS-TEST-\d{4})", pdf.name, re.I)
        if match:
            pdf_by_invoice[match.group(1).upper()] = pdf

    if len(pdf_by_invoice) < 50:
        raise SystemExit(
            f"Expected at least 50 TCS test PDFs, found {len(pdf_by_invoice)}"
        )

    RESULTS.mkdir(parents=True, exist_ok=True)

    detailed = []
    field_correct = {field: 0 for field in FIELDS}
    field_total = {field: 0 for field in FIELDS}

    for index, row in enumerate(rows, start=1):
        invoice_number = str(row.get("invoice_number", "")).strip()
        pdf = pdf_by_invoice.get(invoice_number.upper())

        if pdf is None:
            raise SystemExit(f"Could not find PDF for invoice {invoice_number}")

        print(f"[{index:02d}/50] {invoice_number} -> {pdf.name}")

        ocr_text = ocr_pdf(pdf)
        field_results = {}
        correct = 0

        for field in FIELDS:
            expected = row.get(f"verified_{field}") or row.get(field, "")
            match = field_present(ocr_text, expected, field)

            field_results[field] = {
                "expected": expected,
                "present_in_ocr": match,
            }

            field_total[field] += 1

            if match:
                field_correct[field] += 1
                correct += 1

        accuracy = correct / len(FIELDS) * 100

        detailed.append(
            {
                "invoice_number": invoice_number,
                "pdf": pdf.name,
                "correct_fields": correct,
                "total_fields": len(FIELDS),
                "field_presence_accuracy_percent": round(accuracy, 2),
                "field_results": field_results,
            }
        )

        print(f"       Field presence: {accuracy:.2f}%")

    total_correct = sum(field_correct.values())
    total_evaluated = sum(field_total.values())
    overall = total_correct / total_evaluated * 100

    summary = [
        {
            "field": field,
            "correct": field_correct[field],
            "evaluated": field_total[field],
            "accuracy_percent": round(
                field_correct[field] / field_total[field] * 100, 2
            ),
        }
        for field in FIELDS
    ]

    summary.append(
        {
            "field": "OVERALL",
            "correct": total_correct,
            "evaluated": total_evaluated,
            "accuracy_percent": round(overall, 2),
        }
    )

    report = {
        "evaluation_type": "OCR information-retention evaluation",
        "dataset": "50 synthetic GST-style invoices",
        "metric": (
            "Whether each human-verified structured invoice field is "
            "present in the Tesseract OCR output."
        ),
        "numeric_matching": (
            "Subtotal, tax amount, and total amount are compared by "
            "numeric value to tolerate comma grouping and decimal "
            "formatting differences."
        ),
        "fields_per_invoice": len(FIELDS),
        "total_field_comparisons": total_evaluated,
        "correct_field_presences": total_correct,
        "overall_field_presence_accuracy_percent": round(overall, 2),
        "results": detailed,
        "field_summary": summary,
        "limitations": [
            "The dataset contains synthetic GST-style invoices.",
            "The reference values come from human-verified invoice fields.",
            "This metric measures business-critical information retention "
            "in OCR output, not character-perfect transcription accuracy.",
            "Numeric formatting differences are normalized for the three "
            "invoice amount fields.",
            "PDF layout differences can affect CER/WER even when "
            "business-critical information is preserved.",
        ],
    }

    json_path = RESULTS / "ocr_accuracy_report.json"
    csv_path = RESULTS / "ocr_accuracy_summary.csv"
    detail_path = RESULTS / "ocr_invoice_results.csv"

    json_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["field", "correct", "evaluated", "accuracy_percent"],
        )
        writer.writeheader()
        writer.writerows(summary)

    with detail_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "invoice_number",
                "pdf",
                "correct_fields",
                "total_fields",
                "field_presence_accuracy_percent",
            ]
        )

        for item in detailed:
            writer.writerow(
                [
                    item["invoice_number"],
                    item["pdf"],
                    item["correct_fields"],
                    item["total_fields"],
                    item["field_presence_accuracy_percent"],
                ]
            )

    print()
    print("OCR evaluation complete.")
    print("Invoices evaluated: 50")
    print(f"Field comparisons: {total_evaluated}")
    print(f"Overall OCR field-presence accuracy: {overall:.2f}%")
    print(f"Reports: {RESULTS}")


if __name__ == "__main__":
    main()
