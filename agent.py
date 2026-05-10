from dotenv import load_dotenv

load_dotenv()

import urllib.error
import urllib.request

from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool

SYSTEM_PROMPT = """You are a literary data assistant.

## Capabilities

- `fetch_text_from_url`: loads document text from a URL into the conversation.
Do not guess line counts or positions—ground them in tool results from the saved file."""


@tool
def fetch_text_from_url(url: str) -> str:
    """Fetch the document from a URL."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; quickstart-research/1.0)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read()
    except urllib.error.URLError as e:
        return f"Fetch failed: {e}"
    return raw.decode("utf-8", errors="replace")


_model = init_chat_model(
    "claude-sonnet-4-6",
    temperature=0.5,
    timeout=600,
    max_tokens=25000,
    streaming=True,
)


def build_graph(checkpointer=None):
    return create_deep_agent(
        model=_model,
        tools=[fetch_text_from_url],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )


# Module-level graph with no checkpointer — used by `langgraph dev`.
# Each runner (FastAPI, script) attaches its own checkpointer via build_graph().
graph = build_graph()
