---
globs: **/docker-compose.yml,**/Dockerfile,**/docker-compose.*.yml,**/.env.example
version: 1.0.0
alwaysApply: false
---

# 基础设施配置规范

## Docker Compose 规范
- 标准端口：前端 3000、后端 8000、DB 5432、Redis 6379
- 每个服务必须有 `healthcheck`
- 敏感信息通过 `.env` 传入，不硬编码在 compose 文件中
- 使用命名卷（named volumes）做数据持久化

## Dockerfile 规范
- 多阶段构建（multi-stage build）减小镜像体积
- 基础镜像锁定版本（`python:3.12-slim`，不用 `:latest`）
- 前端：`npm ci` → 构建阶段 → nginx 静态文件
- 后端：非 root 用户运行
- `.dockerignore` 必须排除 `node_modules`、`.venv`、`__pycache__`、`.git`

## 环境变量规范
- `.env.example` 提交到 Git（不含真实值）
- `.env` 不进 Git（在 `.gitignore` 中）
- 变量命名：大写 + 下划线（`DATABASE_URL`、`SECRET_KEY`）
- 必需变量标注 `# 必填`，可选变量标注默认值

## 安全配置
- CORS 限制可信源，禁用 `allow_origins=["*"]`
- 生产环境强制 HTTPS
- 数据库密码、API Key 通过环境变量注入
- Dockerfile 中不得用 `ENV` 设置密钥

## .env.example 模板
```env
# 数据库连接 — 必填
DATABASE_URL=postgresql://user:password@db:5432/dbname

# Redis — 必填
REDIS_URL=redis://redis:6379/0

# 应用密钥 — 必填，生成方式: openssl rand -hex 32
SECRET_KEY=change-me-to-random-string
```
