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
from app.services.ocr_service import OCRError, ocr_image, ocr_pdf

logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parents[2]
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".png", ".jpg", ".jpeg", ".gif", ".webp"}


class DocumentProcessingError(Exception):
    """Base error for document processing failures."""


class DocumentFileNotFoundError(DocumentProcessingError):
    """Raised when the stored document file cannot be found."""


class UnsupportedDocumentTypeError(DocumentProcessingError):
    """Raised when the document format cannot be extracted."""


class DocumentExtractionError(DocumentProcessingError):
    """Raised when document extraction fails unexpectedly."""


@dataclass(slots=True)
class DocumentProcessingOutcome:
    message: str
    extracted_text: ExtractedDocumentText | None


def _extract_pdf_text(document_path: Path) -> str:
    """Extract embedded PDF text first, then fall back to OCR for scanned PDFs."""
    try:
        with pymupdf.open(str(document_path)) as pdf_document:
            extracted_pages = []
            for page_number, page in enumerate(pdf_document, start=1):
                text = page.get_text("text").strip()
                if text:
                    extracted_pages.append(f"[Page {page_number}]\n{text}")

        text = "\n\n".join(extracted_pages).strip()
        if text:
            return text

        logger.info("No embedded text found in %s; starting OCR fallback", document_path.name)
        return ocr_pdf(document_path)
    except OCRError:
        raise
    except Exception as exc:
        logger.exception("Failed to read PDF %s", document_path)
        raise DocumentExtractionError("Failed to read PDF document") from exc


def _extract_docx_text(document_path: Path) -> str:
    try:
        from docx import Document as DocxDocument
    except ImportError as exc:
        raise DocumentExtractionError(
            "DOCX processing dependencies are not installed"
        ) from exc

    try:
        docx_document = DocxDocument(str(document_path))
        sections: list[str] = []

        for paragraph in docx_document.paragraphs:
            text = paragraph.text.strip()
            if text:
                sections.append(text)

        for table_index, table in enumerate(docx_document.tables, start=1):
            rows: list[str] = []
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells]
                if any(cells):
                    rows.append(" | ".join(cells))
            if rows:
                sections.append(f"[Table {table_index}]\n" + "\n".join(rows))

        return "\n\n".join(sections).strip()
    except Exception as exc:
        logger.exception("Failed to extract DOCX %s", document_path)
        raise DocumentExtractionError("Failed to extract text from DOCX document") from exc


def process_document(document: Document, db: Session) -> DocumentProcessingOutcome:
    """Extract text from a supported document, including OCR fallback for scans."""
    upload_root = (BACKEND_ROOT / "uploads").resolve()
    document_path = (BACKEND_ROOT / document.file_path).resolve()

    if not document_path.is_relative_to(upload_root):
        document.status = DocumentStatus.FAILED
        db.commit()
        raise DocumentFileNotFoundError("Document file path is invalid")

    if not document_path.exists() or not document_path.is_file():
        document.status = DocumentStatus.FAILED
        db.commit()
        raise DocumentFileNotFoundError("Document file not found")

    extension = document_path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        document.status = DocumentStatus.FAILED
        db.commit()
        raise UnsupportedDocumentTypeError(
            f"Unsupported document type: {extension or 'unknown'}"
        )

    document.status = DocumentStatus.PROCESSING
    db.commit()

    try:
        if extension == ".pdf":
            extracted_text = _extract_pdf_text(document_path)
            extraction_method = "PDF text extraction" if extracted_text else "PDF OCR"
        elif extension == ".docx":
            extracted_text = _extract_docx_text(document_path)
            extraction_method = "DOCX text extraction"
        else:
            extracted_text = ocr_image(document_path)
            extraction_method = "image OCR"
    except OCRError as exc:
        document.status = DocumentStatus.FAILED
        db.commit()
        raise DocumentExtractionError(str(exc)) from exc
    except DocumentExtractionError:
        document.status = DocumentStatus.FAILED
        db.commit()
        raise
    except Exception as exc:
        document.status = DocumentStatus.FAILED
        db.commit()
        logger.exception("Unexpected extraction failure for document %s", document.id)
        raise DocumentExtractionError("Failed to extract document text") from exc

    if not extracted_text.strip():
        document.status = DocumentStatus.FAILED
        db.commit()
        return DocumentProcessingOutcome(
            message="No extractable text found. The document may be blank or unreadable.",
            extracted_text=None,
        )

    try:
        stored_text = db.scalar(
            select(ExtractedDocumentText).where(
                ExtractedDocumentText.document_id == document.id
            )
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
        message=f"{extraction_method} completed successfully",
        extracted_text=stored_text,
    )


process_pdf_document = process_document
