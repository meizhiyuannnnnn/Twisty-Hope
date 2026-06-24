# 音频分离工具

> 免费在线音频人声/伴奏分离 Web 应用 — 基于 Demucs AI 模型

---

## 项目概况

| 项目 | 内容 |
|------|------|
| **项目名称** | 音频分离工具 |
| **版本** | v1.0 |
| **开发日期** | 2026-06-02 ~ 2026-06-03 |
| **技术栈** | React + Vite + TypeScript (前端) / Python FastAPI (后端) / Demucs (AI) |
| **部署方式** | Docker Compose |
| **状态** | ✅ 已完成 |

---

## 版本记录

### v1.0 — 2026-06-03

**功能：**
- 音频文件上传（MP3/WAV/FLAC/M4A/OGG，100MB 上限）
- 2 轨分离：人声 + 伴奏
- 4 轨分离：人声 + 鼓 + 贝斯 + 其他
- 实时 WebSocket 进度推送
- 分轨独立播放控制（独奏/静音/音量）
- 和弦自动识别
- 变速变调处理
- 历史记录（localStorage 持久化）
- 关闭网站自动清除当前结果（sessionStorage），历史记录独立保留

**本次修复（2026-06-03）：**
- WebSocket 自动连接 + HTTP 轮询回退机制（防止处理卡死）
- sessionStorage 替代 localStorage 持久化会话（关闭标签页自动清除）
- 处理计时器 + 首次模型下载提示
- Dockerfile 跨平台兼容修复

**技术决策：**
- Demucs 模型从 ModelScope 下载（国内可访问，避免 GitHub 依赖）
- 前端 sessionStorage 存储会话，localStorage 存储历史
- Redis 发布/订阅实现实时进度推送
- Worker 单线程串行处理（FIFO）

---

## 文件结构

```
音频分离工具/
├── README.md                        # 本文件
├── docker-compose.yml               # 一键部署编排
├── .env / .env.example              # 环境变量配置
├── docs/                            # 项目文档
│   ├── prd-audio-separation.md      # 产品需求文档
│   ├── claude-final-review.md       # Claude 终审报告
│   └── deploy-guide.md              # 部署指南
├── web/                             # React 前端源码
│   ├── src/
│   │   ├── components/              # UI 组件
│   │   ├── pages/                   # 页面
│   │   ├── hooks/                   # 自定义 Hooks
│   │   ├── stores/                  # Zustand 状态管理
│   │   ├── services/                # API 调用
│   │   └── types/                   # TypeScript 类型
│   ├── Dockerfile                   # 生产构建
│   ├── Dockerfile.dev               # 开发模式
│   ├── nginx.conf                   # Nginx 配置
│   └── vite.config.ts               # Vite 配置 + API 代理
└── backend/                         # Python FastAPI 后端
    ├── app/
    │   ├── api/                     # API 路由 + WebSocket
    │   ├── ai/                      # AI 模型（Demucs）
    │   ├── models/                  # 数据库模型
    │   ├── schemas/                 # Pydantic 模型
    │   ├── services/                # 业务逻辑
    │   └── worker/                  # Redis 任务 Worker
    ├── tests/                       # 测试套件
    ├── Dockerfile
    └── requirements.txt
```

---

## 快速启动

```bash
# 生产模式（Docker）— 在项目目录内执行
cd 音频分离工具
docker compose up -d --build

# 前端开发模式（热更新）
cd 音频分离工具/web
npm run dev
```

网站访问：http://localhost:3000

---

## 关键 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/upload` | POST | 上传音频文件 |
| `/api/task/{id}` | GET | 查询任务状态 |
| `/api/task/{id}/separate` | POST | 触发分离 |
| `/api/task/{id}/chords` | POST | 触发和弦分析 |
| `/api/task/{id}/transform` | POST | 触发变速变调 |
| `/api/task/{id}/download/{stem}` | GET | 下载分轨文件 |
| `/ws/task/{id}` | WS | 实时进度推送 |

---

## 维护记录

| 日期 | 内容 |
|------|------|
| 2026-06-03 | v1.0 完成 — 修复 WebSocket 卡死 + 关闭清除会话 + 项目归档 |
| 2026-06-02 | 初始开发完成 — 前后端 + Docker 部署 |
