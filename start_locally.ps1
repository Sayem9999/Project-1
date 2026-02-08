# Start Local Development
$ErrorActionPreference = "Stop"

$env:Path = "$PSScriptRoot\tools\ffmpeg-8.0.1-essentials_build\bin;$env:Path"

Write-Host "Starting Backend..." -ForegroundColor Green
Start-Process -FilePath "python" -ArgumentList "-m uvicorn app.main:app --reload --port 8000" -WorkingDirectory "backend" -NoNewWindow

Write-Host "Starting Frontend..." -ForegroundColor Green
Start-Process -FilePath "npm.cmd" -ArgumentList "run dev" -WorkingDirectory "frontend" -NoNewWindow

Write-Host "Application starting..."
Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:3000"
