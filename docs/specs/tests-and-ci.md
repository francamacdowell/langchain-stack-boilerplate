# Task Spec — Tests & CI

**Phase:** 3 (Tests & CI)
**Status:** Draft, ready for planning
**Owner:** Engineering
**Date:** 2026-05-10

---

## 1. Outcomes

Concrete success states once Phase 3 ships:

- A contributor on a fresh checkout runs `make install && make test` and the suite passes in under 30 seconds — with **no** Anthropic API key, **no** Langfuse stack running, **no** internet access, and **no** Docker running.
- Every push to any branch and every pull request targeting `main` triggers a GitHub Actions workflow that runs four checks — pytest suite, ruff lint+format, `uv.lock` sync, Docker build — and the workflow goes red if any one of them fails.
- `pytest-cov` measures line coverage on `tracing.py`, `agent.py`, and `api.py`; CI fails if combined coverage drops below **80 %**.
- The test suite is deterministic and free: no live LLM call, no real outbound HTTP, no live Langfuse SDK. Re-running CI on the same commit produces identical results.
- The `make ci` target (or `make lint test`) runs the same commands as GitHub Actions — "green locally" implies "green in CI."
- A regression introduced in any of the three target modules surfaces in a single, localized test failure with a stack trace pointing at the assertion (not buried inside `deepagents` or `langgraph`).
- The `Dockerfile` builds successfully against the current source tree (today it does not — `tracing.py` is missing from the `COPY` directives, so the runtime image is broken). The Docker-build CI gate enforces this stays true.

## 2. In Scope / Out of Scope

### In scope

- pytest-based test suite covering:
  - `tracing.py`: env-var validation, handler caching, `build_config` shape, `shutdown` wiring
  - `agent.py`: `fetch_text_from_url` happy + error paths, `build_graph()` produces an invokable graph that processes a message end-to-end against a **fake** chat model
  - `api.py`: `/health`, `/chat` (success + error), `/chat/stream` (SSE chunk shape + error path), `_extract_text`, `_thread`
- pytest configuration (`[tool.pytest.ini_options]`) and coverage configuration (`[tool.coverage.*]`) in `pyproject.toml`
- A new `[dependency-groups]` test group in `pyproject.toml` with: `pytest`, `pytest-asyncio`, `pytest-cov`, `httpx`, `ruff`
- ruff configuration (`[tool.ruff]`) covering existing sources without churn
- `.github/workflows/ci.yml` running on `push` (any branch) and `pull_request` (target: `main`)
- CI steps: install `uv` → `uv sync --frozen --group test` → `uv lock --check` → `uv run ruff check && uv run ruff format --check` → `uv run pytest --cov --cov-fail-under=80` → `docker compose build`
- Makefile targets: `make test`, `make lint`, `make ci` (composes the others)
- Fix `Dockerfile` so `tracing.py` is copied into both the builder and runtime stages (hard-coupled to the Docker-build gate — the gate cannot pass without this fix)
- README "Testing" section walking a contributor from clone to green test run
- Roadmap update — check off Phase 3 entries

### Out of scope

- Static type checking (mypy, pyright) — explicitly deselected during Phase 3 scoping
- Live integration tests against the real Anthropic API or real URLs (mocking only)
- Tests against a running Langfuse stack (`langfuse.langchain.CallbackHandler` is mocked at the import seam)
- Tests for `main.py` (it is a one-shot demo script for humans, not a regression target)
- Pre-commit hooks (`pre-commit` framework or git hooks)
- GitHub branch protection rules / required status configuration (set in repo settings, not by code)
- Multi-Python-version test matrix — Python 3.12 only (per `pyproject.toml requires-python = ">=3.12"`)
- Codecov / Coveralls / external coverage hosting (coverage report stays in CI logs and artifacts)
- Mutation testing, property-based testing, load testing, snapshot testing
- LLM-as-judge evaluation pipelines (already out-of-scope in the Langfuse spec)

## 3. Constraints and Assumptions

### Constraints

