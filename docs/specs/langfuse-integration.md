# Task Spec — Langfuse Integration

**Phase:** 2 (Observability & Docs)
**Status:** Draft, ready for implementation
**Owner:** Engineering
**Date:** 2026-05-09

---

## 1. Objective

Wire **Langfuse** observability into the agent so that every LLM call, tool invocation, and graph traversal step originating from `agent.py` is automatically traced and visible in a Langfuse dashboard — both for local development and for the containerized FastAPI service.

## 2. Context

| Area | Current state |
|---|---|
| Agent | `agent.py` builds a `deepagents` graph; one tool (`fetch_text_from_url`); model is `claude-sonnet-4-6`, streaming on |
| Runners | `api.py` (FastAPI: `/chat`, `/chat/stream`), `main.py` (one-shot demo), `langgraph dev` (Studio UI) |
| State | `InMemorySaver` checkpointer in `api.py` and `main.py`; module-level `graph` in `agent.py` has none |
| Containerization | Single `docker-compose.yml` with one `api` service |
| Observability today | None — no tracing, no metrics beyond `/health` |

## 3. Goals

- All LLM calls, tool calls, and graph node traversals from `agent.py` produce traces visible in a Langfuse dashboard.
- A request's `thread_id` maps to a Langfuse **session_id**, so multi-turn conversations group as one session.
- **Self-hosted Langfuse** is the only supported deployment path. Provisioned via a separate Docker Compose file (`docker-compose.langfuse.yml`).
- `agent.py` itself stays untouched. The callback is attached at invocation time in the runner (`api.py`, `main.py`).
- Pending events flush cleanly on process / container shutdown (no silent drops).

## 4. Non-Goals

- Building a chat UI (per [roadmap](../constitution/roadmap.md), UI surface is the Langfuse dashboard itself).
- LLM-as-judge evaluation pipelines.
- Migrating prompts into Langfuse Prompt Management.
- Tracing through `langgraph dev` Studio — module-level `graph` has no callbacks attached and is out of scope for v1.
- Postgres-backed checkpointer (covered separately in Phase 3).

## 5. Architecture Decision — Self-Hosted

**Decision:** Self-hosted Langfuse only. Cloud is deliberately out of scope for this Task Spec (see §10).

Rationale:
- Keeps prompts and trace data inside the team's perimeter — non-negotiable for several downstream use cases.
- Single deployment story to maintain (one set of docs, one compose file).

**Footprint to plan for:** 4 cores / 16 GiB RAM minimum, ~100 GiB storage. Self-hosted via Docker Compose lacks high-availability, scaling, and backups — production hardening is a Phase 3 concern.

Self-hosted Langfuse stack (per upstream):

- `langfuse-web` — UI + API (port 3000)
- `langfuse-worker` — async event processor
- `postgres` — transactional store
- `clickhouse` — OLAP store for traces, observations, scores
- `redis` (or `valkey`) — cache + queues
- `minio` — S3-compatible blob storage for events and exports

All containers must run with **UTC timezone** (Langfuse requirement — non-UTC causes empty/incorrect query results).

## 6. Integration Design

### 6.1 Dependency

Add the SDK as a direct dependency:

```bash
uv add langfuse
```

The Python SDK exposes the LangChain integration at `langfuse.langchain.CallbackHandler`. No separate `langfuse-langchain` package is needed.

### 6.2 Environment variables

Append to `.env` (and create a `.env.example` documenting them):

```env
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_HOST="http://localhost:3000"   # self-hosted Langfuse on the host
```

When the API runs inside Docker (`make docker-up`) and Langfuse runs inside Docker (`make langfuse-up`) on the same host, set `LANGFUSE_HOST=http://host.docker.internal:3000`. The `docker-compose.langfuse.yml` adds `host.docker.internal:host-gateway` so this works on Linux too.

If any of the three is missing, the app **must fail at startup**, not at first request. This avoids silent observability gaps in production.

### 6.3 New module: `tracing.py`

Centralize the handler lifecycle so callers don't repeat themselves:

```python
from functools import lru_cache
from langfuse import get_client
from langfuse.langchain import CallbackHandler


@lru_cache(maxsize=1)
def get_handler() -> CallbackHandler:
    return CallbackHandler()


def shutdown() -> None:
    get_client().shutdown()
```

`lru_cache` gives a process-singleton handler. `shutdown()` flushes the in-memory event queue.

### 6.4 Wire into `api.py`

Three changes:

1. Import `get_handler`, `shutdown`.
2. Extend `_config(thread_id)` to inject the callback and metadata:
   ```python
   def _config(thread_id: str) -> dict:
       return {
           "configurable": {"thread_id": thread_id},
           "callbacks": [get_handler()],
           "metadata": {"langfuse_session_id": thread_id},
       }
   ```
3. Register a shutdown hook so events flush on container stop:
   ```python
   app.add_event_handler("shutdown", shutdown)
   ```

### 6.5 Wire into `main.py`

```python
from tracing import get_handler, shutdown

result = agent.invoke(
    {"messages": [{"role": "user", "content": content}]},
    config={
        "configurable": {"thread_id": "great-gatsby-da"},
        "callbacks": [get_handler()],
        "metadata": {"langfuse_session_id": "great-gatsby-da"},
    },
)
shutdown()
```

`shutdown()` at the end of the script is mandatory — `main.py` exits faster than the SDK's background flush interval.

