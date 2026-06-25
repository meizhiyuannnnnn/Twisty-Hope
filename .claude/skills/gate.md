---
description: 代码质量门禁 — 一键运行全部质量检查（Prettier+ESLint+TypeScript / Ruff+MyPy+Pytest）
allowed-tools: Bash, Read, Glob, Grep
---

# /gate — 代码质量门禁

## 用途
一键运行项目全部代码质量检查，生成统一质量报告。

## 触发时机
- 功能开发完成，提交 Review 前
- maint-agent 修复后验证
- Claude 终审前
- 说"跑质量检查"、"门禁"、"gate"

## 执行流程

### 1. 前端检查
如果项目有 `web/` 目录：
```bash
cd web && npx prettier --check "src/**/*.{ts,tsx,css}"
cd web && npx eslint "src/**/*.{ts,tsx}"
cd web && npx tsc --noEmit
cd web && npx vitest run
```

### 2. 后端检查
如果项目有 `backend/` 目录：
```bash
cd backend && ruff check .
cd backend && mypy app/
cd backend && pytest --cov=app --cov-report=term
```

### 3. Subagent 合规检查
确认所有 Agent 产出均来自独立 Subagent 调用，Claude 未直接扮演 Agent。

## 输出格式

```markdown
## 质量门禁报告

**项目**：[项目名称]
**时间**：[时间]
**门禁结果**：✅ 全部通过 / ❌ 未通过

### 前端
| 检查项 | 结果 |
|--------|------|
| Prettier | ✅/❌ |
| ESLint | ✅/❌ |
| TypeScript | ✅/❌ |
| Vitest | ✅/❌ (X/Y 通过) |

### 后端
| 检查项 | 结果 |
|--------|------|
| Ruff | ✅/❌ |
| MyPy | ✅/❌ |
| Pytest | ✅/❌ (X/Y 通过) |

### Subagent 合规
| 检查项 | 结果 |
|--------|------|
| 所有产出来自独立 Subagent | ✅/❌ |
| 无 Claude 直接扮演 Agent | ✅/❌ |
```
