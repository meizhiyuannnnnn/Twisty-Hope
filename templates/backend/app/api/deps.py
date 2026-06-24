"""API 依赖注入"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

# 数据库会话依赖
DBSession = Depends(get_db)
