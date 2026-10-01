from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.ocr_service import ocr_image

RESULTS = ROOT / "evaluation" / "results"
DATASET = ROOT / "evaluation" / "multilingual_samples"

SAMPLES = [
    {
        "id": "ML-01",
        "title": "Bilingual Invoice 01",
        "lines": [
            "INVOICE / चालान",
            "Invoice Number / चालान नंबर: ML-001",
            "Vendor / विक्रेता: Kisan Hardware",
            "Buyer / खरीदार: ABC Retail",
            "Total Amount / कुल राशि: 12500.00",
        ],
        "fields": ["ML-001", "Kisan Hardware", "ABC Retail", "12500.00", "चालान", "विक्रेता", "खरीदार", "कुल राशि"],
    },
    {
        "id": "ML-02",
        "title": "Bilingual Invoice 02",
        "lines": [
            "INVOICE / चालान",
            "Invoice Number / चालान नंबर: ML-002",
            "Vendor / विक्रेता: Maharashtra Traders",
            "Buyer / खरीदार: Sunrise Stores",
            "Total Amount / कुल राशि: 8750.50",
        ],
        "fields": ["ML-002", "Maharashtra Traders", "Sunrise Stores", "8750.50", "चालान", "विक्रेता", "खरीदार", "कुल राशि"],
    },
    {
        "id": "ML-03",
        "title": "Bilingual Invoice 03",
        "lines": [
            "INVOICE / चालान",
            "Invoice Number / चालान नंबर: ML-003",
            "Vendor / विक्रेता: Vidarbha Supplies",
            "Buyer / खरीदार: Green Mart",
            "Total Amount / कुल राशि: 19400.75",
        ],
        "fields": ["ML-003", "Vidarbha Supplies", "Green Mart", "19400.75", "चालान", "विक्रेता", "खरीदार", "कुल राशि"],
    },
    {
        "id": "ML-04",
        "title": "Hindi Document 01",
        "lines": [
            "चालान",
            "चालान नंबर: ML-004",
            "विक्रेता: किसान हार्डवेयर",
            "खरीदार: एबीसी रिटेल",
            "कुल राशि: 5600.00",
        ],
        "fields": ["ML-004", "किसान हार्डवेयर", "एबीसी रिटेल", "5600.00", "चालान", "विक्रेता", "खरीदार", "कुल राशि"],
    },
    {
        "id": "ML-05",
        "title": "Hindi Document 02",
        "lines": [
            "चालान",
            "चालान नंबर: ML-005",
            "विक्रेता: महाराष्ट्र ट्रेडर्स",
            "खरीदार: सनराइज स्टोर्स",
            "कुल राशि: 9200.25",
        ],
        "fields": ["ML-005", "महाराष्ट्र ट्रेडर्स", "सनराइज स्टोर्स", "9200.25", "चालान", "विक्रेता", "खरीदार", "कुल राशि"],
    },
    {
        "id": "ML-06",
        "title": "Hindi Document 03",
        "lines": [
            "चालान",
            "चालान नंबर: ML-006",
            "विक्रेता: विदर्भ सप्लायर्स",
            "खरीदार: ग्रीन मार्ट",
            "कुल राशि: 15100.00",
        ],
        "fields": ["ML-006", "विदर्भ सप्लायर्स", "ग्रीन मार्ट", "15100.00", "चालान", "विक्रेता", "खरीदार", "कुल राशि"],
    },
]


def normalize(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def find_font() -> Path:
    candidates = [
        Path(r"C:\Windows\Fonts\Nirmala.ttc"),
        Path(r"C:\Windows\Fonts\Nirmala.ttc"),
        Path(r"C:\Windows\Fonts\Nirmala.ttf"),
        Path(r"C:\Windows\Fonts\NirmalaUI.ttf"),
        Path(r"C:\Windows\Fonts\mangal.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return path
    raise SystemExit(
        "No Devanagari-capable Windows font found. Expected Nirmala.ttc, "
        "Nirmala.ttf, NirmalaUI.ttf, or mangal.ttf."
    )


def create_samples() -> None:
    from PIL import Image, ImageDraw, ImageFont

    DATASET.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype(str(find_font()), 34)

    for sample in SAMPLES:
        image = Image.new("RGB", (1500, 500), "white")
        draw = ImageDraw.Draw(image)
        y = 40
        for line in sample["lines"]:
            draw.text((50, y), line, fill="black", font=font)
            y += 70
        image.save(DATASET / f'{sample["id"]}.png')


def main() -> None:
    create_samples()

    RESULTS.mkdir(parents=True, exist_ok=True)
    rows = []
    total = 0
    correct = 0

    for sample in SAMPLES:
        image_path = DATASET / f'{sample["id"]}.png'
        lang = "eng+hin"
        text = ocr_image(image_path, lang=lang)
        normalized_text = normalize(text)

        sample_correct = 0
        for expected in sample["fields"]:
            matched = normalize(expected) in normalized_text
            sample_correct += int(matched)
            total += 1
            correct += int(matched)

        accuracy = sample_correct / len(sample["fields"]) * 100
        rows.append({
            "sample_id": sample["id"],
            "language_mode": lang,
            "correct_fields": sample_correct,
            "total_fields": len(sample["fields"]),
            "field_presence_accuracy_percent": round(accuracy, 2),
        })
        print(f'{sample["id"]}: {accuracy:.2f}%')

    overall = correct / total * 100
    report = {
        "evaluation_type": "Multilingual OCR information-retention evaluation",
        "languages": ["English", "Hindi"],
        "language_mode": "eng+hin",
        "dataset": "6 synthetic bilingual/Hindi document images",
        "samples": len(SAMPLES),
        "field_comparisons": total,
        "correct_field_presences": correct,
        "overall_field_presence_accuracy_percent": round(overall, 2),
        "metric": "Whether human-defined business-critical fields are present in OCR output.",
        "limitations": [
            "The dataset is synthetic and small.",
            "This evaluates English/Hindi OCR language support, not real-world multilingual document variability.",
            "The metric measures information retention rather than character-perfect transcription accuracy.",
            "Handwritten text is not included in this evaluation.",
        ],
        "results": rows,
    }

    (RESULTS / "multilingual_ocr_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    with (RESULTS / "multilingual_ocr_summary.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "sample_id",
                "language_mode",
                "correct_fields",
                "total_fields",
                "field_presence_accuracy_percent",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print()
    print("Multilingual OCR evaluation complete.")
    print(f"Samples evaluated: {len(SAMPLES)}")
    print(f"Field comparisons: {total}")
    print(f"Overall field-presence accuracy: {overall:.2f}%")
    print(f"Reports: {RESULTS}")


if __name__ == "__main__":
    main()
