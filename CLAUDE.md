# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Package Management

This project uses `uv`. Always use `uv` — do not use `pip` directly.

```bash
uv run python main.py        # run the app
uv add <package>             # add a dependency
uv sync                      # install/sync dependencies from uv.lock
```

## Stack

- **Python 3.12**
- **deepagents** — the primary agent framework; wraps LangChain with first-class support for Anthropic and Google Gemini models
- **LangChain** + **LangGraph** — graph-based agent orchestration, with `langgraph-prebuilt` for ready-made agent patterns and `langgraph-checkpoint` for state persistence
- **langchain-anthropic** / **langchain-google-genai** — model integrations (Claude and Gemini)

## Architecture

`main.py` is the entry point placeholder. The intended pattern for this boilerplate is:

- Define agents using `deepagents` (which builds on LangChain tool/message abstractions)
- Compose multi-agent workflows with LangGraph (`StateGraph`, prebuilt `create_react_agent`, etc.)
- Wire model providers via `langchain-anthropic` (Claude) or `langchain-google-genai` (Gemini) — both are installed and ready to use
- LangGraph checkpointers (from `langgraph-checkpoint`) enable stateful/resumable workflows when needed
