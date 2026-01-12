# Makefile for Housing ML project

.PHONY: help install test lint format clean build run deploy

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	uv sync

test: ## Run tests
	uv run pytest

lint: ## Run linting
	uv run flake8 src/ test/

format: ## Format code
	uv run black src/ test/
	uv run isort src/ test/

clean: ## Clean up
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf dist/
	rm -rf build/

build: ## Build Docker images
	docker build -t housing-api .
	docker build -t housing-streamlit -f Dockerfile.streamlit .

build-api: ## Build API Docker image
	docker build -t housing-api .

build-dashboard: ## Build dashboard Docker image
	docker build -t housing-streamlit -f Dockerfile.streamlit .

run: ## Run the API locally
	uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

run-dashboard: ## Run the dashboard locally
	streamlit run app.py

run-compose: ## Run both services with docker-compose
	docker-compose up

deploy: ## Deploy to production (placeholder)
	@echo "Deploying to production..."

train: ## Run model training
	uv run python -m src.model_training.train

infer: ## Run inference
	uv run python -m src.inference_pipeline.inference --input data/sample.csv --output predictions.csv