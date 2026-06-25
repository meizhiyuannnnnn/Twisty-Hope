---
description: 功能开发 — 并行启动 fe-agent + be-agent 开发功能，然后 test-agent 测试验证
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Skill, Agent
---

# /develop-feature — 功能开发

## 用途
对指定功能模块，同时唤醒 fe-agent 和 be-agent 并行开发，完成后跑 test-agent 验证。

## 前置条件
- PRD 已确认（req-agent 产出）
- 架构设计已确认（arch-agent 产出）
- API 规范已定义

## 触发时机
- 架构确认后，说"开发 XX 功能"、"实现 XX 模块"

## 执行流程

### 1. 确认范围
列出待开发功能清单，向李振远确认。

### 2. 并行启动 fe-agent + be-agent
同时以 Subagent 唤醒：

**fe-agent**（加载 `agents/fe-agent.md`）：
- 输入：架构设计 + API 文档 + UI 原型（如有）+ PRD 验收标准
- 产出：页面骨架 + 组件 + 状态管理 + API 对接 + 自测

**be-agent**（加载 `agents/be-agent.md`）：
- 输入：架构设计 + OpenAPI 规范 + 数据库设计 + PRD 验收标准
- 产出：Models + Schemas + Services + Routers + 自测

### 3. 联调检查
审阅 fe-agent 和 be-agent 的 API 契约是否对齐，不一致则协调修正。

### 4. 测试（test-agent）
唤醒 test-agent（加载 `agents/test-agent.md`），传递 PRD 验收标准 + API 文档。

### 5. 质量门禁
运行 `/gate`。

### 6. 汇报
汇总各 Agent 状态和测试结果。

## 输出格式

```markdown
## /develop-feature 执行报告

**功能**：[功能名称]
**时间**：[时间]

### Agent 状态
| Agent | 任务 | 状态 |
|-------|------|------|
| fe-agent | 前端开发 | ✅ |
| be-agent | 后端开发 | ✅ |
| test-agent | 测试 | ✅ |

### 质量门禁
| 检查项 | 结果 |
|--------|------|
| Prettier / ESLint / tsc | ✅ |
| Ruff / MyPy / Pytest | ✅ |
```
