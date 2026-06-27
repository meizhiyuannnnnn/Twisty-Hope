#!/bin/bash
# Claude Code Stop hook: Log session summary when Claude finishes
# Records what was worked on for audit trail and sprint tracking

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SESSION_LOG_DIR="production/session-logs"

mkdir -p "$SESSION_LOG_DIR" 2>/dev/null

# Log recent git activity from this session (check up to 8 hours for long sessions)
RECENT_COMMITS=$(git log --oneline --since="8 hours ago" 2>/dev/null)
MODIFIED_FILES=$(git diff --name-only 2>/dev/null)

# --- Archive active session state on shutdown (do NOT delete) ---
# active.md persists across clean exits so multi-session recovery works.
# It is only valid to delete active.md manually or when explicitly superseded.
STATE_FILE="production/session-state/active.md"
if [ -f "$STATE_FILE" ]; then
    {
        echo "## Archived Session State: $TIMESTAMP"
        cat "$STATE_FILE"
        echo "---"
        echo ""
    } >> "$SESSION_LOG_DIR/session-log.md" 2>/dev/null
fi

if [ -n "$RECENT_COMMITS" ] || [ -n "$MODIFIED_FILES" ]; then
    {
        echo "## Session End: $TIMESTAMP"
        if [ -n "$RECENT_COMMITS" ]; then
            echo "### Commits"
            echo "$RECENT_COMMITS"
        fi
        if [ -n "$MODIFIED_FILES" ]; then
            echo "### Uncommitted Changes"
            echo "$MODIFIED_FILES"
        fi
        echo "---"
        echo ""
    } >> "$SESSION_LOG_DIR/session-log.md" 2>/dev/null
fi

# --- Game project health check ---
# Check if game project has uncommitted changes
GAME_PROJECT_DIR="$HOME/Documents/新建游戏项目"
if [ -d "$GAME_PROJECT_DIR/.git" ]; then
    GAME_UNCOMMITTED=$(cd "$GAME_PROJECT_DIR" && git status --porcelain 2>/dev/null | wc -l)
    if [ "$GAME_UNCOMMITTED" -gt 0 ]; then
        echo "⚠️  游戏项目有 $GAME_UNCOMMITTED 个未提交的文件"
        echo "   路径: $GAME_PROJECT_DIR"
        echo "   建议: 在 Godot 验证通过后立即 commit"
        echo ""
    fi
fi

# --- Session state reminder ---
# Remind to update active.md if it hasn't been touched recently
if [ -f "$STATE_FILE" ]; then
    STATE_AGE=$(( $(date +%s) - $(stat -c %Y "$STATE_FILE" 2>/dev/null || echo 0) ))
    if [ "$STATE_AGE" -gt 3600 ]; then  # 1 hour
        echo "⚠️  会话状态文件超过 1 小时未更新"
        echo "   建议: 更新 production/session-state/active.md 记录本次工作"
        echo ""
    fi
else
    echo "⚠️  会话状态文件不存在: production/session-state/active.md"
    echo "   建议: 创建并初始化会话状态文件"
    echo ""
fi

exit 0
