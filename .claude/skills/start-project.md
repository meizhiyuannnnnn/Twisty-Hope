---
description: 新项目启动向导 — 环境检查、项目初始化、需求分析一站式流程
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Skill, Agent
---

# /start-project — 新项目启动向导

## 用途
新项目从零到 PRD：环境检查 → 项目脚手架 → 需求分析，一站式启动。

## 触发时机
- 李振远确认新项目立项
- 说"开始新项目"、"创建项目"、"启动 P00X"

## 执行流程

### 第一阶段：环境检查
检查开发环境版本：Node.js >= 20、npm >= 10、Python >= 3.11、Docker >= 24、Git >= 2.40。若有未达标项报告并询问是否继续。

### 第二阶段：项目初始化
1. 向李振远确认：项目名称、项目编号（P00X）、是否需要桌面端
2. 创建 `pXXX-项目名/` 文件夹
3. 从 `templates/web/` 复制前端模板，`npm install`
4. 从 `templates/backend/` 复制后端模板，创建 venv，`pip install -r requirements.txt`
5. 如需桌面端，从 `templates/desktop/` 复制
6. 复制共享 lint 配置（`.prettierrc`、`eslint.config.js`、`ruff.toml`、`mypy.ini`）
7. 创建 `.env.example` 和 `.env`

### 第三阶段：需求分析
1. 以 `Agent` 工具唤醒 `req-agent`（加载 `agents/req-agent.md`）
2. 传递：项目背景、目标用户、时间约束
3. req-agent 产出 PRD → 提交李振远确认

### 第四阶段：收尾
1. 更新 `CLAUDE.md` 项目看板表格
2. 汇总汇报

## 输出格式

```markdown
## /start-project 执行报告

**项目**：[名称] (P00X)
**时间**：[时间]

### 环境检查
| 工具 | 版本 | 状态 |
|------|------|------|
| Node.js | X.Y.Z | ✅ |
| Python | X.Y.Z | ✅ |
| Docker | X.Y.Z | ✅ |

### 项目初始化
- ✅ web/ — React + Vite + TypeScript
- ✅ backend/ — FastAPI + SQLAlchemy
- ✅ lint 配置
- ✅ .env.example

### 需求分析
- req-agent 已唤醒
- 下一步：李振远确认 PRD
```
