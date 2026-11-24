# SessionStart hook: 会话开始时输出公司仓库与游戏项目状态
# 由 PowerShell 执行（原 bash hook 在本机无法运行）
# 输出会作为上下文注入

$ErrorActionPreference = 'SilentlyContinue'
$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $repo

Write-Output '=== 彼方希冀程序开发公司 — Session Context ==='

$branch = git rev-parse --abbrev-ref HEAD 2>$null
if ($branch) {
    Write-Output "Branch: $branch"
    Write-Output ''
    Write-Output 'Recent commits:'
    git log --oneline -5 2>$null | ForEach-Object { Write-Output "  $_" }
}

# 会话状态恢复
$stateFile = Join-Path $repo 'production\session-state\active.md'
if (Test-Path $stateFile) {
    Write-Output ''
    Write-Output '=== ACTIVE SESSION STATE DETECTED ==='
    $lines = Get-Content -LiteralPath $stateFile -Encoding utf8
    $tail = if ($lines.Count -gt 20) { $lines[-20..-1] } else { $lines }
    $tail | ForEach-Object { Write-Output "  $_" }
    Write-Output "=== END SESSION STATE PREVIEW ($($lines.Count) lines total) ==="
}

# 游戏项目健康检查
$gameDir = Join-Path $env:USERPROFILE 'Documents\新建游戏项目'
if (Test-Path (Join-Path $gameDir '.git')) {
    $n = (git -C $gameDir status --porcelain 2>$null | Measure-Object).Count
    $last = git -C $gameDir log -1 --format="%h %ad %s" --date=short 2>$null
    Write-Output ''
    Write-Output "Game project: $gameDir"
    Write-Output "Last commit: $last"
    Write-Output "Pending files: $n"
}

Write-Output '==================================='

exit 0
