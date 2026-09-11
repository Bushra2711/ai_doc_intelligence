# Step 2 – Architecture and Data Acquisition

## 1. Objective

Define the document ingestion, validation, storage, and processing architecture for DocuMind AI.

The implementation separates upload/ingestion from document processing so that new document sources and processing methods can be added without changing the storage contract.

---

## 2. Supported Initial Document Sources

The ingestion layer accepts the following document formats:

| Source / Format | Extension | Processing Path |
|---|---|---|
| Digital PDF | `.pdf` | PDF text extraction, OCR fallback |
| Word document | `.docx` | DOCX text extraction |
| Scanned invoice/image | `.png`, `.jpg`, `.jpeg` | OCR |
| Image document | `.gif`, `.webp` | OCR |

The project architecture also reserves the ingestion boundary for future enterprise sources such as email attachments, purchase orders, receipts, contracts, compliance forms, and policy documents identified during requirement analysis.

---

## 3. High-Level Architecture

```text
User / Enterprise Source
          |
          v
     Upload API
          |
          v
 Document Ingestion Layer
   |       |       |
   |       |       +--> MIME/type validation
   |       +----------> Size validation
   +------------------> Safe filename + unique storage name
          |
          v
   File Storage (uploads/)
          |
          +------> Document Metadata (PostgreSQL/SQLite)
          |
          v
  Document Processing Layer
          |
          +--> PDF text extraction
          +--> OCR for scanned PDFs/images
          +--> DOCX extraction
          |
          v
   Extracted Text Storage
          |
          v
     AI Analysis Layer
          |
          v
 Validation / Compliance / Confidence / Reporting
```

---

## 4. Ingestion Responsibilities

`backend/app/services/document_ingestion.py` is responsible for:

1. Sanitizing the client-provided filename to its final path component.
2. Validating the file extension against the supported format allow-list.
3. Validating the MIME type against the expected MIME type.
4. Enforcing the 10 MB upload limit.
5. Generating a UUID-based storage filename to avoid collisions.
6. Ensuring the final storage path remains inside the configured upload directory.
7. Persisting the file before its database metadata is committed.
8. Returning a consistent ingestion result to the API layer.

The API layer then stores document ownership, metadata, and processing status in the `documents` table.

---

## 5. Storage Model

Each uploaded document stores:

- Document ID
- User ID / owner
- Original filename
- Relative storage path
- MIME type
- File size
- Processing status
- Creation timestamp
- Update timestamp

The current implementation stores physical files under the backend `uploads/` directory and stores their relative path in the document record.

This keeps the storage contract independent from the processing implementation and allows a future object-storage adapter to replace local storage without redesigning document processing.

---

## 6. Processing Flow

```text
Upload
  |
  v
Validate
  |
  v
Persist File
  |
  v
Persist Metadata
  |
  v
Process Document
  |
  +--> PDF with embedded text --> Extract text
  |
  +--> Scanned PDF -------------> OCR
  |
  +--> DOCX --------------------> Extract paragraphs/tables
  |
  +--> Image --------------------> OCR
  |
  v
Store Extracted Text
  |
  v
AI Analysis
```

OCR support was implemented in Step 1. Step 2 establishes the ingestion boundary around that processing capability.

---

## 7. Error Handling

The ingestion layer uses explicit error categories:

- `UnsupportedFileTypeError`
- `InvalidFileError`
- `FileTooLargeError`
- `DocumentIngestionError`

The API maps these to appropriate HTTP responses while database failures remove the newly stored physical file to avoid orphaned uploads.

---

## 8. Security and Reliability Considerations

The ingestion design includes:

- Filename path sanitization
- Extension allow-listing
- MIME-type validation
- Maximum upload size
- UUID-based stored filenames
- Upload-directory path containment validation
- Database/file cleanup when metadata persistence fails
- User ownership checks on document operations

These controls provide a baseline for the secure document-processing requirement and can be extended later with malware scanning, encryption, object storage, retention policies, and role-based access control.

---

## 9. Data Acquisition Plan

The evaluation dataset should contain representative enterprise documents required by the project requirements:

- Digital PDF invoices
- Scanned invoices
- Invoice images
- Purchase orders
- Receipts
- Contracts
- Compliance forms
- Email attachments
- Policy documents
- Regulatory guidelines

Each evaluation document should later be associated with ground-truth annotations so extraction and classification results can be measured objectively.

---

## 10. TCS Step Mapping

| Requirement | Implementation |
|---|---|
| Document ingestion architecture | Upload API + `document_ingestion.py` |
| Multiple document formats | PDF, DOCX, PNG, JPG, JPEG, GIF, WEBP |
| Secure ingestion | Filename, MIME, size and path validation |
| Storage | Local `uploads/` + document metadata |
| OCR integration boundary | `document_processing.py` |
| Dataset acquisition plan | Section 9 |
| Extensible architecture | Separate ingestion and processing services |

---

## 11. Step 2 Completion Criteria

Step 2 is considered implemented when:

- The ingestion layer validates supported formats.
- Upload size is enforced.
- Files receive unique storage names.
- Uploaded files are stored safely.
- Document metadata is persisted.
- Ingestion failures are handled without leaving orphan files after database failure.
- Existing OCR/text extraction remains available through the processing layer.
- Dataset requirements are documented.
- The architecture is documented for future enterprise sources.

---

## 12. Suggested Commit Messages

- `feat: add secure document ingestion service`
- `refactor: route uploads through document ingestion layer`
