---
description: 版本发布流程 — 版本号更新、CHANGELOG 生成、打 Tag、构建验证
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Skill
---

# /release — 版本发布

## 用途
标准版本发布流程：质量门禁 → 版本号 → CHANGELOG → git tag → 推送 → 验证。

## 触发时机
- 修复积累到可发布时
- Milestone 节点
- 正式上线前
- 说"发布"、"上线"、"release"

## 执行流程

### 1. 质量门禁（阻断点）
先运行 `/gate`，不通过则中止。

### 2. 确认版本号
- 查看自上一版本以来的 commit：`git log --oneline <last-tag>..HEAD`
- 向李振远确认版本类型：patch / minor / major
- Semver 规则：patch（Bug 修复）、minor（兼容新功能）、major（破坏性变更）

### 3. 更新版本号
- 前端：`cd web && npm version patch`
- 后端：更新 `backend/app/core/config.py` 中的 VERSION

### 4. 生成 CHANGELOG
按类型分组：Bug 修复 / 新功能 / 安全 / 依赖更新

### 5. 提交、打 Tag、推送
```bash
git add .
git commit -m "chore: release vX.Y.Z"
git tag -a vX.Y.Z -m "vX.Y.Z: [简述]"
git push origin main --tags
```

### 6. 验证
- `docker compose build` 确认构建通过

## 输出格式

```markdown
## /release 执行报告

**版本**：vX.Y.Z
**类型**：patch / minor / major
**变更项**：X 项
**Tag**：✅ 已推送
**质量门禁**：✅ 通过
**Docker 构建**：✅ 通过
```
