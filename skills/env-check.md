# Skill: env-check

## 用途

检查开发环境是否符合公司技术栈版本要求。

## 使用时机

- 新项目初始化前
- 新成员加入时
- 环境出现异常时

## 执行步骤

```bash
# 检查 Node.js
node --version  # 期望 >= 20

# 检查 npm
npm --version   # 期望 >= 10

# 检查 Python
python --version  # 期望 >= 3.11

# 检查 Docker
docker --version          # 期望 >= 24
docker compose version    # 期望 >= 2

# 检查 Git
git --version  # 期望 >= 2.40
```

## 公司版本基线

| 工具 | 最低版本 | 检查命令 |
|------|---------|---------|
| Node.js | 20.x | `node --version` |
| npm | 10.x | `npm --version` |
| Python | 3.11 | `python --version` |
| Docker | 24.x | `docker --version` |
| Docker Compose | 2.x | `docker compose version` |
| Git | 2.40+ | `git --version` |

## 输出格式

```markdown
## 环境检查报告

**时间**：[时间]

| 工具 | 当前版本 | 最低要求 | 状态 |
|------|---------|---------|------|
| Node.js | 22.3.0 | 20.x | ✅ |
| npm | 10.8.0 | 10.x | ✅ |
| Python | 3.12.0 | 3.11 | ✅ |
| Docker | 26.1.0 | 24.x | ✅ |
| Docker Compose | 2.27.0 | 2.x | ✅ |
| Git | 2.45.0 | 2.40 | ✅ |

**结论**：✅ 全部达标 / ⚠️ X 项不达标
```

## 可用 Agent

- Claude（协调者）
- devops-agent
