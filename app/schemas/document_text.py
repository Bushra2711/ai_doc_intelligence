from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.document import DocumentStatus


class ExtractedDocumentTextBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ExtractedDocumentTextCreate(ExtractedDocumentTextBase):
    document_id: str = Field(min_length=1, max_length=36)
    extracted_text: str = Field(min_length=1)


class ExtractedDocumentTextResponse(ExtractedDocumentTextBase):
    id: str
    document_id: str
    extracted_text: str
    created_at: datetime
    updated_at: datetime


class DocumentProcessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: str
    status: DocumentStatus
    message: str
    extracted_text_id: str | None = None
