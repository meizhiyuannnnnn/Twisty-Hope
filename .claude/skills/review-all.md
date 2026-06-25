---
description: 全栈审查 — 质量门禁 + Claude 代码 Review + sec-agent 安全审查，一次跑完
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Skill, Agent
---

# /review-all — 全栈审查

## 用途
对当前项目运行三项检查：质量门禁 + Claude 代码审查 + sec-agent 安全审查。

## 触发时机
- 功能阶段性完成
- 上线前最终检查
- 说"全面审查"、"最终检查"、"上线前检查"

## 执行流程

### 1. 质量门禁（基础层）
运行 `/gate` 的全部检查。不通过则先修再继续。

### 2. Claude 代码审查
审查 git diff（相对于 main），检查：
- 代码质量（可读性、复杂度）
- 架构一致性（是否符合架构设计）
- 性能隐患（N+1 查询、不必要的重渲染）
- 可复用性（重复代码、抽象机会）

### 3. 安全审查（sec-agent）
以 Subagent 唤醒 sec-agent（加载 `agents/sec-agent.md`），代码安全检查清单。

### 4. 汇总报告
合并三项结果，分阻断项和建议项。

## 输出格式

```markdown
## /review-all 综合审查报告

**项目**：[项目名称]
**审查时间**：[时间]
**综合结论**：✅ 可合并 / ⚠️ 有建议 / ❌ 有阻断

### 质量门禁
✅ 全部通过 / ❌ 未通过

### 代码审查 (Claude)
审查文件 X 个，发现问题 Y 个

### 安全审查 (sec-agent)
发现问题 X 个 (🔴 Y, 🟡 Z)

### 阻断项
[必须修复的问题]

### 建议项
[后续可修的问题]
```
