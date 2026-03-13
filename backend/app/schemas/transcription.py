from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.transcription_job import TranscriptionJobStatus


class TranscriptionJobRead(BaseModel):
    id: int
    status: TranscriptionJobStatus
    source_filename: str
    language: str | None
    model_name: str | None
    duration_seconds: Decimal | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    transcript_available: bool = False

    model_config = ConfigDict(from_attributes=True)


class TranscriptionJobList(BaseModel):
    jobs: list[TranscriptionJobRead]


class TranscriptRead(BaseModel):
    job_id: int
    status: TranscriptionJobStatus
    full_text: str
    segments_json: list[dict] | None
    confidence: float | None
    created_at: datetime


class TranscriptionDownloadPayload(BaseModel):
    job_id: int
    status: TranscriptionJobStatus
    source_filename: str
    transcript: TranscriptRead
