from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class PipelineStep:
    name: str
    status: str
    detail: str = ""


class DocumentPipeline(Generic[T]):
    """Small, dependency-free orchestration layer for deterministic document workflows."""

    def __init__(self) -> None:
        self.steps: list[PipelineStep] = []

    def run(self, name: str, fn: Callable[[], T]) -> T:
        try:
            result = fn()
            self.steps.append(PipelineStep(name=name, status="SUCCESS"))
            return result
        except Exception as exc:
            self.steps.append(PipelineStep(name=name, status="FAILED", detail=str(exc)))
            raise