- Python 3.12 only — enforced by `pyproject.toml requires-python`.
- **`uv` only** — CI must use `uv sync --frozen` and `uv run`, never `pip` (per [Mission](../constitution/mission.md) and [Tech Stack](../constitution/tech-stack.md)).
- Tests must run **without** `ANTHROPIC_API_KEY`, **without** `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_HOST`, and **without** internet access. CI workflows must not declare these as required secrets.
- `tracing._require_env` raises when those env vars are missing — tests must monkeypatch the handler factory or the env, not real-load Langfuse.
- The self-hosted Langfuse stack (per `docker-compose.langfuse.yml`) must **not** be started in CI — it is heavyweight (~3 min cold start, 16 GiB RAM minimum).
- `langgraph dev` and Studio UI are not exercised in CI (already non-goal in [Langfuse spec](langfuse-integration.md) §10).
- GitHub Actions runners use `ubuntu-latest` — no macOS-only tooling on the CI path.
- Docker build inside CI must use the standard `docker compose build` (no buildx-only features) so it matches `make docker-build` locally.
- The `Dockerfile` today does not include `tracing.py` in either `COPY` directive. The Docker-build CI gate will surface this immediately; the fix is required for any CI run to be green.

### Assumptions (correct any that are wrong before implementation)

- The repo will eventually be hosted on GitHub. Until then, the workflow file lives in-tree and is dormant. README badge URL is left as a TODO comment with `<owner>/<repo>` placeholder.
- Coverage measured against `tracing.py`, `agent.py`, `api.py` only. `main.py` is excluded from coverage measurement (not a CI target).
- ruff is configured with project defaults (E, F, I, UP, B rule families) — implementer chooses the exact set during planning if a stricter or looser starting point is preferred.
- Test layout: a single `tests/` directory at the repo root, with files named `test_tracing.py`, `test_agent.py`, `test_api.py`. No nested packages.
- `make test` accepts pytest passthrough args (e.g., `make test ARGS="-k tracing"`); exact Makefile mechanic is implementer's choice.

## 4. Decisions Already Made

These are pinned. Do not relitigate during planning.

| Decision | Choice | Source / rationale |
|---|---|---|
| Test framework | **pytest** | Python ecosystem standard; integrates with pytest-asyncio and pytest-cov out of the box |
| Async test runner | **pytest-asyncio** in auto mode | `/chat` and `/chat/stream` are async; auto mode avoids decorating every test |
| ASGI test client | **httpx.AsyncClient via `ASGITransport`** | Supports streaming endpoints; `fastapi.testclient.TestClient` is sync and awkward for SSE |
| LLM mocking | **`langchain_core.language_models.fake_chat_models.FakeListChatModel`** | Drop-in `BaseChatModel`; tool calling can be simulated by feeding scripted message sequences |
| LLM injection seam | **monkeypatch `agent._model`** (or refactor to a small factory if cleaner) — leave the seam choice to the planning step | The plan decides whether to monkeypatch in-place or introduce a tiny `_make_model()` indirection |
| HTTP mocking for `fetch_text_from_url` | **monkeypatch `urllib.request.urlopen`** | The tool uses stdlib `urllib`; `respx` would require switching to `httpx` |
| Langfuse SDK mocking | **monkeypatch `tracing.get_handler` and `tracing.get_client`** at test boundary | Avoids importing the real `CallbackHandler` against missing env |
| Coverage tool | **pytest-cov + coverage.py** | Standard pairing; `--cov-fail-under=80` gates CI |
| Coverage target | **80 % line, hard fail** | Per Phase 3 scoping decision |
| Linter / formatter | **ruff** (single tool for both) | Replaces black + flake8 + isort; fast; widely adopted |
| Static type checker | **None in this phase** | Explicitly deselected during Phase 3 scoping |
| CI provider | **GitHub Actions** | Per Phase 3 scoping decision; default for open-source Python |
| CI workflow path | `.github/workflows/ci.yml` | Convention |
| CI triggers | `push` (any branch) and `pull_request` (target: `main`) | Standard policy for "every push and PR" per [Roadmap](../constitution/roadmap.md) |
| CI runner | `ubuntu-latest` | GitHub Actions default; matches Linux-based deployment targets |
| `uv` install in CI | `astral-sh/setup-uv@v3` (or current major) action | Standard, maintained by upstream |
| Test dependency group | `[dependency-groups]` test group in `pyproject.toml`, installed via `uv sync --group test` | Native uv feature; keeps runtime image lean |
| Test directory layout | `tests/` at repo root, files named `test_<module>.py` | One-to-one mapping with target source files |
| Python version in CI | **3.12 only** (no matrix) | Per `pyproject.toml requires-python = ">=3.12"`; matrix would add cost without adding signal for a boilerplate |

## 5. Task Breakdown

Independent work-packages. Sequencing, dependencies, and step ordering are decided in `/planning-phase`.

