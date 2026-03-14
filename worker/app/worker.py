from redis import Redis
from rq import Worker

from worker.app.bootstrap import setup_backend_path

setup_backend_path()

from app.core.config import settings  # noqa: E402


def run() -> None:
    connection = Redis.from_url(settings.redis_url)
    worker = Worker(
        [settings.transcription_queue_name],
        connection=connection,
        name=f"{settings.worker_name}-{settings.worker_platform}",
    )
    worker.work()


if __name__ == "__main__":
    run()
