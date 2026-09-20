from io import BytesIO

from fastapi import UploadFile
import pytest

from app.services.document_ingestion import (
    MAX_UPLOAD_SIZE,
    UnsupportedFileTypeError,
    validate_upload_metadata,
)


def make_upload(filename: str, content_type: str, content: bytes = b"test") -> UploadFile:
    return UploadFile(
        file=BytesIO(content),
        filename=filename,
        headers={"content-type": content_type},
    )


def test_supported_pdf_metadata_is_accepted():
    upload = make_upload("invoice.pdf", "application/pdf", b"%PDF")

    name, extension, mime = validate_upload_metadata(upload)

    assert name == "invoice.pdf"
    assert extension == ".pdf"
    assert mime == "application/pdf"


def test_unsupported_extension_is_rejected():
    upload = make_upload("invoice.exe", "application/octet-stream")

    with pytest.raises(UnsupportedFileTypeError):
        validate_upload_metadata(upload)


def test_upload_size_limit_is_10_mb():
    assert MAX_UPLOAD_SIZE == 10 * 1024 * 1024
