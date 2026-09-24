# Multi-Source Document Ingestion

## Objective

TCS Step 2 requires document ingestion from APIs, portals, and batch uploads, with metadata tagging and indexing.

DocuMind now represents these three ingestion paths explicitly:

| Source | Entry point | Metadata |
|---|---|---|
| Portal | Web UI document upload | `ingestion_source=portal` |
| API | Authenticated `POST /api/v1/documents/upload?ingestion_source=api` | `ingestion_source=api` |
| Batch | Authenticated `POST /api/v1/documents/batch-upload` | `ingestion_source=batch` |

## Supported document formats

The ingestion layer accepts:

- PDF
- DOCX
- PNG
- JPG/JPEG
- GIF
- WEBP

Maximum upload size is 10 MB per file.

## Security and validation

Before persistence, the ingestion service:

1. Sanitizes the original filename to its basename.
2. Validates the extension against an allow-list.
3. Validates the MIME type against the expected type.
4. Reads at most 10 MB + 1 byte to enforce the size limit.
5. Generates a UUID-prefixed stored filename.
6. Resolves the destination path and verifies it remains inside the upload directory.
7. Rolls back database metadata and removes stored files if persistence fails.

The batch endpoint accepts up to 50 files per request and cleans up already-written files if a later file in the same batch fails validation or database persistence.

## Metadata and indexing

The `documents.ingestion_source` field records the ingestion path and is indexed for source-level filtering and reporting.

Existing documents are migrated with the default source value `portal` so the schema remains backward compatible.

## Verification

After applying the Alembic migration:

```powershell
cd backend
alembic upgrade head
python -m pytest -q
```

Then use the authenticated Swagger UI to demonstrate:

1. Upload one PDF/image/DOCX through the web portal.
2. Call `POST /api/v1/documents/upload` with `ingestion_source=api`.
3. Call `POST /api/v1/documents/batch-upload` with multiple supported files.
4. Call `GET /api/v1/documents` and verify each returned document contains its `ingestion_source`.
5. Continue the normal Process -> Analyze -> Validate workflow for the ingested documents.

## Evidence boundary

This implementation demonstrates API, portal, and batch ingestion locally. It does not claim a live external email connector, enterprise portal connector, or cloud data-lake integration. Those are deployment-specific extensions.

## TCS mapping

**Step 2 - Architecture and Data Acquisition**

- Ingestion from APIs: implemented.
- Portal/web ingestion: implemented.
- Batch ingestion: implemented.
- Metadata tagging: implemented through `ingestion_source`.
- Metadata indexing: database index on `ingestion_source`.
- Secure raw-document persistence: implemented through validated local upload storage; production cloud data-lake controls remain environment-specific.
