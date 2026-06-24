# Skill: project-init

## 用途

从模板一键初始化新项目，创建标准化目录结构并安装依赖。

## 使用时机

- 新项目立项后
- 李振远确认项目启动

## 执行步骤

```bash
# 1. 创建项目文件夹
mkdir <项目名>
cd <项目名>

# 2. 复制 web 模板
cp -r ../templates/web web
cd web
# 替换 {{PROJECT_NAME}} 为实际项目名
# 安装依赖
npm install
cd ..

# 3. 复制 backend 模板
cp -r ../templates/backend backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..

# 4. 复制桌面模板（如需要）
cp -r ../templates/desktop desktop
cd desktop && npm install && cd ..

# 5. 创建项目配置文件
cp ../.env.example .env.example
touch .env

# 6. 复制公司共享配置
cp ../.prettierrc web/.prettierrc
cp ../eslint.config.js web/eslint.config.js
cp ../ruff.toml backend/ruff.toml
cp ../mypy.ini backend/mypy.ini

# 7. 初始化 Git
git init  # 或 git checkout -b feat/<项目名>
```

## 输出

```markdown
## 项目初始化完成

**项目名**：[项目名]
**路径**：[路径]
**初始化内容**：
- ✅ web/ — React + Vite + TypeScript 前端
- ✅ backend/ — FastAPI + SQLAlchemy 后端
- ✅ desktop/ — Electron 桌面壳（如有）
- ✅ .env.example — 环境变量模板
- ✅ 共享配置 — Prettier / ESLint / Ruff / MyPy

**下一步**：
1. 填写 .env 环境变量
2. 更新 CLAUDE.md 项目看板
3. 启动 req-agent 编写 PRD
```

## 可用 Agent

- Claude（协调者）
