from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class InvoiceAccuracyRequest(BaseModel):
    expected: dict[str, Any] = Field(default_factory=dict)


class InvoiceAccuracyResponse(BaseModel):
    document_id: str
    accuracy_percent: float
    correct_fields: int
    total_fields: int
    field_results: dict[str, dict[str, Any]]
