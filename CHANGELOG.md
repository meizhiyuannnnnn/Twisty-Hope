# Changelog

本文件记录彼方希冀程序开发公司所有项目的版本变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。
 
---

## [P001] 音频分离工具

### v1.0.0 — 2026-06-03

#### Added
- 音频文件上传（MP3/WAV/FLAC/M4A/OGG）
- Demucs AI 音源分离（人声/鼓/贝斯/其他）
- 分离结果在线试听和下载
- Docker Compose 一键部署（PostgreSQL + Redis + FastAPI + Nginx）
- 后台任务队列（Redis Queue）
- 文件自动清理（24h 过期）

#### Technical
- React 18 + Vite 5 + TypeScript 前端
- FastAPI 0.100+ 后端
- SQLAlchemy 2.0 异步 ORM
- Alembic 数据库迁移
- Pytest + Playwright 全量测试
- Docker 多阶段构建

---

## [Unreleased]

### Added
- `tools/wrap_debug_prints.py` — GDScript 调试输出守卫工具
- `.claude/hooks/*.ps1` — PowerShell 版会话/提交钩子（3 个）
- `.claude/settings.dsh.json` — DeepSeek Harness 的 hook 配置（本地文件，不入库）
- `.claude/docs/automation-setup.md` — 自动化配置与编码约定说明
- 游戏项目远程备份：GitHub 私有仓库 `meizhiyuannnnnn/Twisty-Hope-Game`
- `p001-audio-separator/docs/prd-audio-separation.md` 附录 A — P001 经验教训（原 `.claude/memory/` 内容，原先未入库）

### Changed
- 路线图 / 工作流文档 / CLAUDE.md 看板统一到实际进度（Phase 0–8 完成，Phase 9 起暂停）
- `production/session-state/active.md` 更新为暂停状态 + 本次会话记录
- 安全修复：清除所有硬编码数据库凭据
- 配置统一：根级 .env.example、settings.json、.gitattributes
- 文档补全：CHANGELOG.md、根级 README.md、memory 体系

### Fixed
- CORS_ORIGINS 格式统一为 JSON 数组
- .claude/ 目录加入 gitignore
- 模板 SECRET_KEY 改为空值 + 启动检查
- 游戏项目：`project.godot` 项目名乱码、54 处调试输出泄漏到导出包（在游戏仓库 `f1133db`）
- CLAUDE.md 中指向 `.claude/memory/` 的死链（该目录未入库）改为指向真实存在的文档
- `.gitattributes` 补 `*.ps1 text eol=crlf`（PS 5.1 在 LF 下会误判中文字符串边界）

### Security
- `zy/` 加入 `.gitignore`：实习成绩表与报告含学号等个人信息，不纳入版本库

### Deprecated
- 游戏仓库 `docs/development-roadmap.md`（Phase 编号与公司路线图冲突，已标注废止）
- `.claude/hooks/*.sh`（本机 bash 不可用，保留作参考）

