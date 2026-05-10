# Tech Stack

Engineering reference for the full lifecycle — local development through production deployment.

## Language & Runtime

- **Python 3.12** (minimum version enforced via `requires-python = ">=3.12"` in `pyproject.toml`)

## Package Management

- **uv** manages all dependencies and virtual environments
- `uv.lock` pins the full resolved dependency graph — never install without it
- Inside Docker: `uv sync --frozen` (strict, no upgrades, no network resolution)
- Never use `pip` directly in any context

## Agent Framework

- **deepagents ≥0.5.7** — primary framework for defining agents; wraps LangChain tool and message abstractions with first-class support for Anthropic and Google models
- All agent definitions live in `agent.py` via `build_graph()` and a module-level `graph` export

## Agent Orchestration

- **langchain ≥1.2.17** — base abstractions (tools, messages, runnables)
- **langgraph** (transitive, resolved via `langgraph-cli`) — `StateGraph`, nodes, edges, `Send`, `Command`
- **langgraph-cli[inmem] ≥0.4.25** — CLI tooling and in-memory checkpointer; `langgraph dev` serves the Studio UI on `:2024`
- LangGraph config: `langgraph.json` points the dev server at `agent.py:graph`

## Model Providers

All providers are resolved as transitive dependencies via `deepagents`.

| Provider | Package | Models |
|---|---|---|
| Anthropic (primary) | `langchain-anthropic` | Claude (Opus, Sonnet, Haiku) |
| Google | `langchain-google-genai` | Gemini |
| OpenRouter (gateway) | `langchain-openrouter ≥0.2.3` | Multi-provider routing |

API keys are injected via environment variables (`.env` / `env_file`), never hardcoded.

## HTTP Layer

- **FastAPI ≥0.136.1** — HTTP surface defined in `api.py`
- **uvicorn[standard] ≥0.46.0** — ASGI server
- Endpoints: `GET /health`, `POST /chat`, `POST /chat/stream`
- Dev server: `make serve` (host, hot-reload); production: `uvicorn api:app` inside container

## Configuration

- **python-dotenv ≥1.2.2** — loads `.env` at runtime
- `.env` is gitignored and listed in `.dockerignore` — never copied into an image layer
- Docker Compose injects it at runtime via `env_file`
- Required variable: `ANTHROPIC_API_KEY`

## Dev Tooling

- **Makefile** — single entry point for all local and Docker workflows

  | Target | Action |
  |---|---|
  | `make install` | `uv sync` |
  | `make run` | One-shot demo via `main.py` |
  | `make serve` | FastAPI dev server on `:8000` |
  | `make dev` | LangGraph Studio on `:2024` |
  | `make docker-build/up/down/logs/shell/clean` | Container lifecycle |

## State Persistence

- **`AsyncPostgresSaver`** (`langgraph-checkpoint-postgres` ≥3.0) — durable, resumable conversations keyed by `thread_id`; backed by Postgres 17
- Postgres runs as a service in `docker-compose.yml`, exposed on `127.0.0.1:5433` (avoids conflict with Langfuse's Postgres on `5432`)
- `setup()` is called at FastAPI lifespan startup — idempotent, creates checkpoint tables on first run
- `main.py` (demo script) retains `InMemorySaver` — no persistence needed for one-shot runs
- Connection string injected via `POSTGRES_URI` env var; Docker Compose overrides it to the internal service name at runtime

## Containerization

- **Dockerfile** — multi-stage build:
  1. Builder stage: `ghcr.io/astral-sh/uv` resolves venv from `uv.lock` via `uv sync --frozen`
  2. Runtime stage: `python:3.12-slim`, runs as non-root user `appuser`
- **docker-compose.yml** — single `api` service; `.env` injected via `env_file`
- Healthcheck: `curl -fsS http://localhost:8000/health` every 30 s
- Only `api.py` is containerized; `main.py` and `langgraph dev` run on the host via `uv`

## Observability

- **Langfuse** — tracing, prompt management, and evals dashboard *(Phase 2, not yet integrated)*
- **Healthcheck endpoint** — `GET /health` is the liveness probe for both Docker and upstream load balancers

## CI/CD

- **GitHub Actions** — `.github/workflows/ci.yml` runs on every push and every PR targeting `main`
- Pipeline: `uv sync --frozen --group test` → `uv lock --check` → `ruff check` → `ruff format --check` → `pytest --cov --cov-fail-under=80` (coverage artifact uploaded) → `docker compose build`
- Local mirror: `make ci` runs the same steps; `make test` and `make lint` run individual checks
- Test framework: **pytest** + **pytest-asyncio** (auto mode) + **pytest-cov**; LLM and HTTP fully mocked — no live API calls in CI

## Deployment Target

TBD — not yet decided. Hard requirements:

- Docker image execution support
- Environment variable injection (no secret baking)
- Outbound HTTPS to `api.anthropic.com`, `generativelanguage.googleapis.com`, and `openrouter.ai`

---

[Mission](mission.md) | [Roadmap](roadmap.md)
