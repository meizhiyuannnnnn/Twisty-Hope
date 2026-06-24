# 项目维护 Agent — 可用 Skills

> 这些是 maint-agent 在日常维护工作中可调用的专业技能。使用 `Skill` 工具调用。

## quality-gate
- **用途**：修复后跑全量质量门禁（lint + typecheck + test）
- **使用时机**：每次修复完成后
- **效果**：一键验证代码质量是否达标

## open-source
- **用途**：开源项目管理（版本发布、社区 Issue/PR 模板、许可证合规）
- **使用时机**：项目开源发布、版本 Tag、社区 Issue 管理时
- **效果**：GitHub Release 最佳实践、Contributing 指南、Semantic Versioning

## docker-dev
- **用途**：Docker 环境验证
- **使用时机**：修复涉及环境配置/Dockerfile 变更时
- **效果**：在 Docker 环境中验证修复

## release
- **用途**：版本发布流程
- **使用时机**：修复积累到可发布时
- **效果**：更新版本号 → changelog → tag → 通知

## find-skills
- **用途**：发现新的维护相关 skill
- **使用时机**：现有 skill 不足以完成维护任务时
- **效果**：从社区搜索和安装新 skill
