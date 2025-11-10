.PHONY: help install run merge analyze regress thesis clean lint format test

help:
	@echo "📊 Environmental Data Analysis - Available Commands"
	@echo ""
	@echo "  make install          Install dependencies with Poetry"
	@echo "  make run              Run the full analysis pipeline"
	@echo "  make merge            Build the merged dataset only"
	@echo "  make analyze          Generate exploratory analysis outputs"
	@echo "  make regress          Execute regression models"
	@echo "  make thesis           Draft thesis-ready summary artifacts"
	@echo "  make clean            Remove output and cache files"
	@echo "  make lint             Check code quality (flake8)"
	@echo "  make format           Format code (black)"
	@echo "  make test             Run tests (pytest)"
	@echo ""

install:
	@echo "📦 Installing dependencies with Poetry..."
	poetry install --no-root
	@echo "✓ Dependencies installed"

run:
	@echo "🚀 Running environmental dataset analysis..."
	poetry run python run.py
	@echo "✓ Analysis complete! Check ./output directory"

merge:
	@echo "🧱 Building merged dataset stage..."
	poetry run python run.py --stage merge
	@echo "✓ Merge stage complete"

analyze:
	@echo "🔎 Running exploratory analysis stage..."
	poetry run python run.py --stage analyze
	@echo "✓ Analyze stage complete"

regress:
	@echo "📐 Executing regression stage..."
	poetry run python run.py --stage regress
	@echo "✓ Regress stage complete"

thesis:
	@echo "📝 Generating thesis synthesis stage..."
	poetry run python run.py --stage thesis
	@echo "✓ Thesis stage complete"

clean:
	@echo "🧹 Cleaning up..."
	rm -rf output __pycache__ .pytest_cache .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Cleanup complete"

lint:
	@echo "🔍 Checking code quality..."
	poetry run flake8 run.py --max-line-length=100
	@echo "✓ Linting complete"

format:
	@echo "✨ Formatting code with black..."
	poetry run black run.py --line-length=100
	@echo "✓ Formatting complete"

test:
	@echo "🧪 Running tests..."
	poetry run pytest tests/ -v
	@echo "✓ Tests complete"