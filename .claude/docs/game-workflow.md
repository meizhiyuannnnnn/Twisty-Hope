# 游戏项目工作流（7 阶段）

> 对应 Skill 位于 `.claude/skills/game/`，按阶段分子目录。

```
① 头脑风暴  →  ② 设计    →  ③ 实现     →  ④ Review  →  ⑤ QA     →  ⑥ 发布   →  ⑦ Live Ops

creative-      game-         gameplay-      all leads     qa-lead       release-      live-ops
director       designer      programmer     code-review   qa-tester     manager       -designer
brainstorm     architect     engine-        design-       smoke-check   launch-       community
                            programmer     review        regression    checklist     -manager
 产出:          产出:         产出:          产出:         产出:         产出:         产出:
 概念文档       GDD/架构      功能代码       Review报告    测试报告      发布版本      运营数据
               UX设计稿
```

## 各阶段说明

| 阶段 | 主导 Agent | 关键 Skill | 产出物 |
|------|-----------|-----------|--------|
| ① 头脑风暴 | `creative-director` | `/brainstorm` | 概念文档、游戏支柱 |
| ② 设计 | `game-designer` + `lead-programmer` | `/design-system`, `/create-architecture` | GDD、架构设计、UX Spec |
| ③ 实现 | Tier 3 专家层 | `/dev-story` | 功能代码 |
| ④ Review | 所有 Lead | `/code-review`, `/design-review` | Review 报告 |
| ⑤ QA | `qa-lead` + `qa-tester` | `/smoke-check`, `/regression-suite` | 测试报告 |
| ⑥ 发布 | `release-manager` | `/release-checklist`, `/launch-checklist` | 发布版本 |
| ⑦ Live Ops | `live-ops-designer` + `community-manager` | `/team-live-ops` | 运营数据、玩家反馈 |

## 启动方式

游戏项目使用 `/start` 启动引导流程，系统检测项目阶段后自动建议下一步。
