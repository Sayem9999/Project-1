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

Write-Host "Starting Tailscale Funnel on port 8000..." -ForegroundColor Green
Write-Host "This will give you a PERMANENT URL for your API." -ForegroundColor Cyan
Write-Host "Press CTRL+C to stop the funnel." -ForegroundColor Gray

& $tailscale funnel 8000
