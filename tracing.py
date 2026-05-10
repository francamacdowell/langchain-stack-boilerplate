import os
import urllib.error
import urllib.request
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


def _check_langfuse_reachable() -> None:
    # The Langfuse SDK swallows network errors on flush — verify at startup.
    host = os.environ["LANGFUSE_HOST"].rstrip("/")
    url = f"{host}/api/public/health"
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Langfuse health check at {url} returned HTTP {resp.status}.")
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"Cannot reach Langfuse at {host} (probed {url}).\n"
            f"  - In Docker? Set LANGFUSE_HOST=http://host.docker.internal:3000 in .env.\n"
            f"  - Langfuse not running? Start it with: make langfuse-up\n"
            f"Underlying error: {e.reason}"
        ) from e


@lru_cache(maxsize=1)
def get_handler() -> CallbackHandler:
    _require_env()
    _check_langfuse_reachable()
    return CallbackHandler()


def build_config(thread_id: str) -> dict:
    return {
        "configurable": {"thread_id": thread_id},
        "callbacks": [get_handler()],
        "metadata": {"langfuse_session_id": thread_id},
    }


def shutdown() -> None:
    get_client().shutdown()
