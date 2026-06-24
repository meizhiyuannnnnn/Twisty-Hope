# 音频分离 Web 应用 — 部署指南

> **适用**: Docker Compose 一键部署
> **要求**: Docker 24+ / Docker Compose v2

---

## 快速启动

```bash
# 1. 克隆项目
git clone <repo-url> && cd <project-root>

# 2. (可选) 配置环境变量
cp .env.example backend/.env

# 3. 启动所有服务
docker compose up -d --build

# 4. 查看运行状态
docker compose ps

# 5. 查看日志
docker compose logs -f
```

启动后访问:
- **前端页面**: http://localhost:3000
- **API 文档 (Swagger)**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

---

## 服务架构

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    web       │────▶│   backend    │────▶│     db       │
│  Nginx:3000  │     │ FastAPI:8000 │     │ PostgreSQL   │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                     ┌──────▼───────┐     ┌──────────────┐
                     │    worker    │────▶│    redis     │
                     │  音频处理    │     │  任务队列     │
                     └──────────────┘     └──────────────┘
```

| 服务 | 端口 | 职责 |
|------|------|------|
| `web` | 3000 | React SPA 静态托管 + API 反向代理 |
| `backend` | 8000 | FastAPI 业务 API、文件上传/下载 |
| `worker` | — | Redis 队列消费，AI 模型推理 |
| `db` | 5432 | PostgreSQL 任务记录存储 |
| `redis` | 6379 | 任务队列 + 速率限制 + 进度发布 |

---

## GPU 加速（可选）

默认使用 CPU 推理（慢）。若有 NVIDIA GPU：

1. 安装 [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
2. 编辑 `docker-compose.yml`，取消 worker 服务的 `deploy.resources` 注释
3. 修改 worker 环境变量 `DEVICE=cuda`
4. 重启: `docker compose up -d --build`

---

## 常用操作

```bash
# 停止服务
docker compose down

# 停止+删除数据卷（⚠️ 会清除数据库和上传文件）
docker compose down -v

# 仅重启某个服务
docker compose restart backend

# 进入容器调试
docker compose exec backend bash
docker compose exec db psql -U postgres -d app

# 查看 Redis 队列长度
docker compose exec redis redis-cli LLEN audio:tasks

# 执行数据库迁移（如需要）
docker compose exec backend alembic upgrade head
```

---

## 生产环境 checklist

- [ ] 修改 `docker-compose.yml` 中 PostgreSQL 密码
- [ ] 配置 `CORS_ORIGINS` 为实际域名
- [ ] 启用 HTTPS（Nginx + Let's Encrypt 或 CDN）
- [ ] 配置防火墙，仅暴露 3000 端口（前端代理了所有后端请求）
- [ ] 设置 `restart: unless-stopped`（已配置）
- [ ] 备份 PostgreSQL 数据卷

---

## 资源预估

| 配置 | CPU 模式 | GPU (T4) 模式 |
|------|---------|--------------|
| 最小内存 | 4 GB | 8 GB |
| 推荐内存 | 8 GB | 16 GB |
| 磁盘 | 20 GB | 20 GB |
| 处理 80MB 文件 | ~30 分钟 | ~3-5 分钟 |
