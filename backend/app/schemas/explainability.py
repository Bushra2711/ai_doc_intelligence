from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

class ExplainabilityFeature(BaseModel):
    feature: str
    value: Any = None
    contribution: float
    direction: str
    reason: str

class DocumentExplainabilityResponse(BaseModel):
    document_id: str
    method: str
    model_layer: str
    prediction: str
    confidence: float = Field(ge=0, le=1)
    base_value: float
    features: list[ExplainabilityFeature]
    explanation: str
    limitation: str
