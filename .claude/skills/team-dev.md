---
description: 团队并行开发 — 同时启动 fe-agent + be-agent 开发功能
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Skill, Agent
---

# /team-dev — 团队并行开发

## 用途
对当前项目的指定功能，同时唤醒 fe-agent 和 be-agent 以独立 Subagent 并行开发。Claude 仅担任调度者和把关者。

## 触发时机
- 架构设计确认后
- 说"并行开发"、"前后端一起做"、"启动团队开发"

## 前置条件
- PRD 已确认（req-agent 产出）
- 架构设计已确认（arch-agent 产出）
- API 规范已定义

## 执行流程

### 1. 确认范围
向李振远确认：功能模块名称、优先级、是否需要 AI 模块。

### 2. 并行启动
**同时**以 Subagent 唤醒：

**fe-agent**（`agents/fe-agent.md`）：
- 输入：架构设计 + API 文档 + UI 原型 + PRD 验收标准
- 产出：页面组件 + 状态管理 + API 对接 + 自测

**be-agent**（`agents/be-agent.md`）：
- 输入：架构设计 + OpenAPI + 数据库设计 + PRD 验收标准
- 产出：Models + Schemas + Services + Routers + 自测

### 3. 集成检查
Claude 审阅前后端 API 契约是否对齐，偏差则协调修正。

### 4. 汇报
合并两个 Agent 产出摘要，汇报李振远。

## 输出格式

```markdown
## /team-dev 执行报告

**功能**：[功能名称]
**项目**：[项目名称]

### fe-agent
| 产出 | 文件数 | 状态 |
|------|--------|------|
| 页面组件 | X | ✅ |
| 状态管理 | X | ✅ |
| API 调用层 | X | ✅ |

### be-agent
| 产出 | 文件数 | 状态 |
|------|--------|------|
| Models | X | ✅ |
| API 端点 | X | ✅ |
| Services | X | ✅ |

### API 契约对齐
✅ 一致 / ⚠️ 有偏差已修正

### 下一步
- 运行 `/gate` 质量门禁
- 唤醒 test-agent 测试
```

## 依赖
- Agent: fe-agent, be-agent
