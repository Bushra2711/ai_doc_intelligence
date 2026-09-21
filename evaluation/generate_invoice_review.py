#!/usr/bin/env python3
"""Generate a human-review CSV from locally uploaded invoice PDFs.

This creates candidate predictions only. The generated values are NOT ground truth.
A human must verify/correct every expected field before running run_batch_evaluation.py.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

try:
    import pymupdf
except ImportError:
    pymupdf = None

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
UPLOADS = BACKEND / "uploads"
OUTPUT = ROOT / "evaluation" / "50_invoice_review.csv"

FIELDS = (
    "invoice_number", "invoice_date", "vendor_name", "vendor_gstin",
    "buyer_name", "buyer_gstin", "subtotal", "tax_amount", "total_amount", "po_number",
)

def main() -> int:
    if pymupdf is None:
        print("Install PyMuPDF first: python -m pip install pymupdf")
        return 2
    sys.path.insert(0, str(BACKEND))
    from app.services.invoice_extraction import extract_invoice_fields

    files = sorted(UPLOADS.glob("*_TCS-TEST-*.pdf"))
    if len(files) != 50:
        print(f"Expected 50 TCS test PDFs in {UPLOADS}; found {len(files)}.")
        return 2

    rows = []
    for path in files:
        doc = pymupdf.open(path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        fields = extract_invoice_fields(text)
        values = {field: getattr(fields, field) for field in FIELDS}
        rows.append({
            "document_id": path.stem,
            **values,
            **{f"verified_{field}": "" for field in FIELDS},
            "verification_status": "",
            "verification_notes": "",
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    columns = ["document_id", *FIELDS, *[f"verified_{f}" for f in FIELDS],
               "verification_status", "verification_notes"]
    with OUTPUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created: {OUTPUT}")
    print("The extracted columns are predictions for review, NOT ground truth.")
    print("Verify every invoice manually, then copy verified_* values into evaluation/invoice_ground_truth.csv.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
