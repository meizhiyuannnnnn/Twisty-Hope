# 后端模板 — Python FastAPI + SQLAlchemy + PostgreSQL

## 使用方法

```bash
# 1. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 2. 安装依赖
pip install fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg alembic pydantic redis pytest httpx python-jose passlib[bcrypt]

# 3. 复制公司配置文件
cp ../../ruff.toml . && cp ../../mypy.ini .

# 4. 启动开发
uvicorn app.main:app --reload --port 8000
```

## 目录结构

```
backend/
├── app/
│   ├── api/              # API 路由
│   │   └── deps.py       # 依赖注入（DB session、认证）
│   ├── models/           # SQLAlchemy 模型
│   ├── schemas/          # Pydantic 校验
│   ├── services/         # 业务逻辑
│   ├── core/             # 配置、安全、数据库连接
│   │   ├── config.py     # pydantic-settings 配置
│   │   ├── security.py   # JWT / 密码哈希
│   │   └── database.py   # AsyncSession 工厂
│   └── main.py           # FastAPI 入口
├── alembic/              # 数据库迁移
├── tests/                # Pytest
└── requirements.txt
```

## app/main.py 模板

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

## app/core/config.py 模板

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "My Project"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/db"
    REDIS_URL: str = "redis://localhost:6379"
    SECRET_KEY: str = "change-me-in-production"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
```

## app/core/database.py 模板

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session
```
