#!/usr/bin/env bash
# bootstrap.sh - One-command setup for contributors
# Usage: ./scripts/bootstrap.sh

set -e

echo "🚀 Setting up edit.ai development environment..."

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | grep -oP '\d+\.\d+')
REQUIRED_VERSION="3.11"

if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
    echo "❌ Python $REQUIRED_VERSION+ required, found $PYTHON_VERSION"
    exit 1
fi
echo "✅ Python $PYTHON_VERSION"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate

# Install pip-tools
echo "📥 Installing pip-tools..."
pip install --quiet pip-tools

# Install dependencies
echo "📥 Installing dependencies from lock file..."
if [ -f "requirements.lock" ]; then
    pip install --quiet -r requirements.lock
else
    echo "⚠️ Lock file not found, installing from requirements.txt"
    pip install --quiet -r requirements.txt
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "⚠️ Please update .env with your API keys"
    else
        echo "DATABASE_URL=sqlite+aiosqlite:///./dev.db" > .env
        echo "SECRET_KEY=dev-secret-key-change-in-production" >> .env
        echo "⚠️ Created minimal .env - add your API keys"
    fi
fi

# Run migrations
echo "🗄️ Running database migrations..."
alembic upgrade head 2>/dev/null || echo "⚠️ Migrations skipped (run 'alembic upgrade head' manually)"

# Verify installation
echo ""
echo "🔍 Verifying installation..."
python -c "
import fastapi
import openai
import redis
print('  ✅ FastAPI')
print('  ✅ OpenAI')
print('  ✅ Redis')
" 2>/dev/null || echo "  ⚠️ Some packages may need manual installation"

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate venv: source venv/bin/activate"
echo "  2. Update .env with your API keys"
echo "  3. Start server: make run"
echo ""
