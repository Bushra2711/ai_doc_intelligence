from __future__ import annotations

import csv
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
UPLOADS = BACKEND / "uploads"
RESULTS = ROOT / "evaluation" / "results"

sys.path.insert(0, str(BACKEND))

# Import User before Document so SQLAlchemy can resolve the Document.user relationship.
from app.models.user import User  # noqa: F401,E402
from app.models.document import Document  # noqa: E402
from app.db.database import SessionLocal  # noqa: E402
from app.services.document_processing import process_document  # noqa: E402


def percentile_95(values: list[float]) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    return statistics.quantiles(values, n=100, method="inclusive")[94]


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)

    db = SessionLocal()
    rows: list[dict[str, object]] = []

    try:
        documents = (
            db.query(Document)
            .filter(Document.filename.like("TCS-TEST-%.pdf"))
            .order_by(Document.filename)
            .all()
        )

        if len(documents) != 50:
            raise RuntimeError(
                f"Expected exactly 50 TCS test invoices, found {len(documents)}."
            )

        timings_ms: list[float] = []

        for index, document in enumerate(documents, start=1):
            started = time.perf_counter()
            success = False
            message = ""
            error = ""

            try:
                outcome = process_document(document, db)
                success = True
                message = outcome.message
            except Exception as exc:
                db.rollback()
                error = f"{type(exc).__name__}: {exc}"

            elapsed_ms = (time.perf_counter() - started) * 1000
            timings_ms.append(elapsed_ms)

            rows.append(
                {
                    "document_id": document.id,
                    "filename": document.filename,
                    "file_path": document.file_path,
                    "status": document.status.value,
                    "success": success,
                    "processing_time_ms": round(elapsed_ms, 3),
                    "processing_time_seconds": round(elapsed_ms / 1000, 6),
                    "message": message,
                    "error": error,
                }
            )

            print(
                f"[{index:02d}/50] {document.filename} -> "
                f"{elapsed_ms / 1000:.3f}s -> "
                f"{'SUCCESS' if success else 'FAILED'}"
            )

        successful_times = [
            float(row["processing_time_ms"])
            for row in rows
            if row["success"]
        ]
        failed_count = len(rows) - len(successful_times)

        summary = {
            "invoice_count": len(rows),
            "successful_invoices": len(successful_times),
            "failed_invoices": failed_count,
            "total_processing_time_seconds": round(sum(successful_times) / 1000, 6),
            "mean_processing_time_ms": round(statistics.mean(successful_times), 3)
            if successful_times
            else 0.0,
            "median_processing_time_ms": round(statistics.median(successful_times), 3)
            if successful_times
            else 0.0,
            "p95_processing_time_ms": round(percentile_95(successful_times), 3)
            if successful_times
            else 0.0,
            "min_processing_time_ms": round(min(successful_times), 3)
            if successful_times
            else 0.0,
            "max_processing_time_ms": round(max(successful_times), 3)
            if successful_times
            else 0.0,
        }

        report = {
            "evaluation": "50-invoice digital PDF processing-time benchmark",
            "scope": "Existing TCS-TEST-0001 through TCS-TEST-0050 documents",
            "timed_operation": "app.services.document_processing.process_document",
            "timing_method": "time.perf_counter() around the processing service call",
            "includes": [
                "embedded PDF text extraction",
                "document status updates",
                "extracted-text database persistence",
            ],
            "excludes": [
                "HTTP upload transfer",
                "authentication/network latency",
                "Tesseract OCR fallback for scanned PDFs",
            ],
            "notes": [
                "The benchmark reprocesses the existing 50 synthetic GST-style PDFs.",
                "The benchmark measures the digital PDF path because these PDFs contain embedded text.",
                "P95 uses Python statistics.quantiles with the inclusive method.",
                "Results are local benchmark measurements and are not a universal SLA guarantee.",
            ],
            "summary": summary,
        }

        with (RESULTS / "processing_time_report.json").open(
            "w", encoding="utf-8"
        ) as file:
            json.dump(report, file, indent=2)

        with (RESULTS / "processing_time_summary.csv").open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(["metric", "value"])
            for key, value in summary.items():
                writer.writerow([key, value])

        with (RESULTS / "processing_time_invoice_results.csv").open(
            "w", newline="", encoding="utf-8"
        ) as file:
            fieldnames = list(rows[0].keys())
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print("\nProcessing-time evaluation complete.")
        print(f"Invoices evaluated: {len(rows)}")
        print(f"Successful: {len(successful_times)}")
        print(f"Failed: {failed_count}")
        print(
            f"Mean processing time: "
            f"{summary['mean_processing_time_ms'] / 1000:.3f}s"
        )
        print(
            f"Median processing time: "
            f"{summary['median_processing_time_ms'] / 1000:.3f}s"
        )
        print(
            f"P95 processing time: "
            f"{summary['p95_processing_time_ms'] / 1000:.3f}s"
        )
        print(
            f"Min processing time: "
            f"{summary['min_processing_time_ms'] / 1000:.3f}s"
        )
        print(
            f"Max processing time: "
            f"{summary['max_processing_time_ms'] / 1000:.3f}s"
        )
        print(f"Reports: {RESULTS}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
