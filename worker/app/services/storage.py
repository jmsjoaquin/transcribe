from pathlib import Path

from worker.app.bootstrap import setup_backend_path

setup_backend_path()

from app.core.config import settings  # noqa: E402


class WorkerStorageError(Exception):
    pass


def resolve_media_path(storage_path: str) -> Path:
    if settings.worker_media_access_mode != "shared_storage":
        raise WorkerStorageError(
            "Only shared_storage mode is currently implemented for worker media access."
        )

    if settings.storage_backend != "local":
        raise WorkerStorageError(
            f"Unsupported storage backend for shared storage mode: {settings.storage_backend}"
        )

    absolute_path = Path(settings.media_root).expanduser().resolve() / storage_path
    if not absolute_path.exists():
        raise WorkerStorageError(
            f"Media file not found at resolved worker path: {absolute_path}"
        )
    return absolute_path
