# 项目类型识别规则

Claude 协调者启动时根据当前工作目录的特征文件自动判定项目类型，选择正确的 Agent 池。

| 识别条件 | 判定为 | 使用 Agent 池 |
|---------|--------|-------------|
| 目录含 `engine.cfg` / `project.godot` | Godot 游戏项目 | `.claude/agents/`（游戏 Agent） |
| 目录含 `*.uproject` | Unreal 游戏项目 | `.claude/agents/`（游戏 Agent） |
| 目录含 `Assets/` + `ProjectSettings/` | Unity 游戏项目 | `.claude/agents/`（游戏 Agent） |
| 目录含 `package.json` + `vite.config.ts` | Web 前端项目 | `agents/`（Web Agent） |
| 目录含 `pyproject.toml` + `app/` | Python 后端项目 | `agents/`（Web Agent） |
| 以上条件均不满足 | 无法判定 | 询问李振远确认项目类型 |

## 运行时切换

- Claude 通过 `cd` 进入不同项目目录后，自动重新判定
- 一个会话中可能同时处理 Web 和游戏任务（不同项目目录），Agent 池按当前目录切换
- 如果同时需要两个项目的 Agent，分别用不同 Subagent 调用，各自加载正确的 Agent 手册