### 6.6 Self-hosted Langfuse — `docker-compose.langfuse.yml`

Vendor the upstream `docker-compose.yml` from `langfuse/langfuse`, rename it to `docker-compose.langfuse.yml`, and:

- Replace every `# CHANGEME` secret with values from a new `.env.langfuse` file (referenced via `env_file`).
- Confirm all containers carry `TZ=UTC` (or are documented as such).
- Bind only the `langfuse-web` port (3000) to the host; keep storage services on the internal network.

`.env.langfuse` is gitignored, mirroring `.env`.

### 6.7 Makefile additions

```makefile
langfuse-up:    ## Start self-hosted Langfuse stack → http://localhost:3000
	docker compose -f docker-compose.langfuse.yml up -d

langfuse-down:  ## Stop the self-hosted Langfuse stack
	docker compose -f docker-compose.langfuse.yml down

langfuse-logs:  ## Tail logs from langfuse-web
	docker compose -f docker-compose.langfuse.yml logs -f langfuse-web
```

The two compose files (`docker-compose.yml` and `docker-compose.langfuse.yml`) stay independent — the API talks to Langfuse over the host network when both are running locally (`LANGFUSE_HOST=http://host.docker.internal:3000` from inside the API container on macOS / Docker Desktop).

### 6.8 README updates

A new "Observability — Langfuse" section covering:

- Required env vars (`LANGFUSE_*`)
- Cloud quickstart (sign up → copy keys → run)
- Self-hosted quickstart (`make langfuse-up`)
- Where to look in the dashboard (Traces, Sessions filtered by `thread_id`)

## 7. Implementation Steps

In order. Each step is independently verifiable.

1. `uv add langfuse` — pin to current major (v3+).
2. Create `tracing.py` with `get_handler()` and `shutdown()`.
3. Update `api.py`: import handler, extend `_config`, register `shutdown` event handler.
4. Update `main.py`: pass handler + metadata in invocation config, call `shutdown()` at end.
5. Create `.env.example` documenting `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`.
6. Vendor `docker-compose.langfuse.yml` from upstream; create `.env.langfuse.example`; add `.env.langfuse` to `.gitignore`.
7. Add `langfuse-up`, `langfuse-down`, `langfuse-logs` Makefile targets.
8. Add Observability section to `README.md`.
9. End-to-end verification (see §8).
10. Update `docs/constitution/roadmap.md` to check off "Langfuse integration".

## 8. Acceptance Criteria

| # | Criterion |
|---|---|
| AC1 | `POST /chat` produces a Langfuse trace with one root span per request and child spans for each LLM call and tool invocation. |
| AC2 | The same `thread_id` reused across requests groups them under a single Langfuse **session**. |
| AC3 | Stopping the API process (`SIGTERM`, `docker compose down`) flushes pending events — no traces lost in the SDK's in-memory queue. |
| AC4 | Missing or malformed `LANGFUSE_*` env vars cause a clear startup error, not a deferred runtime error. |
| AC5 | `make langfuse-up` brings up a working self-hosted dashboard at `http://localhost:3000` within ~3 minutes — and is the only supported way to reach a Langfuse dashboard. |
| AC6 | `main.py` produces a trace end-to-end (visible in dashboard) when run via `make run`. |
| AC7 | README's Observability section walks a fresh user from zero to a visible trace in under 5 minutes. |

## 9. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Self-hosted infra footprint is heavy (16 GiB / 4 cores) | Documented up front in README; self-hosted Langfuse runs in its own compose file separate from the API stack so it can be stopped independently. |
| Network failures silently drop events | SDK queues events in memory; `shutdown()` flushes on exit; README documents the queued-in-memory trade-off. |
| Singleton `CallbackHandler` across threads | The SDK is thread-safe by design (it's the documented integration pattern). Confirm with a load test before declaring AC1 met. |
| Sensitive prompts persisted in Langfuse storage | Self-hosted by design — data stays on team-controlled infra. Document retention/cleanup policies as a follow-up. |
| Upstream `docker-compose.langfuse.yml` drift | Pin Langfuse images to a specific tag, not `latest`. Track upstream releases manually during Phase 2. |
| Studio dev (`langgraph dev`) traffic is invisible | Documented as a non-goal for v1; revisit if dev-time tracing becomes a real need. |

## 10. Out of Scope (Future Task Specs)

- **Langfuse Cloud configuration** — not supported in this iteration; team chose self-hosting only.
- LLM-as-judge evaluation pipelines.
- Langfuse Prompt Management — moving system prompts into Langfuse with versioning.
- Dataset-driven regression suites.
- Tracing through `langgraph dev` (would require wrapping the module-level `graph`).
- Sampling / cost controls on traces.
- Production hardening of the self-hosted stack (HA, backups, scaling) — Phase 3.

## 11. References

- [Langfuse + LangChain integration](https://langfuse.com/docs/integrations/langchain/tracing)
- [Langfuse self-hosting overview](https://langfuse.com/self-hosting)
- [Langfuse self-hosted via Docker Compose](https://langfuse.com/self-hosting/deployment/docker-compose)
- [Langfuse repository](https://github.com/langfuse/langfuse)

---

[Mission](../constitution/mission.md) | [Tech Stack](../constitution/tech-stack.md) | [Roadmap](../constitution/roadmap.md)
