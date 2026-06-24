# 后端模板 — Python FastAPI + SQLAlchemy + PostgreSQL

## 快速启动

```bash
# 1. 复制模板到新项目
cp -r templates/backend 新项目/backend
cd 新项目/backend

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 复制公司配置文件
cp ../../ruff.toml .
cp ../../mypy.ini .

# 5. 初始化数据库（需先启动 PostgreSQL）
alembic upgrade head

# 6. 启动开发
uvicorn app.main:app --reload --port 8000
```

## 技术栈

| 层面 | 技术 |
|------|------|
| 框架 | FastAPI + Uvicorn |
| 类型校验 | Pydantic v2 |
| ORM | SQLAlchemy 2.0 (async) |
| 数据库 | PostgreSQL + asyncpg |
| 缓存 | Redis |
| 迁移 | Alembic |
| 认证 | JWT + bcrypt |
| 测试 | Pytest + httpx |
| 格式化 | Ruff + MyPy |

## 模板包含

- ✅ 可运行的 FastAPI 应用（含 `/health` 端点）
- ✅ CORS 中间件配置
- ✅ 环境变量配置（pydantic-settings）
- ✅ 数据库异步会话管理
- ✅ JWT 认证工具
- ✅ Alembic 迁移配置
- ✅ Pytest 测试示例（含异步测试）
- ✅ 标准目录结构（api/models/schemas/services/core）

## 变量替换

模板中的 `{{PROJECT_NAME}}` 需替换为实际项目名。
