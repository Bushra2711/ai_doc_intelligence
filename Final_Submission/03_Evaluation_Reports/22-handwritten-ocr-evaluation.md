# Handwritten OCR Evaluation

## Purpose

This document records a pilot handwritten-document OCR validation for the document intelligence platform.

## Test setup

- OCR engine: Tesseract 5.5.3
- OCR language: English (eng)
- Sample count: 1
- Sample type: handwritten invoice-style note
- Test image: evaluation/handwritten_samples/HW-001.jpg
- PSM modes tested: 6 and 11
- Evaluated fields: invoice number, invoice date, vendor, buyer, subtotal, tax amount, total amount, and PO number.

## Ground truth

| Field | Ground truth |
|---|---|
| Invoice Number | HW-001 |
| Invoice Date | 23-09-2026 |
| Vendor | Kisan hardware |
| Buyer | Mohammdi Retail |
| Subtotal | 5000.00 |
| Tax Amount | 900.00 |
| Total Amount | 5900.00 |
| PO Number | PO-1001 |

## Observed OCR behavior

Tesseract produced partial recognition in both tested page-segmentation modes. Examples include approximate recognition of the invoice number and buyer name, while several numeric values and the vendor/PO values were not recovered exactly.

The evaluation uses a conservative field-presence/exact-value metric: a field counts as correct only when its normalized expected value is present in the OCR output. Approximate or partially recognized values are not counted as exact matches.

Based on the observed OCR output from the test image, neither PSM 6 nor PSM 11 achieved an exact match for all eight fields. The preliminary exact field-match result was 0/8 (0.00%) for the manually reviewed sample.

## Interpretation

This is a pilot handwritten OCR validation, not a production accuracy estimate. One handwritten sample is insufficient to characterize real-world handwriting variability. The result demonstrates that the current Tesseract-based OCR pipeline does not reliably extract all structured invoice fields from this sample.

## Evidence

The execution script is evaluation/run_handwritten_ocr_evaluation.py

The generated machine-readable report is evaluation/results/handwritten_ocr_report.json

The handwritten image is retained as a local evaluation artifact and is not required to be committed to the repository.

## Limitation

A larger handwritten dataset with multiple writers, writing styles, document layouts, and image-quality conditions is required before reporting a representative handwritten OCR accuracy metric.
