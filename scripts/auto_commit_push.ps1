$repo = "D:\mirmironnnn oxirgiiii\Unreal Engine\Unreal Engine\Odilbek"
$memSrc = "C:\Users\Windows 11\.claude\projects\D--mirmironnnn-oxirgiiii-Unreal-Engine-Unreal-Engine-Odilbek\memory"
$memDst = Join-Path $repo "memory"

Set-Location $repo

# Mirror this project's auto-memory notes into the repo so they get versioned too
if (Test-Path $memSrc) {
    if (-not (Test-Path $memDst)) { New-Item -ItemType Directory -Path $memDst | Out-Null }
    Copy-Item -Path (Join-Path $memSrc "*") -Destination $memDst -Recurse -Force
}

# Wait out a transient index.lock left by another git process instead of failing the hook
$lockFile = Join-Path $repo ".git\index.lock"
$waited = 0
while ((Test-Path $lockFile) -and ($waited -lt 10)) {
    Start-Sleep -Seconds 1
    $waited++
}

git add -A *> $null

$staged = git diff --cached --name-only
if ([string]::IsNullOrWhiteSpace($staged)) {
    exit 0
}

$msg = "Auto session update $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git -c user.name="Odilbek" -c user.email="odilovislombek10@gmail.com" commit -m $msg *> $null
git push origin main *> $null
exit 0
