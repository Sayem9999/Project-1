# Makefile for edit.ai backend
# Usage: make <target>

.PHONY: help install dev-setup test lint clean run

# Default target
help:
	@echo "Available targets:"
	@echo "  dev-setup    - One-command development setup"
	@echo "  install      - Install dependencies from lock file"
	@echo "  lock         - Generate requirements.lock from requirements.in"
# Makefile for edit.ai backend
# Usage: make <target>

.PHONY: help install dev-setup test lint clean run setup-ide

# Default target
help:
	@echo "Available targets:"
	@echo "  dev-setup    - One-command development setup"
	@echo "  install      - Install dependencies from lock file"
	@echo "  lock         - Generate requirements.lock from requirements.in"
	@echo "  test         - Run all tests"
	@echo "  lint         - Run linting checks"
	@echo "  ready        - Run backend readiness preflight"
	@echo "  run          - Start development server"
	@echo "  clean        - Remove generated files"
# Generate lock file from requirements.in
lock:
	pip-compile requirements.in -o requirements.lock --strip-extras

# Run database migrations
migrate:
	alembic upgrade head

# Run all tests
test:
	pytest tests/ -v --tb=short

# Readiness preflight
ready:
	python scripts/readiness_check.py

# Run tests with coverage
test-cov:
	pytest tests/ -v --cov=app --cov-report=html

# Run linting
lint:
	ruff check app/
	mypy app/ --ignore-missing-imports

# Start development server
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start with Celery worker
run-full:
	@echo "Starting Redis check..."
	redis-cli ping || echo "Warning: Redis not running"
	@echo "Starting Celery worker in background..."
	celery -A app.celery_app worker --loglevel=info &
	@echo "Starting FastAPI..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Clean generated files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage 2>/dev/null || true

# Format code
format:
	ruff format app/

# Check if all dependencies are installed correctly
check:
	python -c "import fastapi; import openai; import redis; import langgraph; print('✅ All core dependencies installed')"
