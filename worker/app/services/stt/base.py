from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(slots=True)
class TranscriptResult:
    full_text: str
    segments: list[dict]
    confidence: float | None = None
    duration_seconds: float | None = None
    detected_language: str | None = None
    model_name: str | None = None


class TranscriptionEngine(Protocol):
    def transcribe(self, file_path: Path, *, language: str | None = None) -> TranscriptResult:
        ...
