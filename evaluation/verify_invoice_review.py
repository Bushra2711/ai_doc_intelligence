#!/usr/bin/env python3
"""Interactively human-verify the 50-invoice review CSV.

The parser predictions are never treated as ground truth automatically.
For each invoice, the reviewer confirms the displayed values against the
actual PDF. Confirmed values are written to verified_* columns and the
verification status is marked HUMAN_VERIFIED.
"""
from __future__ import annotations

import csv
from pathlib import Path

try:
    import pymupdf
except ImportError:
    pymupdf = None

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
UPLOADS = BACKEND / "uploads"
INPUT = ROOT / "evaluation" / "50_invoice_review.csv"
OUTPUT = INPUT

FIELDS = (
    "invoice_number", "invoice_date", "vendor_name", "vendor_gstin",
    "buyer_name", "buyer_gstin", "subtotal", "tax_amount", "total_amount", "po_number",
)

def find_pdf(document_id: str) -> Path | None:
    matches = list(UPLOADS.glob(f"{document_id}.pdf"))
    if matches:
        return matches[0]
    return next(iter(UPLOADS.glob(f"*_{document_id.split('_')[-1]}.pdf")), None)

def show_source(pdf: Path | None) -> None:
    if pymupdf is None or pdf is None:
        return
    doc = pymupdf.open(pdf)
    source = "\n".join(page.get_text() for page in doc)
    doc.close()
    print("\n--- SOURCE PDF TEXT ---")
    print(source[:12000])
    print("--- END SOURCE PDF TEXT ---\n")

def main() -> int:
    if not INPUT.exists():
        print(f"Missing {INPUT}. Run generate_invoice_review.py first.")
        return 2
    if pymupdf is None:
        print("Install PyMuPDF first: python -m pip install pymupdf")
        return 2

    with INPUT.open("r", newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
        columns = list(rows[0].keys()) if rows else []

    if len(rows) != 50:
        print(f"Expected 50 rows; found {len(rows)}.")
        return 2

    print("\nHUMAN VERIFICATION")
    print("For each invoice, compare the prediction with the SOURCE PDF text.")
    print("Press Y only when ALL 10 fields are correct.")
    print("Press N to correct fields one by one.")
    print("These confirmed values are human-verified ground truth candidates.\n")

    verified_count = 0
    for index, row in enumerate(rows, 1):
        print("=" * 78)
        print(f"[{index}/50] {row['document_id']}")
        print("=" * 78)
        pdf = find_pdf(row["document_id"])
        show_source(pdf)

        for field in FIELDS:
            print(f"{field:18}: {row.get(field, '')}")

        answer = input("\nAre ALL 10 values correct according to the PDF? [Y/n/q]: ").strip().lower()
        if answer == "q":
            print("Stopped. Previously saved confirmations will remain in the CSV.")
            break

        if answer in ("", "y", "yes"):
            for field in FIELDS:
                row[f"verified_{field}"] = row.get(field, "")
            row["verification_status"] = "HUMAN_VERIFIED"
            row["verification_notes"] = "Reviewer confirmed all 10 fields against source PDF."
            verified_count += 1
            continue

        print("\nEnter a corrected value, or press Enter to keep the displayed value.")
        for field in FIELDS:
            current = row.get(field, "")
            value = input(f"{field} [{current}]: ")
            row[f"verified_{field}"] = value if value != "" else current
        row["verification_status"] = "HUMAN_VERIFIED"
        row["verification_notes"] = "Reviewer checked source PDF and confirmed/corrected fields."
        verified_count += 1

    with OUTPUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved: {OUTPUT}")
    print(f"Human-verified rows in this run: {verified_count}")
    print("Next: review that all 50 rows show HUMAN_VERIFIED, then create invoice_ground_truth.csv.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
