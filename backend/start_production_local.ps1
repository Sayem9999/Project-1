param(
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$pythonExe = Join-Path $scriptDir ".venv\Scripts\python.exe"

Write-Host "--- Starting Proedit API (Production Local) ---" -ForegroundColor Cyan

# Ensure storage
if (-not (Test-Path "storage")) { New-Item -ItemType Directory "storage" }
if (-not (Test-Path "storage/uploads")) { New-Item -ItemType Directory "storage/uploads" }
if (-not (Test-Path "storage/outputs")) { New-Item -ItemType Directory "storage/outputs" }

# Load env variables
if (Test-Path ".env") {
    Get-Content .env | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
            $parts = $line.Split("=", 2)
            $name = $parts[0].Trim()
            $value = $parts[1].Trim().Trim('"').Trim("'")
            [Environment]::SetEnvironmentVariable($name, $value)
        }
    }
}

$env:ENVIRONMENT = "production"

Write-Host "API running on: http://localhost:$Port" -ForegroundColor Green
Write-Host "Connect your Cloudflare Tunnel to this port." -ForegroundColor Blue

& $pythonExe -m uvicorn app.main:app `
    --host 0.0.0.0 `
    --port $Port `
    --workers 4 `
    --log-level info `
    --timeout-keep-alive 65
