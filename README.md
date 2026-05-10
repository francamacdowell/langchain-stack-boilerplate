# langchain-stack-boilerplate

Python 3.12 boilerplate for LangChain / LangGraph / `deepagents` applications, with a FastAPI wrapper and Docker support.

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) installed
- Docker + Docker Compose (required for the containerized workflow and for self-hosted Langfuse)
- `.env` at the repo root — copy [`.env.example`](.env.example) and fill in `ANTHROPIC_API_KEY` plus the Langfuse keys (see [Observability](#observability)).

## Running locally

```bash
make install   # install dependencies
make run       # run the demo agent (main.py)
make serve     # FastAPI on http://localhost:8000
make dev       # LangGraph dev server + Studio UI on http://localhost:2024
```

## Running with Docker (FastAPI only)

```bash
make docker-build   # build the image
make docker-up      # start → http://localhost:8000
make docker-down    # stop
```

Run `make help` to see all available targets.

## Observability

Tracing is provided by **self-hosted Langfuse**.

**1. Bring up Langfuse**

```bash
cp .env.langfuse.example .env.langfuse   # then fill in every secret
make langfuse-up                         # http://localhost:3000 (~3 min for first start)
```

`ENCRYPTION_KEY` must be 64 hex chars (`openssl rand -hex 32`). Hardware: 4 cores / 16 GiB RAM minimum.

**2. Create a project in the Langfuse UI**

Sign up locally at `http://localhost:3000`, create a project, and copy the public/secret keys from project settings.

**3. Wire the agent to Langfuse**

Add the keys to `.env`:

```env
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_HOST="http://localhost:3000"     # API on host
# LANGFUSE_HOST="http://host.docker.internal:3000"   # API in Docker
```

`make serve` (or `make run`, `make docker-up`) will fail at startup with a clear error if any of the three is missing.

**4. View traces**

Each `POST /chat` produces one trace; the request's `thread_id` becomes the Langfuse session, so multi-turn conversations group together. Stop the stack with `make langfuse-down`.

## State Persistence

Conversation history is stored in **Postgres** via `langgraph-checkpoint-postgres`. Each `thread_id` maps to a durable session that survives API restarts.

**Required env vars** (add to `.env`):

```env
POSTGRES_PASSWORD="changeme"
POSTGRES_URI="postgresql://postgres:changeme@localhost:5433/langgraph"
# When running via make docker-up, docker-compose.yml overrides POSTGRES_URI
# automatically to use the internal service name (postgres:5432).
```

**Local dev** — start Postgres, then the API:

```bash
make postgres-up   # Postgres on localhost:5433
make serve         # FastAPI on http://localhost:8000
make postgres-down # stop Postgres when done
```

**Docker** — Postgres starts automatically with the API:

```bash
make docker-up    # starts both api and postgres → http://localhost:8000
make docker-down  # stops both
```

`make serve` (and `make docker-up`) will fail at startup with a clear error if `POSTGRES_URI` is missing.

## Testing

<!-- CI badge — replace <owner>/<repo> once the repo is published on GitHub -->
<!-- [![CI](https://github.com/<owner>/<repo>/actions/workflows/ci.yml/badge.svg)](https://github.com/<owner>/<repo>/actions/workflows/ci.yml) -->

The test suite runs offline — no API key, no Langfuse stack, no internet access required.

```bash
make install   # installs runtime + test dependencies
make test      # run tests with ≥80 % coverage gate
make lint      # ruff check + format check
make ci        # mirrors the full GitHub Actions run locally
```

Pass pytest flags via `ARGS`:
```bash
make test ARGS="-k tracing -v"
```

CI runs automatically on every push and pull request via `.github/workflows/ci.yml`.

## Constitution

- [Mission](docs/constitution/mission.md) — vision, scope, and guiding principles
- [Tech Stack](docs/constitution/tech-stack.md) — full stack reference, dev through deployment
- [Roadmap](docs/constitution/roadmap.md) — phases and current status
