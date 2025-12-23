.PHONY: help install run run-all run-modelB run-modelC run-modelD merge analyze regress thesis clean lint format test

help:
	@echo "📊 Environmental-Health Regression Pipeline"
	@echo ""
	@echo "⚙️  SETUP:"
	@echo "  make install          Install dependencies with Poetry"
	@echo ""
	@echo "🔬 RUN MODELS:"
	@echo "  make run              Run all 3 models (B, C, D)"
	@echo "  make run-modelB       Run only Model B (PM2.5 → DALY)"
	@echo "  make run-modelC       Run only Model C (Sectoral Emissions → PM2.5)"
	@echo "  make run-modelD       Run only Model D (PM2.5 → YLL)"
	@echo ""
	@echo "🧹 CLEANUP:"
	@echo "  make clean            Remove output, cache, and logs"
	@echo "  make clean-output     Remove only output files"
	@echo ""
	@echo "📝 CODE QUALITY:"
	@echo "  make lint             Check code with flake8"
	@echo "  make format           Format code with black"
	@echo ""

install:
	@echo "📦 Installing dependencies with Poetry..."
	poetry install --no-root
	@echo "✓ Dependencies installed"

run: run-all

run-all:
	@echo "🚀 Running all 3 models (B, C, D)..."
	poetry run python run.py
	@echo "✓ All models complete! Check ./output directory"

run-modelB:
	@echo "🔬 Running Model B: PM₂.₅ → DALY (Health Burden)..."
	poetry run python run.py --model B
	@echo "✓ Model B complete! Check ./output/panel_b_health.csv"

run-modelC:
	@echo "🔬 Running Model C: Sectoral Emissions → PM₂.₅ (Panel FE)..."
	poetry run python run.py --model C
	@echo "✓ Model C complete! Check ./output/panel_c_sectoral.csv"

run-modelD:
	@echo "🔬 Running Model D: PM₂.₅ → YLL (Mortality Burden)..."
	poetry run python run.py --model D
	@echo "✓ Model D complete! Check ./output/panel_d_mortality.csv"

clean:
	@echo "🧹 Cleaning up output, cache, and logs..."
	rm -rf output __pycache__ .pytest_cache .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Cleanup complete"

clean-output:
	@echo "🧹 Cleaning output directory only..."
	rm -rf output/*.csv output/*.txt output/*.png
	@echo "✓ Output files removed (keeping logs)"

lint:
	@echo "🔍 Checking code quality..."
	poetry run flake8 run.py src/ --max-line-length=100
	@echo "✓ Linting complete"

format:
	@echo "✨ Formatting code with black..."
	poetry run black run.py src/ --line-length=100
	@echo "✓ Formatting complete"

test:
	@echo "🧪 Running tests..."
	poetry run pytest tests/ -v
	@echo "✓ Tests complete"