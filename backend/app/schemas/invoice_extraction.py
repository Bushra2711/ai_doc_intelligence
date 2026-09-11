from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class InvoiceFieldsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    invoice_number: str | None = None
    invoice_date: str | None = None
    due_date: str | None = None
    vendor_name: str | None = None
    vendor_gstin: str | None = None
    buyer_name: str | None = None
    buyer_gstin: str | None = None
    subtotal: float | None = None
    tax_amount: float | None = None
    total_amount: float | None = None
    currency: str | None = None
    po_number: str | None = None


class InvoiceExtractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: str
    fields: InvoiceFieldsResponse
