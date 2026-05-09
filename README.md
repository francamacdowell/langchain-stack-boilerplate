# langchain-stack-boilerplate

Python 3.12 boilerplate for LangChain / LangGraph / `deepagents` applications, with a FastAPI wrapper and Docker support.

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) installed
- Docker + Docker Compose (for containerized workflow only)
- `.env` at the repo root:

  ```env
  ANTHROPIC_API_KEY="sk-ant-..."
  ```

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
