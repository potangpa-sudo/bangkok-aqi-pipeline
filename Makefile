.PHONY: setup run transform test dashboard clean all

setup:
	@echo "📦 Installing dependencies..."
	python3 -m pip install -r requirements.txt
	@echo "📁 Creating directories..."
	mkdir -p data/raw data/screenshots
	@echo "✅ Setup complete!"

run:
	@echo "🚀 Running full pipeline..."
	python3 -m src.pipeline
	@echo "✅ Pipeline complete!"

transform:
	@echo "🔄 Running SQL transformations only..."
	python3 -m src.run_sql
	@echo "✅ Transformations complete!"

test:
	@echo "🧪 Running tests..."
	python3 -m src.tests
	@echo "✅ Tests passed!"

dashboard:
	@echo "📊 Launching Streamlit dashboard..."
	python3 -m streamlit run app/dashboard.py

clean:
	@echo "🧹 Cleaning generated files..."
	rm -rf data/warehouse.duckdb data/raw/*.json
	rm -rf __pycache__ src/__pycache__ app/__pycache__
	@echo "✅ Clean complete!"

all: setup run test dashboard
