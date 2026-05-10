.DEFAULT_GOAL := help

.PHONY: help install run serve dev clean \
	test lint lint-fix ci \
	postgres-up postgres-down \
	docker-build docker-up docker-down docker-logs docker-shell docker-clean \
	langfuse-up langfuse-down langfuse-logs

LANGFUSE_COMPOSE := docker compose --env-file .env.langfuse -f docker-compose.langfuse.yml

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Install / sync all dependencies (including test group)
	uv sync --group test

test: ## Run tests with coverage (≥80 % gate)
	uv run pytest --cov --cov-fail-under=80 $(ARGS)

lint: ## Check style and formatting (ruff)
	uv run ruff check . && uv run ruff format --check .

lint-fix: ## Auto-fix style and formatting issues
	uv run ruff check --fix . && uv run ruff format .

ci: ## Mirror the full GitHub Actions CI run locally
	uv lock --check
	$(MAKE) lint
	$(MAKE) test
	docker compose build

run: ## One-shot demo
	uv run python main.py

clean: ## Remove __pycache__ and .pyc files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

postgres-up: ## Start Postgres for local dev → localhost:5433
	docker compose up -d postgres

postgres-down: ## Stop the Postgres service
	docker compose stop postgres

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
