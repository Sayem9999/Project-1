@echo off
REM bootstrap.bat - One-command setup for Windows contributors
REM Usage: scripts\bootstrap.bat

echo 🚀 Setting up edit.ai development environment...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.11+
    exit /b 1
)
echo ✅ Python found

REM Create virtual environment if not exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install pip-tools
echo 📥 Installing pip-tools...
pip install --quiet pip-tools

REM Install dependencies
echo 📥 Installing dependencies...
if exist "requirements.lock" (
    pip install --quiet -r requirements.lock
) else (
    pip install --quiet -r requirements.txt
)

REM Check for .env file
if not exist ".env" (
    echo 📝 Creating .env from template...
    if exist ".env.example" (
        copy .env.example .env
        echo ⚠️ Please update .env with your API keys
    ) else (
        echo DATABASE_URL=sqlite+aiosqlite:///./dev.db > .env
        echo SECRET_KEY=dev-secret-key-change-in-production >> .env
        echo ⚠️ Created minimal .env - add your API keys
    )
)

REM Run migrations
echo 🗄️ Running database migrations...
alembic upgrade head 2>nul || echo ⚠️ Migrations skipped

echo.
echo ✨ Setup complete!
echo.
echo Next steps:
echo   1. Activate venv: venv\Scripts\activate
echo   2. Update .env with your API keys
echo   3. Start server: uvicorn app.main:app --reload
echo.
