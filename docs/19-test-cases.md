# Step 19 - Test Cases

| Test Case | Test Condition | Expected Result | Actual Result | Defect |
|---|---|---|---|---|
| TC01 | Extract Invoice Total from 50 annotated invoices | Match ground truth within ±0.01 | 50/50 matched; 100.00% | N |
| TC02 | Extract Vendor Name from 50 annotated invoices | Match ground truth | 50/50 matched; 100.00% | N |
| TC03 | Extract Invoice Number from 50 annotated invoices | Match ground truth | 50/50 matched; 100.00% | N |
| TC04 | Extract Invoice Date from 50 annotated invoices | Match ground truth | 50/50 matched; 100.00% | N |
| TC05 | Extract Vendor and Buyer GSTIN fields | Match human-verified values | 50/50 for each field; 100.00% | N |
| TC06 | Extract Subtotal and Tax Amount | Match human-verified values | 50/50 for each field; 100.00% | N |
| TC07 | Extract PO Number | Match human-verified value | 50/50 matched; 100.00% | N |
| TC08 | OCR information retention on 50 invoices | Evaluated business fields retained | 98.80% field-presence result | N |
| TC09 | Process 50 digital PDF invoices | All process successfully and timing is recorded | 50/50 successful; mean 0.046s; P95 0.054s | N |
| TC10 | Invoice confidence evaluation | Evidence-based score is produced | 50/50 HIGH; average 96.00% | N |
| TC11 | Invoice compliance validation | Implemented rules return consistent PASS/WARNING/FAIL results | 450 PASS, 0 WARNING, 50 FAIL; all failures are buyer_gstin_format on synthetic identifiers | N |
| TC12 | Regression test suite | No regression failures | 13/13 tests passed | N |

## Detailed Example: TC01

**Test Case #:** TC01  
**Application / Screen:** Document Processing Dashboard / Invoice Evaluation  
**Test Step #:** 1  
**Test Case:** Verify extracted Invoice Total against human-verified ground truth.  
**Pre-Requisites:** Pipeline available; 50 human-verified invoices available.  
**Input:** TCS-TEST-0001 through TCS-TEST-0050.  
**Expected Result:** Extracted total equals ground truth within ±0.01.  
**Actual Result:** 50/50 matches; 100.00% field-level accuracy.  
**Defect:** N  
**Evidence:** evaluation/results/invoice_accuracy_summary.csv and evaluation/results/invoice_accuracy_report.json.

## Detailed Example: TC08

**Test Case #:** TC08  
**Application / Screen:** Document Processing / OCR Evaluation  
**Test Case:** Verify retention of evaluated business-critical fields in OCR output.  
**Input:** 50 synthetic GST-style invoices.  
**Expected Result:** Required information is retained in OCR output.  
**Actual Result:** 98.80% field-presence result across 500 field comparisons.  
**Defect:** N  
**Evidence:** evaluation/results/ocr_accuracy_summary.csv and evaluation/results/ocr_accuracy_report.json.

## Detailed Example: TC09

**Test Case #:** TC09  
**Application / Screen:** Document Processing Pipeline  
**Test Case:** Measure processing time for 50 digital PDF invoices.  
**Expected Result:** All invoices process successfully and timing statistics are recorded.  
**Actual Result:** 50/50 successful; mean 0.046 seconds; median 0.045 seconds; P95 0.054 seconds; maximum 0.092 seconds.  
**Defect:** N  
**Evidence:** evaluation/results/processing_time_summary.csv and evaluation/results/processing_time_report.json.

## Test Data Limitation

The invoice evaluation dataset is synthetic GST-style test data. The 100.00% extraction result therefore represents this evaluation dataset and should not be interpreted as a guarantee of performance on unseen real-world invoices.