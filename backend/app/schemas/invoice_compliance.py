from __future__ import annotations

from pydantic import BaseModel, Field


class ComplianceCheckResponse(BaseModel):
    rule: str
    status: str
    message: str


class InvoiceComplianceResponse(BaseModel):
    document_id: str
    overall_status: str
    passed: int = Field(ge=0)
    warnings: int = Field(ge=0)
    failed: int = Field(ge=0)
    checks: list[ComplianceCheckResponse]
