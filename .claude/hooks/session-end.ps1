# SessionEnd hook: 记录会话结束时的仓库状态
# 由 PowerShell 执行（原 bash hook 在本机无法运行）
# 编码：统一以 UTF-8 追加，避免历史日志出现乱码

$ErrorActionPreference = 'SilentlyContinue'
$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $repo

function Write-Log([string]$text) { Add-Content -LiteralPath $logFile -Value $text -Encoding utf8 }
function Is-Mojibake([string]$s) { return $s -match '[\uFF5E\uFF56\uFF5B\uFF5A]' }

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$logFile = Join-Path $repo 'production\session-logs\session-log.md'
New-Item -ItemType Directory -Path (Split-Path $logFile) -Force | Out-Null

$stateFile = Join-Path $repo 'production\session-state\active.md'

# 归档会话状态（保留 active.md 以便下次恢复）
if (Test-Path $stateFile) {
    $state = Get-Content -LiteralPath $stateFile -Raw -Encoding utf8
    if ($state -and -not (Is-Mojibake $state)) {
        Write-Log ''
        Write-Log "## Archived Session State: $timestamp"
        [System.IO.File]::AppendAllText($logFile, $state + [Environment]::NewLine, (New-Object System.Text.UTF8Encoding($false)))
    }
}

# 记录本次会话的提交与未提交改动
$commits = git log --oneline --since='8 hours ago' 2>$null
$dirty = git diff --name-only 2>$null
if ($commits -or $dirty) {
    Write-Log ''
    Write-Log "## Session End: $timestamp"
    if ($commits) { Write-Log '### Commits'; $commits | ForEach-Object { Write-Log $_ } }
    if ($dirty) { Write-Log '### Uncommitted Changes'; $dirty | ForEach-Object { Write-Log $_ } }
}

# 游戏项目健康检查
$gameDir = Join-Path $env:USERPROFILE 'Documents\新建游戏项目'
if (Test-Path (Join-Path $gameDir '.git')) {
    $n = (git -C $gameDir status --porcelain 2>$null | Measure-Object).Count
    if ($n -gt 0) { Write-Host "⚠️  游戏项目有 $n 个未提交的文件 — $gameDir" }
}
