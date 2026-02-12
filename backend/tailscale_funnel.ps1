param(
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

# Use absolute path to ensure it works even if PATH hasn't updated
$tailscale = "C:\Program Files\Tailscale\tailscale.exe"

Write-Host "Checking Tailscale status..." -ForegroundColor Cyan
try {
    $status = & $tailscale status --json | ConvertFrom-Json
    if ($status.BackendState -ne "Running") {
        Write-Host "Tailscale is not logged in. Starting login process..." -ForegroundColor Yellow
        & $tailscale up
    }
}
catch {
    Write-Host "Tailscale backend not found. Ensure Tailscale is running." -ForegroundColor Red
    exit 1
}

Write-Host "Cleaning up previous funnel configurations..." -ForegroundColor Gray
try {
    & $tailscale funnel reset | Out-Null
}
catch {}

try {
    & $tailscale serve reset | Out-Null
}
catch {}

Write-Host "Starting Tailscale Funnel on port $Port (background mode)..." -ForegroundColor Green
Write-Host "This will give you a stable public URL for your API." -ForegroundColor Cyan

& $tailscale funnel --yes --bg $Port | Out-Null
& $tailscale funnel status
