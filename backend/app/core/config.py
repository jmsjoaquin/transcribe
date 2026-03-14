from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Transcribe API"
    database_url: str = "postgresql+psycopg://admin:password123@localhost:5433/transcribe_db"
    redis_url: str = "redis://localhost:6379/0"
    transcription_queue_name: str = "transcriptions"
    transcription_job_timeout_seconds: int = 14400
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 1440
    access_token_cookie_name: str = "access_token"
    access_token_cookie_secure: bool = False
    storage_backend: str = "local"
    media_root: str = "./media"
    public_media_base_url: str = ""
    worker_media_access_mode: str = "shared_storage"
    worker_name: str = "transcribe-worker"
    worker_platform: str = "macos-dev"
    whisper_model_size: str = "small"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    cors_allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env", "worker/.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
