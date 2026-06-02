"""Application configuration via pydantic-settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings, loaded from environment variables / .env file."""

    PROJECT_NAME: str = "音频分离工具"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/app"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100 MB
    MAX_DURATION: int = 15 * 60  # 15 minutes in seconds

    # Allowed audio MIME types
    ALLOWED_MIME_TYPES: list[str] = [
        "audio/mpeg",
        "audio/mp3",
        "audio/wav",
        "audio/x-wav",
        "audio/wave",
        "audio/flac",
        "audio/x-flac",
        "audio/mp4",
        "audio/x-m4a",
        "audio/ogg",
        "application/ogg",
        "audio/vorbis",
    ]

    # Rate limiting
    RATE_LIMIT_PER_HOUR: int = 20

    # File cleanup
    FILE_RETENTION_HOURS: int = 24

    # Output encoding
    MP3_BITRATE: str = "320k"

    # AI Model settings
    DEMUCS_MODEL: str = "htdemucs"  # Options: htdemucs, htdemucs_ft, htdemucs_6s
    DEVICE: str = "cuda"  # "cuda" or "cpu"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
