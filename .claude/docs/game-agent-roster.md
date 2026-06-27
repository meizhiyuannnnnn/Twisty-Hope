# 游戏 Agent 名册

> 完整 Agent 列表、层级、模型分配。游戏项目启动时由 Claude 协调者按需查阅。
> 源文件位于 `.claude/agents/`，每个 Agent 独立 `.md` 定义。

## Tier 1 — 导演层（Opus）

| Agent | 标识 | 职责 |
|-------|------|------|
| 创意总监 | `creative-director` | 守护游戏创意愿景，解决设计冲突 |
| 技术总监 | `technical-director` | 技术架构决策，性能目标设定 |
| 制作人 | `producer` | 跨部门协调，范围/进度管理 |

## Tier 2 — 部门主管层（Sonnet）

| Agent | 标识 | 职责 |
|-------|------|------|
| 游戏设计师 | `game-designer` | 玩法系统与机制设计 |
| 主程 | `lead-programmer` | 代码架构与工程标准 |
| 美术总监 | `art-director` | 视觉方向与资产管线 |
| 音频总监 | `audio-director` | 音效设计与音乐方向 |
| 叙事总监 | `narrative-director` | 故事/对话/世界观 |
| QA 主管 | `qa-lead` | 质量策略与测试计划 |
| 发布经理 | `release-manager` | 发布就绪与发布协调 |
| 本地化主管 | `localization-lead` | 多语言支持与文化适配 |

## Tier 3 — 专家层

### 编程组（Sonnet）
`gameplay-programmer` `engine-programmer` `ai-programmer` `network-programmer` `tools-programmer` `ui-programmer`

### 设计组（Sonnet）
`systems-designer` `level-designer` `economy-designer` `ux-designer` `world-builder` `live-ops-designer`

### 美术/音频组（Sonnet）
`technical-artist` `sound-designer` `prototyper`

### QA/生产组（Sonnet/Haiku）
`qa-tester`(Haiku) `performance-analyst` `security-engineer` `devops-engineer`(Haiku) `analytics-engineer` `accessibility-specialist`(Haiku) `community-manager`(Haiku) `writer`

## Godot 4 引擎专家

| Agent | 标识 | 模型 |
|-------|------|------|
| Godot 总专家 | `godot-specialist` | Sonnet |
| GDScript 专家 | `godot-gdscript-specialist` | Sonnet |
| Shader 专家 | `godot-shader-specialist` | Sonnet |
| GDExtension 专家 | `godot-gdextension-specialist` | Sonnet |
| C# 专家 | `godot-csharp-specialist` | Sonnet |

## 模型分层策略

| Tier | 模型 | 适用场景 |
|------|------|---------|
| Haiku | `claude-haiku-4-5` | 只读状态检查、格式化、简单查询 |
| Sonnet | `claude-sonnet-4-6` | 实现、设计撰写、单系统分析（默认） |
| Opus | `claude-opus-4-8` | 多文档综合、高风险的阶段门禁判定、跨系统全局审查 |
