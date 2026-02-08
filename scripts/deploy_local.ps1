$ErrorActionPreference = "Stop"

$ROOT_DIR = Resolve-Path "$PSScriptRoot\.."
$BACKEND_DIR = "$ROOT_DIR\backend"
$FRONTEND_DIR = "$ROOT_DIR\frontend"
$RUNTIME_DIR = "$ROOT_DIR\.runtime"
$LOG_DIR = "$RUNTIME_DIR\logs"
$PID_DIR = "$RUNTIME_DIR\pids"

New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $PID_DIR | Out-Null
New-Item -ItemType Directory -Force -Path "$BACKEND_DIR\storage\uploads" | Out-Null
New-Item -ItemType Directory -Force -Path "$BACKEND_DIR\storage\outputs" | Out-Null

if (-not (Test-Path "$BACKEND_DIR\.env")) {
    Copy-Item "$BACKEND_DIR\.env.example" "$BACKEND_DIR\.env"
}

# Update .env for local dev if needed
$envContent = Get-Content "$BACKEND_DIR\.env" -Raw
if ($envContent -match "SECRET_KEY=change-me") {
    $envContent = $envContent -replace "SECRET_KEY=change-me", "SECRET_KEY=local-dev-secret-key"
    Set-Content "$BACKEND_DIR\.env" $envContent
}

# Venv setup
if (-not (Test-Path "$BACKEND_DIR\.venv")) {
    Write-Host "Creating virtual environment..."
    Set-Location "$BACKEND_DIR"
    python -m venv .venv
}

# Install backend deps
Write-Host "Installing backend dependencies..."
& "$BACKEND_DIR\.venv\Scripts\pip" install -r "$BACKEND_DIR\requirements.txt" | Out-Null

# Install frontend deps & build
Write-Host "Installing frontend dependencies & building..."
Set-Location "$FRONTEND_DIR"
cmd /c "npm install" | Out-Null
cmd /c "npm run build" | Out-Null

# Stop existing
& "$PSScriptRoot\stop_local.ps1"

# Start Backend
Write-Host "Starting Backend..."
$backendJob = Start-Process -FilePath "$BACKEND_DIR\.venv\Scripts\uvicorn.exe" -ArgumentList "app.main:app", "--host", "0.0.0.0", "--port", "8000" -WorkingDirectory "$BACKEND_DIR" -PassThru -NoNewWindow -RedirectStandardOutput "$LOG_DIR\backend.log" -RedirectStandardError "$LOG_DIR\backend.err.log"

# Start Frontend
Write-Host "Starting Frontend..."
$env:HOSTNAME = "0.0.0.0"
$env:PORT = "3000"
$frontendJob = Start-Process -FilePath "cmd" -ArgumentList "/c npm run start" -WorkingDirectory "$FRONTEND_DIR" -PassThru -NoNewWindow -RedirectStandardOutput "$LOG_DIR\frontend.log" -RedirectStandardError "$LOG_DIR\frontend.err.log"

# Wait for health
Write-Host "Waiting for services..."
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -Method Get -ErrorAction Stop
        if ($response.StatusCode -eq 200) { break }
    }
    catch {
        Start-Sleep -Seconds 1
    }
}
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:3000" -Method Get -ErrorAction Stop
        if ($response.StatusCode -eq 200) { break }
    }
    catch {
        Start-Sleep -Seconds 1
    }
}

$backendJob.Id | Out-File "$PID_DIR\backend.pid" -NoNewline
$frontendJob.Id | Out-File "$PID_DIR\frontend.pid" -NoNewline

Write-Host "Deployment started."
Write-Host "Backend PID: $($backendJob.Id)"
Write-Host "Frontend PID: $($frontendJob.Id)"