- **WP-1 — Test scaffolding**
  Add the `[dependency-groups]` test group (`pytest`, `pytest-asyncio`, `pytest-cov`, `httpx`, `ruff`); create `tests/` and `tests/conftest.py`; configure `[tool.pytest.ini_options]` (asyncio_mode = "auto", testpaths) and `[tool.coverage.run]` / `[tool.coverage.report]` in `pyproject.toml`.

- **WP-2 — `tests/test_tracing.py`**
  Cover: `_require_env` raises with each of the three vars missing individually and with all three set; `get_handler()` returns the same instance on repeat calls (lru_cache); `build_config(thread_id)` returns the expected dict shape including `configurable.thread_id`, `callbacks`, `metadata.langfuse_session_id`; `shutdown()` calls `get_client().shutdown()`.

- **WP-3 — `tests/test_agent.py`**
  Cover: `fetch_text_from_url` happy path (urlopen returns bytes → tool returns decoded string); `fetch_text_from_url` URLError path (returns the `"Fetch failed: ..."` string, never raises); `build_graph()` returns an object with `.invoke` / `.ainvoke`; an end-to-end invocation with a fake chat model that triggers `fetch_text_from_url` and produces a final assistant message.

- **WP-4 — `tests/test_api.py`**
  Cover: `GET /health` returns `{"status": "ok"}`; `POST /chat` with empty `thread_id` (server generates uuid) and with provided `thread_id` (round-trip); `POST /chat` 500 path when the agent raises; `POST /chat/stream` SSE chunk shape (`data: {...}\n\n`, terminated by `data: [DONE]\n\n`); `POST /chat/stream` error path emits `data: {"error": "..."}\n\n` then `[DONE]`; `_extract_text` for `str`, `list` of dict-blocks, `list` of non-dict items, and a non-iterable.

- **WP-5 — ruff configuration**
  Add `[tool.ruff]` to `pyproject.toml` with the chosen rule set; run `ruff check --fix` and `ruff format` once on existing sources; commit the result so the CI gate is green from the first run.

- **WP-6 — GitHub Actions workflow**
  `.github/workflows/ci.yml`: triggers `push` + `pull_request` (main); single job (or split jobs) running checkout → `astral-sh/setup-uv` → `uv sync --frozen --group test` → `uv lock --check` → `uv run ruff check` → `uv run ruff format --check` → `uv run pytest --cov --cov-fail-under=80 --cov-report=term --cov-report=xml` → `docker compose build`. Upload the coverage XML as a workflow artifact.

- **WP-7 — `Dockerfile` fix** *(hard-coupled to WP-6)*
  Add `tracing.py` to both `COPY` directives in `Dockerfile` (builder stage line and runtime stage line). The Docker-build CI gate from WP-6 cannot pass without this; ship the two together.

- **WP-8 — Makefile targets and README**
  Add `make test`, `make lint`, `make ci` (composes the previous two plus `uv lock --check` and `docker compose build`); add a "Testing" section to `README.md` walking through `make install` → `make test` → `make ci`; add a CI badge stub with a `<owner>/<repo>` TODO placeholder.

- **WP-9 — Roadmap update**
  Check off "Test module" and "CI pipeline" entries in `docs/constitution/roadmap.md`; update [Tech Stack](../constitution/tech-stack.md) §CI/CD ("TBD") with a one-line summary of the new workflow.

## 6. Verification Criteria

Each criterion is a pass/fail statement. Test methodology (which fixtures, which commands, in what order) is decided in `/planning-phase`.

For **Outcome 1** (full suite green offline):

- [ ] `make install && make test` exits 0 on a fresh checkout with `ANTHROPIC_API_KEY` and `LANGFUSE_*` unset.
- [ ] The suite completes in under 30 s on a developer laptop (Apple Silicon or modern x86).
- [ ] No test imports trigger a real network call (verified by running tests with networking disabled, or by inspection if that is impractical).

For **Outcome 2** (CI runs the full bundle):

- [ ] `.github/workflows/ci.yml` declares triggers on `push` (no branch filter) and `pull_request` with `branches: [main]`.
- [ ] Workflow exposes four logical checks (whether as one job with steps or four jobs): pytest, ruff, `uv lock --check`, Docker build.
- [ ] Deliberately introducing a regression in any one of the four (a stale lock, an unformatted file, a broken Dockerfile `COPY`, a failing assertion) causes the workflow to go red.
- [ ] Workflow uses `uv sync --frozen` and never invokes `pip`.

