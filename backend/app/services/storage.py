from __future__ import annotations

import re
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings

ALLOWED_MEDIA_EXTENSIONS = {
    ".aac",
    ".aiff",
    ".avi",
    ".flac",
    ".m4a",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp3",
    ".mp4",
    ".mpeg",
    ".mpg",
    ".ogg",
    ".wav",
    ".webm",
    ".wmv",
}


class StorageError(Exception):
    pass


@dataclass(slots=True)
class StoredMedia:
    storage_path: str
    absolute_path: Path
    original_filename: str


def save_upload(upload: UploadFile) -> StoredMedia:
    if settings.storage_backend != "local":
        raise StorageError(f"Unsupported storage backend: {settings.storage_backend}")

    if not upload.filename:
        raise StorageError("Uploaded file must include a filename.")

    suffix = Path(upload.filename).suffix.lower()
    content_type = upload.content_type or ""
    if suffix not in ALLOWED_MEDIA_EXTENSIONS and not content_type.startswith(("audio/", "video/")):
        raise StorageError("Only audio and video uploads are supported.")

    safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(upload.filename).stem).strip("-") or "upload"
    relative_path = Path("uploads") / f"{uuid.uuid4().hex}_{safe_stem}{suffix}"
    absolute_path = Path(settings.media_root).expanduser().resolve() / relative_path
    absolute_path.parent.mkdir(parents=True, exist_ok=True)

    with absolute_path.open("wb") as destination:
        upload.file.seek(0)
        shutil.copyfileobj(upload.file, destination)

    return StoredMedia(
        storage_path=relative_path.as_posix(),
        absolute_path=absolute_path,
        original_filename=upload.filename,
    )


def delete_local_file(storage_path: str) -> None:
    if settings.storage_backend != "local":
        return

    absolute_path = Path(settings.media_root).expanduser().resolve() / storage_path
    try:
        absolute_path.unlink()
    except FileNotFoundError:
        return
