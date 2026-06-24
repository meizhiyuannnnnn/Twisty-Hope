# Skill: quality-gate

## 用途

一键运行项目的全部代码质量检查，生成统一质量报告。

## 使用时机

- 功能开发完成，提交 Review 前
- CI 流水线中自动运行
- maint-agent 修复后验证
- Claude 终审前最后检查

## 执行步骤

```bash
# 1. 前端检查（如有 web/ 目录）
cd web
npx prettier --check "src/**/*.{ts,tsx,css}"
npx eslint "src/**/*.{ts,tsx}"
npx tsc --noEmit
npx vitest run --coverage

# 2. 后端检查（如有 backend/ 目录）
cd ../backend
ruff check .
mypy app/
pytest --cov=app --cov-report=term
```

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
| ESLint   | ✅/❌ |
| TypeScript | ✅/❌ |
| Vitest | ✅/❌ (X/Y 通过) |

### 后端
| 检查项 | 结果 |
|--------|------|
| Ruff | ✅/❌ |
| MyPy | ✅/❌ |
| Pytest | ✅/❌ (X/Y 通过) |

### 未通过项
[如有失败，列出具体错误]
```

### 3. Subagent 合规检查
```bash
# 检查 Claude 对话记录，确认所有 Agent 产出均来自独立 Subagent 调用
# 违规：Claude 在对话中直接扮演 Agent 角色产出内容
# 合规：Claude 使用 Agent 工具以 subagent_type="general-purpose" 调用
```

| 检查项 | 结果 |
|--------|------|
| 所有 Agent 产出均来自 Subagent | ✅/❌ |
| 无 Claude 直接扮演 Agent 的产出 | ✅/❌ |

## 可用 Agent

- Claude（协调者）
- test-agent
- maint-agent
