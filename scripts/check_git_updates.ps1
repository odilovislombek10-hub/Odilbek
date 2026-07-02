$repo = "D:\mirmironnnn oxirgiiii\Unreal Engine\Unreal Engine\Odilbek"
$logDir = Join-Path $repo "logs"
$seenRemoteFile = Join-Path $logDir "last_seen_origin_main.txt"
$seenStatusFile = Join-Path $logDir "last_seen_status_hash.txt"
$logFile = Join-Path $logDir "git_update_monitor.log"

if (-not (Test-Path -LiteralPath $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

function Write-MonitorLog {
    param([string]$Message)
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
    Add-Content -LiteralPath $logFile -Value $line -Encoding UTF8
}

function Send-UserNotice {
    param([string]$Message)
    Write-MonitorLog $Message
    try {
        $user = $env:USERNAME
        if (-not [string]::IsNullOrWhiteSpace($user)) {
            msg $user $Message *> $null
        }
    } catch {
        Write-MonitorLog "Notice failed: $($_.Exception.Message)"
    }
}

Set-Location -LiteralPath $repo

git fetch origin main *> $null
if ($LASTEXITCODE -ne 0) {
    Write-MonitorLog "Fetch failed for origin/main"
    exit 1
}

$remoteHead = (git rev-parse origin/main).Trim()
if (-not (Test-Path -LiteralPath $seenRemoteFile)) {
    Set-Content -LiteralPath $seenRemoteFile -Value $remoteHead -Encoding ASCII
    Write-MonitorLog "Initialized remote monitor at $remoteHead"
} else {
    $lastSeen = (Get-Content -LiteralPath $seenRemoteFile -Raw).Trim()
    if ($remoteHead -ne $lastSeen) {
        $summary = git log --oneline "$lastSeen..$remoteHead" 2>$null
        Set-Content -LiteralPath $seenRemoteFile -Value $remoteHead -Encoding ASCII
        Send-UserNotice "Odilbek GitHub'da yangi commit bor: $remoteHead. $summary"
    }
}

$status = git status --porcelain
$statusText = ($status -join "`n").Trim()
$statusHash = if ([string]::IsNullOrWhiteSpace($statusText)) {
    "clean"
} else {
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($statusText)
    $hash = [System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)
    [BitConverter]::ToString($hash).Replace("-", "").ToLowerInvariant()
}

if (-not (Test-Path -LiteralPath $seenStatusFile)) {
    Set-Content -LiteralPath $seenStatusFile -Value $statusHash -Encoding ASCII
    Write-MonitorLog "Initialized local status monitor as $statusHash"
} else {
    $lastStatusHash = (Get-Content -LiteralPath $seenStatusFile -Raw).Trim()
    if ($statusHash -ne $lastStatusHash) {
        Set-Content -LiteralPath $seenStatusFile -Value $statusHash -Encoding ASCII
        if ($statusHash -eq "clean") {
            Send-UserNotice "Odilbek Git working tree toza bo'ldi."
        } else {
            Send-UserNotice "Odilbek papkasida yangi commit qilinmagan Git o'zgarish bor."
        }
    }
}
