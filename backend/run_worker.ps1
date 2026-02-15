param(
    [string]$Queue = ""
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
$pythonExe = Join-Path $scriptDir ".venv\Scripts\python.exe"

function Import-DotEnvFile {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        return
    }

    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if ([string]::IsNullOrWhiteSpace($line)) { return }
        if ($line.StartsWith("#")) { return }
        if (-not $line.Contains("=")) { return }

        $parts = $line.Split("=", 2)
        $name = $parts[0].Trim()
        $value = $parts[1].Trim().Trim('"').Trim("'")

        if ([string]::IsNullOrWhiteSpace($name)) { return }

        # [FORCE OVERWRITE] Prioritize the values in the .env file over system/shell environment variables.
        # This prevents issues where a global DATABASE_URL (e.g. from Render/Postgres) shadows the local SQLite one.
        [Environment]::SetEnvironmentVariable($name, $value)
        Set-Item -Path ("Env:{0}" -f $name) -Value $value
    }
}

# Auto-load local env file so double-click startup works without manual exports.
Import-DotEnvFile (Join-Path $scriptDir ".env")
Import-DotEnvFile (Join-Path $scriptDir ".env.local")

if (-not [Environment]::GetEnvironmentVariable("ENVIRONMENT")) {
    $env:ENVIRONMENT = "production"
}

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

# Normalize REDIS_URL in case it was saved with spaces/quotes/prefix text.
$redisUrlRaw = [Environment]::GetEnvironmentVariable("REDIS_URL")
if ($null -eq $redisUrlRaw) {
    $redisUrl = ""
}
else {
    $redisUrl = $redisUrlRaw
}
$redisUrl = $redisUrl.Trim().Trim('"').Trim("'")
if ($redisUrl -match "^[A-Za-z_][A-Za-z0-9_]*=") {
    $redisUrl = $redisUrl.Split("=", 2)[1].Trim()
}
$env:REDIS_URL = $redisUrl

if ($redisUrl -notmatch "^rediss?://") {
    Write-Host "Invalid REDIS_URL (must start with redis:// or rediss://): $redisUrl" -ForegroundColor Red
    exit 1
}

$uri = $null
if (-not [System.Uri]::TryCreate($redisUrl, [System.UriKind]::Absolute, [ref]$uri) -or [string]::IsNullOrWhiteSpace($uri.Host)) {
    Write-Host "Invalid REDIS_URL host. Current value: $redisUrl" -ForegroundColor Red
    exit 1
}

if (-not [Environment]::GetEnvironmentVariable("REDIS_SSL_CERT_REQS")) {
    $env:REDIS_SSL_CERT_REQS = "required"
}

Write-Host "Starting external Celery worker in low-memory mode..." -ForegroundColor Cyan
if (!(Test-Path $pythonExe)) {
    Write-Host "Python not found at: $pythonExe" -ForegroundColor Red
    Write-Host "Create the backend venv first: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

$configuredQueue = [Environment]::GetEnvironmentVariable("CELERY_VIDEO_QUEUE")
if ([string]::IsNullOrWhiteSpace($Queue)) {
    if ([string]::IsNullOrWhiteSpace($configuredQueue)) {
        $Queue = "video,celery"
    }
    else {
        $Queue = "$($configuredQueue.Trim()),video,celery"
    }
}
Write-Host ("Using REDIS_URL host: {0}" -f $uri.Host) -ForegroundColor DarkCyan
Write-Host ("Listening queues: {0}" -f $Queue) -ForegroundColor DarkCyan

& $pythonExe -m celery -A app.celery_app worker `
    --pool=solo `
    --concurrency=1 `
    --without-gossip `
    --without-mingle `
    --without-heartbeat `
    -Q $Queue `
    --loglevel=info

$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    Write-Host "Celery exited with code $exitCode" -ForegroundColor Red
    exit $exitCode
}
