from __future__ import annotations

import csv
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
RESULTS = ROOT / "evaluation" / "results"

sys.path.insert(0, str(BACKEND))

from app.models.user import User  # noqa: F401,E402
from app.models.document import Document  # noqa: E402
from app.models.document_text import ExtractedDocumentText  # noqa: E402
from app.db.database import SessionLocal  # noqa: E402
from app.services.invoice_extraction import extract_invoice_fields_dict  # noqa: E402
from app.services.invoice_compliance import evaluate_invoice_compliance  # noqa: E402
from app.services.invoice_confidence import invoice_confidence_dict  # noqa: E402


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    db = SessionLocal()

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

        text_by_document = {
            row.document_id: row
            for row in db.query(ExtractedDocumentText)
            .filter(ExtractedDocumentText.document_id.in_([d.id for d in documents]))
            .all()
        }

        rows: list[dict[str, object]] = []
        confidence_scores: list[float] = []
        compliance_statuses: list[str] = []
        check_statuses: Counter[str] = Counter()

        for index, document in enumerate(documents, start=1):
            extracted = text_by_document.get(document.id)
            if extracted is None:
                raise RuntimeError(
                    f"No extracted text found for {document.filename}."
                )

            fields = extract_invoice_fields_dict(extracted.extracted_text)
            confidence = invoice_confidence_dict(fields)
            compliance = evaluate_invoice_compliance(fields)

            score = float(confidence["overall_score"])
            confidence_scores.append(score)
            compliance_statuses.append(str(compliance["overall_status"]))

            for check in compliance["checks"]:
                check_statuses[check["status"]] += 1

            rows.append(
                {
                    "document_id": document.id,
                    "filename": document.filename,
                    "confidence_score": score,
                    "confidence_level": confidence["overall_level"],
                    "compliance_status": compliance["overall_status"],
                    "compliance_passed": compliance["passed"],
                    "compliance_warnings": compliance["warnings"],
                    "compliance_failed": compliance["failed"],
                }
            )

            print(
                f"[{index:02d}/50] {document.filename} -> "
                f"confidence {score:.2f} ({confidence['overall_level']}) -> "
                f"{compliance['overall_status']}"
            )

        confidence_levels = Counter(
            str(row["confidence_level"]) for row in rows
        )
        compliance_counts = Counter(compliance_statuses)

        summary = {
            "invoice_count": len(rows),
            "average_confidence_score": round(statistics.mean(confidence_scores), 4),
            "median_confidence_score": round(statistics.median(confidence_scores), 4),
            "minimum_confidence_score": round(min(confidence_scores), 4),
            "maximum_confidence_score": round(max(confidence_scores), 4),
            "high_confidence_invoices": confidence_levels.get("HIGH", 0),
            "medium_confidence_invoices": confidence_levels.get("MEDIUM", 0),
            "low_confidence_invoices": confidence_levels.get("LOW", 0),
            "missing_confidence_invoices": confidence_levels.get("MISSING", 0),
            "compliant_invoices": compliance_counts.get("COMPLIANT", 0),
            "compliant_with_warnings_invoices": compliance_counts.get(
                "COMPLIANT_WITH_WARNINGS", 0
            ),
            "non_compliant_invoices": compliance_counts.get("NON_COMPLIANT", 0),
            "total_compliance_pass_checks": check_statuses.get("PASS", 0),
            "total_compliance_warning_checks": check_statuses.get("WARNING", 0),
            "total_compliance_failed_checks": check_statuses.get("FAIL", 0),
        }

        report = {
            "evaluation": "50-invoice compliance and confidence evaluation",
            "scope": "Existing TCS-TEST-0001 through TCS-TEST-0050 documents",
            "confidence_method": (
                "Transparent heuristic confidence calculated from extracted-field "
                "evidence and consistency checks."
            ),
            "compliance_method": (
                "Deterministic invoice validation rules covering required fields, "
                "GSTIN structure, amount reconciliation, tax reconciliation, "
                "line-item reconciliation, and purchase-order reference."
            ),
            "important_limitations": [
                "Confidence scores are evidence-based heuristic scores, not calibrated probabilities.",
                "Compliance checks validate the implemented rules and extracted values; they do not establish legal or tax compliance.",
                "The evaluation uses synthetic GST-style invoices and should not be treated as evidence of performance on all real-world invoice formats.",
            ],
            "summary": summary,
        }

        with (RESULTS / "invoice_quality_report.json").open(
            "w", encoding="utf-8"
        ) as file:
            json.dump(report, file, indent=2)

        with (RESULTS / "invoice_quality_summary.csv").open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(["metric", "value"])
            for key, value in summary.items():
                writer.writerow([key, value])

        with (RESULTS / "invoice_quality_invoice_results.csv").open(
            "w", newline="", encoding="utf-8"
        ) as file:
            fieldnames = list(rows[0].keys())
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print("\nInvoice quality evaluation complete.")
        print(f"Invoices evaluated: {len(rows)}")
        print(f"Average confidence: {summary['average_confidence_score']:.2%}")
        print(f"Median confidence: {summary['median_confidence_score']:.2%}")
        print(
            f"Confidence range: "
            f"{summary['minimum_confidence_score']:.2%} - "
            f"{summary['maximum_confidence_score']:.2%}"
        )
        print(
            f"Compliance: {summary['compliant_invoices']} compliant, "
            f"{summary['compliant_with_warnings_invoices']} with warnings, "
            f"{summary['non_compliant_invoices']} non-compliant"
        )
        print(
            f"Checks: {summary['total_compliance_pass_checks']} PASS, "
            f"{summary['total_compliance_warning_checks']} WARNING, "
            f"{summary['total_compliance_failed_checks']} FAIL"
        )
        print(f"Reports: {RESULTS}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
