from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.db.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.document_analysis import DocumentAnalysis
from app.models.document_text import ExtractedDocumentText
from app.schemas.document_text import (
    DocumentProcessResponse,
    ExtractedDocumentTextResponse,
)
from app.models.user import User
#from app.schemas.document_text import DocumentProcessResponse
from app.schemas.document import DocumentResponse
from app.services.document_processing import (
    DocumentExtractionError,
    DocumentFileNotFoundError,
    UnsupportedDocumentTypeError,
    process_document as process_document_service,
)
from app.schemas.document_analysis import DocumentAnalysisResponse
from app.services.document_analysis import (
    DocumentAnalysisError,
    ExtractedTextNotFoundError,
    analyze_document,
)

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_FILE_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}

UPLOAD_DIRECTORY = Path(__file__).resolve().parents[4] / "uploads"
MAX_UPLOAD_SIZE = 10 * 1024 * 1024


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    """Upload a supported document and persist its metadata."""
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File name is required")

    safe_filename = Path(file.filename).name
    extension = Path(safe_filename).suffix.lower()
    if extension not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Allowed types: PDF, DOCX, PNG, JPG, JPEG, GIF, WEBP",
        )

    mime_type = file.content_type or ALLOWED_FILE_TYPES[extension]
    if mime_type != ALLOWED_FILE_TYPES[extension]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type",
        )

    UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
    file_bytes = await file.read(MAX_UPLOAD_SIZE + 1)
    if len(file_bytes) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size must not exceed 10 MB",
        )

    stored_name = f"{uuid4()}_{safe_filename}"
    file_path = UPLOAD_DIRECTORY / stored_name
    file_path.write_bytes(file_bytes)

    document = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_path=str(file_path.relative_to(file_path.parents[1])),
        file_type=mime_type,
        file_size=len(file_bytes),
        status=DocumentStatus.UPLOADED,
    )
    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except SQLAlchemyError as exc:
        db.rollback()
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save uploaded document",
        ) from exc

    return DocumentResponse.model_validate(document)


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DocumentResponse]:
    """Return all documents belonging to the authenticated user."""
    documents = db.scalars(
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
    ).all()
    return [DocumentResponse.model_validate(document) for document in documents]


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    """Return one document that belongs to the authenticated user."""
    document = db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return DocumentResponse.model_validate(document)
@router.get(
    "/{document_id}/text",
    response_model=ExtractedDocumentTextResponse,
)
def get_document_text(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExtractedDocumentTextResponse:

    document = db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    extracted_text = db.scalar(
        select(ExtractedDocumentText).where(
            ExtractedDocumentText.document_id == document.id
        )
    )

    if extracted_text is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extracted text not found. Process the document first.",
        )

    return ExtractedDocumentTextResponse.model_validate(extracted_text)


@router.post("/{document_id}/process", response_model=DocumentProcessResponse)
def process_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    
) -> DocumentProcessResponse:
    """Extract text from the authenticated user's PDF document."""
    document = db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    try:
        outcome = process_document_service(document, db)
    except DocumentFileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except UnsupportedDocumentTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except DocumentExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return DocumentProcessResponse(
        document_id=document.id,
        status=document.status,
        message=outcome.message,
        extracted_text_id=outcome.extracted_text.id if outcome.extracted_text else None,
    )
@router.post(
    "/{document_id}/analyze",
    response_model=DocumentAnalysisResponse,
)
def analyze_document_endpoint(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentAnalysisResponse:
    """Analyze the extracted text of the authenticated user's document."""

    document = db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    try:
        outcome = analyze_document(document, db)
    except ExtractedTextNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except DocumentAnalysisError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI analysis is temporarily unavailable. Extracted text is still available.",
        ) from exc

    return DocumentAnalysisResponse.model_validate(outcome.analysis)


@router.get(
    "/{document_id}/analysis",
    response_model=DocumentAnalysisResponse,
)
def get_document_analysis(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentAnalysisResponse:
    """Return the saved analysis of the authenticated user's document."""

    document = db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    analysis = db.scalar(
        select(DocumentAnalysis).where(
            DocumentAnalysis.document_id == document.id
        )
    )

    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found. Analyze the document first.",
        )

    return DocumentAnalysisResponse.model_validate(analysis)
@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete the authenticated user's document."""

    document = db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Delete extracted text first
    extracted_text = db.scalar(
        select(ExtractedDocumentText).where(
            ExtractedDocumentText.document_id == document.id
        )
    )

    if extracted_text is not None:
        db.delete(extracted_text)

    # Delete AI analysis
    analysis = db.scalar(
        select(DocumentAnalysis).where(
            DocumentAnalysis.document_id == document.id
        )
    )

    if analysis is not None:
        db.delete(analysis)

    # Delete physical uploaded file
    file_path = Path(document.file_path)

    if not file_path.is_absolute():
        file_path = UPLOAD_DIRECTORY.parent / file_path

    if file_path.exists():
        file_path.unlink()

    # Delete document from database
    db.delete(document)
    db.commit()

    return None