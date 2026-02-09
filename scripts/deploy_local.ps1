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
$backendHealth = $false
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -Method Get -ErrorAction Stop
        if ($response.StatusCode -eq 200) { 
            $backendHealth = $true
            break 
        }
    }
    catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $backendHealth) {
    Write-Error "Backend failed to start or failed health check."
    exit 1
}

# Verify Backend PID is still running
if (-not (Get-Process -Id $backendJob.Id -ErrorAction SilentlyContinue)) {
    Write-Error "Backend process exited unexpectedly."
    exit 1
}

$frontendHealth = $false
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:3000" -Method Get -ErrorAction Stop
        if ($response.StatusCode -eq 200) { 
            $frontendHealth = $true
            break 
        }
    }
    catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $frontendHealth) {
    Write-Error "Frontend failed to start or failed health check."
    exit 1
}

# Find actual Frontend Node PID (the one running next)
# We look for a node process started recently with command line containing "next"
$frontendPid = 0
$candidates = Get-CimInstance Win32_Process | Where-Object { $_.Name -like "node.exe" -and $_.CommandLine -like "*next*" }
# Simple heuristic: pick the one started most recently, or if multiple, the parent of the child?
# Actually cleaner: rely on the fact we just started it.
# But since we can't easily get children of the shell we started, let's look for the process whose ParentProcessId points to our shell... hard to track.
# Better: Look for the process listening on port 3000.
$netstat = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
if ($netstat) {
    $frontendPid = $netstat.OwningProcess
}

if ($frontendPid -eq 0) {
    Write-Warning "Could not determine Frontend PID via port 3000. Using shell PID (unreliable for stopping)."
    $frontendPid = $frontendJob.Id
}

# Verify Frontend PID is still running
if (-not (Get-Process -Id $frontendPid -ErrorAction SilentlyContinue)) {
    Write-Error "Frontend process (PID $frontendPid) exited unexpectedly."
    exit 1
}

$backendJob.Id | Out-File "$PID_DIR\backend.pid" -NoNewline
$frontendPid | Out-File "$PID_DIR\frontend.pid" -NoNewline

Write-Host "Deployment started successfully." -ForegroundColor Green
Write-Host "Backend PID: $($backendJob.Id)"
Write-Host "Frontend PID: $frontendPid"
