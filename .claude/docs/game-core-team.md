# 游戏核心团队定义 — 《彼方希冀》

> 基于实际使用数据（131 个会话的 Agent 审计日志）定义的核心团队。
> 49 个 Agent 中，只有 8 个被实际使用，其余 41 个休眠。

---

## 核心团队（5 个）

**每次会话可能用到，是日常开发的主力。**

### 1. godot-gdscript-specialist

| 项目 | 内容 |
|------|------|
| **实际调用次数** | 20+ 次（最高频） |
| **职责** | GDScript 代码编写、Bug 修复、系统实现 |
| **何时唤醒** | 任何 GDScript 代码任务 |
| **典型任务** | 实现资源系统、修复事件逻辑、优化性能 |
| **模型** | Sonnet |

**为什么是核心**：项目的代码主力，90% 的实现工作由这个 Agent 完成。

---

### 2. technical-artist

| 项目 | 内容 |
|------|------|
| **实际调用次数** | 7 次 |
| **职责** | 视觉效果、Shader、粒子系统、素材接入 |
| **何时唤醒** | 需要视觉效果优化时 |
| **典型任务** | 背景接缝修复、雪花粒子调优、像素素材接入 |
| **模型** | Sonnet |

**为什么是核心**：Phase 2 视觉升级的主力，负责代码与美术的交叉地带。

---

### 3. lead-programmer

| 项目 | 内容 |
|------|------|
| **实际调用次数** | 5 次 |
| **职责** | 架构决策、代码审查、复杂重构、技术把关 |
| **何时唤醒** | 需要架构决策或代码审查时 |
| **典型任务** | 设计系统架构、审查核心代码、重构复杂逻辑 |
| **模型** | Sonnet |

**为什么是核心**：技术方向的把关者，确保代码质量和架构一致性。

---

### 4. gameplay-programmer

| 项目 | 内容 |
|------|------|
| **实际调用次数** | 2 次 |
| **职责** | 游戏逻辑、系统交互、事件系统、玩法实现 |
| **何时唤醒** | 需要实现具体玩法逻辑时 |
| **典型任务** | 实现饥饿系统、事件触发逻辑、车厢效果 |
| **模型** | Sonnet |

**为什么是核心**：专注于玩法层面的实现，与 godot-gdscript-specialist 互补（后者更偏引擎层面）。

---

### 5. art-director

| 项目 | 内容 |
|------|------|
| **实际调用次数** | 2 次 |
| **职责** | 美术方向、素材选型、风格一致性、视觉决策 |
| **何时唤醒** | 需要美术方向决策时 |
| **典型任务** | 选择像素素材、定义色彩调色板、审查视觉一致性 |
| **模型** | Sonnet |

**为什么是核心**：视觉质量的守门人，确保像素风格统一、色彩对比符合设计。

---

## 按需团队（3 个）

**特定问题时唤醒，不是日常使用。**

### 6. creative-director

| 项目 | 内容 |
|------|------|
| **实际调用次数** | 1 次 |
| **职责** | 创意愿景、玩法方向、设计冲突仲裁 |
| **何时唤醒** | 玩法方向有争议、需要创意决策时 |
| **典型任务** | 决定核心玩法优先级、解决设计冲突 |
| **模型** | Opus |

---

### 7. game-designer

| 项目 | 内容 |
|------|------|
| **实际调用次数** | 1 次 |
| **职责** | 系统设计、数值平衡、事件设计、玩法文档 |
| **何时唤醒** | 需要设计新系统或调整数值时 |
| **典型任务** | 设计资源经济系统、平衡事件难度、编写 GDD |
| **模型** | Sonnet |

---

### 8. technical-director

| 项目 | 内容 |
|------|------|
| **实际调用次数** | 1 次 |
| **职责** | 技术架构重大决策、性能瓶颈分析、跨系统技术冲突 |
| **何时唤醒** | 需要重大技术决策或解决性能问题时 |
| **典型任务** | 选择渲染方案、解决内存泄漏、优化帧率 |
| **模型** | Opus |

---

## 休眠团队（41 个）

**Phase 2 不需要，Phase 3+ 按需启用。**

