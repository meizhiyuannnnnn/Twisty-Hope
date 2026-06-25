---
description: 团队并行审查 — 同时启动质量门禁 + Claude Review + sec-agent 安全审查
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Skill, Agent
---

# /team-review — 团队并行审查

## 用途
并行运行三项审查：质量门禁 + Claude 代码审查 + sec-agent 安全审查。

## 触发时机
- 功能开发完成
- 上线前最终检查
- 说"全面审查"、"团队审查"

## 执行流程

### 并行执行三项检查

**轨道 1 — 质量门禁**：运行 `/gate` 全部检查。

**轨道 2 — Claude 代码审查**：审阅 git diff，检查代码质量、架构一致性、性能。

**轨道 3 — 安全审查**：以 Subagent 唤醒 sec-agent（`agents/sec-agent.md`），输出安全报告。

### 汇总报告
合并三项结果，标注阻断项和建议项。

## 输出格式

```markdown
## /team-review 综合审查报告

**项目**：[项目名称]
**时间**：[时间]
**综合结论**：✅ 可合并 / ⚠️ 有建议 / ❌ 有阻断

### 质量门禁
✅ / ❌

### 代码审查 (Claude)
发现问题 X 个

### 安全审查 (sec-agent)
发现问题 X 个 (🔴 Y, 🟡 Z)

### 阻断项
[必须修复]

### 建议项
[后续修复]
```

## 依赖
- Skill: quality-gate
- Agent: sec-agent
