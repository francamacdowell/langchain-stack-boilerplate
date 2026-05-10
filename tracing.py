import os
from functools import lru_cache

from langfuse import get_client
from langfuse.langchain import CallbackHandler

_REQUIRED = ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST")


def _require_env() -> None:
    missing = [k for k in _REQUIRED if not os.getenv(k)]
    if missing:
        raise RuntimeError(
            f"Missing Langfuse env vars: {', '.join(missing)}. Set them in .env (see .env.example)."
        )


@lru_cache(maxsize=1)
def get_handler() -> CallbackHandler:
    _require_env()
    return CallbackHandler()


def build_config(thread_id: str) -> dict:
    return {
        "configurable": {"thread_id": thread_id},
        "callbacks": [get_handler()],
        "metadata": {"langfuse_session_id": thread_id},
    }


def shutdown() -> None:
    get_client().shutdown()
