from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.document import DocumentStatus


class DocumentSchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DocumentCreate(DocumentSchemaBase):
    filename: str = Field(min_length=1, max_length=255)
    file_path: str = Field(min_length=1, max_length=500)
    file_type: str = Field(min_length=1, max_length=50)
    file_size: int = Field(ge=0)
    status: DocumentStatus = DocumentStatus.UPLOADED


class DocumentResponse(DocumentSchemaBase):
    id: str
    user_id: str
    filename: str
    file_path: str
    file_type: str
    file_size: int
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime
