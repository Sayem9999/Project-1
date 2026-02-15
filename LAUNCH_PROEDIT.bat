@echo off
setlocal
cd /d %~dp0
echo 🚀 INITIALIZING PROEDIT SUITE...
powershell -ExecutionPolicy Bypass -File ".\start_locally.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ ERROR: Failed to launch. Make sure you have the .venv folder in the backend directory.
    pause
)
exit /b 0
