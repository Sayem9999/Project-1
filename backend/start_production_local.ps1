param(
    [int]$Port = 8000,
    [int]$Workers = 1
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$pythonExe = Join-Path $scriptDir ".venv\Scripts\python.exe"

Write-Host "--- Starting Proedit API (Production Local) ---" -ForegroundColor Cyan

# Permanent Fix: Kill any existing process on the target port
Write-Host "Checking for existing processes on port $Port..." -ForegroundColor Gray
$prevProcess = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($prevProcess) {
    Write-Host "Cleaning up existing process (PID: $prevProcess) on port $Port..." -ForegroundColor Yellow
    Stop-Process -Id $prevProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

# Ensure storage
if (-not (Test-Path "storage")) { New-Item -ItemType Directory "storage" }
if (-not (Test-Path "storage/uploads")) { New-Item -ItemType Directory "storage/uploads" }
if (-not (Test-Path "storage/outputs")) { New-Item -ItemType Directory "storage/outputs" }

# Load env variables with override
if (Test-Path ".env") {
    Get-Content .env | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
            $parts = $line.Split("=", 2)
            $name = $parts[0].Trim()
            $value = $parts[1].Trim().Trim('"').Trim("'")
            # Force set in process scope to override system env vars
            [Environment]::SetEnvironmentVariable($name, $value, [EnvironmentVariableTarget]::Process)
        }
    }
}

$env:ENVIRONMENT = "production"

Write-Host "API running on: http://localhost:$Port" -ForegroundColor Green
Write-Host "Connect your Cloudflare Tunnel to this port." -ForegroundColor Blue

& $pythonExe -m uvicorn app.main:app `
    --host 0.0.0.0 `
    --port $Port `
    --workers $Workers `
    --log-level info `
    --timeout-keep-alive 65
