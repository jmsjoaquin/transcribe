from __future__ import annotations

import json
from pathlib import Path

from fastapi import UploadFile
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from sqlalchemy.orm import Session

from app.models.transcription_job import TranscriptionJob, TranscriptionJobStatus
from app.models.transcript import Transcript
from app.models.user import User
from app.repositories import transcript as transcript_repository
from app.repositories import transcription_job as job_repository
from app.schemas.transcription import (
    TranscriptRead,
    TranscriptionDownloadPayload,
    TranscriptionJobRead,
)
from app.services.storage import StorageError, delete_local_file, save_upload


class TranscriptionError(Exception):
    pass


def list_jobs_for_user(db: Session, user: User) -> list[TranscriptionJobRead]:
    jobs = job_repository.list_for_user(db, user_id=user.id)
    return [_serialize_job(job) for job in jobs]


def create_transcription_job(
    db: Session,
    *,
    user: User,
    upload: UploadFile,
    language: str | None,
    model_name: str | None,
) -> TranscriptionJobRead:
    try:
        stored_media = save_upload(upload)
    except StorageError as exc:
        raise TranscriptionError(str(exc)) from exc

    job = TranscriptionJob(
        user_id=user.id,
        status=TranscriptionJobStatus.PENDING,
        source_filename=stored_media.original_filename,
        storage_path=stored_media.storage_path,
        language=language or None,
        model_name=model_name or None,
    )

    try:
        job_repository.create(db, job)
        db.commit()
    except Exception:
        db.rollback()
        delete_local_file(stored_media.storage_path)
        raise

    db.refresh(job)
    return _serialize_job(job)


def get_job_for_user(db: Session, *, job_id: int, user: User) -> TranscriptionJobRead:
    job = _get_owned_job(db, job_id=job_id, user=user)
    return _serialize_job(job)


def get_job_result_for_user(db: Session, *, job_id: int, user: User) -> TranscriptRead:
    job = _get_owned_job(db, job_id=job_id, user=user)
    transcript = transcript_repository.get_by_job_id(db, job_id=job.id)

    if transcript is None:
        if job.status in {TranscriptionJobStatus.PENDING, TranscriptionJobStatus.PROCESSING}:
            raise TranscriptionError("Transcript is not ready yet.")
        if job.status == TranscriptionJobStatus.FAILED:
            raise TranscriptionError(job.error_message or "Transcription failed.")
        raise TranscriptionError("Transcript data is not available for this job.")

    return _serialize_transcript(job, transcript)


def build_transcript_download_response(
    db: Session,
    *,
    job_id: int,
    user: User,
    format_name: str,
) -> Response:
    job = _get_owned_job(db, job_id=job_id, user=user)
    transcript = transcript_repository.get_by_job_id(db, job_id=job.id)

    if transcript is None:
        raise TranscriptionError("Transcript is not ready for download.")

    safe_basename = Path(job.source_filename).stem or f"job-{job.id}"
    if format_name == "txt":
        return PlainTextResponse(
            transcript.full_text,
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{safe_basename}.txt"'},
        )

    if format_name == "json":
        payload = TranscriptionDownloadPayload(
            job_id=job.id,
            status=job.status,
            source_filename=job.source_filename,
            transcript=_serialize_transcript(job, transcript),
        )
        return JSONResponse(
            content=json.loads(payload.model_dump_json()),
            headers={"Content-Disposition": f'attachment; filename="{safe_basename}.json"'},
        )

    raise TranscriptionError("Unsupported download format. Use 'txt' or 'json'.")


def _get_owned_job(db: Session, *, job_id: int, user: User) -> TranscriptionJob:
    job = job_repository.get_by_id_for_user(db, job_id=job_id, user_id=user.id)
    if job is None:
        raise TranscriptionError("Transcription job not found.")
    return job


def _serialize_job(job: TranscriptionJob) -> TranscriptionJobRead:
    return TranscriptionJobRead(
        id=job.id,
        status=job.status,
        source_filename=job.source_filename,
        language=job.language,
        model_name=job.model_name,
        duration_seconds=job.duration_seconds,
        error_message=job.error_message,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        transcript_available=job.transcript is not None,
    )


def _serialize_transcript(job: TranscriptionJob, transcript: Transcript) -> TranscriptRead:
    return TranscriptRead(
        job_id=job.id,
        status=job.status,
        full_text=transcript.full_text,
        segments_json=transcript.segments_json,
        confidence=transcript.confidence,
        created_at=transcript.created_at,
    )
