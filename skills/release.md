# Skill: release

## 用途

标准版本发布流程 — 更新版本号 → 生成 CHANGELOG → git tag → 触发构建。

## 使用时机

- 修复积累到可发布时
- Milestone 节点
- 正式上线

## 执行步骤

### 1. 更新版本号

```bash
# 前端 package.json
cd web
npm version patch  # 或 minor / major

# 后端
# 更新 backend/app/core/config.py 中的 VERSION
# 或使用 .env 中的 VERSION 变量
```

### 2. 生成 CHANGELOG

```markdown
## v1.0.1 (2026-06-10)

### 🐛 Bug 修复
- 修复 WebSocket 在 Firefox 下断连不重试的问题

### 🔒 安全
- 升级 axios 到 1.7.4（修复 CVE-2024-xxxx）

### 📦 依赖更新
- React 18.3.1 → 18.3.2
```

### 3. 打 Tag

```bash
git add .
git commit -m "chore: release v1.0.1"
git tag -a v1.0.1 -m "v1.0.1: 修复 WebSocket + 安全补丁"
git push origin main --tags
```

### 4. 验证

```bash
# 跑质量门禁
quality-gate

# Docker 构建验证
docker compose build
```

## 版本号规则（Semver）

| 变更类型 | 版本号 | 示例 |
|---------|--------|------|
| Bug 修复 | patch (x.y.Z) | v1.0.0 → v1.0.1 |
| 新功能（兼容） | minor (x.Y.z) | v1.0.0 → v1.1.0 |
| 破坏性变更 | major (X.y.z) | v1.0.0 → v2.0.0 |

## 输出

```markdown
## 发布完成

**版本**：v1.0.1
**类型**：patch
**变更项**：3 项
**Tag**：✅ 已推送
**验证**：✅ quality-gate 通过
```

## 可用 Agent

- maint-agent
- devops-agent
- Claude（协调者）
