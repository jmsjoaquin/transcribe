from sqlalchemy import Select, desc, select
from sqlalchemy.orm import Session

from app.models.transcription_job import TranscriptionJob


def create(db: Session, job: TranscriptionJob) -> TranscriptionJob:
    db.add(job)
    return job


def get_by_id_for_user(db: Session, *, job_id: int, user_id: int) -> TranscriptionJob | None:
    statement = select(TranscriptionJob).where(
        TranscriptionJob.id == job_id,
        TranscriptionJob.user_id == user_id,
    )
    return db.scalar(statement)


def list_for_user(db: Session, *, user_id: int, limit: int = 50) -> list[TranscriptionJob]:
    statement: Select[tuple[TranscriptionJob]] = (
        select(TranscriptionJob)
        .where(TranscriptionJob.user_id == user_id)
        .order_by(desc(TranscriptionJob.created_at), desc(TranscriptionJob.id))
        .limit(limit)
    )
    return list(db.scalars(statement))
