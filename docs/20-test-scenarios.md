# Step 20 - Test Scenarios

## TS01 - End-to-End Invoice Processing

**Req Id:** REQ01  
**Test Scenario Id:** TS01  
**Application / Screen:** Document Processing Dashboard  
**High-Level Test Condition:** Upload an invoice and verify ingestion, extraction, validation, confidence scoring, and dashboard visibility.  
**Expected Result:** Document is processed and structured invoice information is available for downstream validation and analytics.  
**Priority:** High

## TS02 - Invoice Extraction Accuracy

**Req Id:** REQ02  
**Test Scenario Id:** TS02  
**Application / Screen:** Invoice Evaluation  
**High-Level Test Condition:** Compare extracted invoice fields against human-verified ground truth for 50 invoices.  
**Expected Result:** Evaluated fields match ground truth within configured normalization and numeric tolerance.  
**Actual Result:** 500/500 field comparisons matched; 100.00%.  
**Priority:** High

## TS03 - OCR Information Retention

**Req Id:** REQ03  
**Test Scenario Id:** TS03  
**Application / Screen:** OCR Evaluation  
**High-Level Test Condition:** Run OCR over the 50-invoice evaluation set and check retention of the ten evaluated business fields.  
**Expected Result:** Required information is retained in OCR output.  
**Actual Result:** 98.80% field-presence result.  
**Priority:** High

## TS04 - Compliance Alert Validation

**Req Id:** REQ04  
**Test Scenario Id:** TS04  
**Application / Screen:** Document Processing Dashboard  
**High-Level Test Condition:** Validate deterministic invoice compliance checks for required fields, GSTIN structure, amount reconciliation, tax reconciliation, line items, and PO reference.  
**Expected Result:** Implemented rules return PASS, WARNING, or FAIL consistently and expose the rule result.  
**Actual Result:** 450 PASS, 0 WARNING, 50 FAIL; all 50 failures were buyer_gstin_format on synthetic identifiers.  
**Priority:** High

## TS05 - Confidence Scoring

**Req Id:** REQ05  
**Test Scenario Id:** TS05  
**Application / Screen:** Invoice Analytics  
**High-Level Test Condition:** Calculate confidence from extracted-field evidence and consistency checks.  
**Expected Result:** A transparent confidence score and confidence level are produced.  
**Actual Result:** 50/50 invoices were HIGH confidence; average 96.00%.  
**Priority:** High

## TS06 - Processing-Time / SLA Benchmark

**Req Id:** REQ06  
**Test Scenario Id:** TS06  
**Application / Screen:** Processing Pipeline  
**High-Level Test Condition:** Benchmark processing of 50 digital PDF invoices.  
**Expected Result:** Successful processing and repeatable timing statistics are recorded.  
**Actual Result:** 50/50 successful; mean 0.046s; median 0.045s; P95 0.054s.  
**Priority:** High

## TS07 - Regression Testing

**Req Id:** REQ07  
**Test Scenario Id:** TS07  
**Application / Screen:** Backend Test Suite  
**High-Level Test Condition:** Execute automated regression tests after parser and evaluation changes.  
**Expected Result:** No regression failures.  
**Actual Result:** 13/13 tests passed.  
**Priority:** High

## TS08 - Role-Based Access and Auditability

**Req Id:** REQ08  
**Test Scenario Id:** TS08  
**Application / Screen:** Authentication / Audit Trail  
**High-Level Test Condition:** Verify role-based access and audit events for supported application actions.  
**Expected Result:** Access is controlled by configured roles and auditable actions are recorded.  
**Actual Result:** Functionality is implemented in the repository; separate execution evidence should be captured before claiming this scenario as externally demonstrated.  
**Priority:** Medium