# Roadmap

## Phase 1 — Foundation

*Goal: a well-documented, containerized baseline anyone can clone and run.*

- [x] Containerized FastAPI service (multi-stage Docker + Docker Compose)
- [x] Constitution: mission, tech-stack, roadmap docs

## Phase 2 — Observability & Docs

*Goal: traces in Langfuse, clear usage documentation.*

- [x] [Task Spec](../specs/langfuse-integration.md) — detailed engineering spec for the Langfuse integration work
- [x] Langfuse integration — wire tracing into the agent; document dashboard setup
- [x] README expansion — usage examples, environment setup, per-feature docs

## Phase 3 — Production

*Goal: a deployment target, durable state, and hardened secrets handling.*

- [ ] Persistent checkpointer — `langgraph-checkpoint-postgres` + Postgres in Docker Compose

---

[Mission](mission.md) | [Tech Stack](tech-stack.md)
