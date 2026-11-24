# PreToolUse hook (Bash|PowerShell): git commit / git push preflight check
# stdin: { "tool_name": "...", "tool_input": { "command": "..." } }
# exit 0 = allow, exit 2 = block (stderr is shown to the model)

$ErrorActionPreference = 'SilentlyContinue'

$raw = [Console]::In.ReadToEnd()
if (-not $raw) { exit 0 }
try { $payload = $raw | ConvertFrom-Json } catch { exit 0 }

$command = $payload.tool_input.command
if (-not $command) { $command = $payload.tool_input.command_line }
if (-not $command) { exit 0 }

$isCommit = $command -match 'git\s+commit'
$isPush = $command -match 'git\s+push'
if (-not ($isCommit -or $isPush)) { exit 0 }

$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $repo

$errors = @()

$credPattern = '(?i)(password|secret|api_key|token)\s*=\s*[''"]\S{8,}[''"]'
$keyPattern = 'ghp_|sk-[A-Za-z0-9]{16,}|xox[baprs]-|sk-ant-'
$privateKeyPattern = 'BEGIN [A-Z ]*PRIVATE KEY'

if ($isCommit) {
    $staged = git diff --cached --name-only --diff-filter=ACM 2>$null
    foreach ($file in $staged) {
        if ($file -notmatch '\.(py|ts|tsx|js|yml|yaml|json|example|env)$') { continue }
        $content = git show ":$file" 2>$null
        if (-not $content) { continue }
        $hitCred = $content | Select-String -Pattern $credPattern -Quiet
        $hitKey = $content | Select-String -Pattern $keyPattern -Quiet
        $hitPriv = $content | Select-String -Pattern $privateKeyPattern -Quiet
        if ($hitCred) { $errors += "[SECURITY] hardcoded-credential: $file" }
        if ($hitKey) { $errors += "[SECURITY] known-api-key: $file" }
        if ($hitPriv) { $errors += "[SECURITY] private-key: $file" }
    }

    if ($command -match '-m\s+["''"]?([^"''"]+)') {
        $msg = $Matches[1]
        $typePattern = '\A(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([\w-]+\))?!?:\s\S'
        $msgBad = $msg -notmatch $typePattern
        if ($msgBad) { $errors += "[FORMAT] not Conventional Commits: $msg" }
    }
}
else {
    if ($command -match '--force') { $errors += '[SECURITY] force-push-blocked' }
}

if ($errors.Count -gt 0) {
    $errors | ForEach-Object { [Console]::Error.WriteLine($_) }
    exit 2
}

exit 0
