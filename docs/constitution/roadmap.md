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

- [x] OSS license (MIT) — `LICENSE` at repo root
- [x] GitHub presence — README badges, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`
- [ ] Demo asset — 60-second Loom walkthrough or hosted demo embedded in the README

**Long-form content**

- [ ] Thesis piece — opinionated article staking a position on a practice decision (candidate title: *"What 'production-ready' actually means for an LLM agent"*)

**Distribution**

Ideas:
- [ ] LinkedIn post
- [ ] Subreddit of interests
- [ ] Hacker News — Show HN post once the repo is polished
- [ ] Reddit — launch posts in `r/LangChain` or other subreddits that is useful

---

[Mission](mission.md) | [Tech Stack](tech-stack.md)
