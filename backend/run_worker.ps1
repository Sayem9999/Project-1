$ErrorActionPreference = "Stop"

param(
    [string]$Queue = "video,celery"
)

$required = @(
    "ENVIRONMENT",
    "REDIS_URL",
    "DATABASE_URL",
    "SECRET_KEY"
)

$missing = @()
foreach ($name in $required) {
    $value = [Environment]::GetEnvironmentVariable($name)
    if ([string]::IsNullOrWhiteSpace($value)) {
        $missing += $name
    }
}

if ($missing.Count -gt 0) {
    Write-Host "Missing required environment variables:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
    Write-Host ""
    Write-Host "Set them in this shell and run again." -ForegroundColor Yellow
    exit 1
}

Write-Host "Starting external Celery worker in low-memory mode..." -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m celery -A app.celery_app worker `
    --pool=solo `
    --concurrency=1 `
    --without-gossip `
    --without-mingle `
    --without-heartbeat `
    -Q $Queue `
    --loglevel=info
