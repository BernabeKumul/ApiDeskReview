# Makefile for FastAPI Backend Project

.PHONY: help install setup run test clean dev docs lint format check-compat

# Default target
help:
	@echo "Available commands:"
	@echo "  setup      - Complete project setup (venv + dependencies + .env)"
	@echo "  install    - Install dependencies"
	@echo "  run        - Run the FastAPI application"
	@echo "  dev        - Run in development mode with auto-reload"
	@echo "  test       - Run tests"
	@echo "  test-cov   - Run tests with coverage"
	@echo "  lint       - Run linting checks"
	@echo "  format     - Format code"
	@echo "  clean      - Clean cache and temp files"
	@echo "  docs       - Open API documentation in browser"
	@echo "  check-compat - Check Python 3.13 compatibility"

# Setup project
setup:
	@echo "🚀 Setting up FastAPI project..."
	python setup.py

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

# Run application
run:
	@echo "🚀 Starting FastAPI application..."
	python run.py

# Run in development mode
dev:
	@echo "🔧 Starting in development mode..."
	uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Run tests
test:
	@echo "🧪 Running tests..."
	pytest tests/ -v

# Run tests with coverage
test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Linting
lint:
	@echo "🔍 Running linting checks..."
	@echo "This would run flake8, black --check, isort --check-only"
	@echo "Install dev dependencies first: pip install flake8 black isort"
	# flake8 app tests
	# black --check app tests
	# isort --check-only app tests

# Format code
format:
	@echo "✨ Formatting code..."
	@echo "This would run black and isort"
	@echo "Install dev dependencies first: pip install black isort"
	# black app tests
	# isort app tests

# Clean cache files
clean:
	@echo "🧹 Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cache cleaned"

# Open documentation
docs:
	@echo "📚 Opening API documentation..."
	@echo "Make sure the server is running, then visit:"
	@echo "  - Swagger UI: http://127.0.0.1:8000/docs"
	@echo "  - ReDoc: http://127.0.0.1:8000/redoc"

# Check Python 3.13 compatibility
check-compat:
	@echo "🧪 Checking Python 3.13 compatibility..."
	python check_compatibility.py

# Development environment info
info:
	@echo "ℹ️  Project Information:"
	@echo "  - Project: FastAPI Backend"
	@echo "  - Python: $(shell python --version)"
	@echo "  - FastAPI: Ready to run"
	@echo "  - API Docs: http://127.0.0.1:8000/docs"
	@echo "  - Health Check: http://127.0.0.1:8000/api/v1/health"