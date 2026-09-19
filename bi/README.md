# DocuMind AI BI Dataset

Import `invoice_kpi_template.csv` into Power BI or Tableau as the schema template. Replace the example row with exports from the DocuMind API/database.

Core measures:
- Invoice Count = count of document_id
- Total Invoice Value = sum of total_amount
- Average Confidence = average of confidence_score
- Average Data Quality = average of data_quality_score
- Compliance Pass Rate = compliant invoices / invoice count
- Average Processing Time = average of processing_time_seconds

The CSV is a portable dashboard artifact; a native .pbix/.twb file must be created with the corresponding desktop BI application if required by the evaluator.
