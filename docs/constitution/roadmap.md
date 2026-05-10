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

## Phase 3 — Tests & CI

*Goal: high test coverage and automated verification on every change.*

- [x] [Task Spec](../specs/tests-and-ci.md) — detailed engineering spec for the Tests & CI work
- [x] Test module — unit + integration tests for `tracing.py`, `agent.py`, and the `/chat` and `/chat/stream` endpoints (96.7 % line coverage)
- [x] CI pipeline — GitHub Actions workflow (`.github/workflows/ci.yml`) running tests, ruff, lock-check, and Docker build on every push and PR

## Phase 4 — Production

*Goal: a deployment target, durable state, and hardened secrets handling.*

- [x] Persistent checkpointer — `langgraph-checkpoint-postgres` + Postgres in Docker Compose

## Phase 5 — Strategic Communication

*Goal: amplify reach and grow community adoption through targeted content across key channels.*

**Repository readiness**

- [ ] OSS license (MIT or Apache 2.0) — required before any public launch
- [ ] GitHub presence — polished README with badges, demo GIF, and contribution guidelines (`CONTRIBUTING.md`)
- [ ] Demo asset — 60-second Loom walkthrough or hosted demo embedded in the README

**Long-form content**

- [ ] Substack post — deep-dive article covering architecture decisions, lessons learned, and the full stack walkthrough
- [ ] Thesis piece — opinionated article staking a position on a stack or practice decision

**Distribution**

- [ ] LinkedIn post
- [ ] Reddit — launch posts in `r/LangChain` or other subreddits that is useful

---

[Mission](mission.md) | [Tech Stack](tech-stack.md)
