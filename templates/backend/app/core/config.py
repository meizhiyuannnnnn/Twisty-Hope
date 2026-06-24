"""应用配置 — 从环境变量加载"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "{{PROJECT_NAME}}"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # 数据库 — 必须通过环境变量显式配置
    DATABASE_URL: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # 安全 — 生产环境必须设置，空值拒绝启动
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

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
