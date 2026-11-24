# 游戏实际工作流 — 《彼方希冀》

> 本文档描述当前阶段的**实际工作循环**，不是理想模型。
> 理想 7 阶段模型见 `game-workflow.md`（Phase 3+ 逐步启用）。
> 进度以 `.claude/docs/game-development-roadmap.md` 为准。

---

## 当前阶段：⏸️ 暂停（2026-11-24）

Phase 0–8 已全部完成（115 事件、6 主线任务、9 车厢、6 职业）。游戏开发于 2026-11-24 收尾归档，恢复时从 **Phase 9 视觉打磨** 开始。

恢复开发前先读：
- 游戏项目 `docs/DEV-STATUS.md`（完成度 / 内容量 / 已知问题）
- 本目录 `game-development-roadmap.md`（Phase 9 任务清单）

下面的工作循环在恢复开发后照常适用。

---

## 实际工作循环（5 步）

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  ① 李振远玩游戏 → 确定本次目标                       │
│       ↓                                             │
│  ② Claude 读取 active.md → 拆解任务                  │
│       ↓                                             │
│  ③ 核心 Agent 实现（Subagent 模式）                  │
│       ↓                                             │
│  ④ Claude Review（对照 quality-standards）           │
│       ↓                                             │
│  ⑤ 李振远在 Godot 验证                              │
│       ↓                                             │
│  通过 → git commit → 回到 ①                         │
│  不通过 → 反馈修正 → 回到 ③                         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 各步骤详解

**① 玩游戏 → 定目标**
- 李振远运行 Godot，玩当前版本
- 发现需要改进的地方（视觉效果、游戏手感、Bug、新功能）
- 用自然语言描述本次目标（"让背景接缝更自然"、"加入角色像素动画"）

**② Claude 拆解任务**
- 读取 `production/session-state/active.md` 恢复上下文
- 将目标拆解为具体的技术任务
- 决定需要唤醒哪些 Agent（参考 core-team.md）
- 每个任务有明确的输入、输出、验收标准

**③ Agent 实现**
- 每个 Agent 以独立 Subagent 运行（强制隔离）
- 遵循 `game-quality-standards.md` 的规范
- 产出：代码修改 + 简要说明

**④ Claude Review**
- 对照 `game-quality-standards.md` 逐项检查
- 代码质量、视觉一致、性能影响、数据安全
- 有问题 → 反馈给 Agent 修正
- 无问题 → 进入 ⑤

**⑤ 李振远验证**
- 在 Godot 中实际运行，看效果
- 通过 → `git commit`（游戏项目仓库）
- 不通过 → 描述问题，回到 ③
- 更新 `active.md` 记录本次完成内容

---

## Commit 纪律

| 规则 | 说明 |
|------|------|
| **每次验证通过后立即 commit** | 不等积累，不攒多个功能 |
| **commit message 用中文** | 描述做了什么、为什么 |
| **两个仓库分别提交** | 游戏项目（Documents/新建游戏项目/）和公司仓库（Desktop/彼方希冀程序开发公司/） |
| **不提交未完成的工作** | 如果功能做了一半，用 `git stash` 或分支 |
| **commit 前检查** | `git status` 确认没有意外文件 |

---

## Agent 调度规则

### 核心 5 个（每次会话可能用到）

| Agent | 何时唤醒 | 职责 |
|-------|---------|------|
| `godot-gdscript-specialist` | GDScript 代码编写、Bug 修复 | 实现主力 |
| `technical-artist` | 视觉效果、Shader、粒子 | 视觉升级 |
| `lead-programmer` | 架构决策、代码审查、复杂重构 | 技术把关 |
| `gameplay-programmer` | 游戏逻辑、系统交互、事件系统 | 玩法实现 |
| `art-director` | 美术方向、素材选型、风格一致性 | 视觉决策 |

### 按需 3 个（特定问题时唤醒）

| Agent | 何时唤醒 | 职责 |
|-------|---------|------|
| `creative-director` | 玩法方向争议、设计冲突 | 创意决策 |
| `game-designer` | 系统设计、数值平衡、事件设计 | 玩法设计 |
| `technical-director` | 技术架构重大决策、性能瓶颈 | 架构决策 |

### 休眠 41 个（按需启用）

以下 Agent 平时不唤醒，Phase 9+ 按需启用。

- **Godot 专项**：godot-shader-specialist、godot-gdextension-specialist、godot-csharp-specialist
- **UE 系列**：unreal-specialist、ue-blueprint-specialist、ue-gas-specialist、ue-replication-specialist、ue-umg-specialist
- **Unity 系列**：unity-specialist 等 5 个
- **设计组**：systems-designer、level-designer、economy-designer、ux-designer、world-builder、live-ops-designer
- **叙事/音频**：narrative-director、audio-director、sound-designer、writer
- **QA/生产**：qa-lead、qa-tester、release-manager、localization-lead
- **QA/工程**：performance-analyst、security-engineer、devops-engineer、analytics-engineer、accessibility-specialist、community-manager
- **其他**：engine-programmer、ai-programmer、network-programmer、tools-programmer、ui-programmer、prototyper

### 调度原则

1. **优先核心**：先看核心 5 个能否解决，不能才考虑按需 3 个
2. **最少唤醒**：一个任务尽量只用一个 Agent，不并行多个
3. **避免重复**：同一个问题不要唤醒两个 Agent 做同样的事
4. **完成就关闭**：Agent 完成任务后立即退出，不保持会话

---

## 会话启动流程

```
1. Claude 自动读取 production/session-state/active.md
2. 询问李振远：本次目标是什么？
3. 李振远描述目标（或从 active.md 的 Open Questions 中选择）
4. Claude 拆解任务，决定 Agent 调度
5. 开始工作循环
```

## 会话结束流程

```
1. 更新 active.md：
   - last_updated 时间
   - 本次完成的内容
   - 下一步计划
   - Open Questions（如有）
2. 检查游戏项目是否有未提交的代码
3. 如有 → 提醒李振远提交
4. 结束会话
```

---

## 与理想工作流的关系

| 理想 7 阶段 | 当前状态 | 何时启用 |
|------------|---------|---------|
| ① 头脑风暴 | ✅ 已完成（Phase 0 前） | — |
| ② 设计 | ✅ 已完成（概念文档、Art Bible） | — |
| ③ 实现 | ✅ 已完成（Phase 0–8） | — |
| ④ Review | ✅ 每轮 Claude 审查 | — |
| ⑤ QA | ⏳ 待启用 | Phase 10（平衡与 Bug 修复时） |
| ⑥ 发布 | ⏳ 待启用 | Phase 11（首次测试版发布前） |
| ⑦ Live Ops | ⏳ 待启用 | 正式发布后 |

**当前不需要完整的 7 阶段流程。** 等到进入 Phase 10–11（系统性 QA、发布流程、社区运营）时，再逐步启用对应阶段和 Agent。

---

> **维护者**：李振远 + Claude
> **最后更新**：2026-11-24
> **下次 Review**：恢复开发时
