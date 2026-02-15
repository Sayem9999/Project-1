param(
    [switch]$SkipFrontend
)

# Hardcoded Auto-Update: Sync Pinokio and New Folder
if (Test-Path ".\scripts\sync_workspaces.ps1") {
    powershell -ExecutionPolicy Bypass -File ".\scripts\sync_workspaces.ps1"
}

# Start Local Development (API + WORKER)
$ErrorActionPreference = "Stop"

# Ensure tools are in path
$env:Path = "$PSScriptRoot\tools\ffmpeg-8.0.1-essentials_build\bin;$env:Path"

Write-Host "Starting Backend API..." -ForegroundColor Green
$backendParams = @{
    FilePath         = ".\.venv\Scripts\python.exe"
    ArgumentList     = "-m uvicorn app.main:app --host 0.0.0.0 --port 8000"
    WorkingDirectory = "backend"
    NoNewWindow      = $true
}
Start-Process @backendParams

Write-Host "Starting Celery Worker (Local)..." -ForegroundColor Cyan
$workerParams = @{
    FilePath         = ".\.venv\Scripts\python.exe"
    ArgumentList     = "-m celery -A app.celery_app.celery_app worker --loglevel=info -Q video_local -P solo"
    WorkingDirectory = "backend"
    NoNewWindow      = $false # Keep worker window visible for logs
}
Start-Process @workerParams

if (-not $SkipFrontend) {
    Write-Host "Starting Local Frontend..." -ForegroundColor Yellow
    Start-Process -FilePath "npm.cmd" -ArgumentList "run dev" -WorkingDirectory "frontend" -NoNewWindow
}
else {
    Write-Host "Skipping Local Frontend (Using Vercel)..." -ForegroundColor Magenta
}

Write-Host "🚀 ProEdit Suite Initialized!" -ForegroundColor Green
Write-Host "API: http://localhost:8000"
if (-not $SkipFrontend) { Write-Host "Frontend: http://localhost:3000" }
Write-Host "Worker logs are in the new window."
Write-Host "------------------------------------------------"
Write-Host "Tip: Run .\backend\tailscale_funnel.ps1 to make your local API reachable from Vercel" -ForegroundColor Cyan
