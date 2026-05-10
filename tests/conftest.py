import json
import os

# Set dummy env vars before any test file imports agent, tracing, or api.
# os.environ.setdefault does not override vars the user already has set.
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-api03-test")
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "pk-lf-test")
os.environ.setdefault("LANGFUSE_SECRET_KEY", "sk-lf-test")
os.environ.setdefault("LANGFUSE_HOST", "http://localhost:3000")


def collect_sse(content: bytes) -> list:
    """Parse raw SSE bytes into a list of dicts or the '[DONE]' sentinel string."""
    results = []
    for line in content.decode().split("\n"):
        line = line.strip()
        if not line.startswith("data: "):
            continue
        payload = line[6:]
        results.append("[DONE]" if payload == "[DONE]" else json.loads(payload))
    return results
