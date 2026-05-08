.DEFAULT_GOAL := help

.PHONY: help install run serve dev clean

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

install: ## Install / sync all dependencies
	uv sync

run: ## One-shot demo
	uv run python main.py

serve: ## FastAPI dev server → http://localhost:8000
	uv run uvicorn api:app --reload --port 8000

dev: ## LangGraph dev server + Studio UI → http://localhost:2024
	uv run langgraph dev

clean: ## Remove __pycache__ and .pyc files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
