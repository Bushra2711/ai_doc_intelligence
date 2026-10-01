# DocuMind AI Evaluation Pack

Use a human-verified dataset with at least 50 invoices. Do not use generated expected values as ground truth.

Create a CSV using invoice_ground_truth_template.csv with document_id, invoice_number, invoice_date, vendor_name, vendor_gstin, buyer_name, buyer_gstin, subtotal, tax_amount, total_amount and po_number.

The backend evaluation service compares predicted values against verified values using normalized text matching and a numeric tolerance of 0.01. Record predicted value, expected value, match result and field-level accuracy.

Final report should include overall field accuracy, per-field accuracy, number of invoices, evaluated fields, mismatches and representative extraction errors.

Important: no claim of 50-invoice accuracy should be made until 50 human-verified invoices have actually been evaluated.
