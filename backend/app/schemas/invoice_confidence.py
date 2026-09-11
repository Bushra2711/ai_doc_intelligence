from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class InvoiceFieldConfidenceResponse(BaseModel):
    field: str
    value: Any = None
    score: float = Field(ge=0, le=1)
    level: str
    reason: str


class InvoiceConfidenceResponse(BaseModel):
    document_id: str
    overall_score: float = Field(ge=0, le=1)
    overall_level: str
    fields: list[InvoiceFieldConfidenceResponse]
