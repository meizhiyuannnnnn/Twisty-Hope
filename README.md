# 彼方希冀程序开发公司

> Web 应用 + 桌面端 AI 产品开发 | AI Agent 协作制

---

## 项目列表

| 编号 | 项目 | 状态 | 技术栈 |
|------|------|------|--------|
| P001 | 音频分离工具 | ✅ v1.0 | React + FastAPI + Demucs AI + Docker |

---

## 快速开始

### 环境要求

- Node.js 18+ | Python 3.11+ | Docker + Docker Compose
- WPS Office 12.0+（文档处理）

### P001 音频分离工具

```bash
cd p001-audio-separator
cp .env.example .env    # 填写配置
docker compose up -d     # 启动全部服务
```

访问 `http://localhost:3000`

---

## 目录结构

```
├── CLAUDE.md              # AI 协调者手册
├── README.md              # 本文件（人类开发者入口）
├── CHANGELOG.md           # 版本变更记录
├── agents/                # Agent 角色手册（13 个 Agent）
├── skills/                # 公司 Skill 定义
├── templates/             # 项目脚手架（web / backend / desktop）
├── .claude/               # Claude Code 配置与记忆
│
├── p001-audio-separator/   # P001 音频分离工具
│   ├── backend/           # FastAPI 后端
│   ├── web/               # React 前端
│   └── docs/              # 项目文档
│
└── [未来项目]/            # P002, P003...
```

---

## 协作规范

- **Agent 制**：所有开发 Agent 以独立 Subagent 运行
- **代码规范**：Prettier + ESLint（前端）、Ruff + MyPy（后端）
- **提交规范**：[Conventional Commits](https://www.conventionalcommits.org/)
- **分支策略**：Trunk-based（main 随时可发布）

---

## 许可证

内部项目，保留所有权利。
