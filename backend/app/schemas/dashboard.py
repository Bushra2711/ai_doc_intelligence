from pydantic import BaseModel, ConfigDict


class DashboardMetricsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_documents: int
    completed_documents: int
    processing_documents: int
    pending_documents: int
    failed_documents: int
    invoice_documents: int
    analyzed_documents: int
    average_invoice_confidence: float | None
    compliance_passed: int
    compliance_warnings: int
    compliance_failed: int
    document_types: dict[str, int]
    status_counts: dict[str, int]
    recent_daily_counts: list[dict[str, int | str]]
