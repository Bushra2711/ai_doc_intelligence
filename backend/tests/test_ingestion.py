from io import BytesIO

import pytest
from fastapi import UploadFile

from app.services.document_ingestion import (
    MAX_UPLOAD_SIZE,
    UnsupportedFileTypeError,
    validate_upload_metadata,
)


def test_supported_pdf_metadata_is_accepted():
    upload = UploadFile(filename="invoice.pdf", file=BytesIO(b"%PDF"))
    upload.content_type = "application/pdf"

    name, extension, mime = validate_upload_metadata(upload)

    assert name == "invoice.pdf"
    assert extension == ".pdf"
    assert mime == "application/pdf"


def test_unsupported_extension_is_rejected():
    upload = UploadFile(filename="invoice.exe", file=BytesIO(b"bad"))
    upload.content_type = "application/octet-stream"

    with pytest.raises(UnsupportedFileTypeError):
        validate_upload_metadata(upload)


def test_upload_size_limit_is_10_mb():
    assert MAX_UPLOAD_SIZE == 10 * 1024 * 1024
