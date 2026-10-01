#!/usr/bin/env python3
"""Run the 50-invoice ground-truth accuracy evaluation against DocuMind AI.

Usage:
  set DOCUMIND_EMAIL=...
  set DOCUMIND_PASSWORD=...
  set DOCUMIND_API_URL=http://127.0.0.1:8000
  python evaluation/run_batch_evaluation.py

The ground-truth CSV must contain document_id plus the invoice fields defined in
invoice_ground_truth_template.csv. Only human-verified values should be entered.
Do not run this evaluator against the blank template or model-generated predictions.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import argparse
from collections import defaultdict
from pathlib import Path
from urllib import error, request

FIELDS = (
    "invoice_number", "invoice_date", "vendor_name", "vendor_gstin",
    "buyer_name", "buyer_gstin", "subtotal", "tax_amount", "total_amount", "po_number",
)

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "invoice_ground_truth.csv"
OUT_DIR = ROOT / "results"


def http_json(base_url: str, path: str, method: str = "GET", token: str | None = None, payload: dict | None = None):
    body = None if payload is None else json.dumps(payload).encode()
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = request.Request(f"{base_url.rstrip('/')}{path}", data=body, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=120) as response:
            raw = response.read().decode()
            return json.loads(raw) if raw else {}
    except error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"{method} {path} failed ({exc.code}): {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Cannot reach API at {base_url}: {exc}") from exc


def parse_value(name: str, value: str):
    value = value.strip()
    if value == "":
        return None
    if name in {"subtotal", "tax_amount", "total_amount"}:
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"{name} must be numeric, got {value!r}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate human-verified invoice ground truth.")
    parser.add_argument(
        "--ground-truth",
        type=Path,
        default=CSV_PATH,
        help="CSV containing human-verified expected values (default: evaluation/invoice_ground_truth.csv)",
    )
    args = parser.parse_args()
    csv_path = args.ground_truth if args.ground_truth.is_absolute() else (ROOT / args.ground_truth)
    base_url = os.getenv("DOCUMIND_API_URL", "http://127.0.0.1:8000")
    email = os.getenv("DOCUMIND_EMAIL")
    password = os.getenv("DOCUMIND_PASSWORD")
    if not email or not password:
        print("Set DOCUMIND_EMAIL and DOCUMIND_PASSWORD before running.", file=sys.stderr)
        return 2
    if not csv_path.exists():
        print(f"Missing {csv_path}", file=sys.stderr)
        return 2

    with csv_path.open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))

    if len(rows) != 50:
        print(f"Expected exactly 50 ground-truth rows; found {len(rows)}.", file=sys.stderr)
        return 2

    missing_id = [i + 2 for i, row in enumerate(rows) if not row.get("document_id", "").strip()]
    if missing_id:
        print(f"Missing document_id in CSV rows: {missing_id}", file=sys.stderr)
        return 2

    missing_ground_truth = []
    for row_number, row in enumerate(rows, start=2):
        for field in FIELDS:
            if not row.get(field, "").strip():
                missing_ground_truth.append(f"row {row_number}: {field}")
    if missing_ground_truth:
        print("Ground truth is incomplete. Fill every expected field with human-verified values.")
        for item in missing_ground_truth[:20]:
            print(f"  - {item}")
        if len(missing_ground_truth) > 20:
            print(f"  ... and {len(missing_ground_truth) - 20} more")
        return 2

    token = http_json(
        base_url,
        "/api/v1/auth/login",
        method="POST",
        payload={"email": email, "password": password},
    )["access_token"]

    documents = http_json(base_url, "/api/v1/documents", token=token)

    # Local review files use stored upload names such as
    # "<uuid>_TCS-TEST-0012", while the API document id is a different UUID.
    # Match those review rows to the authenticated user's document by the
    # original filename (TCS-TEST-0012.pdf) or by the invoice number.
    import re
    api_by_filename = {str(doc.get("filename", "")).lower(): doc for doc in documents}
    api_by_stored_path = {}
    api_by_invoice = {}
    for doc in documents:
        stored_name = Path(str(doc.get("file_path", ""))).name.lower()
        if stored_name:
            api_by_stored_path[stored_name] = doc
        match = re.search(r"TCS-TEST-\\d{4}", str(doc.get("filename", "")), re.IGNORECASE)
        if match:
            api_by_invoice[match.group(0).upper()] = doc
        if not match:
            match = re.search(r"TCS-TEST-\\d{4}", stored_name, re.IGNORECASE)
            if match:
                api_by_invoice[match.group(0).upper()] = doc

    resolved = []
    unresolved = []
    for row in rows:
        local_id = row["document_id"].strip()
        if local_id in {str(doc.get("id")) for doc in documents}:
            doc = next(doc for doc in documents if str(doc.get("id")) == local_id)
        else:
            invoice_match = re.search(r"TCS-TEST-\\d{4}", local_id, re.IGNORECASE)
            invoice_number = invoice_match.group(0).upper() if invoice_match else ""
            doc = api_by_invoice.get(invoice_number)
            if doc is None:
                doc = api_by_stored_path.get(f"{local_id.lower()}.pdf")
            if doc is None:
                doc = api_by_filename.get(f"{local_id.lower()}.pdf")
        if doc is None:
            unresolved.append(local_id)
        else:
            resolved.append((row, doc))

    if unresolved:
        print("These review rows could not be mapped to authenticated documents:")
        for item in unresolved:
            print(f"  - {item}")
        print("The evaluator matches TCS-TEST-#### from the local filename to the API document filename.")
        return 2

    results = []
    field_stats = defaultdict(lambda: {"correct": 0, "total": 0})
    for number, (row, doc) in enumerate(resolved, start=1):
        # Prefer explicitly human-verified values when present.
        expected = {}
        for field in FIELDS:
            source = row.get(f"verified_{field}", "").strip()
            if source == "":
                source = row.get(field, "")
            expected[field] = parse_value(field, source)
        document_id = str(doc["id"])
        result = http_json(
            base_url,
            f"/api/v1/documents/{document_id}/evaluate-accuracy",
            method="POST",
            token=token,
            payload={"expected": expected},
        )
        results.append(result)
        for field, detail in result["field_results"].items():
            field_stats[field]["total"] += 1
            if detail["match"]:
                field_stats[field]["correct"] += 1
        print(f"[{number:02d}/50] {row["document_id"]} -> API {document_id} -> {result["accuracy_percent"]:.2f}%")

    total_correct = sum(item["correct_fields"] for item in results)
    total_fields = sum(item["total_fields"] for item in results)
    overall = (total_correct / total_fields * 100) if total_fields else 0.0

    OUT_DIR.mkdir(exist_ok=True)
    report = {
        "invoices_evaluated": len(results),
        "fields_per_invoice": len(FIELDS),
        "total_fields_evaluated": total_fields,
        "correct_fields": total_correct,
        "mismatched_fields": total_fields - total_correct,
        "overall_field_accuracy_percent": round(overall, 2),
        "per_field_accuracy_percent": {
            field: round(stats["correct"] / stats["total"] * 100, 2)
            for field, stats in field_stats.items()
        },
        "invoice_results": results,
    }
    (OUT_DIR / "invoice_accuracy_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    with (OUT_DIR / "invoice_accuracy_summary.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["field", "correct", "evaluated", "accuracy_percent"])
        for field in FIELDS:
            stats = field_stats[field]
            accuracy = stats["correct"] / stats["total"] * 100 if stats["total"] else 0
            writer.writerow([field, stats["correct"], stats["total"], f"{accuracy:.2f}"])

    print("\nEvaluation complete.")
    print(f"Invoices evaluated: {len(results)}")
    print(f"Overall field accuracy: {overall:.2f}%")
    print(f"Reports: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