For **Outcome 3** (≥80 % coverage):

- [ ] CI invokes pytest with `--cov-fail-under=80`.
- [ ] Coverage is measured on `tracing.py`, `agent.py`, `api.py` (and only these — `main.py` excluded via `[tool.coverage.run] omit`).
- [ ] Coverage XML is uploaded as a workflow artifact and the per-file table is printed in the CI summary.
- [ ] Lowering coverage to 79 % (e.g., by deleting one tested branch) fails CI.

For **Outcome 4** (deterministic, free):

- [ ] Every test that exercises `agent.py` or `api.py` patches the chat model — verified by grep on the test files (`FakeListChatModel` or equivalent appears wherever an invocation occurs).
- [ ] Every test exercising `fetch_text_from_url` patches `urllib.request.urlopen`.
- [ ] Every test importing from `tracing.py` patches `get_handler` / `get_client` / `CallbackHandler` at the import boundary.
- [ ] Two consecutive CI runs against the same commit produce identical pass/fail outcomes (no flakes from network or LLM nondeterminism).

For **Outcome 5** (localized failure traces):

- [ ] Manual regression injection: deleting one branch from `_require_env`, one from `_extract_text`, and one from `fetch_text_from_url` each surfaces a single failing test whose stack trace points at the assertion in the test file (not at a frame inside `deepagents` / `langgraph` / `httpx`).

For **Outcome 6** (local = CI parity):

- [ ] `make ci` runs the same shell commands as the GitHub Actions workflow steps, in the same order.
- [ ] `make ci` on a clean checkout produces the same exit status as the workflow on the same commit.

For **Outcome 7** (Dockerfile builds):

- [ ] `docker compose build` succeeds on a clean checkout.
- [ ] The resulting image, when run, can `import tracing` without `ModuleNotFoundError` (verified by a one-shot `docker compose run --rm api python -c "import tracing"` in CI or as a manual smoke test).

### Edge cases / failure modes that must be exercised

- `_require_env` raises when **any single** Langfuse var is missing (test all three independently, plus the all-set case).
- `get_handler()` is called twice → returns the same instance.
- `/chat` with `thread_id=""` → server generates a uuid; with a non-empty `thread_id` → it round-trips unchanged.
- `/chat/stream` happy path: SSE frame shape is exactly `data: {"content": "...", "thread_id": "..."}\n\n`, and the stream terminates with `data: [DONE]\n\n`.
- `/chat/stream` error path: a streamed `data: {"error": "..."}\n\n` is followed by `data: [DONE]\n\n` (the `[DONE]` is **not** suppressed on error).
- `_extract_text` on a `str`, on a `list[dict]` with `text` keys, on a `list[dict]` with missing `text` keys (returns empty string for that block), on a `list` of non-dict items, and on a non-iterable object.
- `fetch_text_from_url` URLError path returns the `"Fetch failed: ..."` string and does **not** raise.

### Criteria that cannot be verified at this stage

- "Production CI parity" — there is no production target yet, so there is nothing to compare CI artifacts against. Re-evaluate once Phase 4 (Production) defines a deployment target.

## Open Questions

- **GitHub URL** — what `<owner>/<repo>` should the README badge point to? **Default**: leave as a TODO comment until the repo is published.
- **Codecov / Coveralls** — out of scope for this phase. Revisit if external coverage hosting becomes a requirement.
- **`make test` argument passthrough** — exact Makefile mechanic is implementer's discretion; the planning step will pick a pattern.

## References

- [Roadmap](../constitution/roadmap.md) — Phase 3 source of truth
- [Tech Stack](../constitution/tech-stack.md) — Python / `uv` / packaging constraints
- [Mission](../constitution/mission.md) — uv-only and minimal-ceremony principles
- [Langfuse spec](langfuse-integration.md) — observability surfaces this phase tests
- [pytest-asyncio docs](https://pytest-asyncio.readthedocs.io)
- [LangChain `FakeListChatModel`](https://python.langchain.com/api_reference/core/language_models/langchain_core.language_models.fake_chat_models.FakeListChatModel.html)
- [`astral-sh/setup-uv` GitHub Action](https://github.com/astral-sh/setup-uv)
- [ruff configuration](https://docs.astral.sh/ruff/configuration/)

---

[Mission](../constitution/mission.md) | [Tech Stack](../constitution/tech-stack.md) | [Roadmap](../constitution/roadmap.md)
