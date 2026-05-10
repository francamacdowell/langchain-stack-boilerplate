# Mission

## Vision

`langchain-stack-boilerplate` exists so that any AI engineer or software developer can start building agent applications without fighting infrastructure. It provides an opinionated, production-shaped baseline — agent framework chosen, HTTP layer wired, container strategy defined — so anyone can clone the repo, understand every decision, and ship a working agent on day one.

## Scope

**In scope**

- Agent orchestration patterns using `deepagents` and LangGraph
- Model provider integration (Claude via Anthropic, Gemini via Google, and OpenRouter gateway)
- HTTP serving with FastAPI (`/health`, `/chat`, `/chat/stream`)
- Local development workflow (`uv` and `make`)
- Containerized deployment of the FastAPI service (Docker + Docker Compose)
- Observability hooks (Langfuse tracing and evaluation)
- Deployment patterns for production (documented, not prescriptive)

**Out of scope**

- Domain-specific business logic
- Frontend or chat UI frameworks
- ML model training or fine-tuning
- Multi-tenant infrastructure
- Non-Python runtimes

## Guiding Principles

**uv-only** — no `pip` in any context, including Docker layers. Reproducibility is enforced by `uv.lock`.

**deepagents-first** — all agent definitions go through `deepagents`. Direct LangGraph usage is reserved for custom orchestration that deepagents does not cover.

**Minimal ceremony** — no abstractions added before they are needed. Three similar lines beat a premature helper.

**Production-shaped from day one** — healthchecks, env-driven config, non-root containers, and `.env` never baked into image layers are defaults, not afterthoughts.

## Success Criteria

A developer clones the repo, sets `ANTHROPIC_API_KEY` in a `.env` file, runs `make install && make serve`, and reaches a working `/chat` endpoint in under five minutes.

A developer discovering the project through a blog post or GitHub understands why each stack decision was made and feels confident adapting it as the starting point for their own agent application.

---

[Tech Stack](tech-stack.md) | [Roadmap](roadmap.md)
