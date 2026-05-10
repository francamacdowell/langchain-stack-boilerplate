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

## Constitution

- [Mission](docs/constitution/mission.md) — vision, scope, and guiding principles
- [Tech Stack](docs/constitution/tech-stack.md) — full stack reference, dev through deployment
- [Roadmap](docs/constitution/roadmap.md) — phases and current status
