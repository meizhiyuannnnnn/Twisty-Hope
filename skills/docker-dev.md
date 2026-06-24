# Skill: docker-dev

## 用途

Docker 开发环境管理 — 构建、启动、停止、查看日志、重建。

## 使用时机

- 本地开发环境搭建
- 数据库/Redis 依赖服务启动
- 调试 Docker 相关问题
- 在 Docker 环境中验证修复

## 常用命令

```bash
# 在项目文件夹内执行

# 启动全部服务
docker compose up -d

# 启动特定服务
docker compose up -d db redis

# 查看日志
docker compose logs -f backend

# 查看服务状态
docker compose ps

# 重建并启动（依赖变更时）
docker compose up -d --build

# 重建特定服务
docker compose up -d --build backend

# 停止全部服务
docker compose down

# 停止并清理数据卷
docker compose down -v

# 进入容器调试
docker compose exec backend bash
docker compose exec db psql -U postgres -d app

# 查看资源使用
docker stats
```

## 常见问题

### 前端构建失败（native binding 丢失）
```bash
# 原因：npm ci 在 Linux 丢失 native binding
# 解决：改用 npm install --legacy-peer-deps
```

### 端口冲突
```bash
# 检查端口占用
docker compose ps
netstat -ano | findstr :3000  # Windows
lsof -i :3000                   # Mac/Linux
```

### 模型下载慢（国内）
```bash
# 设置 ModelScope 镜像
HF_ENDPOINT=https://hf-mirror.com
```

## 可用 Agent

- devops-agent
- maint-agent
- Claude（协调者）
