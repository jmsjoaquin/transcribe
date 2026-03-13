from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Transcribe API"
    database_url: str = "postgresql+psycopg://admin:password123@localhost:5433/transcribe_db"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 1440
    access_token_cookie_name: str = "access_token"
    access_token_cookie_secure: bool = False
    storage_backend: str = "local"
    media_root: str = "./media"
    public_media_base_url: str = ""
    cors_allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
