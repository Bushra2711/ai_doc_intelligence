from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.db.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.document_analysis import DocumentAnalysis
from app.models.document_text import ExtractedDocumentText
from app.schemas.document_text import DocumentProcessResponse, ExtractedDocumentTextResponse
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.schemas.invoice_extraction import InvoiceExtractionResponse
from app.schemas.invoice_accuracy import InvoiceAccuracyRequest, InvoiceAccuracyResponse
from app.services.document_ingestion import DocumentIngestionError, FileTooLargeError, InvalidFileError, UnsupportedFileTypeError, ingest_upload
from app.services.document_processing import DocumentExtractionError, DocumentFileNotFoundError, UnsupportedDocumentTypeError, process_document as process_document_service
from app.schemas.document_analysis import DocumentAnalysisResponse
from app.services.document_analysis import DocumentAnalysisError, ExtractedTextNotFoundError, analyze_document
from app.services.invoice_extraction import extract_invoice_fields_dict
from app.services.invoice_accuracy import evaluate_invoice_accuracy

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIRECTORY = Path(__file__).resolve().parents[4] / "uploads"


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> DocumentResponse:
    """Ingest a supported enterprise document and persist its metadata."""
    try:
        ingested = await ingest_upload(file, UPLOAD_DIRECTORY)
    except (UnsupportedFileTypeError, InvalidFileError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except FileTooLargeError as exc:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(exc)) from exc
    except DocumentIngestionError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    document = Document(user_id=current_user.id, filename=ingested.original_filename, file_path=ingested.relative_path, file_type=ingested.content_type, file_size=ingested.file_size, status=DocumentStatus.UPLOADED)
    stored_path = UPLOAD_DIRECTORY / ingested.stored_filename
    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except SQLAlchemyError as exc:
        db.rollback()
        stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to save uploaded document metadata") from exc
    return DocumentResponse.model_validate(document)


@router.get("", response_model=list[DocumentResponse])
def list_documents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[DocumentResponse]:
    documents = db.scalars(select(Document).where(Document.user_id == current_user.id).order_by(Document.created_at.desc())).all()
    return [DocumentResponse.model_validate(document) for document in documents]


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> DocumentResponse:
    document = db.scalar(select(Document).where(Document.id == document_id, Document.user_id == current_user.id))
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentResponse.model_validate(document)


@router.get("/{document_id}/text", response_model=ExtractedDocumentTextResponse)
def get_document_text(document_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ExtractedDocumentTextResponse:
    document = db.scalar(select(Document).where(Document.id == document_id, Document.user_id == current_user.id))
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    extracted_text = db.scalar(select(ExtractedDocumentText).where(ExtractedDocumentText.document_id == document.id))
    if extracted_text is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extracted text not found. Process the document first.")
    return ExtractedDocumentTextResponse.model_validate(extracted_text)


@router.get("/{document_id}/extract-invoice", response_model=InvoiceExtractionResponse)
def extract_invoice(document_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> InvoiceExtractionResponse:
    """Extract structured invoice fields from previously extracted document text."""
    document = db.scalar(select(Document).where(Document.id == document_id, Document.user_id == current_user.id))
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    extracted_text = db.scalar(select(ExtractedDocumentText).where(ExtractedDocumentText.document_id == document.id))
    if extracted_text is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Extracted text not found. Process the document first.")
    fields = extract_invoice_fields_dict(extracted_text.extracted_text)
    return InvoiceExtractionResponse(document_id=document.id, fields=fields)


@router.post("/{document_id}/evaluate-accuracy", response_model=InvoiceAccuracyResponse)
def evaluate_accuracy(document_id: str, payload: InvoiceAccuracyRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> InvoiceAccuracyResponse:
    """Evaluate invoice extraction against human-verified ground-truth fields."""
    document = db.scalar(select(Document).where(Document.id == document_id, Document.user_id == current_user.id))
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    extracted_text = db.scalar(select(ExtractedDocumentText).where(ExtractedDocumentText.document_id == document.id))
    if extracted_text is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Extracted text not found. Process the document first.")
    predicted = extract_invoice_fields_dict(extracted_text.extracted_text)
    result = evaluate_invoice_accuracy(predicted, payload.expected)
    return InvoiceAccuracyResponse(document_id=document.id, **result)


@router.post("/{document_id}/process", response_model=DocumentProcessResponse)
def process_document(document_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> DocumentProcessResponse:
    document = db.scalar(select(Document).where(Document.id == document_id, Document.user_id == current_user.id))
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    try:
        outcome = process_document_service(document, db)
    except DocumentFileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except UnsupportedDocumentTypeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except DocumentExtractionError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    return DocumentProcessResponse(document_id=document.id, status=document.status, message=outcome.message, extracted_text_id=outcome.extracted_text.id if outcome.extracted_text else None)


@router.post("/{document_id}/analyze", response_model=DocumentAnalysisResponse)
def analyze_document_endpoint(document_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> DocumentAnalysisResponse:
    document = db.scalar(select(Document).where(Document.id == document_id, Document.user_id == current_user.id))
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    try:
        outcome = analyze_document(document, db)
    except ExtractedTextNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except DocumentAnalysisError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI analysis is temporarily unavailable. Extracted text is still available.") from exc
    return DocumentAnalysisResponse.model_validate(outcome.analysis)


@router.get("/{document_id}/analysis", response_model=DocumentAnalysisResponse)
def get_document_analysis(document_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> DocumentAnalysisResponse:
    document = db.scalar(select(Document).where(Document.id == document_id, Document.user_id == current_user.id))
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    analysis = db.scalar(select(DocumentAnalysis).where(DocumentAnalysis.document_id == document.id))
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found. Analyze the document first.")
    return DocumentAnalysisResponse.model_validate(analysis)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    document = db.scalar(select(Document).where(Document.id == document_id, Document.user_id == current_user.id))
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    extracted_text = db.scalar(select(ExtractedDocumentText).where(ExtractedDocumentText.document_id == document.id))
    if extracted_text is not None: db.delete(extracted_text)
    analysis = db.scalar(select(DocumentAnalysis).where(DocumentAnalysis.document_id == document.id))
    if analysis is not None: db.delete(analysis)
    file_path = Path(document.file_path)
    if not file_path.is_absolute(): file_path = UPLOAD_DIRECTORY.parent / file_path
    if file_path.exists(): file_path.unlink()
    db.delete(document)
    db.commit()
    return None
