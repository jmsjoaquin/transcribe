from __future__ import annotations

from pathlib import Path

from worker.app.bootstrap import setup_backend_path
from worker.app.services.stt.base import TranscriptResult

setup_backend_path()

from app.core.config import settings  # noqa: E402


class FasterWhisperEngine:
    def __init__(self) -> None:
        self._model = None

    def transcribe(self, file_path: Path, *, language: str | None = None) -> TranscriptResult:
        model = self._get_model()
        segments_iter, info = model.transcribe(str(file_path), language=language or None)

        segments: list[dict] = []
        text_chunks: list[str] = []
        for segment in segments_iter:
            segment_text = segment.text.strip()
            segments.append(
                {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment_text,
                }
            )
            if segment_text:
                text_chunks.append(segment_text)

        return TranscriptResult(
            full_text=" ".join(text_chunks).strip(),
            segments=segments,
            duration_seconds=getattr(info, "duration", None),
            detected_language=getattr(info, "language", language),
            model_name=settings.whisper_model_size,
        )

    def _get_model(self):
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise RuntimeError(
                    "faster-whisper is not installed in the worker environment."
                ) from exc

            self._model = WhisperModel(
                settings.whisper_model_size,
                device=settings.whisper_device,
                compute_type=settings.whisper_compute_type,
            )
        return self._model
