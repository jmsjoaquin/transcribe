from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transcript import Transcript


def get_by_job_id(db: Session, *, job_id: int) -> Transcript | None:
    statement = select(Transcript).where(Transcript.job_id == job_id)
    return db.scalar(statement)
