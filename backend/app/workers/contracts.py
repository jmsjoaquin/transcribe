from datetime import datetime

from pydantic import BaseModel


class TranscriptionJobMessage(BaseModel):
    job_id: int
    user_id: int
    storage_backend: str
    storage_path: str
    source_filename: str
    language: str | None
    model_name: str | None
    media_access_mode: str
    submitted_at: datetime
