---
globs: **/backend/app/**,**/app/**/*.py,**/templates/backend/**
version: 1.0.0
alwaysApply: false
---

# 后端开发规范 — FastAPI + SQLAlchemy + Python

## 技术栈约束
- 框架：FastAPI 0.100+（async）
- 语言：Python 3.11+（type hints 全覆盖）
- ORM：SQLAlchemy 2.0（async + sync）
- 数据校验：Pydantic v2
- 数据库：PostgreSQL 16+
- 缓存：Redis 7+
- 测试：Pytest + httpx
- 代码规范：Ruff + MyPy

## 代码结构
```
backend/
├── app/
│   ├── api/              # API 路由
│   ├── models/           # SQLAlchemy 模型
│   ├── schemas/          # Pydantic Schema
│   ├── services/         # 业务逻辑层
│   ├── core/             # 核心配置
│   └── main.py           # 应用入口
├── alembic/              # 数据库迁移
├── tests/                # 测试
├── requirements.txt
└── Dockerfile
```

## API 设计约定
- 路由命名：RESTful — `GET /users`、`POST /users`、`GET /users/{id}`
- 版本管理：URL 前缀 `/api/v1/`
- 错误响应：统一格式 `{"detail": "...", "code": "ERROR_CODE"}`
- 分页：`offset` + `limit`，返回 `total` + `items`

## Python 规范
- Type hints 必须覆盖所有函数签名
- 禁止裸 `except:`，至少指定 `except Exception`
- 敏感信息不入日志（密码、密钥、Token）
- SQL 参数化查询，禁止字符串拼接
- 配置外置：不硬编码路径、密钥、阈值

## 分层标准
```python
@router.post("/users", response_model=UserOut)
async def create_user(
    user_in: UserCreate,                    # Pydantic 校验
    db: AsyncSession = Depends(get_db),     # 依赖注入
) -> UserOut:
    user = await user_service.create(db, user_in)  # 业务层
    return UserOut.model_validate(user)
```

## 格式化
- Ruff（`ruff.toml`）
- MyPy strict mode（`mypy.ini`）
