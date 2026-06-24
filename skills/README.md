# 公司 Skill 目录

本目录存放公司级 Skill 定义，供 Claude 协调者和各 Agent 在项目流程中调用。

## 与 Agent SKILLS.md 的区别

| 维度 | skills/ | agents/*/SKILLS.md |
|------|---------|-------------------|
| **层级** | 公司级（跨项目共享） | Agent 级（该 Agent 专属） |
| **内容** | Skill 的完整定义与执行步骤 | 该 Agent 可用的 Skill 列表与使用指引 |
| **调用者** | Claude 协调者、各 Agent | 该 Agent 自身 |

## 现有 Skills

| Skill | 用途 | 触发时机 |
|-------|------|---------|
| `env-check` | 开发环境版本检查 | 新项目启动前 |
| `project-init` | 从模板初始化新项目 | 项目立项后 |
| `quality-gate` | 代码质量门禁 | 每轮开发后 |
| `docker-dev` | Docker 开发环境管理 | 开发/调试阶段 |
| `release` | 版本发布流程 | Milestone 交付前 |

## 如何新增 Skill

1. 识别新需求（公司级通用流程需要标准化）
2. 在 `skills/` 下创建 `skill-name.md`
3. 参考现有 skill 格式编写（用途 / 使用时机 / 执行步骤 / 输出）
4. 在相关 Agent 的 SKILLS.md 中添加引用
5. 更新 CLAUDE.md 的 skills 列表
