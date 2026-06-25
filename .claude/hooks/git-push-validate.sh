#!/usr/bin/env bash
# git-push-validate.sh — git push 前置校验
# 推送到 main/master 时警告并拦截
set -euo pipefail

# 仅当命令是 git push 时执行
INPUT=$(cat 2>/dev/null || echo "")
if ! echo "$INPUT" | grep -qE '"command"\s*:\s*"git push'; then
  exit 0
fi

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" ]]; then
  echo "⚠️  【警告】正在向 $CURRENT_BRANCH 分支推送。"
  echo "  请确认："
  echo "  1. 是否已经过 Claude Review？"
  echo "  2. 是否通过了 /gate 质量门禁？"
  echo "  3. 是否有未解决的阻断项？"
  echo ""
  echo "  如需继续推送，请使用 feature branch + PR，或由 Claude 协调者确认。"
  exit 2
fi

echo "✅ 分支 $CURRENT_BRANCH 推送检查通过"
exit 0
