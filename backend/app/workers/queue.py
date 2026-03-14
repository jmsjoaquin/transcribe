from redis import Redis
from rq import Queue

from app.core.config import settings
from app.models.transcription_job import TranscriptionJob
from app.workers.contracts import TranscriptionJobMessage


class QueueDispatchError(Exception):
    pass


def enqueue_transcription_job(job: TranscriptionJob) -> str:
    message = TranscriptionJobMessage(
        job_id=job.id,
        user_id=job.user_id,
        storage_backend=settings.storage_backend,
        storage_path=job.storage_path,
        source_filename=job.source_filename,
        language=job.language,
        model_name=job.model_name,
        media_access_mode=settings.worker_media_access_mode,
        submitted_at=job.created_at,
    )

    try:
        connection = Redis.from_url(settings.redis_url)
        queue = Queue(
            name=settings.transcription_queue_name,
            connection=connection,
            default_timeout=settings.transcription_job_timeout_seconds,
        )
        queued_job = queue.enqueue(
            "worker.app.jobs.transcriptions.process_transcription_job",
            message.model_dump(mode="json"),
            job_id=f"transcription:{job.id}",
        )
    except Exception as exc:
        raise QueueDispatchError("Failed to enqueue transcription job.") from exc

    return queued_job.id
