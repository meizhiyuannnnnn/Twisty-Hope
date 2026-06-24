"""Application configuration via pydantic-settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings, loaded from environment variables / .env file."""

    PROJECT_NAME: str = "音频分离工具"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database — 必须通过环境变量或 .env 显式配置
    DATABASE_URL: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Security
    SECRET_KEY: str = ""  # 生产环境必须设置，空值拒绝启动

    # CORS — 生产环境填写实际域名
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DEBUG and not self.SECRET_KEY:
            raise ValueError(
                "SECRET_KEY 未设置。生产环境必须设置 SECRET_KEY 环境变量。"
            )
        if not self.DATABASE_URL:
            raise ValueError(
                "DATABASE_URL 未设置。请通过环境变量或 .env 文件配置数据库连接。"
            )


settings = Settings()
