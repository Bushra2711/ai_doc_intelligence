from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pymupdf
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentStatus
from app.models.document_text import ExtractedDocumentText

logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parents[2]


class DocumentProcessingError(Exception):
    """Base error for document processing failures."""


class DocumentFileNotFoundError(DocumentProcessingError):
    """Raised when the stored document file cannot be found."""


class UnsupportedDocumentTypeError(DocumentProcessingError):
    """Raised when the document format cannot be extracted."""


class DocumentExtractionError(DocumentProcessingError):
    """Raised when PDF extraction fails unexpectedly."""


@dataclass(slots=True)
class DocumentProcessingOutcome:
    message: str
    extracted_text: ExtractedDocumentText | None


def process_document(document: Document, db: Session) -> DocumentProcessingOutcome:
    """Extract text from a supported document and persist the extracted content."""
    upload_root = (BACKEND_ROOT / "uploads").resolve()
    document_path = (BACKEND_ROOT / document.file_path).resolve()
    if not document_path.is_relative_to(upload_root):
        document.status = DocumentStatus.FAILED
        db.commit()
        raise DocumentFileNotFoundError("Document file path is invalid")

    if not document_path.exists():
        document.status = DocumentStatus.FAILED
        db.commit()
        raise DocumentFileNotFoundError("Document file not found")

    extension = document_path.suffix.lower()
    if extension not in {".pdf", ".docx", ".png", ".jpg", ".jpeg", ".gif", ".webp"}:
        document.status = DocumentStatus.FAILED
        db.commit()
        raise UnsupportedDocumentTypeError("Only PDF documents can be processed")

    document.status = DocumentStatus.PROCESSING
    db.commit()

    try:
        if extension == ".pdf":
            with pymupdf.open(str(document_path)) as pdf_document:
                extracted_pages = [
                    page.get_text("text").strip()
                    for page in pdf_document
                    if page.get_text("text").strip()
                ]
        elif extension == ".docx":
            try:
                from docx import Document as DocxDocument
            except ImportError as exc:
                raise DocumentExtractionError(
                    "DOCX processing dependencies are not installed"
                ) from exc
            docx_document = DocxDocument(str(document_path))
            extracted_pages = [
                paragraph.text.strip()
                for paragraph in docx_document.paragraphs
                if paragraph.text.strip()
            ]
        else:
            try:
                import pytesseract
                from PIL import Image
            except ImportError as exc:
                raise DocumentExtractionError(
                    "Image OCR dependencies are not installed"
                ) from exc
            extracted_pages = [pytesseract.image_to_string(Image.open(document_path)).strip()]
    except Exception as exc:
        document.status = DocumentStatus.FAILED
        db.commit()
        logger.exception("Failed to extract PDF text for document %s", document.id)
        raise DocumentExtractionError("Failed to extract text from PDF") from exc

    extracted_text = "\n".join(extracted_pages).strip()
    if not extracted_text:
        document.status = DocumentStatus.FAILED
        db.commit()
        return DocumentProcessingOutcome(
            message="No extractable text found in the PDF",
            extracted_text=None,
        )

    try:
        stored_text = db.scalar(
            select(ExtractedDocumentText).where(ExtractedDocumentText.document_id == document.id)
        )
        if stored_text is None:
            stored_text = ExtractedDocumentText(
                document_id=document.id,
                extracted_text=extracted_text,
            )
        else:
            stored_text.extracted_text = extracted_text

        db.add(stored_text)
        document.status = DocumentStatus.COMPLETED
        db.commit()
        db.refresh(stored_text)
        db.refresh(document)
    except SQLAlchemyError as exc:
        document.status = DocumentStatus.FAILED
        db.commit()
        logger.exception("Failed to store extracted text for document %s", document.id)
        raise DocumentExtractionError("Failed to store extracted text") from exc

    return DocumentProcessingOutcome(
        message=f"{extension[1:].upper()} text extracted successfully",
        extracted_text=stored_text,
    )


    process_pdf_document = process_document
