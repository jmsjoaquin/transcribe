from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from worker.app.bootstrap import setup_backend_path
from worker.app.services.storage import WorkerStorageError, resolve_media_path
from worker.app.services.stt.factory import get_transcription_engine

setup_backend_path()

from app.db.session import SessionLocal  # noqa: E402
from app.models.transcription_job import TranscriptionJob, TranscriptionJobStatus  # noqa: E402
from app.models.transcript import Transcript  # noqa: E402
from app.workers.contracts import TranscriptionJobMessage  # noqa: E402


def process_transcription_job(payload: dict) -> None:
    message = TranscriptionJobMessage.model_validate(payload)
    db = SessionLocal()

    try:
        job = db.get(TranscriptionJob, message.job_id)
        if job is None:
            return

        job.status = TranscriptionJobStatus.PROCESSING
        job.started_at = datetime.now(UTC)
        job.error_message = None
        db.commit()
        db.refresh(job)

        media_path = resolve_media_path(job.storage_path)
        engine = get_transcription_engine()
        result = engine.transcribe(media_path, language=job.language)

        transcript = job.transcript
        if transcript is None:
            transcript = Transcript(job_id=job.id, full_text=result.full_text)
            db.add(transcript)

        transcript.full_text = result.full_text
        transcript.segments_json = result.segments
        transcript.confidence = result.confidence

        job.status = TranscriptionJobStatus.COMPLETED
        job.completed_at = datetime.now(UTC)
        job.error_message = None
        if result.duration_seconds is not None:
            job.duration_seconds = Decimal(str(result.duration_seconds))
        if result.detected_language and not job.language:
            job.language = result.detected_language
        if result.model_name:
            job.model_name = result.model_name

        db.commit()
    except Exception as exc:
        db.rollback()
        _mark_job_failed(db, message.job_id, exc)
        raise
    finally:
        db.close()


def _mark_job_failed(db, job_id: int, exc: Exception) -> None:
    job = db.get(TranscriptionJob, job_id)
    if job is None:
        return

    job.status = TranscriptionJobStatus.FAILED
    job.completed_at = datetime.now(UTC)
    if isinstance(exc, WorkerStorageError):
        job.error_message = str(exc)
    else:
        job.error_message = str(exc) or exc.__class__.__name__
    db.commit()
