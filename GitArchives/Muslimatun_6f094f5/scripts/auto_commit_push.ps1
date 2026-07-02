$repo = "D:\mirmironnnn oxirgiiii\Unreal Engine\Unreal Engine\Muslimatun"
Set-Location $repo

git add -A *> $null

$staged = git diff --cached --name-only
if ([string]::IsNullOrWhiteSpace($staged)) {
    exit 0
}

$msg = "Auto session update $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git -c user.name="Odilbek" -c user.email="odilovislombek10@gmail.com" commit -m $msg *> $null
git push origin main *> $null
exit 0
