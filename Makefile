.DEFAULT_GOAL := help

.PHONY: help install run serve dev clean \
	docker-build docker-up docker-down docker-logs docker-shell docker-clean \
	langfuse-up langfuse-down langfuse-logs

LANGFUSE_COMPOSE := docker compose --env-file .env.langfuse -f docker-compose.langfuse.yml

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

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

docker-build: ## Build the FastAPI Docker image
	docker compose build

docker-up: ## Start FastAPI in Docker → http://localhost:8000
	docker compose up -d

docker-down: ## Stop the Docker stack
	docker compose down

docker-logs: ## Tail logs from the api container
	docker compose logs -f api

docker-shell: ## Open a shell inside the api container
	docker compose exec api bash

docker-clean: ## Stop the stack and remove the local image
	docker compose down --rmi local

langfuse-up: ## Start self-hosted Langfuse → http://localhost:3000
	$(LANGFUSE_COMPOSE) up -d

langfuse-down: ## Stop the self-hosted Langfuse stack
	$(LANGFUSE_COMPOSE) down

langfuse-logs: ## Tail logs from langfuse-web
	$(LANGFUSE_COMPOSE) logs -f langfuse-web
