#!/usr/bin/env bash
# git-commit-validate.sh — git commit 前置校验
# 检查：硬编码凭据 / Conventional Commits 格式 / 遗留 TODO
set -euo pipefail

# 仅当命令是 git commit 时执行
INPUT=$(cat 2>/dev/null || echo "")
if ! echo "$INPUT" | grep -qE '"command"\s*:\s*"git commit'; then
  exit 0
fi

HAS_ERROR=false

# --- 1. 硬编码凭据检查 ---
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)
for FILE in $STAGED_FILES; do
  [[ ! -f "$FILE" ]] && continue
  case "$FILE" in
    *.py|*.ts|*.tsx|*.js|*.yml|*.yaml|*.env|*.json|*.example)
      CONTENT=$(git show ":$FILE" 2>/dev/null || true)
      # 检查硬编码密钥/密码/Token
      if echo "$CONTENT" | grep -PinE "(password|secret|api_key|token)\s*=\s*['\"][^$]{8,}['\"]" > /dev/null 2>&1; then
        echo "[SECURITY] $FILE 可能包含硬编码凭据，禁止提交。"
        HAS_ERROR=true
      fi
      # 检查 GitHub Token / OpenAI Key 等已知格式
      if echo "$CONTENT" | grep -PinE "(ghp_|sk-|xox[baprs]-|sk-ant-)" > /dev/null 2>&1; then
        echo "[SECURITY] $FILE 包含已知格式的 API Token/Key，禁止提交。"
        HAS_ERROR=true
      fi
      # 检查私钥
      if echo "$CONTENT" | grep -q "BEGIN.*PRIVATE KEY" > /dev/null 2>&1; then
        echo "[SECURITY] $FILE 包含私钥，禁止提交。"
        HAS_ERROR=true
      fi
      ;;
  esac
done

# --- 2. Conventional Commits 格式检查 ---
# Claude Code 的 git commit 通常通过 Bash tool 传完整命令，不是用 COMMIT_EDITMSG
# 所以检查 commit message 在命令中
COMMIT_MSG=$(echo "$INPUT" | grep -oP '"command"\s*:\s*"git commit[^"]*"-m\s*"[^"]*"' 2>/dev/null | grep -oP '(?<=-m ")[^"]+' | head -1 || true)
if [ -n "$COMMIT_MSG" ]; then
  CC_REGEX='^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-zA-Z0-9_-]+\))?!?:\s.+'
  if ! echo "$COMMIT_MSG" | grep -qE "$CC_REGEX"; then
    echo "[格式] 提交信息不符合 Conventional Commits 规范。"
    echo "  期望: type(scope): 描述"
    echo "  例如: feat(web): 添加用户登录页"
    echo "  类型: feat | fix | docs | style | refactor | perf | test | build | ci | chore | revert"
    HAS_ERROR=true
  fi
fi

# --- 3. 遗留 TODO 检查（警告，不阻断）---
for FILE in $STAGED_FILES; do
  [[ ! -f "$FILE" ]] && continue
  case "$FILE" in
    *.py|*.ts|*.tsx|*.js|*.md)
      MATCHES=$(git show ":$FILE" 2>/dev/null | grep -Pin '(TODO|FIXME|HACK)\s*:' | grep -vP '(TODO|FIXME|HACK).*#\d+' || true)
      if [ -n "$MATCHES" ]; then
        echo "[INFO] $FILE 包含无跟踪编号的 TODO/FIXME:"
        echo "$MATCHES"
        echo "  建议: TODO(#issue): 描述"
      fi
      ;;
  esac
done

if [ "$HAS_ERROR" = true ]; then
  echo ""
  echo "修复方法：凭据移入 .env，Token 用环境变量。"
  exit 1
fi

echo "✅ git commit 校验通过"
exit 0
