---
description: 需求到架构流水线 — req-agent 产出 PRD 后确认，自动交接给 arch-agent
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Skill, Agent
---

# /team-init — 需求到架构流水线

## 用途
按顺序运行：req-agent（需求分析）→ 李振远确认 → arch-agent（架构设计），完成需求到设计全流程。

## 触发时机
- 新项目立项后
- 说"启动需求分析"、"开始设计"、"需求到架构"

## 前置条件
- 项目文件夹已初始化（通过 `/start-project` 或手动）
- 李振远提供了项目背景和目标

## 执行流程

### 1. req-agent — 需求分析
- 以 Subagent 唤醒 req-agent（`agents/req-agent.md`）
- 传递：项目背景、目标用户、约束条件
- 产出：PRD 文档（功能列表 + 验收标准 + 优先级）

### 2. 需求确认（阻断点）
- PRD 提交李振远
- 等待确认或修改反馈
- 修改则回到步骤 1，确认则进入步骤 3

### 3. arch-agent — 架构设计
- 以 Subagent 唤醒 arch-agent（`agents/arch-agent.md`）
- 传递：已确认 PRD + 技术栈约束
- 产出：架构设计文档（模块划分 + API + 数据库 + 技术选型）

### 4. 架构确认
- 方案提交李振远确认

### 5. 流转通知
通知下游 Agent 就绪，传递架构方案。

## 输出格式

```markdown
## /team-init 执行报告

**项目**：[项目名称]
**时间**：[时间]

### 第一阶段：需求分析 (req-agent)
- **产出**：PRD 文档
- **功能点**：X 个 (P0: X, P1: Y, P2: Z)
- **状态**：✅ 李振远已确认

### 第二阶段：架构设计 (arch-agent)
- **产出**：架构设计文档
- **模块**：前端 X / 后端 Y
- **API 端点**：X 个
- **数据库表**：Y 张
- **状态**：待李振远确认

### 下一步
1. 李振远确认架构
2. 启动 `/team-dev` 并行开发
```

## 依赖
- Agent: req-agent, arch-agent