### Godot 专项（3 个）
- `godot-shader-specialist` — 复杂 Shader 效果
- `godot-gdextension-specialist` — C++ 原生扩展
- `godot-csharp-specialist` — C# 绑定

### 引擎系列（10 个）
- **Unreal**（5 个）：unreal-specialist、ue-blueprint-specialist、ue-gas-specialist、ue-replication-specialist、ue-umg-specialist
- **Unity**（5 个）：unity-specialist、unity-dots-specialist、unity-shader-specialist、unity-addressables-specialist、unity-ui-specialist

### 设计组（6 个）
- `systems-designer` — 子系统机制设计
- `level-designer` — 关卡布局
- `economy-designer` — 资源经济平衡
- `ux-designer` — 用户体验设计
- `world-builder` — 世界观构建
- `live-ops-designer` — 运营活动设计

### 叙事/音频组（4 个）
- `narrative-director` — 故事/对话/世界观
- `audio-director` — 音效设计与音乐方向
- `sound-designer` — 音效制作
- `writer` — 对话/物品描述/环境文本

### QA/生产组（4 个）
- `qa-lead` — 质量策略与测试计划
- `qa-tester` — 测试用例编写
- `release-manager` — 发布就绪与协调
- `localization-lead` — 多语言支持

### 工程/分析组（6 个）
- `performance-analyst` — 性能分析与优化
- `security-engineer` — 安全审查
- `devops-engineer` — CI/CD 配置
- `analytics-engineer` — 数据分析
- `accessibility-specialist` — 无障碍设计
- `community-manager` — 社区管理

### 其他编程组（6 个）
- `engine-programmer` — 引擎层代码
- `ai-programmer` — AI 系统
- `network-programmer` — 多人联网
- `tools-programmer` — 开发工具
- `ui-programmer` — UI 系统
- `prototyper` — 原型开发

### 管理组（2 个）
- `producer` — 项目管理（Tier 1）
- `technical-artist` — 已计入核心团队

---

## 调度决策原则

### 优先级

1. **核心 5 个优先**：先看核心能否解决，不能才考虑按需 3 个
2. **最少唤醒**：一个任务尽量只用一个 Agent，避免并行多个
3. **完成就关闭**：Agent 完成任务后立即退出，不保持会话
4. **避免重复**：同一个问题不要唤醒两个 Agent 做同样的事

### 决策流程

```
任务描述
    ↓
核心 5 个能否解决？
    ├── 是 → 选择最合适的 1 个
    └── 否 → 按需 3 个能否解决？
                ├── 是 → 选择最合适的 1 个
                └── 否 → 考虑休眠团队（Phase 3+）
```

### 典型场景

| 场景 | 唤醒谁 | 理由 |
|------|--------|------|
| 实现资源消耗逻辑 | `godot-gdscript-specialist` | 纯代码实现 |
| 修复背景接缝 | `technical-artist` | 视觉效果 |
| 设计新的车厢类型 | `game-designer` + `gameplay-programmer` | 设计 + 实现 |
| 审查核心架构 | `lead-programmer` | 技术把关 |
| 选择像素素材风格 | `art-director` | 美术决策 |
| 决定主线剧情方向 | `creative-director` | 创意决策 |
| 优化帧率瓶颈 | `technical-director` + `lead-programmer` | 重大技术决策 |

---

## 团队协作模式

### 串行协作（默认）

```
Agent A 完成 → Claude Review → Agent B 基于 A 的产出继续
```

适用于：有依赖关系的任务（设计 → 实现 → 审查）

### 并行协作（谨慎使用）

```
Agent A + Agent B 同时工作（不同文件）→ Claude 合并 Review
```

适用于：独立模块（背景 Shader + UI 逻辑）

**并行前提**：
- 两个 Agent 修改的文件不重叠
- 有明确的接口约定
- Claude 负责合并和一致性检查

---

> **维护者**：李振远 + Claude
> **最后更新**：2026-06-27
> **数据来源**：131 个会话的 Agent 审计日志（2026-06-26 ~ 2026-06-27）
> **下次 Review**：Phase 2 完成后
