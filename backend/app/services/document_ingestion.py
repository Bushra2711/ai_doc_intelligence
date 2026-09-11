from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


ALLOWED_FILE_TYPES: dict[str, str] = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}

MAX_UPLOAD_SIZE = 10 * 1024 * 1024


class DocumentIngestionError(Exception):
    """Base error for document ingestion failures."""


class UnsupportedFileTypeError(DocumentIngestionError):
    """Raised when an uploaded file type is not supported."""


class InvalidFileError(DocumentIngestionError):
    """Raised when uploaded file metadata or content is invalid."""


class FileTooLargeError(DocumentIngestionError):
    """Raised when an uploaded file exceeds the configured size limit."""


@dataclass(slots=True)
class IngestedFile:
    """Metadata for a file persisted by the ingestion layer."""

    original_filename: str
    stored_filename: str
    relative_path: str
    content_type: str
    file_size: int


def validate_upload_metadata(file: UploadFile) -> tuple[str, str, str]:
    """Validate filename, extension and MIME type before persisting a file."""
    if not file.filename:
        raise InvalidFileError("File name is required")

    safe_filename = Path(file.filename).name
    extension = Path(safe_filename).suffix.lower()

    if extension not in ALLOWED_FILE_TYPES:
        allowed = ", ".join(ext.lstrip(".").upper() for ext in ALLOWED_FILE_TYPES)
        raise UnsupportedFileTypeError(f"Unsupported file type. Allowed types: {allowed}")

    expected_mime_type = ALLOWED_FILE_TYPES[extension]
    content_type = file.content_type or expected_mime_type

    if content_type != expected_mime_type:
        raise UnsupportedFileTypeError("Unsupported file type")

    return safe_filename, extension, expected_mime_type


async def ingest_upload(file: UploadFile, upload_directory: Path) -> IngestedFile:
    """Validate and securely persist an uploaded enterprise document."""
    safe_filename, _, content_type = validate_upload_metadata(file)

    upload_directory.mkdir(parents=True, exist_ok=True)
    file_bytes = await file.read(MAX_UPLOAD_SIZE + 1)

    if len(file_bytes) > MAX_UPLOAD_SIZE:
        raise FileTooLargeError("File size must not exceed 10 MB")

    stored_filename = f"{uuid4()}_{safe_filename}"
    destination = (upload_directory / stored_filename).resolve()
    upload_root = upload_directory.resolve()

    if not destination.is_relative_to(upload_root):
        raise InvalidFileError("Invalid upload destination")

    try:
        destination.write_bytes(file_bytes)
    except OSError as exc:
        raise DocumentIngestionError("Unable to store uploaded document") from exc

    return IngestedFile(
        original_filename=file.filename,
        stored_filename=stored_filename,
        relative_path=f"uploads/{stored_filename}",
        content_type=content_type,
        file_size=len(file_bytes),
    )
