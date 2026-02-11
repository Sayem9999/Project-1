@echo off
setlocal
set "CELERY_VIDEO_QUEUE=video_local"

if /I "%~1" NEQ "RUN" (
  start "ProEdit Worker" cmd /k ""%~f0" RUN"
  exit /b 0
)

cd /d "%~dp0"

powershell -NoProfile -ExecutionPolicy Bypass -File ".\run_worker.ps1"
set "RC=%ERRORLEVEL%"
echo.
if "%RC%"=="0" (
  echo [INFO] Worker process exited with code 0.
) else (
  echo [ERROR] Worker failed to start. Exit code: %RC%
)
echo Press any key to close this window.
pause >nul
