# Contributing

Thank you for your interest in contributing to `langchain-stack-boilerplate`.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — the only package manager used in this project (no `pip`)
- Docker + Docker Compose — required for the containerized workflow and self-hosted Langfuse
- A `.env` file at the repo root (copy `.env.example` and fill in your keys)

## Local dev setup

```bash
git clone git@github.com:francamacdowell/langchain-stack-boilerplate.git
cd langchain-stack-boilerplate
cp .env.example .env   # fill in ANTHROPIC_API_KEY and Langfuse keys
make install           # installs all dependencies via uv
```

## Development loop

```bash
make run     # one-shot demo (main.py)
make serve   # FastAPI dev server → http://localhost:8000
```

Run `make help` to see all available targets.

## Testing and linting

The test suite runs fully offline — no live API keys, no running services required.

```bash
make test       # pytest with ≥80 % coverage gate
make lint       # ruff check + ruff format --check
make lint-fix   # auto-fix style issues
make ci         # mirrors the full GitHub Actions pipeline locally
```

Pass extra pytest flags via `ARGS`:

```bash
make test ARGS="-k tracing -v"
```

## Branch and commit conventions

- **Branches**: `feat-*`, `fix-*`, `docs-*`, `chore-*`
  Example: `feat-streaming-endpoint`, `fix-postgres-timeout`
- **Commits**: [conventional commit](https://www.conventionalcommits.org/) prefixes —
  `feat:`, `fix:`, `docs:`, `chore:`, `ci:`, `test:`, `refactor:`
- Keep commits small and focused; one logical change per commit.

## Opening a pull request

1. Branch off `main`.
2. Make your changes; run `make ci` to confirm everything passes.
3. Push and open a PR targeting `main`.
4. CI runs automatically when the PR is opened.
5. Once CI is green and the diff looks good, the PR can be merged.

**PR checklist**:

- [ ] `make lint` passes
- [ ] `make test` passes with ≥ 80 % coverage
- [ ] `docker compose build` passes (if `Dockerfile` or dependencies changed)
- [ ] No `.env` or secret files committed

## Guiding principles

The project's guiding principles are in the [mission doc](docs/constitution/mission.md).
The two most relevant for contributors:

- **uv-only** — never use `pip`, including in Docker layers.
- **Minimal ceremony** — no abstractions before they are needed; three similar lines beat a premature helper.

See also: [Tech Stack](docs/constitution/tech-stack.md) | [Roadmap](docs/constitution/roadmap.md)
