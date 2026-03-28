from redis import Redis
from rq import SimpleWorker, Worker

from worker.app.bootstrap import setup_backend_path

setup_backend_path()

from app.core.config import settings  # noqa: E402


def run() -> None:
    connection = Redis.from_url(settings.redis_url)
    worker_class = SimpleWorker if settings.worker_use_simple_worker else Worker
    worker = worker_class(
        [settings.transcription_queue_name],
        connection=connection,
        name=f"{settings.worker_name}-{settings.worker_platform}",
    )
    worker.work()


if __name__ == "__main__":
    run()
